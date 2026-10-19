# from __future__ import annotations
from arkimapslib.unittest import recipe_tests, RecipeTestCase


@recipe_tests("tiles/wflags10m")
class WFLAGS10MMixin(RecipeTestCase):
    def test_dispatch(self) -> None:
        self.fill_pantry()

        orders = self.make_orders()
        self.assertEqual(len(orders), 1)

        self.assertRenders(orders[0])

        self.assertMgribArgsEqual(orders[0], cosmo={}, ifs={})
