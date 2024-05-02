# from __future__ import annotations
import abc
import contextlib
import datetime
import logging
import os
import re
import subprocess
import sys
import tempfile
from collections import defaultdict
from pathlib import Path
from typing import TYPE_CHECKING, Any, BinaryIO, Dict, List, NamedTuple, Optional, Set, Tuple

try:
    import arkimet

    HAS_ARKIMET = True
except ModuleNotFoundError:
    HAS_ARKIMET = False

import eccodes

from .inputs import Input, InputFile, Inputs, Instant
from .outputbundle import InputProcessingStats
from .types import ModelStep

if TYPE_CHECKING:
    from . import orders, outputbundle

log = logging.getLogger("arkimaps.pantry")


def keep_only_first_grib(fname: Path) -> None:
    """
    Truncate a GRIB file so that only the first GRIB is kept
    """
    with fname.open("r+b") as infd:
        gid = eccodes.codes_grib_new_from_file(infd)
        try:
            if eccodes.codes_get_message_offset(gid) != 0:
                raise RuntimeError(f"{fname}: first grib does not start at offset 0")
            infd.truncate(eccodes.codes_get_message_size(gid))
        finally:
            eccodes.codes_release(gid)


class ProcessLogEntry(NamedTuple):
    """
    Entry used to trace input processing operations
    """

    input: Input
    message: str


class Pantry(abc.ABC):
    """
    Storage of GRIB files used as inputs to recipes
    """

    def __init__(self, inputs: Inputs, **kwargs) -> None:
        # List of input definitions, indexed by name
        self.inputs = inputs
        # Log of input processing operations performed
        self.process_log: List[ProcessLogEntry] = []
        # Per-input processing statistics
        self.input_stats: Dict[Input, InputProcessingStats] = defaultdict(InputProcessingStats)
        # Set of available steps for each input
        self.input_instants: Dict[Input, Set[Instant]] = defaultdict(set)
        # Set of input steps for which the data in the pantry contains multiple
        # elements and needs to be truncated
        self.input_instants_to_truncate: Dict[Input, Set[Instant]] = defaultdict(set)

    def add_instant(self, inp: Input, instant: Instant) -> None:
        """
        Notify that the pantry contains data for this input for the given step
        """
        instants = self.input_instants[inp]

        if instant in instants:
            log.warning("%s: multiple data found for %s", inp.name, instant)
            self.input_instants_to_truncate[inp].add(instant)
        instants.add(instant)

    def log_input_processing(self, input: Input, message: str):
        """
        Trace one input processing step
        """
        self.process_log.append(ProcessLogEntry(input, message))

    def store_processing_artifacts(self, tarout):
        """
        Store relevant processing artifacts in the output tarball
        """
        pass

    @contextlib.contextmanager
    def open_dispatch_input(self, path: Optional[Path] = None):
        """
        Open the binary input stream, from a file, or standard input if path is
        None
        """
        if path is None:
            yield sys.stdin.buffer
        else:
            with path.open("rb") as fd:
                yield fd


class EmptyPantry(Pantry):
    """
    Pantry with no disk-based storage, used as input registry only to generate documentation
    """

    pass


class DiskPantry(Pantry):
    """
    Pantry with disk-based storage
    """

    def __init__(self, *, root: Path, **kwargs) -> None:
        super().__init__(**kwargs)
        self.data_root: Path = root / "pantry"

    def get_basename(self, inp: Input, instant: Instant, fmt="grib") -> Path:
        """
        Return the relative name within the pantry of the file corresponding to
        the given input and instant
        """
        if inp.spec.model is None:
            pantry_basename = inp.name
        else:
            pantry_basename = f"{inp.spec.model}_{inp.name}"
        return Path(pantry_basename + f"{instant.pantry_suffix()}.{fmt}")

    def get_fullname(self, inp: Input, instant: Instant, fmt="grib") -> Path:
        """
        Return the relative name within the pantry of the file corresponding to
        the given input and instant
        """
        return self.data_root / self.get_basename(inp, instant, fmt=fmt)

    def get_accessory_fullname(self, inp: Input, suffix: str) -> Path:
        """
        Return the relative name within the pantry of the file corresponding to
        the given input and instant
        """
        if inp.spec.model is None:
            pantry_basename = inp.name
        else:
            pantry_basename = f"{inp.spec.model}_{inp.name}"
        return self.data_root / f"{pantry_basename}-{suffix}"

    def get_input_file(self, inp: Input, instant: Instant, fmt="grib") -> InputFile:
        """
        Return an InputFile from the pantry corresponding to the given input and instant
        """
        return InputFile(self.get_fullname(inp, instant, fmt=fmt), inp, instant)

    def get_eccodes_fullname(self, inp: Input, fmt="grib") -> Path:
        if inp.spec.model is None:
            pantry_basename = inp.name
        else:
            pantry_basename = f"{inp.spec.model}_{inp.name}"
        return self.data_root / f"{pantry_basename}_[year]_[month]_[day]_[hour]_[minute]_[second]+[endStep].{fmt}"

    def get_instants(self, input_name: str, model: Optional[str] = None) -> Dict[Optional[Instant], InputFile]:
        """
        Return the instants available in the pantry for the input with the given
        name
        """
        res: Dict[Optional[Instant], InputFile] = {}

        # Skip inputs for mismatching models (see #114)
        inps = self.inputs.get(input_name, model)
        if not inps:
            return res

        for inp in inps:
            instants = inp.get_instants(self)
            for instant, input_file in instants.items():
                # Keep the first available version for each instant
                res.setdefault(instant, input_file)
        return res

    def notify_pantry_filled(self):
        """
        Let inputs know that we are done filtering initial data
        """
        for inp, instants in self.input_instants_to_truncate.items():
            for instant in instants:
                fname = self.get_fullname(inp, instant)
                keep_only_first_grib(fname)
        self.input_instants_to_truncate.clear()

    def rescan(self):
        fn_match = re.compile(
            r"^(?:(?P<model>\w+)_)?(?P<name>\w+)_" r"(?P<reftime>\d+_\d+_\d+_\d+_\d+_\d+)\+(?P<step>\d+)\.(?P<ext>\w+)$"
        )
        for fn in self.data_root.iterdir():
            if "grib_filter_rules" in fn.name or fn.name == "static" or fn.name.endswith("-processed"):
                continue

            mo = fn_match.match(fn.name)
            if not mo:
                log.warning("%s: unrecognised file found in pantry", fn)
                continue

            inps = self.inputs.get(mo.group("name"))
            model = mo.group("model")
            if model:
                inps = [inp for inp in inps if inp.spec.model == model]
            inp = inps[0]

            reftime = mo.group("reftime")
            step = int(mo.group("step"))
            self.add_instant(inp, Instant(datetime.datetime.strptime(reftime, "%Y_%m_%d_%H_%M_%S"), step))


class DispatchPantry(DiskPantry, abc.ABC):
    """
    Pantry with dispatching methods
    """

    @abc.abstractmethod
    def fill(self, path: Optional[Path] = None, input_filter: Optional[Set[str]] = None):
        """
        Read data from standard input and acquire it into the pantry.

        If path is given, read dispatching input from the given path. If None,
        read from stdin
        """


if HAS_ARKIMET:

    class ArkimetBasePantry(Pantry):
        """
        Base for all Arkimet pantries
        """

        def __init__(self, session: "arkimet.dataset.Session", **kw):
            super().__init__(**kw)
            self.session = session
            self.cached_matchers: Dict[Input, Optional[arkimet.Matcher]] = {}

        def arkimet_matcher(self, inp: Input) -> Optional[arkimet.Matcher]:
            """
            If the input has an arkimet match expression, return its compiled
            Matcher
            """
            if inp not in self.cached_matchers:
                cached: Optional[arkimet.Matcher] = None
                expression: Optional[str] = getattr(inp.spec, "arkimet", None)
                if expression is not None and expression != "skip":
                    cached = self.session.matcher(inp.spec.arkimet)
                self.cached_matchers[inp] = cached
                return cached
            else:
                return self.cached_matchers[inp]

    class ArkimetEmptyPantry(ArkimetBasePantry, EmptyPantry):
        """
        Storage-less arkimet pantry only used to load recipes
        """

    class ArkimetPantry(ArkimetBasePantry, DispatchPantry):
        """
        Arkimet-based storage of GRIB files to be processed
        """

        def fill(self, path: Optional[Path] = None, input_filter: Optional[Set[str]] = None):
            """
            Read data from standard input and acquire it into the pantry
            """
            # Create pantry dir if missing
            self.data_root.mkdir(parents=True, exist_ok=True)

            # Dispatch todo-list
            todo_list: List[Tuple[Any, Input]] = []
            for inps in self.inputs.values():
                for inp in inps:
                    if getattr(inp.spec, "arkimet", None) == "skip":
                        continue
                    if input_filter is not None and inp.name not in input_filter:
                        continue
                    matcher = self.arkimet_matcher(inp)
                    if matcher is None:
                        if hasattr(inp.spec, "eccodes"):
                            log.info(
                                "%s (model=%s): skipping input with no arkimet matcher filter", inp.name, inp.spec.model
                            )
                        continue
                    todo_list.append((matcher, inp))

            dispatcher = ArkimetDispatcher(self, todo_list)
            with self.open_dispatch_input(path=path) as infd:
                dispatcher.read(infd)

            self.notify_pantry_filled()

    class ArkimetDispatcher:
        """
        Read a stream of arkimet metadata and store its data into a dataset
        """

        def __init__(self, pantry: "ArkimetPantry", todo_list: List[Tuple[Any, Input]]) -> None:
            self.pantry = pantry
            self.data_root = pantry.data_root
            self.todo_list = todo_list

        def dispatch(self, md: arkimet.Metadata) -> bool:
            for matcher, inp in self.todo_list:
                if matcher.match(md):
                    trange = md.to_python("timerange")
                    style = trange["style"]
                    if style == "GRIB1":
                        if trange["trange_type"] in (0, 1):
                            output_step = trange["p1"]
                        elif trange["trange_type"] in (2, 3, 4, 5, 6, 7):
                            output_step = trange["p2"]
                        else:
                            log.warning("unsupported timerange %s: skipping input", trange)
                            continue
                        try:
                            step = ModelStep.from_grib1(output_step, trange["unit"])
                        except NotImplementedError as e:
                            log.warning("skipping input: %s", e)
                            continue
                    elif style == "Timedef":
                        output_step = trange["step_len"]
                        output_step_unit = trange["step_unit"]
                        try:
                            step = ModelStep.from_timedef(output_step, output_step_unit)
                        except NotImplementedError as e:
                            log.warning("skipping input: %s", e)
                            continue
                    else:
                        log.warning("unsupported timerange style in %s: skipping input", trange)
                        continue

                    reftime = md.to_python("reftime")["time"]
                    instant = Instant(reftime, step)

                    source = md.to_python("source")
                    if inp.spec.model is None:
                        pantry_basename = inp.name
                    else:
                        pantry_basename = f"{inp.spec.model}_{inp.name}"

                    relname = pantry_basename + instant.pantry_suffix() + "." + source["format"]

                    dest = os.path.join(self.data_root, relname)
                    # TODO: implement Metadata.write_data to write directly without
                    # needing to create an intermediate python bytes object
                    with open(dest, "ab") as out:
                        out.write(md.data)

                    # Take note of having added one element to this file
                    self.pantry.add_instant(inp, instant)
            return True

        def read(self, infd: BinaryIO):
            """
            Read data from an input file, or standard input.

            The input file is the output of arki-query --inline, which is the same
            as is given as input to arkimet processors.
            """
            arkimet.Metadata.read_bundle(infd, dest=self.dispatch)


class EccodesPantry(DispatchPantry):
    """
    eccodes-based storage of GRIB files to be processed
    """

    def __init__(self, grib_input=False, **kwargs) -> None:
        super().__init__(**kwargs)
        self.grib_input = grib_input
        self.grib_filter_rules = os.path.join(self.data_root, "grib_filter_rules")

    def fill(self, path: Optional[Path] = None, input_filter: Optional[Set[str]] = None):
        """
        Read data from standard input and acquire it into the pantry
        """
        # Create pantry dir if missing
        self.data_root.mkdir(parents=True, exist_ok=True)

        # Build grib_filter rules
        with open(self.grib_filter_rules, "w") as f:
            for inps in self.inputs.values():
                for inp in inps:
                    eccodes = getattr(inp.spec, "eccodes", None)
                    if eccodes is None:
                        if hasattr(inp.spec, "arkimet"):
                            log.info("%s (model=%s): skipping input with no eccodes filter", inp.name, inp.spec.model)
                        continue
                    elif eccodes == "skip":
                        continue
                    if input_filter is not None and inp.name not in input_filter:
                        continue
                    print(f"if ( {eccodes} ) {{", file=f)
                    print(
                        f'  print "s:{inp.spec.model or ""},{inp.name},'
                        '[year],[month],[day],[hour],[minute],[second],[endStep]";',
                        file=f,
                    )
                    print(f'  write "{self.get_eccodes_fullname(inp)}";', file=f)
                    print("}", file=f)

        if self.grib_input:
            self.read_grib(path)
        else:
            self.read_arkimet(path)

        self.notify_pantry_filled()

    def _parse_filter_output(self, line: bytes):
        if not line.startswith(b"s:"):
            return
        modelname, name, ye, mo, da, ho, mi, se, step = line[2:].split(b",")
        reftime = datetime.datetime(int(ye), int(mo), int(da), int(ho), int(mi), int(se))
        model: Optional[str]
        if not modelname:
            model = None
        else:
            model = modelname.decode()
        for inp in self.inputs[name.decode()]:
            if inp.spec.model == model:
                self.add_instant(inp, Instant(reftime, int(step)))

    def read_grib(self, path: Optional[Path]):
        """
        Run grib_filter on GRIB input
        """
        cmd = ["grib_filter", self.grib_filter_rules, ("-" if path is None else str(path))]
        res = subprocess.run(cmd, stdin=sys.stdin, stdout=subprocess.PIPE, check=True)
        for line in res.stdout.splitlines():
            self._parse_filter_output(line)

    def read_arkimet(self, path: Optional[Path]):
        """
        Run grib_filter on arkimet input
        """
        with tempfile.TemporaryFile("w+b") as outfd:
            try:
                proc = subprocess.Popen(
                    ["grib_filter", self.grib_filter_rules, "-"], stdin=subprocess.PIPE, stdout=outfd
                )

                def dispatch(md: arkimet.Metadata) -> bool:
                    assert proc.stdin is not None
                    proc.stdin.write(md.data)
                    return True

                with self.open_dispatch_input(path=path) as infd:
                    arkimet.Metadata.read_bundle(infd, dest=dispatch)
            finally:
                assert proc.stdin is not None
                proc.stdin.close()
                proc.wait()
                if proc.returncode != 0:
                    raise RuntimeError(f"grib_filter failed with return code {proc.returncode}")

            outfd.seek(0)
            for line in outfd:
                self._parse_filter_output(line)

    def store_processing_artifacts(self, bundle: "outputbundle.Writer"):
        """
        Store relevant processing artifacts in the output tarball
        """
        with open(self.grib_filter_rules, "rb") as data:
            bundle.add_artifact("grib_filter_rules", data)
