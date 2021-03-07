# from __future__ import annotations
import unittest
import os
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
            punti_citta = kitchen.pantry.inputs.get("punti_citta")
            for i in punti_citta:
                self.assertEqual(i.__class__.__name__, "Static")

            orders = self.make_orders(kitchen)
            self.assertEqual(len(orders), 1)

            sources = orders[0].sources
            self.assertEqual(os.path.basename(sources["litota3"].pathname), "litota3+12.grib")
            self.assertEqual(os.path.basename(sources["sottozone_allerta_er"].pathname), "Sottozone_allerta_ER")
            self.assertEqual(os.path.basename(sources["punti_citta"].pathname), "puntiCitta.geo")

            self.assertRenders(kitchen, orders[0])

            mgrib_args = self.get_debug_trace(orders[0], "add_grib")
            expected_mgrib_args = {
                "cosmo": {},
                "ifs": {},
            }
            self.assertEqual(mgrib_args, expected_mgrib_args[self.model_name])


add_recipe_test_cases(__name__, "litota3_nord")
