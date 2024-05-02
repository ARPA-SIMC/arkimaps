# from __future__ import annotations
from arkimapslib.unittest import recipe_tests


@recipe_tests("mslp")
class MSLPMixin:
    def test_dispatch(self):
        self.fill_pantry()

        orders = self.make_orders()
        self.assertEqual(len(orders), 1)

        self.assertRenders(orders[0])

        self.assertMgribArgsEqual(
            orders[0],
            cosmo={"grib_automatic_scaling": False, "grib_scaling_factor": 0.01},
            ifs={"grib_automatic_scaling": False, "grib_scaling_factor": 0.01},
        )

    def test_legend(self):
        # Test that mslp does not produce a legend
        self.fill_pantry(flavour_name="ita_small_tiles")
        orders = self.make_orders(flavour_name="ita_small_tiles")
        self.assertEqual(len(orders), 2)
        self.assertEqual(str(orders[0]), "mslp+012/6/32/22+w4h4")
        self.assertEqual(str(orders[1]), "mslp+012/7/65/44+w7h7")
