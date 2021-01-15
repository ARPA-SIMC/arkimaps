from arkimapslib.render import Renderer
import unittest
import os


class HCCMixin:
    kitchen_class = None

    def test_dispatch(self):
        with self.kitchen_class() as kitchen:
            kitchen.load_recipes("recipes")
            kitchen.pantry.fill(kitchen.recipes, path=self.get_sample_path("hcc", 12))

            orders = list(kitchen.pantry.orders(kitchen.recipes))
            self.assertEqual(len(orders), 1)

            renderer = Renderer()
            with self.assertLogs() as log:
                renderer.render_one(orders[0])

            mgrib_args_prefix = "INFO:arkimaps.order.hcc+012:add_grib mgrib "
            mgrib_args = None
            for l in log.output:
                if l.startswith(mgrib_args_prefix):
                    mgrib_args = l[len(mgrib_args_prefix):]

            self.assertIsNotNone(orders[0].output)
            self.assertEqual(os.path.basename(orders[0].output), "hcc+012.png")

            expected_mgrib_args = {
                "cosmo": "{'grib_automatic_scaling': False, 'grib_scaling_factor': 0.08}",
                "ifs": "{'grib_automatic_scaling': False, 'grib_scaling_factor': 8}",
            }

            self.assertIsNotNone(mgrib_args)
            self.assertEqual(mgrib_args, expected_mgrib_args[self.model_name])


class ArkimetMixin:
    from arkimapslib.kitchen import ArkimetKitchen
    kitchen_class = ArkimetKitchen


class EccodesMixin:
    from arkimapslib.kitchen import EccodesKitchen
    kitchen_class = EccodesKitchen


class CosmoMixin:
    model_name = "cosmo"

    def get_sample_path(self, recipe, step):
        return os.path.join("testdata", recipe, f"cosmo+{step}.arkimet")


class IFSMixin:
    model_name = "ifs"

    def get_sample_path(self, recipe, step):
        return os.path.join("testdata", recipe, f"ifs+{step}.arkimet")


class TestHCCArkimetCosmo(ArkimetMixin, CosmoMixin, HCCMixin, unittest.TestCase):
    pass


class TestHCCArkimetIFS(ArkimetMixin, IFSMixin, HCCMixin, unittest.TestCase):
    pass


class TestHCCECcodesCosmo(EccodesMixin, CosmoMixin, HCCMixin, unittest.TestCase):
    pass


class TestHCCECcodesIFS(EccodesMixin, IFSMixin, HCCMixin, unittest.TestCase):
    pass
