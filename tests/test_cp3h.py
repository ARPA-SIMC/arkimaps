# from __future__ import annotations
from arkimapslib.unittest import add_recipe_test_cases


class CP3HMixin:
    def test_dispatch(self):
        self.fill_pantry(expected=[f"{self.model_name}_cp+{step}.grib" for step in range(3, 13, 3)])

        # Check that the right input was selected
        cpdec3h = self.kitchen.pantry.inputs.get("cpdec3h")
        for i in cpdec3h:
            self.assertEqual(i.__class__.__name__, "Decumulate")

        orders = self.make_orders()
        self.assertGreaterEqual(len(orders), 4)
        orders = [o for o in orders if o.basename == "cp3h+012"]
        self.assertEqual(len(orders), 1)

        self.assertRenders(orders[0])

        self.assertMgribArgsEqual(orders[0], cosmo={}, ifs={})


add_recipe_test_cases(__name__, "cp3h")
