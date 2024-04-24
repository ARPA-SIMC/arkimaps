# from __future__ import annotations
import contextlib
import datetime
import os
import re
import tempfile
import unittest
from pathlib import Path
from typing import Iterator, List, Optional

import arkimet
import numpy

import arkimapslib.inputs
from arkimapslib.config import Config
from arkimapslib.inputs import Instant, Input, Inputs
from arkimapslib.pantry import DiskPantry
from arkimapslib.types import ModelStep


class TestInputs(unittest.TestCase):
    @contextlib.contextmanager
    def pantry(self, inputs: Optional[List[arkimapslib.inputs.Input]] = None) -> Iterator[DiskPantry]:
        if inputs is None:
            inputs = []

        inputs_ = Inputs()
        for inp in inputs:
            inputs_.add(inp)

        with tempfile.TemporaryDirectory() as tempdir:
            pantry_dir = Path(tempdir)
            (pantry_dir / "pantry").mkdir(parents=True)
            pantry = DiskPantry(root=pantry_dir, inputs=inputs_)
            yield pantry

    def add_to_pantry(
        self, pantry: DiskPantry, fname: str, instant: Optional[Instant] = None, name: Optional[str] = None
    ) -> None:
        fn_match = re.compile(
            r"^(?:(?P<model>\w+)_)?(?P<name>\w+)_" r"(?P<reftime>\d+_\d+_\d+_\d+_\d+_\d+)\+(?P<step>\d+)\.(?P<ext>\w+)$"
        )

        mo = fn_match.match(os.path.basename(fname))
        assert mo is not None
        if instant is None:
            instant = Instant(
                datetime.datetime.strptime(mo.group("reftime"), "%Y_%m_%d_%H_%M_%S"), int(mo.group("step"))
            )

        if name is None:
            name = mo.group("name")

        # Look for an input that was already in the pantry
        inp: Input
        old_inputs = pantry.inputs.get(name)
        if old_inputs is not None:
            old_inputs = [x for x in old_inputs if x.spec.model == mo.group("model")]
        if not old_inputs:
            inp = arkimapslib.inputs.Source(
                config=Config(), model=mo.group("model"), name=name, defined_in=__file__, arkimet="", eccodes=""
            )
            pantry.inputs.add(inp)
        else:
            assert len(old_inputs) == 1
            inp = old_inputs[0]

        testsource = os.path.join("testdata", fname)
        with open(testsource, "rb") as infd:
            mds = arkimet.Metadata.read_bundle(infd)
        self.assertGreater(len(mds), 0)

        data_file = pantry.get_fullname(inp, instant)

        # Write one GRIB to data_file
        with open(data_file, "wb") as out:
            out.write(mds[0].data)

        pantry.add_instant(inp, instant)

    def test_trim(self) -> None:
        test = arkimapslib.inputs.Source(config=Config(), name="test", defined_in=__file__, arkimet="", eccodes="")
        testsource = os.path.join("testdata", "t2m", "cosmo_t2m_2021_1_10_0_0_0+12.arkimet")
        with open(testsource, "rb") as infd:
            mds = arkimet.Metadata.read_bundle(infd)
        self.assertEqual(len(mds), 1)

        with self.pantry(inputs=[test]) as pantry:
            # Instant corresponding to the test sample
            instant1 = Instant(datetime.datetime(2021, 1, 10), 0)

            data_file = pantry.get_fullname(test, instant1)

            # Write one GRIB to data_file
            with open(data_file, "wb") as out:
                out.write(mds[0].data)

            # Notify one data in the test instant
            pantry.add_instant(test, instant1)
            self.assertCountEqual(pantry.input_instants[test], [instant1])
            self.assertCountEqual(pantry.input_instants_to_truncate[test], [])
            self.assertEqual(os.path.getsize(data_file), len(mds[0].data))

            # Notify pantry filled, nothing gets truncated
            pantry.notify_pantry_filled()
            self.assertCountEqual(pantry.input_instants[test], [instant1])
            self.assertCountEqual(pantry.input_instants_to_truncate[test], [])
            self.assertEqual(os.path.getsize(data_file), len(mds[0].data))

            # Append one more GRIB to data_file
            with open(data_file, "ab") as out:
                out.write(mds[0].data)

            # Notify one more data in the test instant: it should notice the duplicate
            with self.assertLogs() as log:
                pantry.add_instant(test, instant1)
            self.assertEqual(
                log.output,
                [
                    "WARNING:arkimaps.pantry:test: multiple data found for 2021-01-10T00:00:00+000",
                ],
            )
            self.assertCountEqual(pantry.input_instants[test], [instant1])
            self.assertCountEqual(pantry.input_instants_to_truncate[test], [instant1])
            self.assertEqual(os.path.getsize(data_file), len(mds[0].data) * 2)

            # Notify pantry filled, data_file gets truncated
            pantry.notify_pantry_filled()
            self.assertCountEqual(pantry.input_instants[test], [instant1])
            self.assertCountEqual(pantry.input_instants_to_truncate[test], [])
            self.assertEqual(os.path.getsize(data_file), len(mds[0].data))

    def test_apply_clip(self) -> None:
        class Tester(arkimapslib.inputs.GribSetMixin):
            def __init__(self, clip: str):
                super().__init__(config=None, name="hzero", defined_in=__file__, clip=clip)

        o = Tester(clip="hzero[hzero < z] = -999")
        hzero = numpy.array([1, 2, 3, 4])
        z = numpy.array([4, 3, 2, 1])
        hzero = o.apply_clip({"hzero": hzero, "z": z})
        self.assertEqual(hzero.tolist(), [-999, -999, 3, 4])

    def test_model_mix_allowed(self) -> None:
        with self.pantry() as pantry:
            # Inputs from two different models
            self.add_to_pantry(
                pantry, "wflags10m/cosmo_u_2021_1_10_0_0_0+12.arkimet", Instant(datetime.datetime(2021, 1, 10), 12)
            )
            self.add_to_pantry(
                pantry, "wflags10m/ifs_v_2021_1_10_0_0_0+12.arkimet", Instant(datetime.datetime(2021, 1, 10), 12)
            )

            # Derived input defined for any model
            cat = Input.create(config=Config(), name="uv", type="cat", inputs=["u", "v"], defined_in=__file__)
            pantry.inputs.add(cat)

            # Derived input prerequisites are not satisfied
            res = cat.get_instants(pantry)
            self.assertCountEqual(res.keys(), [Instant(datetime.datetime(2021, 1, 10), 12)])

            # Check that the output file is not tagged with the model name
            input_file = list(res.values())[0]
            self.assertRegex(str(input_file.pathname), r"/pantry/uv_")

    def test_model_mix_restricted(self) -> None:
        with self.pantry() as pantry:
            # Inputs from two different models
            self.add_to_pantry(
                pantry, "wflags10m/cosmo_u_2021_1_10_0_0_0+12.arkimet", Instant(datetime.datetime(2021, 1, 10), 12)
            )
            self.add_to_pantry(
                pantry, "wflags10m/ifs_v_2021_1_10_0_0_0+12.arkimet", Instant(datetime.datetime(2021, 1, 10), 12)
            )

            # Derived input defined only for cosmo
            cat = Input.create(
                config=Config(), model="cosmo", name="uv", type="cat", inputs=["u", "v"], defined_in=__file__
            )
            pantry.inputs.add(cat)

            # Derived input prerequisites are not satisfied
            self.assertEqual(cat.get_instants(pantry), {})

        with self.pantry() as pantry:
            # Inputs from two different models
            self.add_to_pantry(
                pantry, "wflags10m/cosmo_u_2021_1_10_0_0_0+12.arkimet", Instant(datetime.datetime(2021, 1, 10), 12)
            )
            self.add_to_pantry(
                pantry, "wflags10m/cosmo_v_2021_1_10_0_0_0+12.arkimet", Instant(datetime.datetime(2021, 1, 10), 12)
            )

            # Derived input defined only for cosmo
            cat = Input.create(
                config=Config(), model="cosmo", name="uv", type="cat", inputs=["u", "v"], defined_in=__file__
            )
            pantry.inputs.add(cat)

            # Derived input prerequisites are not satisfied
            res = cat.get_instants(pantry)
            self.assertCountEqual(res.keys(), [Instant(datetime.datetime(2021, 1, 10), 12)])

            # Check that the output file is tagged with the model name
            input_file = list(res.values())[0]
            self.assertRegex(str(input_file.pathname), r"/pantry/cosmo_uv_")

    def test_static(self) -> None:
        with self.pantry() as pantry:
            static_dir = pantry.data_root / "static"
            static_dir.mkdir(parents=True)
            with (static_dir / "testfile").open("wt") as fd:
                print("testdata", file=fd)

            config = Config()
            config.static_dir.insert(0, static_dir)

            inp = Input.create(
                config=config, name="testfile", path=Path("testfile"), type="static", defined_in=__file__
            )

            self.assertEqual(inp.abspath, static_dir / "testfile")
            self.assertEqual(inp.spec.path, Path("testfile"))


class TestModelStep(unittest.TestCase):
    def test_from_int(self) -> None:
        ms = ModelStep(0)
        self.assertEqual(str(ms), "0h")
        ms = ModelStep(12)
        self.assertEqual(str(ms), "12h")

    def test_from_str(self) -> None:
        ms = ModelStep("0h")
        self.assertEqual(str(ms), "0h")

        ms = ModelStep("12h")
        self.assertEqual(str(ms), "12h")

        with self.assertRaises(ValueError):
            ModelStep("30m")
        with self.assertRaises(ValueError):
            ModelStep("43200s")
        with self.assertRaises(ValueError):
            ModelStep("")
        with self.assertRaises(ValueError):
            ModelStep("h")

    def test_from_modelstep(self) -> None:
        ms = ModelStep(ModelStep("0h"))
        self.assertEqual(str(ms), "0h")

        ms = ModelStep(ModelStep("12h"))
        self.assertEqual(str(ms), "12h")

    def test_equals(self) -> None:
        ms = ModelStep(0)
        self.assertEqual(ms, 0)
        self.assertEqual(ms, "0h")
        self.assertEqual(ms, ModelStep("0h"))
        self.assertTrue(ms.is_zero())

        ms = ModelStep(12)
        self.assertEqual(ms, 12)
        self.assertEqual(ms, "12h")
        self.assertEqual(ms, ModelStep("12h"))
        self.assertFalse(ms.is_zero())

        with self.assertRaises(ValueError):
            ms == "720m"
        with self.assertRaises(ValueError):
            ms == "43200s"
        with self.assertRaises(ValueError):
            ms == ""
        with self.assertRaises(ValueError):
            ms == "h"

    def test_lt(self) -> None:
        ms = ModelStep(0)
        self.assertLess(ms, 1)
        self.assertLess(ms, "1h")
        self.assertLess(ms, ModelStep("1h"))

        ms = ModelStep(12)
        self.assertLess(ms, 13)
        self.assertLess(ms, "13h")
        self.assertLess(ms, ModelStep("13h"))

        with self.assertRaises(ValueError):
            ms < "721m"
        with self.assertRaises(ValueError):
            ms < "43201s"
        with self.assertRaises(ValueError):
            ms < ""
        with self.assertRaises(ValueError):
            ms < "h"

    def test_suffix(self) -> None:
        ms = ModelStep(0)
        self.assertEqual(ms.suffix(), "+000")
        ms = ModelStep(12)
        self.assertEqual(ms.suffix(), "+012")

    def test_hashable(self) -> None:
        steps = {
            ModelStep(0),
            ModelStep(12),
        }
        self.assertEqual(len(steps), 2)
        self.assertEqual(
            steps,
            {
                ModelStep(0),
                ModelStep(12),
            },
        )


class TestInstant(unittest.TestCase):
    def test_access(self) -> None:
        i = Instant(datetime.datetime(2023, 1, 1), 12)
        self.assertEqual(i.reftime, datetime.datetime(2023, 1, 1))
        self.assertEqual(i.step, 12)

        self.assertTrue(i == Instant(datetime.datetime(2023, 1, 1), 12))
        self.assertTrue(i != Instant(datetime.datetime(2023, 1, 1), 11))
        self.assertTrue(i != Instant(datetime.datetime(2023, 1, 2), 12))

    def test_lt(self) -> None:
        i = Instant(datetime.datetime(2023, 1, 1), 12)
        self.assertLess(i, Instant(datetime.datetime(2023, 1, 1), 13))
        self.assertLess(i, Instant(datetime.datetime(2023, 1, 2), 12))
