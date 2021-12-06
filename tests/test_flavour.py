# from __future__ import annotations
import contextlib
import os
import tempfile
from typing import Dict, Any, Optional, List
import unittest
import yaml
from arkimapslib.kitchen import ArkimetKitchen


def flavour(name: str, steps: Optional[Dict[str, Any]] = None, **kw) -> Dict[str, Any]:
    return {
        "name": name,
        "steps": steps if steps is not None else {},
        **kw
    }


class TestFlavour(unittest.TestCase):
    recipe_name = "t2m"
    expected_basemap_args = {}

    @contextlib.contextmanager
    def kitchen(self, flavours: List[Dict[str, Any]], recipes: Dict[str, Any], inputs: Optional[Dict[str, Any]] = None):
        if inputs is None:
            inputs = {}

        with tempfile.TemporaryDirectory() as recipe_dir:
            # Write flavours definition
            with open(os.path.join(recipe_dir, "flavours.yaml"), "wt") as fd:
                yaml.dump({"flavours": flavours}, fd)

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
                        **inputs,
                    },
                }, fd)

            # Write recipes definitions
            for name, steps in recipes.items():
                with open(os.path.join(recipe_dir, f"{name}.yaml"), "wt") as fd:
                    yaml.dump({"recipe": steps}, fd)

            with ArkimetKitchen() as kitchen:
                kitchen.load_recipes([recipe_dir])
                kitchen.pantry.fill(path="testdata/t2m/cosmo_t2m_2021_1_10_0_0_0+12.arkimet")
                yield kitchen

    def get_step(self, order, step_name: str):
        """
        Return the debug trace arguments of the first step in the order's
        debug_trace log with the given name.

        Fails the test if not found
        """
        for step in order.order_steps:
            if step.name == step_name:
                return step
        self.fail(f"Step {step_name} not found in debug trace of order {order}")

    def make_order(self, kitchen, flavour: str = "default", recipe: str = "t2m"):
        orders = kitchen.make_orders(flavour, recipe=recipe)
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
        with self.kitchen(flavours=[flavour("test", {"add_coastlines_fg": {"params": test_params}})],
                          recipes={"test": [
                              {"step": "add_coastlines_fg"},
                              {"step": "add_grib", "grib": "t2m"},
                          ]}) as kitchen:
            order = self.make_order(kitchen, "test", "test")
            add_coastlines_fg = self.get_step(order, "add_coastlines_fg")
            self.assertEqual(add_coastlines_fg.params["params"], test_params)

    def test_default_shape(self):
        with self.kitchen(flavours=[
                              flavour("test", steps={"add_user_boundaries": {"shape": "test"}}),
                          ],
                          recipes={
                              "t2m": [{"step": "add_grib", "grib": "t2m"}, {"step": "add_user_boundaries"}],
                          },
                          inputs={
                              "test": {
                                  "type": "shape",
                                  "path": "shapes/Sottozone_allerta_ER",
                              }
                          }) as kitchen:
            order = self.make_order(kitchen, "test", "t2m")
            add_user_boundaries = self.get_step(order, "add_user_boundaries")
            self.assertEqual(add_user_boundaries.params["shape"], "test")

    def test_step_filter(self):
        with self.kitchen(flavours=[
                              flavour("default"),
                              flavour("test", steps={"add_contour": {"skip": True}}),
                          ],
                          recipes={
                              "t2m": [{"step": "add_grib", "grib": "t2m"}, {"step": "add_contour"}],
                          }) as kitchen:

            order = self.make_order(kitchen, "default", "t2m")
            self.assertEqual([x.name for x in order.order_steps], ["add_grib", "add_contour"])

            order = self.make_order(kitchen, "test", "t2m")
            self.assertEqual([x.name for x in order.order_steps], ["add_grib"])

    def test_recipe_filter(self):
        with self.kitchen(flavours=[
                              flavour("default"),
                              flavour("test", recipes_filter=["t2m"]),
                          ],
                          recipes={
                              "t2m": [{"step": "add_grib", "grib": "t2m"}],
                              "tcc": [{"step": "add_grib", "grib": "t2m"}],
                          }) as kitchen:
            orders = kitchen.make_orders(flavour=kitchen.flavours.get("default"))
            self.assertCountEqual(
                    [o.basename for o in orders],
                    ["t2m_2021-01-10T00:00:00+012", "tcc_2021-01-10T00:00:00+012"])

            orders = kitchen.make_orders(flavour=kitchen.flavours.get("test"))
            self.assertCountEqual(
                    [o.basename for o in orders],
                    ["t2m_2021-01-10T00:00:00+012"])
