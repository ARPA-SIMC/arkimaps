from __future__ import annotations
from typing import TYPE_CHECKING, ContextManager, Optional
import contextlib
import subprocess
import sys
import os
import arkimet
import logging

if TYPE_CHECKING:
    from .recipes import Recipes

log = logging.getLogger("arkimaps.pantry")


class Pantry:
    """
    Storage of GRIB files to be processed
    """
    def __init__(self, root: str):
        # Root directory where inputs are stored
        self.root = root
        # Arkimet session (if using arkimet, else None)
        self.session: Optional[arkimet.dataset.Session] = None

    def fill(self, recipes: Recipes):
        """
        Read data from standard input and acquire it into the pantry
        """
        raise NotImplementedError(f"{self.__class__.__name__}.fill() not implemented")

    @contextlib.contextmanager
    def input(self, path: Optional[str] = None):
        """
        Open the binary input stream, from a file, or standard input if path is
        None
        """
        if path is None:
            yield sys.stdin.buffer
        else:
            with open(path, "rb") as fd:
                yield fd


class ArkimetPantry(Pantry):
    """
    Arkimet-based storage of GRIB files to be processed
    """
    def __init__(self, root: str):
        super().__init__(root)
        self.session = arkimet.dataset.Session(force_dir_segments=True)
        self.ds_root = os.path.join(self.root, 'pantry')

        self.config = arkimet.cfg.Section({
            "format": "grib",
            "step": "yearly",
            "name": "pantry",
            "path": self.ds_root,
            "type": "iseg",
            "unique": "reftime, level, timerange, product",
            # Tell datasets to be fast at the cost of leaving an inconsistent
            # state in case of errors. We can do that since we work on a
            # temporary directory.
            "eatmydata": "yes",
        })

    def fill(self, recipes: Recipes):
        """
        Read data from standard input and acquire it into the pantry
        """
        with self.writer() as writer:
            dispatcher = ArkimetDispatcher(writer)
            dispatcher.read()

    @contextlib.contextmanager
    def reader(self) -> ContextManager[arkimet.dataset.Reader]:
        """
        Create and return a dataset reader to query the data stored in the
        pantry
        """
        with self.session.dataset_reader(cfg=self.config) as reader:
            yield reader

    @contextlib.contextmanager
    def writer(self) -> ContextManager[arkimet.dataset.Writer]:
        """
        Create and return a dataset writer to store new data in the pantry
        """
        os.makedirs(self.ds_root, exist_ok=True)
        with self.session.dataset_writer(cfg=self.config) as writer:
            yield writer


class ArkimetDispatcher:
    """
    Read a stream of arkimet metadata and store its data into a dataset
    """
    def __init__(self, writer: arkimet.dataset.Writer):
        self.writer = writer
        self.batch = []

    def flush_batch(self):
        if not self.batch:
            return
        res = self.writer.acquire_batch(self.batch, drop_cached_data_on_commit=True)
        count_nok = sum(1 for x in res if x != "ok")
        if count_nok > 0:
            raise RuntimeError(f"{count_nok} elements not imported correctly")
        log.debug("imported %d items into pantry", len(self.batch))
        self.batch = []

    def dispatch(self, md: arkimet.Metadata) -> bool:
        self.batch.append(md)
        if len(self.batch) >= 200:
            self.flush_batch()
        return True

    def read(self, path: Optional[str] = None):
        """
        Read data from an input file, or standard input.

        The input file is the output of arki-query --inline, which is the same
        as is given as input to arkimet processors.
        """
        with self.input(path) as infd:
            arkimet.Metadata.read_bundle(infd, dest=self.dispatch)
            self.flush_batch()


class GribPantry(Pantry):
    """
    eccodes-based storage of GRIB files to be processed
    """
    def __init__(self, root: str):
        super().__init__(root)
        self.grib_filter_rules = os.path.join(self.root, "grib_filter_rules")

    def fill(self, recipes: Recipes):
        """
        Read data from standard input and acquire it into the pantry
        """
        # Build grib_filter rules
        with open(self.grib_filter_rules, "w") as f:
            for recipe in recipes.recipes:
                # Create one directory per recipe
                recipe_dir = os.path.join(self.root, recipe.name)
                os.makedirs(recipe_dir, exist_ok=True)
                for name, expr in recipe.inputs_grib:
                    print(f"if ( {expr} ) {{", file=f)
                    print(f'  write "{recipe_dir}/{name}+[endStep].grib";', file=f)
                    print(f"}}", file=f)

        # Run grib_filter on input
        try:
            proc = subprocess.Popen(["grib_filter", self.grib_filter_rules, "-"], stdin=subprocess.PIPE)

            def dispatch(md: arkimet.Metadata) -> bool:
                proc.stdin.write(md.data)
                return True

            with self.input(path=None) as infd:
                arkimet.Metadata.read_bundle(infd, dest=dispatch)

        finally:
            proc.stdin.close()
            proc.wait()
            if proc.returncode != 0:
                raise RuntimeError(f"grib_filter failed with return code {proc.returncode}")
