# from __future__ import annotations
from arkimapslib.unittest import add_recipe_test_cases


class ALT0CosmoMixin:
    def test_process(self):
        self.fill_pantry(expected=["cosmo_alt0_2021_1_10_0_0_0+12.grib"])

        orders = self.make_orders()
        self.assertEqual(len(orders), 1)

        self.assertRenders(orders[0])

        self.assertMgribArgsEqual(orders[0], cosmo={}, ifs={})


class ALT0IFSMixin:
    def test_process(self):
        self.fill_pantry(expected=[
            "ifs_alt0ground_2021_1_10_0_0_0+12.grib",
            "ifs_z_2021_1_10_0_0_0+0.grib",
        ])

        orders = self.make_orders()
        self.assertEqual(len(orders), 1)

        self.assertRenders(orders[0])

        self.assertMgribArgsEqual(orders[0], cosmo={}, ifs={})


add_recipe_test_cases(__name__, "alt0")
