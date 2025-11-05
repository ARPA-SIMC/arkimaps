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
from arkimapslib.inputs import Input, Inputs, GribSetInputSpec
from arkimapslib.pantry import DiskPantry
from arkimapslib.types import Instant


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
                config=Config(),
                name=name,
                defined_in=__file__,
                args={"model": mo.group("model"), "arkimet": "", "eccodes": ""},
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
        test = arkimapslib.inputs.Source(
            config=Config(), name="test", defined_in=__file__, args={"arkimet": "", "eccodes": ""}
        )
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
        class Tester(arkimapslib.inputs.GribSetMixin[GribSetInputSpec], spec=GribSetInputSpec):
            def __init__(self, clip: str):
                super().__init__(config=None, name="hzero", defined_in=__file__, args={"clip": clip})

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
            cat = Input.create(config=Config(), name="uv", type="cat", args={"inputs": ["u", "v"]}, defined_in=__file__)
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
                config=Config(),
                name="uv",
                type="cat",
                args={"model": "cosmo", "inputs": ["u", "v"]},
                defined_in=__file__,
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
                config=Config(),
                name="uv",
                type="cat",
                args={"model": "cosmo", "inputs": ["u", "v"]},
                defined_in=__file__,
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
                config=config, name="testfile", args={"path": Path("testfile")}, type="static", defined_in=__file__
            )

            self.assertEqual(inp.abspath, static_dir / "testfile")
            self.assertEqual(inp.spec.path, Path("testfile"))
