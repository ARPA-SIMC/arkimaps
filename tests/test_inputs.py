# from __future__ import annotations
import contextlib
import datetime
import os
import tempfile
from typing import Optional, List
import unittest
from arkimapslib.pantry import DiskPantry
import arkimapslib.inputs
from arkimapslib.inputs import Instant
import arkimet


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

    def test_trim(self):
        test = arkimapslib.inputs.Source(name="test", defined_in=__file__, arkimet="", eccodes="")
        testsource = os.path.join("testdata", "t2m", "cosmo_t2m_2021_1_10_0_0_0+12.arkimet")
        with open(testsource, "rb") as infd:
            mds = arkimet.Metadata.read_bundle(infd)
        self.assertEqual(len(mds), 1)

        with self.pantry(inputs=[test]) as pantry:
            # Instant corresponding to the test sample
            instant1 = Instant(datetime.datetime(2021, 1, 10), 0)

            data_file = os.path.join(pantry.data_root, test.pantry_basename + instant1.pantry_suffix() + ".grib")

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
