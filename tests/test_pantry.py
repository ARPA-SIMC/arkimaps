# from __future__ import annotations
from unittest import TestCase
import contextlib
import os
import tempfile
from typing import Optional

from arkimapslib import pantry
from arkimapslib.inputs import Input


class PantryTestMixin:
    @contextlib.contextmanager
    def workdir(self, workdir: Optional[str] = None):
        """
        Make sure a working directory exists even if not specified
        """
        if workdir is None:
            with tempfile.TemporaryDirectory() as workdir:
                yield workdir
        else:
            yield workdir

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

    def test_separate_steps(self):
        def add_inputs(pantry):
            pantry.add_input(Input.create(
                name="test",
                defined_in="memory",
                arkimet="product:GRIB1,,2,11;level:GRIB1,105,2",
                eccodes='shortName is "2t" and indicatorOfTypeOfLevel == 105'))
            pantry.add_input(Input.create(
                name="derived",
                defined_in="memory",
                type="cat",
                inputs=["test"]))

        # Processing in a single step
        # First step: fill
        with self.pantry() as pantry:
            add_inputs(pantry)
            pantry.fill(self.get_test_data("cosmo", "t2m", "t2m", 12))
            inp = pantry.inputs.get("test")[0]
            steps = inp.get_steps(pantry)
            self.assertCountEqual(steps.keys(), [12])

            inp = pantry.inputs.get("derived")[0]
            steps = inp.get_steps(pantry)
            self.assertCountEqual(steps.keys(), [12])

        # Processing in separate steps
        with tempfile.TemporaryDirectory() as workdir:
            # First step: fill
            with self.pantry(workdir) as pantry:
                add_inputs(pantry)
                pantry.fill(self.get_test_data("cosmo", "t2m", "t2m", 12))

            # Second step: render
            with self.pantry(workdir) as pantry:
                add_inputs(pantry)
                pantry.rescan()
                inp = pantry.inputs.get("test")[0]
                steps = inp.get_steps(pantry)
                self.assertCountEqual(steps.keys(), [12])

                inp = pantry.inputs.get("derived")[0]
                steps = inp.get_steps(pantry)
                self.assertCountEqual(steps.keys(), [12])

            # Another render attempt, derived inputs should be found
            with self.pantry(workdir) as pantry:
                add_inputs(pantry)
                pantry.rescan()
                inp = pantry.inputs.get("test")[0]
                steps = inp.get_steps(pantry)
                self.assertCountEqual(steps.keys(), [12])

                inp = pantry.inputs.get("derived")[0]
                steps = inp.get_steps(pantry)
                self.assertCountEqual(steps.keys(), [12])


class TestArkimetPantry(PantryTestMixin, TestCase):
    @contextlib.contextmanager
    def pantry(self, workdir=None):
        import arkimet
        with arkimet.dataset.Session() as session:
            with self.workdir(workdir) as workdir:
                yield pantry.ArkimetPantry(root=workdir, session=session)


class TestEccodesPantry(PantryTestMixin, TestCase):
    @contextlib.contextmanager
    def pantry(self, workdir=None):
        with self.workdir(workdir) as workdir:
            yield pantry.EccodesPantry(root=workdir)
