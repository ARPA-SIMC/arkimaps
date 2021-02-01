from arkimapslib.render import Renderer
from arkimapslib.unittest import add_recipe_test_cases
import os


class TP2HMixin:
    kitchen_class = None

    def test_dispatch(self):
        with self.kitchen_class() as kitchen:
            kitchen.load_recipes("recipes")

            # Check that the right input was selected
            recipe = kitchen.recipes.get("tp1h")
            for i in recipe.inputs["tp"]:
                self.assertEqual(i.__class__.__name__, "Decumulate")

            kitchen.pantry.fill(kitchen.recipes, path=self.get_sample_path("tp1h", 12))

            orders = list(kitchen.pantry.orders(kitchen.recipes))
            self.assertEqual(len(orders), 1)

            renderer = Renderer()
            with self.assertLogs() as log:
                renderer.render_one(orders[0])

            mgrib_args_prefix = "INFO:arkimaps.order.tp1h+012:add_grib mgrib "
            mgrib_args = None
            for l in log.output:
                if l.startswith(mgrib_args_prefix):
                    mgrib_args = l[len(mgrib_args_prefix):]

            self.assertIsNotNone(orders[0].output)
            self.assertEqual(os.path.basename(orders[0].output), "tp1h+012.png")

            expected_mgrib_args = {
                "cosmo": "{}",
                "ifs": "{}",
            }

            self.assertIsNotNone(mgrib_args)
            self.assertEqual(mgrib_args, expected_mgrib_args[self.model_name])


add_recipe_test_cases(__name__, "TP2H")
