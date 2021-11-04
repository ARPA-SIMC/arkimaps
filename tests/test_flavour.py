# from __future__ import annotations
import contextlib
import os
import tempfile
from typing import Dict, Any
import unittest
import yaml
from arkimapslib.unittest import IFSMixin, ArkimetMixin, RecipeTestMixin


class TestFlavour(IFSMixin, ArkimetMixin, RecipeTestMixin, unittest.TestCase):
    recipe_name = "t2m"
    expected_basemap_args = {}

    @contextlib.contextmanager
    def recipes(self, flavours: Dict[str, Any], recipes: Dict[str, Any]):
        with tempfile.TemporaryDirectory() as recipe_dir:
            # Write flavours definition
            with open(os.path.join(recipe_dir, "flavours.yaml"), "wt") as fd:
                flavour_data = []
                for name, steps in flavours.items():
                    flavour_data.append({
                        "name": name,
                        "steps": steps,
                    })
                yaml.dump({"flavours": flavour_data}, fd)

            # Write inputs definition
            with open(os.path.join(recipe_dir, "inputs.yaml"), "wt") as fd:
                yaml.dump({
                    "inputs": {
                        "t2m": [
                            {
                                "model": "cosmo",
                                "arkimet": "product:GRIB1,,2,11;level:GRIB1,105,2",
                                "eccodes": 'shortName is "2t" and indicatorOfTypeOfLevel == 105'
                                           ' and timeRangeIndicator == 0 and level == 2',
                            }
                        ],
                    },
                }, fd)

            # Write recipes definitions
            for name, steps in recipes.items():
                with open(os.path.join(recipe_dir, f"{name}.yaml"), "wt") as fd:
                    yaml.dump({"recipe": steps}, fd)

            self.load_recipes([recipe_dir])
            self.kitchen.pantry.fill(path="testdata/t2m/cosmo_t2m+12.arkimet")

            yield recipe_dir

    def make_order(self, flavour: str, recipe: str):
        recipe = self.kitchen.recipes.get(recipe)
        flavour = self.kitchen.flavours.get(flavour)
        orders = flavour.make_orders(recipe, self.kitchen.pantry)
        self.assertEqual(len(orders), 1)
        return orders[0]

    def test_default_params(self):
        test_params = {
            "map_coastline_sea_shade_colour": "#f2f2f2",
            "map_grid": "off",
            "map_coastline_sea_shade": "off",
            "map_label": "off",
            "map_coastline_colour": "#000000",
            "map_coastline_resolution": "medium",
        }
        with self.recipes(flavours={
                              "test": {
                                "add_coastlines_fg": {"params": test_params}
                              }
                          },
                          recipes={"test": [
                              {"step": "add_coastlines_fg"},
                              {"step": "add_grib", "grib": "t2m"},
                          ]}):
            order = self.make_order("test", "test")
            add_coastlines_fg = self.get_step(order, "add_coastlines_fg")
            self.assertEqual(add_coastlines_fg.params["params"], test_params)

    def test_default_shape(self):
        # FIXME: reactivate test once #82 is fixed
        self.skipTest("This currently makes Magics error out, see #82")
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
            flavour = self.kitchen.flavours.get("test")
            orders = flavour.make_orders(recipe, self.kitchen.pantry)
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

            steps = [x.name for x in orders[0].order_steps]
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
