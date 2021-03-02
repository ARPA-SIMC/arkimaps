# from __future__ import annotations
from arkimapslib.render import Renderer
from arkimapslib.unittest import add_recipe_test_cases
import unittest
import os


class TP1HMixin:
    def test_dispatch(self):
        # For IFS and Eccodes, we have a problem:
        #  - IFS has a 3h resolution, so does not provide data for tp1h
        #  - grib_filter errors out if the input is empty, with the same error
        #    code as other kinds of errors
        # So we can't successfully run a dispatch from an empty file in case
        # we're running the IFS case with grib_filter dispatch. Rather than
        # handling this corner case, which is mostly test specific, we skip
        # that test
        if self.model_name == "ifs":
            raise unittest.SkipTest("tp1h tests for IFS skipped, see code for reason")

        with self.kitchen_class() as kitchen:
            self.fill_pantry(kitchen, expected=[f"{self.model_name}_tp+{step}.grib" for step in range(0, 13)])

            # Check that the right input was selected
            tpdec1h = kitchen.pantry.inputs.get("tpdec1h")
            for i in tpdec1h:
                self.assertEqual(i.__class__.__name__, "Decumulate")

            orders = self.make_orders(kitchen)
            # Preprocessing means we cannot reduce test input to only get one
            # order, so we get orders from every step from 0 to 12. We filter
            # later to keep only +12h to test
            if self.model_name == "ifs":
                self.assertEqual(len(orders), 0)
                return
            else:
                self.assertGreaterEqual(len(orders), 12)
            orders = [o for o in orders if o.basename == "tp1h+012"]
            self.assertEqual(len(orders), 1)

            renderer = Renderer(kitchen.workdir)
            with self.assertLogs() as log:
                renderer.render_one(orders[0])

            mgrib_args_prefix = "INFO:arkimaps.order.tp1h+012:add_grib mgrib "
            mgrib_args = None
            for l in log.output:
                if l.startswith(mgrib_args_prefix):
                    mgrib_args = l[len(mgrib_args_prefix):]

            self.assertIsNotNone(orders[0].output)
            self.assertEqual(os.path.basename(orders[0].output), "tp1h+012.png")

            expected_mgrib_args = {
                "cosmo": "{}",
                "ifs": "{}",
            }

            self.assertIsNotNone(mgrib_args)
            self.assertEqual(mgrib_args, expected_mgrib_args[self.model_name])


add_recipe_test_cases(__name__, "tp1h")
