import unittest
import sys
import os


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


def add_recipe_test_cases(module_name, recipe_name):
    module = sys.modules[module_name]
    for model in ("IFS", "Cosmo"):
        for dispatch in ("Arkimet", "Eccodes"):
            cls_name = f"Test{recipe_name}{dispatch}{model}"

            dispatch_mixin = globals()[f"{dispatch}Mixin"]
            model_mixin = globals()[f"{model}Mixin"]
            test_mixin = getattr(module, f"{recipe_name}Mixin")

            test_case = type(cls_name, (dispatch_mixin, model_mixin, test_mixin, unittest.TestCase), {})
            setattr(module, cls_name, test_case)
