# from __future__ import annotations
from arkimapslib.unittest import add_recipe_test_cases


class WFLAGSMixin:
    def test_dispatch(self):
        self.fill_pantry()

        orders = self.make_orders()
        self.assertEqual(len(orders), 1)
        self.assertEqual(orders[0].basename, "wflags+012")

        self.assertRenders(orders[0])

        self.assertMgribArgsEqual(orders[0], cosmo={}, ifs={})


add_recipe_test_cases(__name__, "wflags")
