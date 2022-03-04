# from __future__ import annotations
from arkimapslib.unittest import add_recipe_test_cases


class RH2MMixin:
    def test_dispatch(self):
        pantry_reftime = "2021_1_10_0_0_0"
        self.fill_pantry(expected=[
            f'{self.model_name}_2d_{pantry_reftime}+12.grib',
            f'{self.model_name}_t2m_{pantry_reftime}+12.grib'])

        # Check that the right input was selected
        cpdec3h = self.kitchen.pantry.inputs.get("rh2m")
        for i in cpdec3h:
            if i.model == "erg5":
                self.assertEqual(i.__class__.__name__, "Source")
            else:
                self.assertEqual(i.__class__.__name__, "VG6DTransform")

        orders = self.make_orders()
        self.assertEqual(len(orders), 1)

        self.assertRenders(orders[0])

        self.assertMgribArgsEqual(orders[0], cosmo={}, ifs={})


class RH2MERG5Mixin:
    def test_dispatch(self):
        pantry_reftime = "2021_1_10_0_0_0"
        self.fill_pantry(expected=[
            f'{self.model_name}_2d_{pantry_reftime}+12.grib',
            f'{self.model_name}_t2m_{pantry_reftime}+12.grib'])

        # Check that the right input was selected
        cpdec3h = self.kitchen.pantry.inputs.get("rh2m")
        for i in cpdec3h:
            if i.model == "erg5":
                self.assertEqual(i.__class__.__name__, "Source")
            else:
                self.assertEqual(i.__class__.__name__, "VG6DTransform")

        orders = self.make_orders()
        self.assertEqual(len(orders), 1)

        self.assertRenders(orders[0])

        self.assertMgribArgsEqual(orders[0], cosmo={}, ifs={})


add_recipe_test_cases(__name__, "rh2m", models=("IFS", "Cosmo", "ERG5"))
