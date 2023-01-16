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
        self.fill_pantry()
        orders = []
        for o in self.make_orders():
            if isinstance(o, LegendOrder):
                orders.append(o)
            elif o.z == 6:
                orders.append(o)

        self.assertEqual(len(orders), 17)

        renderer = Renderer(self.kitchen.workdir)
        with tempfile.NamedTemporaryFile() as tf:
            with tarfile.open(mode="w|", fileobj=tf) as tarout:
                rendered = renderer.render(orders, tarout)

        self.assertCountEqual(orders, rendered)
