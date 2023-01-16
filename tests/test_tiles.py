# from __future__ import annotations
import tarfile
import tempfile
import unittest

from arkimapslib.kitchen import EccodesKitchen
from arkimapslib.orders import TileOrder, LegendOrder
from arkimapslib.render import Renderer
from arkimapslib.unittest import RecipeTestMixin


class TestTiles(RecipeTestMixin, unittest.TestCase):
    kitchen_class = EccodesKitchen
    flavour_name = "ita_small_tiles"
    recipe_name = "t2m"
    model_name = "ifs"

    def test_tessellate(self):
        self.assertCountEqual(TileOrder.tessellate(0, 0, 0, 0, 1, 1), [])

        self.assertCountEqual(TileOrder.tessellate(0, 1, 0, 1, 2, 2), [
            (0, 0, 1, 1),
        ])

        self.assertCountEqual(TileOrder.tessellate(0, 2, 0, 2, 2, 2), [
            (0, 0, 2, 2),
        ])

        self.assertCountEqual(TileOrder.tessellate(0, 3, 0, 3, 2, 2), [
            (0, 0, 2, 2), (2, 0, 1, 1),
            (0, 2, 1, 1), (2, 2, 1, 1),
        ])

    def test_render(self):
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

        self.assertCountEqual([(o.x, o.y, o.width) for o in orders if not isinstance(o, LegendOrder)], [
            (32, 22, 2), (32, 24, 2),
            (34, 22, 2), (34, 24, 2),
        ])

        renderer = Renderer(self.kitchen.config, self.kitchen.workdir)
        with tempfile.NamedTemporaryFile() as tf:
            with tarfile.open(mode="w|", fileobj=tf) as tarout:
                rendered = renderer.render(orders, tarout)

            with tarfile.open(tf.name, mode="r") as tar:
                output_names = set(tar.getnames())

        self.assertCountEqual(orders, rendered)

        self.assertIn("2021-01-10T00:00:00/t2m_ita_small_tiles+legend.png", output_names)

        self.assertEqual(len(output_names), 17)

        for order in orders:
            for output in order.outputs:
                self.assertIn(output.relpath, output_names)
