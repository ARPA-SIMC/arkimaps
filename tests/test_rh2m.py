# from __future__ import annotations
from arkimapslib.unittest import add_recipe_test_cases


class RH2MMixin:
    def test_dispatch(self):
        with self.kitchen_class() as kitchen:
            kitchen.load_recipes("recipes")
            kitchen.pantry.fill(path=self.get_sample_path("t2m", 12))
            kitchen.pantry.fill(path=self.get_sample_path("2d", 12))
            kitchen.pantry.fill(path=self.get_sample_path("mslp", 12))

            # Check that the right input was selected
            cpdec3h = kitchen.pantry.inputs.get("rh2m")
            for i in cpdec3h:
                self.assertEqual(i.__class__.__name__, "VG6DTransform")

            orders = self.make_orders(kitchen)
            self.assertEqual(len(orders), 1)

            self.assertRenders(kitchen, orders[0])

            mgrib_args = self.get_debug_trace(orders[0], "add_grib")
            expected_mgrib_args = {
                "cosmo": {},
                "ifs": {},
            }
            self.assertEqual(mgrib_args, expected_mgrib_args[self.model_name])


add_recipe_test_cases(__name__, "rh2m")
