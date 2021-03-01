# from __future__ import annotations
from arkimapslib.render import Renderer
from arkimapslib.unittest import add_recipe_test_cases
import os


class CP3HMixin:
    def test_dispatch(self):
        with self.kitchen_class() as kitchen:
            self.fill_pantry(kitchen, expected=[f"{self.model_name}_cp+{step}.grib" for step in range(3, 13, 3)])

            # Check that the right input was selected
            cpdec3h = kitchen.pantry.inputs.get("cpdec3h")
            for i in cpdec3h:
                self.assertEqual(i.__class__.__name__, "Decumulate")

            orders = self.make_orders(kitchen)
            self.assertGreaterEqual(len(orders), 4)
            orders = [o for o in orders if o.basename == "cp3h+012"]
            self.assertEqual(len(orders), 1)

            renderer = Renderer(kitchen.workdir)
            with self.assertLogs() as log:
                renderer.render_one(orders[0])

            mgrib_args_prefix = "INFO:arkimaps.order.cp3h+012:add_grib mgrib "
            mgrib_args = None
            for l in log.output:
                if l.startswith(mgrib_args_prefix):
                    mgrib_args = l[len(mgrib_args_prefix):]

            self.assertIsNotNone(orders[0].output)
            self.assertEqual(os.path.basename(orders[0].output), "cp3h+012.png")

            expected_mgrib_args = {
                "cosmo": "{}",
                "ifs": "{}",
            }

            self.assertIsNotNone(mgrib_args)
            self.assertEqual(mgrib_args, expected_mgrib_args[self.model_name])


add_recipe_test_cases(__name__, "cp3h")
