from __future__ import annotations
from typing import ContextManager, Optional
import contextlib
import sys
import os
import arkimet


class Pantry:
    """
    Storage of GRIB files to be processed
    """
    def __init__(self, root: str):
        self.root = root
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


class Dispatcher:
    """
    Read a stream of arkimet metadata and store its data into a dataset
    """
    def __init__(self, writer: arkimet.dataset.Writer):
        self.writer = writer

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

    def dispatch(self, md: arkimet.Metadata) -> bool:
        self.writer.acquire(md)
        return True

    def read(self, path: Optional[str] = None):
        """
        Read data from an input file, or standard input.

        The input file is the output of arki-query --inline, which is the same
        as is given as input to arkimet processors.
        """
        with self.input(path) as infd:
            # TODO: batch multiple writes together?
            arkimet.Metadata.read_bundle(infd, dest=self.dispatch)
