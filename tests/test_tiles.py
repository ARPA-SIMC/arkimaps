# from __future__ import annotations
import tarfile
import tempfile
import unittest

from arkimapslib.kitchen import EccodesKitchen
from arkimapslib.orders import LegendOrder
from arkimapslib.render import Renderer
from arkimapslib.unittest import RecipeTestMixin


class TestTiles(RecipeTestMixin, unittest.TestCase):
    kitchen_class = EccodesKitchen
    flavour_name = "ita_small_tiles"
    recipe_name = "t2m"
    model_name = "ifs"

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

        self.assertEqual(len(orders), 17)

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
