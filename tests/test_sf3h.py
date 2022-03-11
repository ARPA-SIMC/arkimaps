# from __future__ import annotations
from arkimapslib.unittest import add_recipe_test_cases


class SF3HCosmoMixin:
    def test_dispatch(self):
        self.maxDiff = None
        pantry_reftime = "2021_1_10_0_0_0"
        self.fill_pantry(expected=[
            f"{self.model_name}_{prod}_{pantry_reftime}+{step}.grib"
            for step in range(0, 13)
            for prod in ("snow_con", "snow_gsp")])

        orders = self.make_orders()
        self.assertGreaterEqual(len(orders), 4)
        orders = [o for o in orders if o.basename == "sf3h+012"]
        self.assertEqual(len(orders), 1)

        self.assertProcessLogEqual(
            ["snow_sum:VG6DTransform:vg6d_transform --output-variable-list=B13205 -"
             f" cosmo_snow_sum_2021_1_10_0_0_0+{step}.grib" for step in range(0, 13)] +
            ["snowdec3h:Decumulate:vg6d_transform --comp-stat-proc=1 '--comp-step=0 03'"
             " --comp-frac-valid=0 --comp-full-steps - cosmo_snowdec3h-decumulated.grib"]
        )

        self.assertRenders(orders[0])

        self.assertMgribArgsEqual(orders[0], cosmo={}, ifs={})


class SF3HIFSMixin:
    def test_dispatch(self):
        pantry_reftime = "2021_1_10_0_0_0"
        self.fill_pantry(expected=[f"{self.model_name}_sf_{pantry_reftime}+{step}.grib" for step in range(3, 13, 3)])

        orders = self.make_orders()
        self.assertGreaterEqual(len(orders), 4)
        orders = [o for o in orders if o.basename == "sf3h+012"]
        self.assertEqual(len(orders), 1)

        self.assertProcessLogEqual([
            "snowdec3h:Decumulate:vg6d_transform --comp-stat-proc=1 '--comp-step=0 03'"
            " --comp-frac-valid=0 --comp-full-steps - ifs_snowdec3h-decumulated.grib",
        ])

        self.assertRenders(orders[0])

        self.assertMgribArgsEqual(orders[0], cosmo={}, ifs={})

# TODO: test the case without convective snowfall


add_recipe_test_cases(__name__, "sf3h")
