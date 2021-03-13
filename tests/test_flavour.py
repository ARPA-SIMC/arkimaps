# from __future__ import annotations
import unittest
import tempfile
import os
import yaml
from arkimapslib.unittest import IFSMixin, ArkimetMixin, RecipeTestMixin


class TestFlavour(IFSMixin, ArkimetMixin, RecipeTestMixin, unittest.TestCase):
    recipe_name = "t2m"
    expected_basemap_args = {}

    def test_default_params(self):
        test_params = {
            "map_coastline_sea_shade_colour": "#f2f2f2",
            "map_grid": "off",
            "map_coastline_sea_shade": "off",
            "map_label": "off",
            "map_coastline_colour": "#000000",
            "map_coastline_resolution": "medium",
        }
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

            self.fill_pantry(recipe_dirs=[extra_recipes, "recipes"])

            orders = self.make_orders(flavour_name="test")
            self.assertEqual(len(orders), 1)

            self.assertRenders(orders[0])

            add_coastlines_fg = self.get_step(orders[0], "add_coastlines_fg")
            self.assertEqual(add_coastlines_fg.params["params"], test_params)

    def test_default_shape(self):
        with tempfile.TemporaryDirectory() as extra_recipes:
            with open(os.path.join(extra_recipes, "test.yaml"), "wt") as fd:
                yaml.dump({
                    "flavours": [
                        {
                            "name": "test",
                            "steps": {
                                "add_user_boundaries": {
                                    "shape": "test",
                                },
                            }
                        }
                    ],
                    "inputs": {
                        "test": {
                            "type": "shape",
                            "path": "shapes/Sottozone_allerta_ER",
                        }
                    },
                    "recipe": [
                        {"step": "add_basemap"},
                        {"step": "add_grib", "grib": "t2m"},
                        {"step": "add_user_boundaries",
                         # "shape": "sottozone_allerta_er",
                         "params": {"map_user_layer_colour": "blue"}},
                    ]
                }, fd)

            self.fill_pantry(recipe_dirs=[extra_recipes, "recipes"])
            recipe = self.kitchen.recipes.get("test")
            orders = recipe.make_orders(self.kitchen.pantry, flavour=self.kitchen.flavours.get("test"))
            self.assertEqual(len(orders), 1)

            self.assertRenders(orders[0], output_name="test+012.png")

            add_user_boundaries = self.get_step(orders[0], "add_user_boundaries")
            self.assertEqual(add_user_boundaries.params["shape"], "test")

    def test_step_filter(self):
        self.maxDiff = None
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
            self.fill_pantry(recipe_dirs=[extra_recipes, "recipes"])

            orders = self.make_orders(flavour_name="test")
            self.assertEqual(len(orders), 1)

            self.assertRenders(orders[0])

            steps = [x.name for x in orders[0].recipe_steps]
            self.assertEqual(steps, [
                'add_basemap',
                'add_coastlines_bg',
                'add_grib',
                # 'add_contour',
                'add_coastlines_fg',
                'add_grid',
                'add_boundaries',
            ])

    def test_recipe_filter(self):
        self.maxDiff = None
        with tempfile.TemporaryDirectory() as extra_recipes:
            with open(os.path.join(extra_recipes, "test.yaml"), "wt") as fd:
                yaml.dump({
                    "flavours": [
                        {
                            "name": "test",
                            "recipes_filter": ["t2m"],
                        }
                    ]
                }, fd)
            self.fill_pantry(recipe_dirs=[extra_recipes, "recipes"])
            self.fill_pantry(recipe_dirs=[extra_recipes, "recipes"], recipe_name="tcc")

            orders = self.kitchen.make_orders(flavour=self.kitchen.flavours.get("default"))
            self.assertCountEqual(
                    [o.basename for o in orders],
                    ["t2m+012", "tcc+012"])

            orders = self.kitchen.make_orders(flavour=self.kitchen.flavours.get("test"))
            self.assertCountEqual(
                    [o.basename for o in orders],
                    ["t2m+012"])
