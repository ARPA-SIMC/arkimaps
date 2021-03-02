from arkimapslib.render import Renderer
from arkimapslib.unittest import add_recipe_test_cases
import os


class MSLPMixin:
    def test_dispatch(self):
        with self.kitchen_class() as kitchen:
            self.fill_pantry(kitchen)

            orders = self.make_orders(kitchen)
            self.assertEqual(len(orders), 1)

            renderer = Renderer(kitchen.workdir)
            with self.assertLogs() as log:
                renderer.render_one(orders[0])

            mgrib_args_prefix = "INFO:arkimaps.order.mslp+012:add_grib mgrib "
            mgrib_args = None
            for l in log.output:
                if l.startswith(mgrib_args_prefix):
                    mgrib_args = l[len(mgrib_args_prefix):]

            self.assertIsNotNone(orders[0].output)
            self.assertEqual(os.path.basename(orders[0].output), "mslp+012.png")

            expected_mgrib_args = {
                "cosmo": "{'grib_automatic_scaling': False, 'grib_scaling_factor': 0.01}",
                "ifs": "{'grib_automatic_scaling': False, 'grib_scaling_factor': 0.01}",
            }

            self.assertIsNotNone(mgrib_args)
            self.assertEqual(mgrib_args, expected_mgrib_args[self.model_name])


add_recipe_test_cases(__name__, "mslp")
