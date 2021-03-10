# from __future__ import annotations
from arkimapslib.unittest import add_recipe_test_cases


class RH2MMixin:
    def test_dispatch(self):
        with self.kitchen_class() as kitchen:
            self.fill_pantry(kitchen)

            # Check that the right input was selected
            cpdec3h = kitchen.pantry.inputs.get("rh2m")
            for i in cpdec3h:
                self.assertEqual(i.__class__.__name__, "VG6DTransform")

            orders = self.make_orders(kitchen)
            self.assertEqual(len(orders), 1)

            self.assertRenders(kitchen, orders[0])

            self.assertMgribArgsEqual(orders[0], cosmo={}, ifs={})


add_recipe_test_cases(__name__, "rh2m")
