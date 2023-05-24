# from __future__ import annotations
import contextlib
import datetime
import os
import re
import tempfile
import unittest
from typing import List, Optional

import arkimet
import numpy

import arkimapslib.inputs
from arkimapslib.config import Config
from arkimapslib.inputs import Instant, Input
from arkimapslib.pantry import Pantry, DiskPantry


class TestInputs(unittest.TestCase):
    @contextlib.contextmanager
    def pantry(self, inputs: Optional[List] = None):
        if inputs is None:
            inputs = ()

        with tempfile.TemporaryDirectory() as pantry_dir:
            os.makedirs(os.path.join(pantry_dir, "pantry"))
            pantry = DiskPantry(pantry_dir)
            for inp in inputs:
                pantry.add_input(inp)
            yield pantry

    def add_to_pantry(
            self,
            pantry: Pantry,
            fname: str,
            instant: Optional[Instant] = None,
            name: Optional[str] = None):
        fn_match = re.compile(
                r"^(?:(?P<model>\w+)_)?(?P<name>\w+)_"
                r"(?P<reftime>\d+_\d+_\d+_\d+_\d+_\d+)\+(?P<step>\d+)\.(?P<ext>\w+)$")

        mo = fn_match.match(os.path.basename(fname))
        if instant is None:
            instant = Instant(
                    datetime.datetime.strptime(mo.group("reftime"), "%Y_%m_%d_%H_%M_%S"),
                    int(mo.group("step")))

        if name is None:
            name = mo.group("name")

        inp = pantry.inputs.get(name)
        if inp is not None:
            inp = [x for x in inp if x.model == mo.group("model")]
        if not inp:
            inp = arkimapslib.inputs.Source(
                    config=Config(),
                    model=mo.group("model"), name=name, defined_in=__file__, arkimet="", eccodes="")
            pantry.add_input(inp)

        testsource = os.path.join("testdata", fname)
        with open(testsource, "rb") as infd:
            mds = arkimet.Metadata.read_bundle(infd)
        self.assertGreater(len(mds), 0)

        data_file = pantry.get_fullname(inp, instant)

        # Write one GRIB to data_file
        with open(data_file, "wb") as out:
            out.write(mds[0].data)

        inp.add_instant(instant)

    def test_trim(self):
        test = arkimapslib.inputs.Source(
                config=Config(),
                name="test", defined_in=__file__, arkimet="", eccodes="")
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
            test.add_instant(instant1)
            self.assertCountEqual(test.instants, [instant1])
            self.assertCountEqual(test.instants_to_truncate, [])
            self.assertEqual(os.path.getsize(data_file), len(mds[0].data))

            # Notify pantry filled, nothing gets truncated
            test.on_pantry_filled(pantry)
            self.assertCountEqual(test.instants, [instant1])
            self.assertCountEqual(test.instants_to_truncate, [])
            self.assertEqual(os.path.getsize(data_file), len(mds[0].data))

            # Append one more GRIB to data_file
            with open(data_file, "ab") as out:
                out.write(mds[0].data)

            # Notify one more data in the test instant: it should notice the duplicate
            with self.assertLogs() as log:
                test.add_instant(instant1)
            self.assertEqual(log.output, [
                'WARNING:arkimaps.inputs:test: multiple data found for 2021-01-10T00:00:00+0',
            ])
            self.assertCountEqual(test.instants, [instant1])
            self.assertCountEqual(test.instants_to_truncate, [instant1])
            self.assertEqual(os.path.getsize(data_file), len(mds[0].data) * 2)

            # Notify pantry filled, data_file gets truncated
            test.on_pantry_filled(pantry)
            self.assertCountEqual(test.instants, [instant1])
            self.assertCountEqual(test.instants_to_truncate, [])
            self.assertEqual(os.path.getsize(data_file), len(mds[0].data))

    def test_apply_clip(self):
        class Tester(arkimapslib.inputs.GribSetMixin):
            def __init__(self, clip: str):
                self.name = "hzero"
                self.defined_in = __file__
                super().__init__(clip=clip)

        o = Tester(clip="hzero[hzero < z] = -999")
        hzero = numpy.array([1, 2, 3, 4])
        z = numpy.array([4, 3, 2, 1])
        hzero = o.apply_clip({"hzero": hzero, "z": z})
        self.assertEqual(hzero.tolist(), [-999, -999, 3, 4])

    def test_model_mix_allowed(self):
        with self.pantry() as pantry:
            # Inputs from two different models
            self.add_to_pantry(pantry, "wflags10m/cosmo_u_2021_1_10_0_0_0+12.arkimet",
                               Instant(datetime.datetime(2021, 1, 10), 12))
            self.add_to_pantry(pantry, "wflags10m/ifs_v_2021_1_10_0_0_0+12.arkimet",
                               Instant(datetime.datetime(2021, 1, 10), 12))

            # Derived input defined for any model
            cat = Input.create(config=Config(), name="uv", type="cat", inputs=["u", "v"], defined_in=__file__)
            pantry.add_input(cat)

            # Derived input prerequisites are not satisfied
            res = cat.get_instants(pantry)
            self.assertCountEqual(res.keys(), [Instant(datetime.datetime(2021, 1, 10), 12)])

            # Check that the output file is not tagged with the model name
            input_file = list(res.values())[0]
            self.assertRegex(input_file.pathname, r"/pantry/uv_")

    def test_model_mix_restricted(self):
        with self.pantry() as pantry:
            # Inputs from two different models
            self.add_to_pantry(pantry, "wflags10m/cosmo_u_2021_1_10_0_0_0+12.arkimet",
                               Instant(datetime.datetime(2021, 1, 10), 12))
            self.add_to_pantry(pantry, "wflags10m/ifs_v_2021_1_10_0_0_0+12.arkimet",
                               Instant(datetime.datetime(2021, 1, 10), 12))

            # Derived input defined only for cosmo
            cat = Input.create(
                config=Config(), model="cosmo", name="uv", type="cat", inputs=["u", "v"], defined_in=__file__)
            pantry.add_input(cat)

            # Derived input prerequisites are not satisfied
            self.assertEqual(cat.get_instants(pantry), {})

        with self.pantry() as pantry:
            # Inputs from two different models
            self.add_to_pantry(pantry, "wflags10m/cosmo_u_2021_1_10_0_0_0+12.arkimet",
                               Instant(datetime.datetime(2021, 1, 10), 12))
            self.add_to_pantry(pantry, "wflags10m/cosmo_v_2021_1_10_0_0_0+12.arkimet",
                               Instant(datetime.datetime(2021, 1, 10), 12))

            # Derived input defined only for cosmo
            cat = Input.create(
                config=Config(), model="cosmo", name="uv", type="cat", inputs=["u", "v"], defined_in=__file__)
            pantry.add_input(cat)

            # Derived input prerequisites are not satisfied
            res = cat.get_instants(pantry)
            self.assertCountEqual(res.keys(), [Instant(datetime.datetime(2021, 1, 10), 12)])

            # Check that the output file is tagged with the model name
            input_file = list(res.values())[0]
            self.assertRegex(input_file.pathname, r"/pantry/cosmo_uv_")

    def test_static(self):
        with self.pantry() as pantry:
            static_dir = os.path.join(pantry.data_root, "static")
            os.makedirs(static_dir)
            with open(os.path.join(static_dir, "testfile"), "wt") as fd:
                print("testdata", file=fd)

            config = Config()
            config.static_dir.insert(0, static_dir)

            inp = Input.create(
                config=config,
                name="testfile",
                path="testfile",
                type="static",
                defined_in=__file__)

            self.assertEqual(inp.abspath, os.path.join(static_dir, "testfile"))
            self.assertEqual(inp.path, "testfile")
