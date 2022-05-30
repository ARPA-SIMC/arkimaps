# from __future__ import annotations
from arkimapslib.unittest import add_recipe_test_cases


class SF3HCosmoMixin:
    def test_process(self):
        self.maxDiff = None
        pantry_reftime = "2021_1_10_0_0_0"
        self.fill_pantry(expected=[
            f"{self.model_name}_{prod}_{pantry_reftime}+{step}.grib"
            for step in range(0, 13)
            for prod in ("snowcon", "snowgsp")])

        orders = self.make_orders()
        self.assertGreaterEqual(len(orders), 4)
        orders = [o for o in orders if o.basename == "sf3h+012"]
        self.assertEqual(len(orders), 1)

        self.assertProcessLogEqual(
            ["snowsum:VG6DTransform:vg6d_transform --output-variable-list=B13205 -"
             f" snowsum_2021_1_10_0_0_0+{step}.grib" for step in range(0, 13)] +
            [f"snow:Or:snowsum_2021_1_10_0_0_0+{step}.grib as snow_2021_1_10_0_0_0+{step}.grib"
             for step in range(0, 13)] +
            ["snowdec3h:Decumulate:vg6d_transform --comp-frac-valid=0 '--comp-step=0 03'"
             " --comp-stat-proc=1 --comp-full-steps - snowdec3h-decumulated.grib"]
        )

        self.assertRenders(orders[0])

        self.assertMgribArgsEqual(orders[0], cosmo={}, ifs={})


class SF3HNoConvMixin:
    def test_process(self):
        self.maxDiff = None
        pantry_reftime = "2021_1_10_0_0_0"
        self.fill_pantry(
            expected=[
                f"{self.model_name}_snowgsp_{pantry_reftime}+{step}.grib"
                for step in range(0, 13)],
            exclude="*_snowcon_*")

        orders = self.make_orders()
        self.assertGreaterEqual(len(orders), 4)
        orders = [o for o in orders if o.basename == "sf3h+012"]
        self.assertEqual(len(orders), 1)

        self.assertProcessLogEqual(
            [f"snow:Or:cosmo_snowgsp_2021_1_10_0_0_0+{step}.grib as snow_2021_1_10_0_0_0+{step}.grib"
             for step in range(0, 13)] +
            ["snowdec3h:Decumulate:vg6d_transform --comp-frac-valid=0 '--comp-step=0 03'"
             " --comp-stat-proc=1 --comp-full-steps - snowdec3h-decumulated.grib"]
        )

        self.assertRenders(orders[0])

        self.assertMgribArgsEqual(orders[0], cosmo={}, ifs={})


class SF3HIFSMixin:
    def test_process(self):
        self.maxDiff = None
        pantry_reftime = "2021_1_10_0_0_0"
        self.fill_pantry(expected=[f"{self.model_name}_sf_{pantry_reftime}+{step}.grib" for step in range(3, 13, 3)])

        orders = self.make_orders()
        self.assertGreaterEqual(len(orders), 4)
        orders = [o for o in orders if o.basename == "sf3h+012"]
        self.assertEqual(len(orders), 1)

        self.assertProcessLogEqual(
            [f"snow:Or:ifs_sf_2021_1_10_0_0_0+{step}.grib as snow_2021_1_10_0_0_0+{step}.grib"
             for step in range(3, 13, 3)] +
            ["snowdec3h:Decumulate:vg6d_transform --comp-frac-valid=0 '--comp-step=0 03'"
             " --comp-stat-proc=1 --comp-full-steps - snowdec3h-decumulated.grib"]
        )

        self.assertRenders(orders[0])

        self.assertMgribArgsEqual(orders[0], cosmo={}, ifs={})


add_recipe_test_cases(__name__, "sf3h")
add_recipe_test_cases(__name__, "sf3h", models=["Cosmo"], test_mixin=SF3HNoConvMixin)
