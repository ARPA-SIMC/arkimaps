from __future__ import annotations
from typing import ContextManager
import contextlib
import os
import arkimet


class Pantry:
    def __init__(self, root: str):
        self.root = root
        self.session = arkimet.dataset.Session(force_dir_segments=True)
        self.ds_root = os.path.join(self.root, 'pantry')
        os.makedirs(self.ds_root, exist_ok=True)

        self.config = arkimet.cfg.Section({
            "format": "grib",
            "step": "yearly",
            "name": "pantry",
            "path": self.ds_root,
            "type": "iseg",
            "unique": "reftime, level, timerange, product",
            # TODO: add options to tell sqlite and file writes to be fast
            # and insecure; use eatmydata until then
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
        with self.session.dataset_writer(cfg=self.config) as writer:
            yield writer
