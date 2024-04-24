# from __future__ import annotations
from arkimapslib.unittest import recipe_tests


@recipe_tests("hzero", models=["Cosmo"])
class HZEROCosmoMixin:
    def test_process(self):
        self.fill_pantry(expected=["cosmo_hzero_2021_1_10_0_0_0+12.grib"])

        orders = self.make_orders()
        self.assertEqual(len(orders), 1)

        self.assertProcessLogEqual([])

        self.assertRenders(orders[0])

        self.assertMgribArgsEqual(orders[0], cosmo={}, ifs={})


@recipe_tests("hzero", models=["IFS"])
class HZEROIFSMixin:
    def test_process(self):
        self.maxDiff = None
        self.fill_pantry(
            expected=[
                "ifs_hzeroground_2021_1_10_0_0_0+12.grib",
                "ifs_z_2021_1_10_0_0_0+0.grib",
            ]
        )

        orders = self.make_orders()
        self.assertEqual(len(orders), 1)

        self.assertProcessLogEqual(
            [
                "hzero:GroundToMSL:groundtomsl"
                " ifs_z_2021_1_10_0_0_0+0.grib"
                " ifs_hzeroground_2021_1_10_0_0_0+12.grib"
                " ifs_hzero_2021_1_10_0_0_0+12.grib"
            ]
        )

        self.assertRenders(orders[0])

        self.assertMgribArgsEqual(orders[0], cosmo={}, ifs={})
