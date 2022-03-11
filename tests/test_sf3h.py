# from __future__ import annotations
from arkimapslib.unittest import add_recipe_test_cases


class SF3HMixin:
    def test_dispatch(self):
        pantry_reftime = "2021_1_10_0_0_0"
        self.fill_pantry(expected=[f"{self.model_name}_sf_{pantry_reftime}+{step}.grib" for step in range(0, 13)])

        # Check that the right input was selected
        sfdec1h = self.kitchen.pantry.inputs.get("sfdec1h")
        for i in sfdec1h:
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
        orders = [o for o in orders if o.basename == "sf1h+012"]
        self.assertEqual(len(orders), 1)

        self.assertRenders(orders[0])

        self.assertMgribArgsEqual(orders[0], cosmo={}, ifs={})


add_recipe_test_cases(__name__, "sf3h")
