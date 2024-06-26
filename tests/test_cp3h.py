# from __future__ import annotations
from arkimapslib.unittest import recipe_tests


@recipe_tests("cp3h")
class CP3HMixin:
    def test_dispatch(self):
        pantry_reftime = "2021_1_10_0_0_0"
        self.fill_pantry(expected=[f"{self.model_name}_cp_{pantry_reftime}+{step}.grib" for step in range(3, 13, 3)])

        # Check that the right input was selected
        cpdec3h = self.kitchen.pantry.inputs.get("cpdec3h")
        for i in cpdec3h:
            self.assertEqual(i.__class__.__name__, "Decumulate")

        orders = self.make_orders()
        self.assertGreaterEqual(len(orders), 4)
        orders = [o for o in orders if o.recipe.name == "cp3h" and o.instant.step == "12h"]
        self.assertEqual(len(orders), 1)

        self.assertRenders(orders[0])

        self.assertMgribArgsEqual(orders[0], cosmo={}, ifs={})
