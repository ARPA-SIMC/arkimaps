# from __future__ import annotations
from typing import Any
from unittest import TestCase
import contextlib
import tempfile
import os
import yaml
from arkimapslib.kitchen import EmptyKitchen


class Workdir(contextlib.ExitStack):
    def __init__(self):
        super().__init__()
        self.workdir = self.enter_context(tempfile.TemporaryDirectory())

    def add_file(self, relpath: str, contents: Any):
        abspath = os.path.join(self.workdir, relpath)
        os.makedirs(os.path.dirname(abspath), exist_ok=True)
        with open(abspath, "wt") as fd:
            yaml.dump(contents, fd)


class TestEmptyKitchen(TestCase):
    def test_load_recipes(self):
        with Workdir() as workdir:
            workdir.add_file("test.yaml", {"recipe": []})
            workdir.add_file("test/test.yaml", {"recipe": []})
            kitchen = EmptyKitchen()
            kitchen.load_recipes(workdir.workdir)

        r = kitchen.recipes.get("test")
        self.assertEqual(r.name, "test")
        self.assertEqual(r.defined_in, "test.yaml")
        r = kitchen.recipes.get("test/test")
        self.assertEqual(r.name, "test/test")
        self.assertEqual(r.defined_in, "test/test.yaml")

    def test_document_recipes(self):
        # Just generate documentation for all shipped recipes, to make sure
        # nothing raises exceptions
        kitchen = EmptyKitchen()
        kitchen.load_recipes("recipes")
        with tempfile.TemporaryDirectory() as workdir:
            kitchen.document_recipes(workdir)
