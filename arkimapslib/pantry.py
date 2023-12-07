# from __future__ import annotations
import contextlib
import datetime
import logging
import os
import re
import subprocess
import sys
import tempfile
from typing import TYPE_CHECKING, Any, BinaryIO, Dict, List, NamedTuple, Optional, Tuple

try:
    import arkimet
except ModuleNotFoundError:
    arkimet = None

from . import inputs

if TYPE_CHECKING:
    from . import orders, outputbundle

log = logging.getLogger("arkimaps.pantry")


class ProcessLogEntry(NamedTuple):
    """
    Entry used to trace input processing operations
    """

    input: inputs.Input
    message: str


class Pantry:
    """
    Storage of GRIB files used as inputs to recipes
    """

    def __init__(self, *args, **kw) -> None:
        # List of input definitions, indexed by name
        self.inputs: Dict[str, List[inputs.Input]] = {}
        # Log of input processing operations performed
        self.process_log: List[ProcessLogEntry] = []

    def summarize_inputs(self, orders: List["orders.Order"]) -> Dict[str, Any]:
        """
        Return a JSON-serializable summary about input processing
        """
        # Collect which inputs have been used by which recipes
        for order in orders:
            for input_file in order.input_files.values():
                input_file.info.stats.used_by.add(order.recipe)

        res: Dict[str, Dict[str, Any]] = {}
        for name, inps in self.inputs.items():
            for input in inps:
                if input.stats.used_by or input.stats.computation_log:
                    res[name] = input.stats.summarize()
        return res

    def log_input_processing(self, input: inputs.Input, message: str):
        """
        Trace one input processing step
        """
        self.process_log.append(ProcessLogEntry(input, message))

    def add_input(self, inp: "inputs.Input"):
        """
        Add an Input definition
        """
        old = self.inputs.get(inp.name)
        if old is None:
            # First time we see this input: add it
            self.inputs[inp.name] = [inp]
            return

        if len(old) == 1 and old[0].model is None:
            # We had an input for model=None (all models)
            # so we refuse to add more
            raise RuntimeError(
                f"{inp.defined_in}: input {inp.name} for (any model) already defined in {old[0].defined_in}"
            )

        for i in old:
            if i.model == inp.model:
                # We already had an input for this model name
                raise RuntimeError(
                    f"{inp.defined_in}: input {inp.name} (model {inp.model}) already defined in {i.defined_in}"
                )

        # Input for a new model: store it
        old.append(inp)

    def fill(self, path: Optional[str] = None):
        """
        Read data from standard input and acquire it into the pantry.

        If path is given, read dispatching input from the given path. If None,
        read from stdin
        """
        raise NotImplementedError(f"{self.__class__.__name__}.fill() not implemented")

    def rescan(self):
        """
        Rescan the contents of an existing working directory.

        Use this method when processing a working directory dispatched by a
        different Pantry instance
        """
        raise NotImplementedError(f"{self.__class__.__name__}.rescan() not implemented")

    def store_processing_artifacts(self, tarout):
        """
        Store relevant processing artifacts in the output tarball
        """
        pass

    @contextlib.contextmanager
    def open_dispatch_input(self, path: Optional[str] = None):
        """
        Open the binary input stream, from a file, or standard input if path is
        None
        """
        if path is None:
            yield sys.stdin.buffer
        else:
            with open(path, "rb") as fd:
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

    def __init__(self, root: str, **kw):
        super().__init__(**kw)
        self.data_root: str = os.path.join(root, "pantry")

    def get_basename(self, inp: "inputs.Input", instant: "inputs.Instant", fmt="grib") -> str:
        """
        Return the relative name within the pantry of the file corresponding to
        the given input and instant
        """
        if inp.model is None:
            pantry_basename = inp.name
        else:
            pantry_basename = f"{inp.model}_{inp.name}"
        return pantry_basename + f"{instant.pantry_suffix()}.{fmt}"

    def get_fullname(self, inp: "inputs.Input", instant: "inputs.Instant", fmt="grib") -> str:
        """
        Return the relative name within the pantry of the file corresponding to
        the given input and instant
        """
        return os.path.join(self.data_root, self.get_basename(inp, instant, fmt=fmt))

    def get_accessory_fullname(self, inp: "inputs.Input", suffix: str) -> str:
        """
        Return the relative name within the pantry of the file corresponding to
        the given input and instant
        """
        if inp.model is None:
            pantry_basename = inp.name
        else:
            pantry_basename = f"{inp.model}_{inp.name}"
        return os.path.join(self.data_root, f"{pantry_basename}-{suffix}")

    def get_input_file(self, inp: "inputs.Input", instant: "inputs.Instant", fmt="grib") -> "inputs.InputFile":
        """
        Return an InputFile from the pantry corresponding to the given input and instant
        """
        return inputs.InputFile(self.get_fullname(inp, instant, fmt=fmt), inp, instant)

    def get_eccodes_fullname(self, inp: "inputs.Input", fmt="grib") -> str:
        if inp.model is None:
            pantry_basename = inp.name
        else:
            pantry_basename = f"{inp.model}_{inp.name}"
        return f"{self.data_root}/{pantry_basename}_[year]_[month]_[day]_[hour]_[minute]_[second]+[endStep].{fmt}"

    def get_instants(
        self, input_name: str, model: Optional[str] = None
    ) -> Dict[Optional[inputs.Instant], "inputs.InputFile"]:
        """
        Return the instants available in the pantry for the input with the given
        name
        """
        inps = self.inputs.get(input_name)
        if inps is None:
            return {}

        res: Dict[Optional[inputs.Instant], "inputs.InputFile"] = {}
        for inp in inps:
            # Skip inputs for mismatching models (see #114)
            if model is not None and inp.model is not None and model != inp.model:
                continue
            instants = inp.get_instants(self)
            for instant, input_file in instants.items():
                # Keep the first available version for each instant
                res.setdefault(instant, input_file)
        return res

    def notify_pantry_filled(self):
        """
        Let inputs know that we are done filtering initial data
        """
        for inps in self.inputs.values():
            for inp in inps:
                inp.on_pantry_filled(self)

    def rescan(self):
        fn_match = re.compile(
            r"^(?:(?P<model>\w+)_)?(?P<name>\w+)_" r"(?P<reftime>\d+_\d+_\d+_\d+_\d+_\d+)\+(?P<step>\d+)\.(?P<ext>\w+)$"
        )
        for fn in os.listdir(self.data_root):
            if "grib_filter_rules" in fn or fn == "static" or fn.endswith("-processed"):
                continue

            mo = fn_match.match(fn)
            if not mo:
                log.warning("%s: unrecognised file found in pantry", fn)
                continue

            inps = self.inputs.get(mo.group("name"))
            model = mo.group("model")
            if model:
                inps = [inp for inp in inps if inp.model == model]
            inp = inps[0]

            reftime = mo.group("reftime")
            step = int(mo.group("step"))
            inp.add_instant(inputs.Instant(datetime.datetime.strptime(reftime, "%Y_%m_%d_%H_%M_%S"), step))


if arkimet is not None:

    class ArkimetEmptyPantry(EmptyPantry):
        """
        Storage-less arkimet pantry only used to load recipes
        """

        def __init__(self, session: "arkimet.dataset.Session", **kw):
            super().__init__(**kw)
            self.session = session

        def add_input(self, inp: "inputs.Input"):
            inp.compile_arkimet_matcher(self.session)
            super().add_input(inp)

    class ArkimetPantry(DiskPantry):
        """
        Arkimet-based storage of GRIB files to be processed
        """

        def __init__(self, session: arkimet.dataset.Session, **kw):
            super().__init__(**kw)
            self.session = session

        def add_input(self, inp: "inputs.Input"):
            inp.compile_arkimet_matcher(self.session)
            super().add_input(inp)

        def fill(self, path: Optional[str] = None):
            """
            Read data from standard input and acquire it into the pantry
            """
            # Create pantry dir if missing
            os.makedirs(self.data_root, exist_ok=True)

            # Dispatch todo-list
            todo_list: List[Tuple[Any, "inputs.Input"]] = []
            for inps in self.inputs.values():
                for inp in inps:
                    if getattr(inp, "arkimet", None) == "skip":
                        continue
                    matcher = getattr(inp, "arkimet_matcher", None)
                    if matcher is None:
                        if hasattr(inp, "eccodes"):
                            log.info(
                                "%s (model=%s): skipping input with no arkimet matcher filter", inp.name, inp.model
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

        def __init__(self, pantry: "ArkimetPantry", todo_list: List[Tuple[Any, "inputs.Input"]]):
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
                            step = inputs.ModelStep.from_grib1(output_step, trange["unit"])
                        except NotImplementedError as e:
                            log.warning("skipping input: %s", e)
                            continue
                    elif style == "Timedef":
                        output_step = trange["step_len"]
                        output_step_unit = trange["step_unit"]
                        try:
                            step = inputs.ModelStep.from_timedef(output_step, output_step_unit)
                        except NotImplementedError as e:
                            log.warning("skipping input: %s", e)
                            continue
                    else:
                        log.warning("unsupported timerange style in %s: skipping input", trange)
                        continue

                    reftime = md.to_python("reftime")["time"]
                    instant = inputs.Instant(reftime, step)

                    source = md.to_python("source")
                    if inp.model is None:
                        pantry_basename = inp.name
                    else:
                        pantry_basename = f"{inp.model}_{inp.name}"

                    relname = pantry_basename + instant.pantry_suffix() + "." + source["format"]

                    dest = os.path.join(self.data_root, relname)
                    # TODO: implement Metadata.write_data to write directly without
                    # needing to create an intermediate python bytes object
                    with open(dest, "ab") as out:
                        out.write(md.data)

                    # Take note of having added one element to this file
                    inp.add_instant(instant)
            return True

        def read(self, infd: BinaryIO):
            """
            Read data from an input file, or standard input.

            The input file is the output of arki-query --inline, which is the same
            as is given as input to arkimet processors.
            """
            arkimet.Metadata.read_bundle(infd, dest=self.dispatch)


class EccodesPantry(DiskPantry):
    """
    eccodes-based storage of GRIB files to be processed
    """

    def __init__(self, grib_input=False, **kw):
        super().__init__(**kw)
        self.grib_input = grib_input
        self.grib_filter_rules = os.path.join(self.data_root, "grib_filter_rules")

    def fill(self, path: Optional[str] = None):
        """
        Read data from standard input and acquire it into the pantry
        """
        # Create pantry dir if missing
        os.makedirs(self.data_root, exist_ok=True)

        # Build grib_filter rules
        with open(self.grib_filter_rules, "w") as f:
            for inps in self.inputs.values():
                for inp in inps:
                    eccodes = getattr(inp, "eccodes", None)
                    if eccodes is None:
                        if hasattr(inp, "arkimet_matcher"):
                            log.info("%s (model=%s): skipping input with no eccodes filter", inp.name, inp.model)
                        continue
                    elif eccodes == "skip":
                        continue
                    print(f"if ( {eccodes} ) {{", file=f)
                    print(
                        f'  print "s:{inp.model or ""},{inp.name},'
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
        model, name, ye, mo, da, ho, mi, se, step = line[2:].split(b",")
        reftime = datetime.datetime(int(ye), int(mo), int(da), int(ho), int(mi), int(se))
        if not model:
            model = None
        else:
            model = model.decode()
        for inp in self.inputs[name.decode()]:
            if inp.model == model:
                inp.add_instant(inputs.Instant(reftime, int(step)))

    def read_grib(self, path: Optional[str]):
        """
        Run grib_filter on GRIB input
        """
        cmd = ["grib_filter", self.grib_filter_rules, ("-" if path is None else path)]
        res = subprocess.run(cmd, stdin=sys.stdin, stdout=subprocess.PIPE, check=True)
        for line in res.stdout.splitlines():
            self._parse_filter_output(line)

    def read_arkimet(self, path: Optional[str]):
        """
        Run grib_filter on arkimet input
        """
        with tempfile.TemporaryFile("w+b") as outfd:
            try:
                proc = subprocess.Popen(
                    ["grib_filter", self.grib_filter_rules, "-"], stdin=subprocess.PIPE, stdout=outfd
                )

                def dispatch(md: arkimet.Metadata) -> bool:
                    proc.stdin.write(md.data)
                    return True

                with self.open_dispatch_input(path=path) as infd:
                    arkimet.Metadata.read_bundle(infd, dest=dispatch)
            finally:
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
