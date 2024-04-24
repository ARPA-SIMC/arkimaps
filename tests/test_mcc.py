# from __future__ import annotations
from arkimapslib.unittest import recipe_tests


@recipe_tests("tiles/mcc")
class MCCMixin:
    def test_dispatch(self):
        self.fill_pantry()

        orders = self.make_orders()
        self.assertEqual(len(orders), 1)

        self.assertRenders(orders[0])

        self.assertMgribArgsEqual(
            orders[0],
            cosmo={"grib_automatic_scaling": False, "grib_scaling_factor": 0.08},
            ifs={"grib_automatic_scaling": False, "grib_scaling_factor": 8},
        )
