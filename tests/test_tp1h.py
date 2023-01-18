# from __future__ import annotations
from arkimapslib.unittest import add_recipe_test_cases
import unittest


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

        pantry_reftime = "2021_1_10_0_0_0"
        self.fill_pantry(expected=[f"{self.model_name}_tp_{pantry_reftime}+{step}.grib" for step in range(0, 13)])

        # Check that the right input was selected
        tpdec1h = self.kitchen.pantry.inputs.get("tpdec1h")
        for i in tpdec1h:
            self.assertEqual(i.__class__.__name__, "Decumulate")

        orders = self.make_orders()
        # Preprocessing means we cannot reduce test input to only get one
        # order, so we get orders from every step from 0 to 12. We filter
        # later to keep only +12h to test
        if self.model_name == "ifs":
            self.assertEqual(len(orders), 0)
            return
        else:
            self.assertGreaterEqual(len(orders), 12)
        orders = [o for o in orders if o.recipe.name == "tiles/tp1h" and o.instant.step == 12]
        self.assertEqual(len(orders), 1)

        self.assertRenders(orders[0])

        self.assertMgribArgsEqual(orders[0], cosmo={}, ifs={})


add_recipe_test_cases(__name__, "tiles/tp1h")
