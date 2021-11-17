# from __future__ import annotations
import contextlib
import os
import tempfile
from typing import Optional, List
import unittest
from arkimapslib.pantry import DiskPantry
import arkimapslib.inputs
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
        testsource = os.path.join("testdata", "t2m", "cosmo_t2m+12.arkimet")
        with open(testsource, "rb") as infd:
            mds = arkimet.Metadata.read_bundle(infd)
        self.assertEqual(len(mds), 1)

        with self.pantry(inputs=[test]) as pantry:
            data_file = os.path.join(pantry.data_root, test.pantry_basename + "+0.grib")

            # Write one GRIB to data_file
            with open(data_file, "wb") as out:
                out.write(mds[0].data)

            # Notify one data in step 0
            test.add_step(0)
            self.assertCountEqual(test.steps, [0])
            self.assertCountEqual(test.steps_to_truncate, [])
            self.assertEqual(os.path.getsize(data_file), len(mds[0].data))

            # Notify pantry filled, nothing gets truncated
            test.on_pantry_filled(pantry)
            self.assertCountEqual(test.steps, [0])
            self.assertCountEqual(test.steps_to_truncate, [])
            self.assertEqual(os.path.getsize(data_file), len(mds[0].data))

            # Append one more GRIB to data_file
            with open(data_file, "ab") as out:
                out.write(mds[0].data)

            # Notify one more data in step 0: it should notice the duplicate
            with self.assertLogs() as log:
                test.add_step(0)
            self.assertEqual(log.output, [
                'WARNING:arkimaps.inputs:test: multiple data found for step +0',
            ])
            self.assertCountEqual(test.steps, [0])
            self.assertCountEqual(test.steps_to_truncate, [0])
            self.assertEqual(os.path.getsize(data_file), len(mds[0].data) * 2)

            # Notify pantry filled, data_file gets truncated
            test.on_pantry_filled(pantry)
            self.assertCountEqual(test.steps, [0])
            self.assertCountEqual(test.steps_to_truncate, [])
            self.assertEqual(os.path.getsize(data_file), len(mds[0].data))
