from arkimapslib.render import Renderer
from arkimapslib.unittest import add_recipe_test_cases
import os


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

            renderer = Renderer(workdir=kitchen.workdir)
            with self.assertLogs() as log:
                renderer.render_one(orders[0])

            mgrib_args_prefix = "INFO:arkimaps.order.rh2m+012:add_grib mgrib "
            mgrib_args = None
            for l in log.output:
                if l.startswith(mgrib_args_prefix):
                    mgrib_args = l[len(mgrib_args_prefix):]

            self.assertIsNotNone(orders[0].output)
            self.assertEqual(os.path.basename(orders[0].output), "rh2m+012.png")

            expected_mgrib_args = {
                "cosmo": "{}",
                "ifs": "{}",
            }

            self.assertIsNotNone(mgrib_args)
            self.assertEqual(mgrib_args, expected_mgrib_args[self.model_name])


add_recipe_test_cases(__name__, "rh2m")
