# from __future__ import annotations
from typing import Optional, BinaryIO, List, Tuple, Any, Dict
import contextlib
import logging
import os
import subprocess
import sys
import tempfile

try:
    import arkimet
except ModuleNotFoundError:
    arkimet = None

from . import inputs

log = logging.getLogger("arkimaps.pantry")


class Pantry:
    """
    Storage of GRIB files used as inputs to recipes
    """
    def __init__(self, *args, **kw):
        # List of input definitions, indexed by name
        self.inputs: Dict[str, List[inputs.Input]] = {}

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
                    f"{inp.defined_in}: input {inp.name} for (any model) already defined in {old[0].defined_in}")

        for i in old:
            if i.model == inp.model:
                # We already had an input for this model name
                raise RuntimeError(
                        f"{inp.defined_in}: input {inp.name} (model {inp.model}) already defined in {i.defined_in}")

        # Input for a new model: store it
        old.append(inp)

    def fill(self, path: Optional[str] = None):
        """
        Read data from standard input and acquire it into the pantry.

        If path is given, read dispatching input from the given path. If None,
        read from stdin
        """
        raise NotImplementedError(f"{self.__class__.__name__}.fill() not implemented")

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

    def get_steps(self, input_name: str) -> Dict[Optional[int], "inputs.InputFile"]:
        """
        Return the steps available in the pantry for the input with the given
        name
        """
        inps = self.inputs.get(input_name)
        if inps is None:
            return {}

        res: Dict[Optional[int], "inputs.InputFile"] = {}
        for inp in inps:
            steps = inp.get_steps(self)
            for step, input_file in steps.items():
                # Keep the first available version for each step
                res.setdefault(step, input_file)
        return res

    def notify_pantry_filled(self):
        """
        Let inputs know that we are done filtering initial data
        """
        for inps in self.inputs.values():
            for inp in inps:
                inp.on_pantry_filled(self)


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
                    matcher = getattr(inp, "arkimet_matcher", None)
                    if matcher is None:
                        if hasattr(inp, "eccodes"):
                            log.info(
                                "%s (model=%s): skipping input with no arkimet matcher filter",
                                inp.name, inp.model)
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
        def __init__(self, pantry: "Pantry", todo_list: List[Tuple[Any, "inputs.Input"]]):
            self.pantry = pantry
            self.data_root = pantry.data_root
            self.todo_list = todo_list

        def dispatch(self, md: arkimet.Metadata) -> bool:
            for matcher, inp in self.todo_list:
                if matcher.match(md):
                    trange = md.to_python("timerange")
                    style = trange["style"]
                    if style == "GRIB1":
                        if trange['trange_type'] in (0, 1):
                            output_step = trange['p1']
                        elif trange['trange_type'] in (2, 3, 4, 5, 6, 7):
                            output_step = trange['p2']
                        else:
                            log.warning("unsupported timerange %s: skipping input", trange)
                            continue
                    elif style == "Timedef":
                        output_step = trange["step_len"]
                    else:
                        log.warning("unsupported timerange style in %s: skipping input", trange)
                        continue

                    source = md.to_python("source")
                    relname = inp.pantry_basename + f"+{output_step}.{source['format']}"

                    dest = os.path.join(self.data_root, relname)
                    # TODO: implement Metadata.write_data to write directly without
                    # needing to create an intermediate python bytes object
                    with open(dest, "ab") as out:
                        out.write(md.data)

                    # Take note of having added one element to this file
                    inp.add_step(output_step)
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
                    print(f"if ( {eccodes} ) {{", file=f)
                    print(f'  print "s:{inp.model or ""},{inp.name},[endStep]";', file=f)
                    print(f'  write "{self.data_root}/{inp.pantry_basename}+[endStep].grib";', file=f)
                    print("}", file=f)

        if self.grib_input:
            self.read_grib(path)
        else:
            self.read_arkimet(path)

        self.notify_pantry_filled()

    def _parse_filter_output(self, line: bytes):
        if not line.startswith(b"s:"):
            return
        model, name, step = line[2:].split(b",")
        if not model:
            model = None
        else:
            model = model.decode()
        for inp in self.inputs[name.decode()]:
            if inp.model == model:
                inp.add_step(int(step))

    def read_grib(self, path: str):
        """
        Run grib_filter on GRIB input
        """
        cmd = ["grib_filter", self.grib_filter_rules, ("-" if path is None else path)]
        res = subprocess.run(cmd, stdin=sys.stdin, stdout=subprocess.PIPE, check=True)
        for line in res.stdout.splitlines():
            self._parse_filter_output(line)

    def read_arkimet(self, path: str):
        """
        Run grib_filter on arkimet input
        """
        with tempfile.TemporaryFile("w+b") as outfd:
            try:
                proc = subprocess.Popen(
                        ["grib_filter", self.grib_filter_rules, "-"],
                        stdin=subprocess.PIPE, stdout=outfd)

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

    def store_processing_artifacts(self, tarout):
        """
        Store relevant processing artifacts in the output tarball
        """
        tarout.add(name=self.grib_filter_rules, arcname="grib_filter_rules")
