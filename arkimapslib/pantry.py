# from __future__ import annotations
# from typing import Optional, BinaryIO, List, Iterator, Tuple
from typing import Optional, BinaryIO, List, Tuple, Dict
import contextlib
import subprocess
import sys
import os
import logging

# if TYPE_CHECKING:
from .inputs import Input, InputFile
from . import recipes
try:
    import arkimet
except ModuleNotFoundError:
    arkimet = None

log = logging.getLogger("arkimaps.pantry")


class Pantry:
    """
    Storage of GRIB files used as inputs to recipes
    """
    def __init__(self):
        # List of input definitions, indexed by name
        self.inputs: Dict[str, List[Input]] = {}

    def add_input(self, inp: Input):
        """
        Add an Input definition to this pantry
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

    def list_all_inputs(self, recipe: "recipes.Recipe") -> List[str]:
        """
        List inputs used by a recipe, and all their inputs, recursively
        """
        res = []
        for input_name in recipe.list_inputs():
            for inp in self.inputs[input_name]:
                inp.add_all_inputs(self, res)
        return res

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


class DiskPantry(Pantry):
    """
    Pantry with disk-based storage
    """
    def __init__(self, root: str):
        super().__init__()
        # Root directory where inputs are stored
        self.data_root = os.path.join(root, "pantry")

    def get_steps(self, input_name: str) -> Dict[int, InputFile]:
        """
        Return the steps available in the pantry for the input with the given
        name
        """
        inputs = self.inputs.get(input_name)
        if inputs is None:
            return {}

        res = {}
        for inp in inputs:
            steps = inp.get_steps(self)
            for step, input_file in steps.items():
                # Keep the first available version for each step
                res.setdefault(step, input_file)
        return res


class ArkimetEmptyPantry(Pantry):
    """
    Storage-less arkimet pantry only used to load recipes
    """
    def __init__(self, session: arkimet.dataset.Session, **kw):
        super().__init__(**kw)
        self.session = session

    def add_input(self, inp: Input):
        inp.compile_arkimet_matcher(self.session)
        super().add_input(inp)


class ArkimetPantry(DiskPantry):
    """
    Arkimet-based storage of GRIB files to be processed
    """
    def __init__(self, session: arkimet.dataset.Session, **kw):
        super().__init__(**kw)
        self.session = session

    def add_input(self, inp: Input):
        inp.compile_arkimet_matcher(self.session)
        super().add_input(inp)

    def fill(self, path: Optional[str] = None):
        """
        Read data from standard input and acquire it into the pantry
        """
        # Create pantry dir if missing
        os.makedirs(self.data_root, exist_ok=True)

        # Dispatch todo-list
        match: List[Tuple[Input, str, str]] = []
        for inputs in self.inputs.values():
            for inp in inputs:
                if not getattr(inp, "arkimet_matcher", None):
                    log.info("%s (model=%s): skipping input with no arkimet matcher filter", inp.name, inp.model)
                    continue
                match.append(inp)

        dispatcher = ArkimetDispatcher(self.data_root, match)
        with self.open_dispatch_input(path=path) as infd:
            dispatcher.read(infd)


class ArkimetDispatcher:
    """
    Read a stream of arkimet metadata and store its data into a dataset
    """
    def __init__(self, data_root: str, todo_list: List[Input]):
        self.data_root = data_root
        self.todo_list = todo_list

    def dispatch(self, md: arkimet.Metadata) -> bool:
        for inp in self.todo_list:
            if inp.arkimet_matcher.match(md):
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

                dest = os.path.join(self.data_root, inp.pantry_basename + f"+{output_step}.{source['format']}")
                # TODO: implement Metadata.write_data to write directly without
                # needing to create an intermediate python bytes object
                with open(dest, "ab") as out:
                    out.write(md.data)
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
    def __init__(self, root: str):
        super().__init__(root)
        self.grib_filter_rules = os.path.join(self.data_root, "grib_filter_rules")

    def fill(self, path: Optional[str] = None):
        """
        Read data from standard input and acquire it into the pantry
        """
        # Create pantry dir if missing
        os.makedirs(self.data_root, exist_ok=True)

        # Build grib_filter rules
        with open(self.grib_filter_rules, "w") as f:
            for inputs in self.inputs.values():
                for inp in inputs:
                    if not getattr(inp, "eccodes", None):
                        log.info("%s (model=%s): skipping input with no eccodes filter", inp.name, inp.model)
                        continue
                    print(f"if ( {inp.eccodes} ) {{", file=f)
                    print(f'  write "{self.data_root}/{inp.pantry_basename}+[endStep].grib";', file=f)
                    print(f"}}", file=f)

        # Run grib_filter on input
        try:
            proc = subprocess.Popen(["grib_filter", self.grib_filter_rules, "-"], stdin=subprocess.PIPE)

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

    def store_processing_artifacts(self, tarout):
        """
        Store relevant processing artifacts in the output tarball
        """
        tarout.add(name=self.grib_filter_rules, arcname="grib_filter_rules")
