# from __future__ import annotations
import tempfile
import unittest
from collections import defaultdict
from typing import Dict, Optional

from arkimapslib import outputbundle
from arkimapslib.kitchen import EccodesKitchen
from arkimapslib.orders import LegendOrder, Order, TileOrder, deg2num, num2deg
from arkimapslib.render import Renderer
from arkimapslib.unittest import RecipeTestMixin


class TestTiles(RecipeTestMixin, unittest.TestCase):
    kitchen_class = EccodesKitchen
    flavour_name = "ita_small_tiles"
    recipe_name = "t2m"
    model_name = "ifs"

    def test_tessellate(self) -> None:
        self.assertCountEqual(TileOrder.tessellate(0, 0, 0, 0, 1), [])

        self.assertCountEqual(
            TileOrder.tessellate(0, 1, 0, 1, 2),
            [
                (0, 0, 1, 1),
            ],
        )

        self.assertCountEqual(
            TileOrder.tessellate(0, 2, 0, 2, 2),
            [
                (0, 0, 2, 2),
            ],
        )

        self.assertCountEqual(
            TileOrder.tessellate(0, 3, 0, 3, 2),
            [
                (0, 0, 2, 2),
                (2, 0, 1, 2),
                (0, 2, 3, 1),
            ],
        )

        self.assertCountEqual(
            TileOrder.tessellate(0, 10, 0, 10, 8),
            [
                (0, 0, 8, 8),
                (8, 0, 2, 8),
                (0, 8, 10, 2),
            ],
        )

        self.assertCountEqual(
            TileOrder.tessellate(0, 4, 0, 5, 8),
            [
                (0, 0, 4, 5),
            ],
        )

        self.assertCountEqual(
            TileOrder.tessellate(0, 10, 0, 10, 4),
            [
                (0, 0, 4, 4),
                (4, 0, 4, 4),
                (0, 4, 4, 4),
                (4, 4, 4, 4),
                (8, 0, 2, 4),
                (8, 4, 2, 4),
                (0, 8, 8, 2),
                (8, 8, 2, 2),
            ],
        )

    def test_render(self) -> None:
        self.kitchen.config.tile_group_width = 2
        self.kitchen.config.tile_group_height = 2

        self.fill_pantry()
        orders = []
        for order in self.make_orders():
            if isinstance(order, LegendOrder):
                orders.append(order)
            elif order.z == 6:
                orders.append(order)

        # self.assertEqual(len(orders), 17)
        self.assertEqual(len(orders), 5)

        self.assertCountEqual(
            [(o.x, o.y, o.width) for o in orders if not isinstance(o, LegendOrder)],
            [
                (32, 22, 2),
                (32, 24, 2),
                (34, 22, 2),
                (34, 24, 2),
            ],
        )

        renderer = Renderer(self.kitchen.config, self.kitchen.workdir)
        with tempfile.NamedTemporaryFile() as tf:
            with outputbundle.ZipWriter(out=tf) as bundle:
                rendered = renderer.render(orders, bundle)

            with outputbundle.ZipReader(tf.name) as bundle:
                output_names = bundle.find()

        self.assertCountEqual(orders, rendered)

        magics_names = []
        for order in orders:
            magics_names.append(order.output.relpath)

        self.assertCountEqual(
            magics_names,
            [
                "2021-01-10T00:00:00/t2m_ita_small_tiles+012/6/32-22-2-2.png",
                "2021-01-10T00:00:00/t2m_ita_small_tiles+012/6/32-24-2-2.png",
                "2021-01-10T00:00:00/t2m_ita_small_tiles+012/6/34-22-2-2.png",
                "2021-01-10T00:00:00/t2m_ita_small_tiles+012/6/34-24-2-2.png",
                "2021-01-10T00:00:00/t2m_ita_small_tiles+legend.png",
            ],
        )

        self.assertCountEqual(
            output_names,
            [
                "version.txt",
                "2021-01-10T00:00:00/t2m_ita_small_tiles+012/6/32/22.png",
                "2021-01-10T00:00:00/t2m_ita_small_tiles+012/6/32/23.png",
                "2021-01-10T00:00:00/t2m_ita_small_tiles+012/6/33/22.png",
                "2021-01-10T00:00:00/t2m_ita_small_tiles+012/6/33/23.png",
                "2021-01-10T00:00:00/t2m_ita_small_tiles+012/6/32/24.png",
                "2021-01-10T00:00:00/t2m_ita_small_tiles+012/6/32/25.png",
                "2021-01-10T00:00:00/t2m_ita_small_tiles+012/6/33/24.png",
                "2021-01-10T00:00:00/t2m_ita_small_tiles+012/6/33/25.png",
                "2021-01-10T00:00:00/t2m_ita_small_tiles+012/6/34/22.png",
                "2021-01-10T00:00:00/t2m_ita_small_tiles+012/6/34/23.png",
                "2021-01-10T00:00:00/t2m_ita_small_tiles+012/6/35/22.png",
                "2021-01-10T00:00:00/t2m_ita_small_tiles+012/6/35/23.png",
                "2021-01-10T00:00:00/t2m_ita_small_tiles+012/6/34/24.png",
                "2021-01-10T00:00:00/t2m_ita_small_tiles+012/6/34/25.png",
                "2021-01-10T00:00:00/t2m_ita_small_tiles+012/6/35/24.png",
                "2021-01-10T00:00:00/t2m_ita_small_tiles+012/6/35/25.png",
                "2021-01-10T00:00:00/t2m_ita_small_tiles+legend.png",
            ],
        )

        # Test summary
        products_info = outputbundle.Products()
        for order in orders:
            products_info.add_order(order)

        product_info = products_info.by_path["2021-01-10T00:00:00/t2m_ita_small_tiles+012/6/34/24.png"]
        self.assertIn("projection", product_info.georef)

    def test_render_twice(self) -> None:
        self.kitchen.config.tile_group_width = 2
        self.kitchen.config.tile_group_height = 2
        self.fill_pantry()

        # First round

        orders1 = []
        for order in self.make_orders():
            if isinstance(order, LegendOrder):
                orders1.append(order)
            elif order.z == 6:
                orders1.append(order)

        self.assertEqual(len(orders1), 5)

        renderer = Renderer(self.kitchen.config, self.kitchen.workdir)
        with tempfile.NamedTemporaryFile() as tf:
            with outputbundle.ZipWriter(out=tf) as bundle:
                renderer.render(orders1, bundle)

            with outputbundle.ZipReader(tf.name) as bundle:
                output_names1 = bundle.find()

        # Second round

        orders2 = []
        for order in self.make_orders():
            if isinstance(order, LegendOrder):
                orders2.append(order)
            elif order.z == 6:
                orders2.append(order)

        self.assertEqual(len(orders2), 5)

        renderer = Renderer(self.kitchen.config, self.kitchen.workdir)
        with tempfile.NamedTemporaryFile() as tf:
            with outputbundle.ZipWriter(out=tf) as bundle:
                renderer.render(orders2, bundle)

            with outputbundle.ZipReader(tf.name) as bundle:
                output_names2 = bundle.find()

        # Test that they match

        self.assertCountEqual(output_names1, output_names2)

        for o1, o2 in zip(orders1, orders2):
            self.assertEqual(str(o1), str(o2))

            self.assertEqual(o1.output.relpath, o2.output.relpath)

    def test_tile_coords(self) -> None:
        self.assertEqual(deg2num(11.25, 41.0, 6), (34, 23))
        self.assertEqual(deg2num(-11.25, 41.0, 6), (30, 23))

        lon, lat = num2deg(34, 23, 6)
        self.assertAlmostEqual(lat, 45.089034, 4)
        self.assertAlmostEqual(lon, 11.25, 2)

        lon, lat = num2deg(35, 24, 6)
        self.assertAlmostEqual(lat, 40.979897, 4)
        self.assertAlmostEqual(lon, 16.874996, 2)

        lon, lat = num2deg(30, 23, 6)
        self.assertAlmostEqual(lat, 45.089034, 4)
        self.assertAlmostEqual(lon, -11.25, 2)

    def test_bounding_box(self) -> None:
        # see issue #139

        # ita_small_tiles defines a domain of (35, 5) - (40, 20)

        self.fill_pantry()
        flavour = self.kitchen.flavours["ita_small_tiles"]
        # print(flavour.summarize())

        # Make orders and compute the area bounding box for each zoom level
        class BBox:
            def __init__(self) -> None:
                self.lat_min: Optional[float] = None
                self.lat_max: Optional[float] = None
                self.lon_min: Optional[float] = None
                self.lon_max: Optional[float] = None

            def add(self, order: Order) -> None:
                lon_min, lat_max = num2deg(order.x, order.y, order.z)
                lon_max, lat_min = num2deg(order.x + order.width + 1, order.y + order.height + 1, order.z)
                if self.lat_min is None or self.lat_min > lat_min:
                    self.lat_min = lat_min
                if self.lat_max is None or self.lat_max < lat_max:
                    self.lat_max = lat_max
                if self.lon_min is None or self.lon_min > lon_min:
                    self.lon_min = lon_min
                if self.lon_max is None or self.lon_max < lon_max:
                    self.lon_max = lon_max

        # Compute tiles and check that the whole domain is contained in the
        # tiles
        by_zoom: Dict[int, BBox] = defaultdict(BBox)
        for order in self.make_orders():
            if isinstance(order, LegendOrder):
                continue
            by_zoom[order.z].add(order)

        self.assertCountEqual(by_zoom.keys(), (6, 7))

        for z in range(flavour.spec.tile.zoom_min, flavour.spec.tile.zoom_max + 1):
            bbox = by_zoom[z]
            self.assertLessEqual(bbox.lat_min, flavour.spec.tile.lat_min)
            self.assertLessEqual(bbox.lon_min, flavour.spec.tile.lon_min)
            self.assertGreaterEqual(bbox.lat_max, flavour.spec.tile.lat_max)
            self.assertGreaterEqual(bbox.lon_max, flavour.spec.tile.lon_max)
