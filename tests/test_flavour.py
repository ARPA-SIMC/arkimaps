# from __future__ import annotations
import contextlib
import os
import tempfile
import unittest
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

from arkimapslib import flavours
from arkimapslib.config import Config
from arkimapslib.definitions import Definitions
from arkimapslib.kitchen import ArkimetKitchen
from arkimapslib.steps import AddBasemapParamsSpec
from arkimapslib.unittest import scan_python_order


def flavour(name: str, steps: Optional[Dict[str, Any]] = None, **kw) -> Dict[str, Any]:
    return {"name": name, "steps": steps if steps is not None else {}, **kw}


class TestFlavour(unittest.TestCase):
    @contextlib.contextmanager
    def kitchen(self, flavours: List[Dict[str, Any]], recipes: Dict[str, Any], inputs: Optional[Dict[str, Any]] = None):
        if inputs is None:
            inputs = {}

        with tempfile.TemporaryDirectory() as tempdir:
            recipe_dir = Path(tempdir)
            # Write flavours definition
            with (recipe_dir / "flavours.yaml").open("wt") as fd:
                yaml.dump({"flavours": flavours}, fd)

            # Write inputs definition
            with (recipe_dir / "inputs.yaml").open("wt") as fd:
                yaml.dump(
                    {
                        "inputs": {
                            "t2m": [
                                {
                                    "model": "cosmo",
                                    "arkimet": "product:GRIB1,,2,11;level:GRIB1,105,2",
                                    "eccodes": 'shortName is "2t" and indicatorOfTypeOfLevel == 105'
                                    " and timeRangeIndicator == 0 and level == 2",
                                }
                            ],
                            **inputs,
                        },
                    },
                    fd,
                )

            # Write recipes definitions
            for name, steps in recipes.items():
                if "/" in name:
                    (recipe_dir / os.path.dirname(name)).mkdir(parents=True, exist_ok=True)
                with (recipe_dir / f"{name}.yaml").open("wt") as fd:
                    yaml.dump({"recipe": steps}, fd)

            definitions = Definitions(config=Config())
            definitions.load([recipe_dir])

            with ArkimetKitchen(definitions=definitions) as kitchen:
                kitchen.pantry.fill(path=Path("testdata/t2m/cosmo_t2m_2021_1_10_0_0_0+12.arkimet"))
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
            "map_grid": False,
            "map_coastline_sea_shade": False,
            "map_label": False,
            "map_coastline_colour": "#000000",
            "map_coastline_resolution": "medium",
        }
        with self.kitchen(
            flavours=[flavour("test", {"add_coastlines_fg": {"params": test_params}})],
            recipes={
                "test": [
                    {"step": "add_coastlines_fg"},
                    {"step": "add_grib", "grib": "t2m"},
                ]
            },
        ) as kitchen:
            order = self.make_order(kitchen, "test", "test")
            add_coastlines_fg = self.get_step(order, "add_coastlines_fg")
            self.assertEqual(add_coastlines_fg.spec.params.dict(exclude_unset=True), test_params)

    def test_default_shape(self):
        with self.kitchen(
            flavours=[
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
            },
        ) as kitchen:
            order = self.make_order(kitchen, "test", "t2m")
            add_user_boundaries = self.get_step(order, "add_user_boundaries")
            self.assertEqual(add_user_boundaries.spec.shape, "test")

    def test_step_filter(self):
        with self.kitchen(
            flavours=[
                flavour("default"),
                flavour("test", steps={"add_contour": {"skip": True}}),
            ],
            recipes={
                "t2m": [{"step": "add_grib", "grib": "t2m"}, {"step": "add_contour"}],
            },
        ) as kitchen:
            order = self.make_order(kitchen, "default", "t2m")
            self.assertEqual([x.name for x in order.order_steps], ["add_grib", "add_contour"])

            order = self.make_order(kitchen, "test", "t2m")
            self.assertEqual([x.name for x in order.order_steps], ["add_grib"])

    def test_recipe_filter(self):
        with self.kitchen(
            flavours=[
                flavour("default"),
                flavour("test", recipes_filter=["t2m"]),
            ],
            recipes={
                "t2m": [{"step": "add_grib", "grib": "t2m"}],
                "tcc": [{"step": "add_grib", "grib": "t2m"}],
            },
        ) as kitchen:
            orders = kitchen.make_orders(flavour=kitchen.defs.flavours["default"])
            self.assertCountEqual([(o.recipe.name, o.instant.step) for o in orders], [("t2m", 12), ("tcc", 12)])

            orders = kitchen.make_orders(flavour=kitchen.defs.flavours["test"])
            self.assertCountEqual([(o.recipe.name, o.instant.step) for o in orders], [("t2m", 12)])

    def test_recipe_filter_subdir(self):
        with self.kitchen(
            flavours=[
                flavour("default"),
                flavour("test", recipes_filter=["test/t2m"]),
            ],
            recipes={
                "test/t2m": [{"step": "add_grib", "grib": "t2m"}],
                "tcc": [{"step": "add_grib", "grib": "t2m"}],
            },
        ) as kitchen:
            orders = kitchen.make_orders(flavour=kitchen.defs.flavours["default"])
            self.assertCountEqual([(o.recipe.name, o.instant.step) for o in orders], [("test/t2m", 12), ("tcc", 12)])

            orders = kitchen.make_orders(flavour=kitchen.defs.flavours["test"])
            self.assertCountEqual([(o.recipe.name, o.instant.step) for o in orders], [("test/t2m", 12)])

    def assertTileSize(self, params: AddBasemapParamsSpec, size_x: int, size_y):
        self.assertAlmostEqual(params.page_x_length, 6.4 * size_x)
        self.assertAlmostEqual(params.page_y_length, 6.4 * size_y)
        self.assertAlmostEqual(params.subpage_x_length, 6.4 * size_x)
        self.assertAlmostEqual(params.subpage_y_length, 6.4 * size_y)
        self.assertAlmostEqual(params.super_page_x_length, 6.4 * size_x)
        self.assertAlmostEqual(params.super_page_y_length, 6.4 * size_y)
        self.assertEqual(params.subpage_x_position, 0)
        self.assertEqual(params.subpage_y_position, 0)
        self.assertEqual(params.output_width, 256 * size_x)

    def test_tiled(self):
        with self.kitchen(
            flavours=[flavour("test", tile={"lat_min": 30.0, "lat_max": 50.0, "lon_min": 0.0, "lon_max": 20.0})],
            recipes={
                "test": [
                    {"step": "add_basemap", "params": {"layout": "test"}},
                    {"step": "add_grib", "grib": "t2m"},
                ]
            },
        ) as kitchen:
            self.assertIsInstance(kitchen.defs.flavours["test"], flavours.Tiled)
            orders = kitchen.make_orders("test", recipe="test")
            self.assertEqual(len(orders), 3)

            basemap = self.get_step(orders[0], "add_basemap")
            params = basemap.spec.params
            self.assertEqual(str(orders[0]), "test+012/3/4/2+w1h2")
            self.assertAlmostEqual(params.subpage_lower_left_latitude, 0)
            self.assertAlmostEqual(params.subpage_lower_left_longitude, 0)
            self.assertAlmostEqual(params.subpage_upper_right_latitude, 66.5132604)
            self.assertAlmostEqual(params.subpage_upper_right_longitude, 45)
            self.assertEqual(params.layout, "test")
            self.assertTileSize(params, 1, 2)
            parts = scan_python_order(orders[0])
            mmap = [p for p in parts if p["__name__"] == "mmap"][0]
            self.assertEqual(mmap["layout"], "test")
            self.assertEqual(mmap["subpage_upper_right_longitude"], 45)

            basemap = self.get_step(orders[1], "add_basemap")
            params = basemap.spec.params
            self.assertEqual(str(orders[1]), "test+012/4/8/5+w1h2")
            self.assertAlmostEqual(params.subpage_lower_left_latitude, 21.9430455)
            self.assertAlmostEqual(params.subpage_lower_left_longitude, 0)
            self.assertAlmostEqual(params.subpage_upper_right_latitude, 55.7765730)
            self.assertAlmostEqual(params.subpage_upper_right_longitude, 22.5)
            self.assertEqual(params.layout, "test")
            self.assertTileSize(params, 1, 2)
            parts = scan_python_order(orders[0])
            mmap = [p for p in parts if p["__name__"] == "mmap"][0]
            self.assertEqual(mmap["layout"], "test")
            self.assertEqual(mmap["subpage_upper_right_longitude"], 45)

            basemap = self.get_step(orders[2], "add_basemap")
            params = basemap.spec.params
            self.assertEqual(str(orders[2]), "test+012/5/16/10+w2h4")
            self.assertAlmostEqual(params.subpage_lower_left_latitude, 21.9430455)
            self.assertAlmostEqual(params.subpage_lower_left_longitude, 0)
            self.assertAlmostEqual(params.subpage_upper_right_latitude, 55.7765730)
            self.assertAlmostEqual(params.subpage_upper_right_longitude, 22.5)
            self.assertEqual(params.layout, "test")
            self.assertTileSize(params, 2, 4)

    def test_tiled1(self):
        with self.kitchen(
            flavours=[
                flavour(
                    "test",
                    tile={
                        "zoom_min": 3,
                        "zoom_max": 5,
                        "lat_min": 43.4,
                        "lat_max": 45.2,
                        "lon_min": 9.0,
                        "lon_max": 13.2,
                    },
                )
            ],
            recipes={
                "test": [
                    {"step": "add_basemap"},
                    {"step": "add_contour", "params": {"legend": True}},
                    {"step": "add_grib", "grib": "t2m"},
                ]
            },
        ) as kitchen:
            self.assertIsInstance(kitchen.defs.flavours["test"], flavours.Tiled)
            orders = kitchen.make_orders("test", recipe="test")
            self.assertEqual(len(orders), 4)

            basemap = self.get_step(orders[0], "add_basemap")
            params = basemap.spec.params
            self.assertAlmostEqual(params.subpage_lower_left_latitude, 40.9798981)
            self.assertAlmostEqual(params.subpage_lower_left_longitude, 0)
            self.assertAlmostEqual(params.subpage_upper_right_latitude, 66.5132604)
            self.assertAlmostEqual(params.subpage_upper_right_longitude, 45)
            self.assertTileSize(params, 1, 1)
            parts = scan_python_order(orders[0])
            mmap = [p for p in parts if p["__name__"] == "mmap"][0]
            self.assertEqual(mmap["subpage_upper_right_longitude"], 45)
            mcont = [p for p in parts if p["__name__"] == "mcont"][0]
            self.assertFalse(mcont["legend"])

            basemap = self.get_step(orders[1], "add_basemap")
            params = basemap.spec.params
            self.assertAlmostEqual(params.subpage_lower_left_latitude, 40.9798981)
            self.assertAlmostEqual(params.subpage_lower_left_longitude, 0)
            self.assertAlmostEqual(params.subpage_upper_right_latitude, 55.7765730)
            self.assertAlmostEqual(params.subpage_upper_right_longitude, 22.5)
            self.assertTileSize(params, 1, 1)

            basemap = self.get_step(orders[2], "add_basemap")
            params = basemap.spec.params
            self.assertAlmostEqual(params.subpage_lower_left_latitude, 40.9798981)
            self.assertAlmostEqual(params.subpage_lower_left_longitude, 0)
            self.assertAlmostEqual(params.subpage_upper_right_latitude, 48.9224993)
            self.assertAlmostEqual(params.subpage_upper_right_longitude, 22.5)
            self.assertTileSize(params, 2, 1)

            contour = self.get_step(orders[2], "add_contour")
            params = contour.spec.params
            self.assertNotIn("contour_legend_only", params.dict(exclude_unset=True))

            # Legend for tiles

            contour = self.get_step(orders[3], "add_legend_basemap")
            params = contour.spec.params
            self.assertEqual(params.subpage_frame, False)
            self.assertEqual(params.page_frame, False)
            self.assertEqual(params.page_id_line, False)

            contour = self.get_step(orders[3], "add_contour")
            params = contour.spec.params
            self.assertTrue(params.legend_only)
            # self.assertTrue(params["test"], 256)
            # self.assertAlmostEqual(params["subpage_lower_left_latitude"], 21.9430455)
            # self.assertAlmostEqual(params["subpage_lower_left_longitude"], 11.25)
            # self.assertAlmostEqual(params["subpage_upper_right_latitude"], 31.9521622)
            # self.assertAlmostEqual(params["subpage_upper_right_longitude"], 22.5)
            # self.assertAlmostEqual(params["page_x_length"], 6.4)
            # self.assertAlmostEqual(params["page_y_length"], 6.4)
            # self.assertAlmostEqual(params["subpage_x_length"], 6.4)
            # self.assertAlmostEqual(params["subpage_y_length"], 6.4)
            # self.assertAlmostEqual(params["super_page_x_length"], 6.4)
            # self.assertAlmostEqual(params["super_page_y_length"], 6.4)
            # self.assertEqual(params["subpage_x_position"], 0)
            # self.assertEqual(params["subpage_y_position"], 0)
            # self.assertEqual(params["output_width"], 256)
