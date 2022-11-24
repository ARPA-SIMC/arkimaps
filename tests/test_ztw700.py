# from __future__ import annotations
from arkimapslib.unittest import add_recipe_test_cases


class ZTW700Mixin:
    def test_dispatch(self):
        self.maxDiff = None

        pantry_reftime = "2021_1_10_0_0_0"
        self.fill_pantry(expected=[
            f'{self.model_name}_t700_{pantry_reftime}+12.grib',
            f'{self.model_name}_u700_{pantry_reftime}+12.grib',
            f'{self.model_name}_v700_{pantry_reftime}+12.grib',
            f'{self.model_name}_z700_{pantry_reftime}+12.grib',
        ])

        orders = self.make_orders()
        self.assertEqual(len(orders), 1)

        self.assertProcessLogEqual([
            f'uv700:Cat:cat {self.model_name}_u700_2021_1_10_0_0_0+12.grib,'
            f'{self.model_name}_v700_2021_1_10_0_0_0+12.grib'
            ' uv700_2021_1_10_0_0_0+12.grib',
        ])

        self.assertRenders(orders[0])

        self.assertMgribArgsEqual(orders[0], cosmo={}, ifs={})


add_recipe_test_cases(__name__, "standalone/ztw700")
