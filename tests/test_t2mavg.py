# from __future__ import annotations
from arkimapslib.unittest import add_recipe_test_cases


class T2MAVGMixin:
    def test_dispatch(self):
        self.fill_pantry()

        orders = self.make_orders()
        self.assertEqual(len(orders), 1)

        self.assertProcessLogEqual([
            "t2mavg:Average:vg6d_transform --comp-frac-valid=0 '--comp-step=0 24'"
            " --comp-stat-proc=254:0 - t2mavg-decumulated.grib",
        ])

        self.assertRenders(orders[0], step=24)

        self.assertMgribArgsEqual(orders[0], cosmo={
                'grib_automatic_scaling': False, 'grib_scaling_offset': -273.15,
            }, ifs={
                'grib_automatic_scaling': False, 'grib_scaling_offset': -273.15,
            })


add_recipe_test_cases(__name__, "t2mavg")
