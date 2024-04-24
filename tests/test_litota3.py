# from __future__ import annotations
import datetime
import os
import unittest
from arkimapslib.unittest import recipe_tests


@recipe_tests("litota3")
class LITOTA3Mixin:
    def test_recipe(self):
        self.maxDiff = None

        # Input for litota3 is not computed by COSMO. See #64
        if self.model_name == "cosmo":
            raise unittest.SkipTest(f"{self.recipe_name} tests for COSMO skipped, we currently miss input data")

        self.fill_pantry(reftime=datetime.datetime(2021, 3, 4))

        litota3 = self.kitchen.pantry.inputs.get("litota3")
        for i in litota3:
            self.assertEqual(i.__class__.__name__, "Source")
        sottozone_allerta_er = self.kitchen.pantry.inputs.get("sottozoneAllertaER")
        for i in sottozone_allerta_er:
            self.assertEqual(i.__class__.__name__, "Shape")
        punti_citta = self.kitchen.pantry.inputs.get("puntiCitta")
        for i in punti_citta:
            self.assertEqual(i.__class__.__name__, "Static")

        orders = self.make_orders()
        self.assertEqual(len(orders), 1)

        input_files = orders[0].input_files
        self.assertEqual(os.path.basename(input_files["litota3"].pathname), "litota3_2021_3_4_0_0_0+12.grib")
        self.assertEqual(len(input_files), 1)

        self.assertRenders(orders[0], reftime=datetime.datetime(2021, 3, 4))

        self.assertMgribArgsEqual(orders[0], cosmo={}, ifs={})


@recipe_tests("litota3")
class LITOTA3NordMixin:
    flavour_name = "nord"

    expected_basemap_args = {
        "page_id_line": False,
        "output_width": 1000,
        "page_x_length": 38,
        "page_y_length": 24,
        "subpage_map_projection": "mercator",
        "subpage_lower_left_latitude": 43.0,
        "subpage_lower_left_longitude": 5.1,
        "subpage_upper_right_latitude": 47.5,
        "subpage_upper_right_longitude": 15.0,
        "subpage_map_vertical_longitude": 10.3,
        "subpage_x_length": 34,
        "subpage_x_position": 2,
        "subpage_y_length": 23,
        "subpage_y_position": 1,
        "super_page_x_length": 40,
        "super_page_y_length": 25,
        "map_grid": True,
        "map_grid_latitude_reference": 45.0,
        "map_grid_longitude_reference": 0.0,
        "map_grid_longitude_increment": 1.0,
        "map_grid_latitude_increment": 1.0,
        "map_grid_colour": "grey",
        "map_grid_line_style": "dash",
        "map_label_colour": "black",
        "map_label_height": 0.4,
        "map_label_latitude_frequency": 1,
    }

    def test_recipe(self):
        self.maxDiff = None

        # Input for litota3 is not computed by COSMO. See #64
        if self.model_name == "cosmo":
            raise unittest.SkipTest(f"{self.recipe_name} tests for COSMO skipped, we currently miss input data")

        self.fill_pantry(reftime=datetime.datetime(2021, 3, 4))

        litota3 = self.kitchen.pantry.inputs.get("litota3")
        for i in litota3:
            self.assertEqual(i.__class__.__name__, "Source")
        sottozone_allerta_er = self.kitchen.pantry.inputs.get("sottozoneAllertaER")
        for i in sottozone_allerta_er:
            self.assertEqual(i.__class__.__name__, "Shape")
        punti_citta = self.kitchen.pantry.inputs.get("puntiCitta")
        for i in punti_citta:
            self.assertEqual(i.__class__.__name__, "Static")

        orders = self.make_orders()
        self.assertEqual(len(orders), 1)

        input_files = orders[0].input_files
        self.assertEqual(os.path.basename(input_files["litota3"].pathname), "litota3_2021_3_4_0_0_0+12.grib")
        self.assertEqual(os.path.basename(input_files["sottozoneAllertaER"].pathname), "Sottozone_allerta_ER")
        self.assertEqual(os.path.basename(input_files["puntiCitta"].pathname), "puntiCitta.geo")

        self.assertRenders(orders[0], reftime=datetime.datetime(2021, 3, 4))

        self.assertMgribArgsEqual(orders[0], cosmo={}, ifs={})
