# from __future__ import annotations
import tempfile
from pathlib import Path
from unittest import TestCase

from arkimapslib import pantry
from arkimapslib.kitchen import ArkimetEmptyKitchen, Kitchen
from arkimapslib.unittest import Workdir, system_definitions


class TestEmptyKitchen(TestCase):
    def test_load_recipes(self) -> None:
        with Workdir() as workdir:
            workdir.add_yaml_file("test.yaml", {"recipe": []})
            workdir.add_yaml_file("test/test.yaml", {"recipe": []})
            kitchen = workdir.as_kitchen()

        r = kitchen.defs.recipes.get("test")
        self.assertEqual(r.name, "test")
        self.assertEqual(r.defined_in, "test.yaml")
        r = kitchen.defs.recipes.get("test/test")
        self.assertEqual(r.name, "test/test")
        self.assertEqual(r.defined_in, "test/test.yaml")

    def test_document_recipes(self) -> None:
        # Just generate documentation for all shipped recipes, to make sure
        # nothing raises exceptions
        definitions = system_definitions()
        kitchen = Kitchen(definitions=definitions)
        kitchen.pantry = pantry.EmptyPantry(inputs=definitions.inputs)
        default_flavour = kitchen.defs.flavours["default"]
        with tempfile.TemporaryDirectory() as workdir:
            kitchen.document_recipes(default_flavour, workdir)


class TestArkimetEmptyKitchen(TestCase):
    def test_merged_arki_query(self) -> None:
        definitions = system_definitions()
        kitchen = ArkimetEmptyKitchen(definitions=definitions)
        default_flavour = kitchen.defs.flavours["default"]
        merged = kitchen.get_merged_arki_query([default_flavour])
        self.assertIsNotNone(merged)
