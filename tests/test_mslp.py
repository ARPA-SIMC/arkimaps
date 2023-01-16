# from __future__ import annotations
from arkimapslib.unittest import add_recipe_test_cases


class MSLPMixin:
    def test_dispatch(self):
        self.fill_pantry()

        orders = self.make_orders()
        self.assertEqual(len(orders), 1)

        self.assertRenders(orders[0])

        self.assertMgribArgsEqual(
            orders[0],
            cosmo={'grib_automatic_scaling': False, 'grib_scaling_factor': 0.01},
            ifs={'grib_automatic_scaling': False, 'grib_scaling_factor': 0.01},
        )

    def test_legend(self):
        # Test that mslp does not produce a legend
        self.fill_pantry(flavour_name="ita_small_tiles")
        orders = self.make_orders(flavour_name="ita_small_tiles")
        self.assertEqual(orders[-1].render_script, "2021-01-10T00:00:00/mslp_ita_small_tiles+012/7/71/50.py")
        self.assertEqual(len(orders), 65)


add_recipe_test_cases(__name__, "mslp")
