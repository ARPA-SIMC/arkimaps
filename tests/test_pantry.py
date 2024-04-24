# from __future__ import annotations
import contextlib
import datetime
import os
import tempfile
from pathlib import Path
from typing import Iterator, Optional
from unittest import TestCase

from arkimapslib import pantry
from arkimapslib.config import Config
from arkimapslib.inputs import Inputs, Input, Instant


class PantryTestMixin:
    @contextlib.contextmanager
    def workdir(self, workdir: Optional[Path] = None) -> Iterator[Path]:
        """
        Make sure a working directory exists even if not specified
        """
        if workdir is None:
            with tempfile.TemporaryDirectory() as tempdir:
                yield Path(tempdir)
        else:
            yield workdir

    def get_test_data(self, model: str, recipe: str, input_name: str, step: int) -> Path:
        return Path("testdata") / recipe / f"{model}_{input_name}_2021_1_10_0_0_0+{step:02d}.arkimet"

    def test_dispatch(self):
        with self.pantry() as pantry:
            pantry.inputs.add(
                Input.create(
                    config=Config(),
                    name="test",
                    defined_in="memory",
                    arkimet="product:GRIB1,,2,11;level:GRIB1,105,2",
                    eccodes='shortName is "2t" and indicatorOfTypeOfLevel == 105',
                )
            )
            pantry.fill(self.get_test_data("cosmo", "t2m", "t2m", 12))
            self.assertIn("test_2021_1_10_0_0_0+12.grib", os.listdir(pantry.data_root))
            instants = pantry.get_instants("test")
            self.assertCountEqual(instants.keys(), [Instant(datetime.datetime(2021, 1, 10), 12)])

    def test_separate_steps(self):
        def add_inputs(pantry):
            pantry.inputs.add(
                Input.create(
                    config=Config(),
                    name="test",
                    defined_in="memory",
                    arkimet="product:GRIB1,,2,11;level:GRIB1,105,2",
                    eccodes='shortName is "2t" and indicatorOfTypeOfLevel == 105',
                )
            )
            pantry.inputs.add(
                Input.create(config=Config(), name="derived", defined_in="memory", type="cat", inputs=["test"])
            )

        # Processing in a single step
        # First step: fill
        with self.pantry() as pantry:
            add_inputs(pantry)
            pantry.fill(self.get_test_data("cosmo", "t2m", "t2m", 12))
            inp = pantry.inputs.get("test")[0]
            instants = inp.get_instants(pantry)
            self.assertCountEqual(instants.keys(), [Instant(datetime.datetime(2021, 1, 10), 12)])

            inp = pantry.inputs.get("derived")[0]
            instants = inp.get_instants(pantry)
            self.assertCountEqual(instants.keys(), [Instant(datetime.datetime(2021, 1, 10), 12)])

        # Processing in separate steps
        with tempfile.TemporaryDirectory() as tmpdir:
            workdir = Path(tmpdir)
            # First step: fill
            with self.pantry(workdir) as pantry:
                add_inputs(pantry)
                pantry.fill(self.get_test_data("cosmo", "t2m", "t2m", 12))

            # Second step: render
            with self.pantry(workdir) as pantry:
                add_inputs(pantry)
                pantry.rescan()
                inp = pantry.inputs.get("test")[0]
                instants = inp.get_instants(pantry)
                self.assertCountEqual(instants.keys(), [Instant(datetime.datetime(2021, 1, 10), 12)])

                inp = pantry.inputs.get("derived")[0]
                instants = inp.get_instants(pantry)
                self.assertCountEqual(instants.keys(), [Instant(datetime.datetime(2021, 1, 10), 12)])

            # Another render attempt, derived inputs should be found
            with self.pantry(workdir) as pantry:
                add_inputs(pantry)
                pantry.rescan()
                inp = pantry.inputs.get("test")[0]
                instants = inp.get_instants(pantry)
                self.assertCountEqual(instants.keys(), [Instant(datetime.datetime(2021, 1, 10), 12)])

                inp = pantry.inputs.get("derived")[0]
                instants = inp.get_instants(pantry)
                self.assertCountEqual(instants.keys(), [Instant(datetime.datetime(2021, 1, 10), 12)])


class TestArkimetPantry(PantryTestMixin, TestCase):
    @contextlib.contextmanager
    def pantry(self, workdir: Optional[Path] = None):
        import arkimet

        with arkimet.dataset.Session() as session:
            with self.workdir(workdir) as workdir:
                yield pantry.ArkimetPantry(root=workdir, session=session, inputs=Inputs())

    def test_dispatch_skip_arkimet(self):
        with self.pantry() as pantry:
            pantry.inputs.add(
                Input.create(
                    config=Config(),
                    name="test",
                    defined_in="memory",
                    arkimet="skip",
                    eccodes='shortName is "2t" and indicatorOfTypeOfLevel == 105',
                )
            )
            pantry.fill(self.get_test_data("cosmo", "t2m", "t2m", 12))
            self.assertEqual(os.listdir(pantry.data_root), [])


class TestEccodesPantry(PantryTestMixin, TestCase):
    @contextlib.contextmanager
    def pantry(self, workdir: Optional[Path] = None):
        with self.workdir(workdir) as workdir:
            yield pantry.EccodesPantry(root=workdir, inputs=Inputs())

    def test_dispatch_skip_eccodes(self):
        with self.pantry() as pantry:
            pantry.inputs.add(
                Input.create(
                    config=Config(),
                    name="test",
                    defined_in="memory",
                    arkimet="product:GRIB1,,2,11;level:GRIB1,105,2",
                    eccodes="skip",
                )
            )
            pantry.fill(self.get_test_data("cosmo", "t2m", "t2m", 12))
            self.assertEqual(os.listdir(pantry.data_root), ["grib_filter_rules"])
