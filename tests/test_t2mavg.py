# from __future__ import annotations
from arkimapslib.unittest import recipe_tests


@recipe_tests("t2mavg")
class T2MAVGMixin:
    def test_dispatch(self):
        self.fill_pantry()

        orders = self.make_orders()
        self.assertEqual(len(orders), 1)

        self.assertProcessLogEqual(
            [
                "t2mavg:Average:vg6d_transform '--comp-step=0 24'"
                " --comp-stat-proc=254:0 --comp-frac-valid=0 - t2mavg-decumulated.grib",
                "t2mavg:Average:grib_filter xxxb",
            ]
        )

        self.assertRenders(orders[0], step=24)

        self.assertMgribArgsEqual(
            orders[0],
            cosmo={
                "grib_automatic_scaling": False,
                "grib_scaling_offset": -273.15,
            },
            ifs={
                "grib_automatic_scaling": False,
                "grib_scaling_offset": -273.15,
            },
        )
