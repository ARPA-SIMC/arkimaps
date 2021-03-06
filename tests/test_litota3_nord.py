# from __future__ import annotations
import unittest
import os
from arkimapslib.render import Renderer
from arkimapslib.unittest import add_recipe_test_cases


class LITOTA3_NORDMixin:
    def test_recipe(self):
        # Input for litota3 is not computed by COSMO. See #64
        if self.model_name == "cosmo":
            raise unittest.SkipTest(f"{self.recipe_name} tests for COSMO skipped, we currently miss input data")

        with self.kitchen_class() as kitchen:
            self.fill_pantry(kitchen)

            litota3 = kitchen.pantry.inputs.get("litota3")
            for i in litota3:
                self.assertEqual(i.__class__.__name__, "Source")
            sottozone_allerta_er = kitchen.pantry.inputs.get("sottozone_allerta_er")
            for i in sottozone_allerta_er:
                self.assertEqual(i.__class__.__name__, "Shape")

            orders = self.make_orders(kitchen)
            self.assertEqual(len(orders), 1)

            renderer = Renderer(workdir=kitchen.workdir)
            with self.assertLogs() as log:
                renderer.render_one(orders[0])

            mgrib_args_prefix = f"INFO:arkimaps.order.{self.recipe_name}+012:add_grib mgrib "
            mgrib_args = None
            for l in log.output:
                if l.startswith(mgrib_args_prefix):
                    mgrib_args = l[len(mgrib_args_prefix):]

            self.assertIsNotNone(orders[0].output)
            self.assertEqual(os.path.basename(orders[0].output), "litota3_nord+012.png")

            expected_mgrib_args = {
                "cosmo": "{}",
                "ifs": "{}",
            }

            self.assertIsNotNone(mgrib_args)
            self.assertEqual(mgrib_args, expected_mgrib_args[self.model_name])


add_recipe_test_cases(__name__, "litota3_nord")
