# from __future__ import annotations
from arkimapslib.unittest import add_recipe_test_cases


class RH2MMixin:
    def test_dispatch(self):
        self.fill_pantry()

        # Check that the right input was selected
        cpdec3h = self.kitchen.pantry.inputs.get("rh2m")
        for i in cpdec3h:
            self.assertEqual(i.__class__.__name__, "VG6DTransform")

        orders = self.make_orders()
        self.assertEqual(len(orders), 1)

        self.assertRenders(orders[0])

        self.assertMgribArgsEqual(orders[0], cosmo={}, ifs={})


add_recipe_test_cases(__name__, "rh2m")
