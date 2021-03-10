# from __future__ import annotations
from arkimapslib.unittest import add_recipe_test_cases


class LCCMixin:
    def test_dispatch(self):
        with self.kitchen_class() as kitchen:
            self.fill_pantry(kitchen)

            orders = self.make_orders(kitchen)
            self.assertEqual(len(orders), 1)
            self.assertEqual(orders[0].basename, "lcc+012")

            self.assertRenders(kitchen, orders[0])

            self.assertMgribArgsEqual(
                orders[0],
                cosmo={'grib_automatic_scaling': False, 'grib_scaling_factor': 0.08},
                ifs={'grib_automatic_scaling': False, 'grib_scaling_factor': 8},
            )


add_recipe_test_cases(__name__, "lcc")
