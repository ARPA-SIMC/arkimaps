# from __future__ import annotations
import datetime
import unittest
from typing import Any, Dict

from arkimapslib import flavours, inputs, orders
from arkimapslib.config import Config
from arkimapslib.inputs import Instant
from arkimapslib.recipes import Recipe


class TestTypes(unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.config = Config()
        self.flavour = flavours.SimpleFlavour(config=self.config, name="flavour", defined_in="flavour.yaml")
        self.instant = Instant(reftime=datetime.datetime(2023, 12, 15), step=12)

    def _compute_georef(self, params: Dict[str, Any]) -> Dict[str, Any]:
        recipe = Recipe(
            name="recipe",
            defined_in="recipe.yaml",
            recipe=[
                {"step": "add_basemap"},
                {
                    "step": "add_basemap",
                    "params": params,
                },
            ],
        )

        order = orders.MapOrder(
            flavour=self.flavour,
            instant=self.instant,
            recipe=recipe,
            input_files=[],
        )

        return order.georeference()

    def test_georef_map_epsg(self):
        georef = self._compute_georef(
            params={
                "subpage_map_projection": "EPSG:3857",
                "subpage_lower_left_longitude": 9.19,
                "subpage_lower_left_latitude": 43.71,
                "subpage_upper_right_longitude": 12.82,
                "subpage_upper_right_latitude": 45.14,
            }
        )

        self.assertEqual(
            georef,
            {
                "projection": "EPSG",
                "epsg": 3857,
                "bbox": [9.19, 43.71, 12.82, 45.14],
            },
        )

    def test_georef_map_cylindrical(self):
        georef = self._compute_georef(
            params={
                "subpage_map_projection": "cylindrical",
                "subpage_lower_left_longitude": 9.19,
                "subpage_lower_left_latitude": 43.71,
                "subpage_upper_right_longitude": 12.82,
                "subpage_upper_right_latitude": 45.14,
            }
        )

        self.assertEqual(
            georef,
            {
                "projection": "EPSG",
                "epsg": 4326,
                "bbox": [9.19, 43.71, 12.82, 45.14],
            },
        )
