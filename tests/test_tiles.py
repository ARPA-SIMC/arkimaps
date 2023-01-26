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
        self.assertCountEqual(TileOrder.tessellate(0, 0, 0, 0, 1), [])

        self.assertCountEqual(TileOrder.tessellate(0, 1, 0, 1, 2), [
            (0, 0, 1, 1),
        ])

        self.assertCountEqual(TileOrder.tessellate(0, 2, 0, 2, 2), [
            (0, 0, 2, 2),
        ])

        self.assertCountEqual(TileOrder.tessellate(0, 3, 0, 3, 2), [
            (0, 0, 2, 2), (2, 0, 1, 2), (0, 2, 3, 1),
        ])

        self.assertCountEqual(TileOrder.tessellate(0, 10, 0, 10, 8), [
            (0, 0, 8, 8), (8, 0, 2, 8), (0, 8, 10, 2),
        ])

        self.assertCountEqual(TileOrder.tessellate(0, 4, 0, 5, 8), [
            (0, 0, 4, 5),
        ])

        self.assertCountEqual(TileOrder.tessellate(0, 10, 0, 10, 4), [
            (0, 0, 4, 4), (4, 0, 4, 4), (0, 4, 4, 4), (4, 4, 4, 4),
            (8, 0, 2, 8), (0, 8, 8, 2), (8, 8, 2, 2),
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
                output_names = tar.getnames()

        self.assertCountEqual(orders, rendered)

        magics_names = []
        for order in orders:
            for output in order.outputs:
                magics_names.append(output.relpath)

        self.assertCountEqual(magics_names, [
            '2021-01-10T00:00:00/t2m_ita_small_tiles+012/6/32-22-2-2.png',
            '2021-01-10T00:00:00/t2m_ita_small_tiles+012/6/32-24-2-2.png',
            '2021-01-10T00:00:00/t2m_ita_small_tiles+012/6/34-22-2-2.png',
            '2021-01-10T00:00:00/t2m_ita_small_tiles+012/6/34-24-2-2.png',
            '2021-01-10T00:00:00/t2m_ita_small_tiles+legend.png',
        ])

        self.assertCountEqual(output_names, [
            '2021-01-10T00:00:00/t2m_ita_small_tiles+012/6/32/22.png',
            '2021-01-10T00:00:00/t2m_ita_small_tiles+012/6/32/23.png',
            '2021-01-10T00:00:00/t2m_ita_small_tiles+012/6/33/22.png',
            '2021-01-10T00:00:00/t2m_ita_small_tiles+012/6/33/23.png',

            '2021-01-10T00:00:00/t2m_ita_small_tiles+012/6/32/24.png',
            '2021-01-10T00:00:00/t2m_ita_small_tiles+012/6/32/25.png',
            '2021-01-10T00:00:00/t2m_ita_small_tiles+012/6/33/24.png',
            '2021-01-10T00:00:00/t2m_ita_small_tiles+012/6/33/25.png',

            '2021-01-10T00:00:00/t2m_ita_small_tiles+012/6/34/22.png',
            '2021-01-10T00:00:00/t2m_ita_small_tiles+012/6/34/23.png',
            '2021-01-10T00:00:00/t2m_ita_small_tiles+012/6/35/22.png',
            '2021-01-10T00:00:00/t2m_ita_small_tiles+012/6/35/23.png',

            '2021-01-10T00:00:00/t2m_ita_small_tiles+012/6/34/24.png',
            '2021-01-10T00:00:00/t2m_ita_small_tiles+012/6/34/25.png',
            '2021-01-10T00:00:00/t2m_ita_small_tiles+012/6/35/24.png',
            '2021-01-10T00:00:00/t2m_ita_small_tiles+012/6/35/25.png',

            '2021-01-10T00:00:00/t2m_ita_small_tiles+legend.png'])

    def test_render_twice(self):
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
            with tarfile.open(mode="w|", fileobj=tf) as tarout:
                renderer.render(orders1, tarout)

            with tarfile.open(tf.name, mode="r") as tar:
                output_names1 = tar.getnames()

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
            with tarfile.open(mode="w|", fileobj=tf) as tarout:
                renderer.render(orders2, tarout)

            with tarfile.open(tf.name, mode="r") as tar:
                output_names2 = tar.getnames()

        # Test that they match

        self.assertCountEqual(output_names1, output_names2)

        for o1, o2 in zip(orders1, orders2):
            self.assertEqual(str(o1), str(o2))

            self.assertEqual(
                    [out.relpath for out in o1.outputs],
                    [out.relpath for out in o2.outputs])
