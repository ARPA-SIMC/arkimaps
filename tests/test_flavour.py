# from __future__ import annotations
import unittest
import tempfile
import os
import yaml
from arkimapslib.unittest import IFSMixin, ArkimetMixin, RecipeTestMixin


class TestFlavour(IFSMixin, ArkimetMixin, RecipeTestMixin, unittest.TestCase):
    recipe_name = "t2m"
    expected_basemap_args = {}

    def test_defaults(self):
        test_params = {
            "map_coastline_sea_shade_colour": "#f2f2f2",
            "map_grid": "off",
            "map_coastline_sea_shade": "off",
            "map_label": "off",
            "map_coastline_colour": "#000000",
            "map_coastline_resolution": "medium",
        }
        with self.kitchen_class() as kitchen:
            with tempfile.TemporaryDirectory() as extra_recipes:
                with open(os.path.join(extra_recipes, "test.yaml"), "wt") as fd:
                    yaml.dump({
                        "flavours": [
                            {
                                "name": "test",
                                "steps": {
                                    "add_coastlines_fg": {
                                        "params": test_params,
                                    },
                                }
                            }
                        ]
                    }, fd)

                self.fill_pantry(kitchen, recipe_dirs=[extra_recipes, "recipes"])

                orders = self.make_orders(kitchen, flavour_names="test")
                self.assertEqual(len(orders), 1)

                self.assertRenders(kitchen, orders[0])

                add_coastlines_fg_trace = self.get_debug_trace(orders[0], "add_coastlines_fg")
                self.assertEqual(add_coastlines_fg_trace["params"], test_params)

    def test_step_filter(self):
        self.maxDiff = None
        with self.kitchen_class() as kitchen:
            with tempfile.TemporaryDirectory() as extra_recipes:
                with open(os.path.join(extra_recipes, "test.yaml"), "wt") as fd:
                    yaml.dump({
                        "flavours": [
                            {
                                "name": "test",
                                "steps": {
                                    "add_contour": {
                                        "skip": True,
                                    },
                                }
                            }
                        ]
                    }, fd)
                self.fill_pantry(kitchen, recipe_dirs=[extra_recipes, "recipes"])

                orders = self.make_orders(kitchen, flavour_names="test")
                self.assertEqual(len(orders), 1)

                self.assertRenders(kitchen, orders[0])

                steps = [x["name"] for x in orders[0].debug_trace]
                self.assertEqual(steps, [
                    'add_basemap',
                    'add_coastlines_bg',
                    'add_grib',
                    # 'add_contour',
                    'add_coastlines_fg',
                    'add_grid',
                    'add_boundaries',
                ])
