# from __future__ import annotations
from arkimapslib.unittest import add_recipe_test_cases


class HZEROCosmoMixin:
    def test_process(self):
        self.fill_pantry(expected=["cosmo_hzero_2021_1_10_0_0_0+12.grib"])

        orders = self.make_orders()
        self.assertEqual(len(orders), 1)

        self.assertProcessLogEqual([])

        self.assertRenders(orders[0])

        self.assertMgribArgsEqual(orders[0], cosmo={}, ifs={})


class HZEROIFSMixin:
    def test_process(self):
        self.maxDiff = None
        self.fill_pantry(expected=[
            "ifs_hzeroground_2021_1_10_0_0_0+12.grib",
            "ifs_z_2021_1_10_0_0_0+0.grib",
        ])

        orders = self.make_orders()
        self.assertEqual(len(orders), 1)

        self.assertProcessLogEqual(
            ["hzero:GroundToMSL:groundtomsl"
             " ifs_z_2021_1_10_0_0_0+0.grib"
             " ifs_hzeroground_2021_1_10_0_0_0+12.grib"
             " ifs_hzero_2021_1_10_0_0_0+12.grib"]
        )

        self.assertRenders(orders[0])

        self.assertMgribArgsEqual(orders[0], cosmo={}, ifs={})


add_recipe_test_cases(__name__, "hzero")
