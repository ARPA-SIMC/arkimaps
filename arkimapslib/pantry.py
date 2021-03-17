# from __future__ import annotations
from typing import Optional, BinaryIO, List, Tuple, Any
import contextlib
import subprocess
import sys
import os
import logging
from . import inputs

# if TYPE_CHECKING:
# from . import recipes
try:
    import arkimet
except ModuleNotFoundError:
    arkimet = None

log = logging.getLogger("arkimaps.pantry")


class PantryMixin:
    """
    Storage of GRIB files used as inputs to recipes
    """
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


class EmptyPantry(inputs.InputRegistry, PantryMixin):
    """
    Pantry with no disk-based storage, used as input registry only to generate documentation
    """
    pass


class DiskPantry(inputs.InputStorage, PantryMixin):
    """
    Pantry with disk-based storage
    """
    def __init__(self, root: str, **kw):
        kw.setdefault("data_root", os.path.join(root, "pantry"))
        super().__init__(**kw)


class ArkimetEmptyPantry(EmptyPantry):
    """
    Storage-less arkimet pantry only used to load recipes
    """
    def __init__(self, session: arkimet.dataset.Session, **kw):
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
        match: List[Tuple[Any, str]] = []
        for inps in self.inputs.values():
            for inp in inps:
                matcher = getattr(inp, "arkimet_matcher", None)
                if matcher is None:
                    log.info("%s (model=%s): skipping input with no arkimet matcher filter", inp.name, inp.model)
                    continue
                match.append((matcher, inp.pantry_basename))

        dispatcher = ArkimetDispatcher(self.data_root, match)
        with self.open_dispatch_input(path=path) as infd:
            dispatcher.read(infd)


class ArkimetDispatcher:
    """
    Read a stream of arkimet metadata and store its data into a dataset
    """
    def __init__(self, data_root: str, todo_list: List[Tuple[Any, str]]):
        self.data_root = data_root
        self.todo_list = todo_list

    def dispatch(self, md: arkimet.Metadata) -> bool:
        for matcher, pantry_basename in self.todo_list:
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

                dest = os.path.join(self.data_root, pantry_basename + f"+{output_step}.{source['format']}")
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
    def __init__(self, **kw):
        super().__init__(**kw)
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
                        log.info("%s (model=%s): skipping input with no eccodes filter", inp.name, inp.model)
                        continue
                    print(f"if ( {eccodes} ) {{", file=f)
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
