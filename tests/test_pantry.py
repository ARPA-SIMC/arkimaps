# from __future__ import annotations
from unittest import TestCase
import contextlib
import tempfile
import os
from arkimapslib import pantry
from arkimapslib.inputs import Input


class PantryTestMixin:
    def get_test_data(self, model, recipe, input_name, step: int):
        return os.path.join("testdata", recipe, f"{model}_{input_name}+{step:02d}.arkimet")

    def test_dispatch(self):
        with self.pantry() as pantry:
            pantry.add_input(Input.create(
                name="test",
                defined_in="memory",
                arkimet="product:GRIB1,,2,11;level:GRIB1,105,2",
                eccodes='shortName is "2t" and indicatorOfTypeOfLevel == 105'))
            pantry.fill(self.get_test_data("cosmo", "t2m", "t2m", 12))
            self.assertIn("test+12.grib", os.listdir(pantry.data_root))
            steps = pantry.get_steps("test")
            self.assertCountEqual(steps.keys(), [12])


class TestArkimetPantry(PantryTestMixin, TestCase):
    @contextlib.contextmanager
    def pantry(self):
        import arkimet
        with arkimet.dataset.Session() as session:
            with tempfile.TemporaryDirectory() as workdir:
                yield pantry.ArkimetPantry(root=workdir, session=session)


class TestEccodesPantry(PantryTestMixin, TestCase):
    @contextlib.contextmanager
    def pantry(self):
        with tempfile.TemporaryDirectory() as workdir:
            yield pantry.EccodesPantry(root=workdir)
