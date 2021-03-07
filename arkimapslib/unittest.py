# from __future__ import annotations
import unittest
import sys
import os
import pickle


class RecipeTestMixin:
    def make_orders(self, kitchen):
        """
        Create all satisfiable orders from the currently tested recipe
        """
        recipe = kitchen.recipes.get(self.recipe_name)
        orders = recipe.make_orders(kitchen.pantry)
        for o in orders:
            pickle.dumps(o)
        return orders

    def fill_pantry(self, kitchen, step=12, expected=None):
        kitchen.load_recipes("recipes")
        recipe = kitchen.recipes.get(self.recipe_name)
        input_names = recipe.list_inputs()

        if expected is None:
            expected = []
            for name in input_names:
                inputs = kitchen.pantry.inputs.get(name)
                if inputs is None:
                    self.fail(f"No input found for {name}")
                for inp in inputs:
                    if inp.NAME != "default":
                        continue
                    if inp.model is None:
                        expected.append(f"{inp.name}+{step}.grib")
                    else:
                        expected.append(f"{self.model_name}_{inp.name}+{step}.grib")

        sample_dir = os.path.join("testdata", self.recipe_name)
        for fn in os.listdir(sample_dir):
            if not fn.endswith(".arkimet"):
                continue
            if not fn.startswith(self.model_name):
                continue
            kitchen.pantry.fill(path=os.path.join(sample_dir, fn))
        for fn in expected:
            self.assertIn(fn, os.listdir(os.path.join(kitchen.pantry.data_root)))


class ArkimetMixin:
    from arkimapslib.kitchen import ArkimetKitchen
    kitchen_class = ArkimetKitchen


class EccodesMixin:
    from arkimapslib.kitchen import EccodesKitchen
    kitchen_class = EccodesKitchen


class CosmoMixin:
    model_name = "cosmo"

    def get_sample_path(self, input_name, step):
        return os.path.join("testdata", self.recipe_name, f"cosmo_{input_name}+{step}.arkimet")


class IFSMixin:
    model_name = "ifs"

    def get_sample_path(self, input_name, step):
        return os.path.join("testdata", self.recipe_name, f"ifs_{input_name}+{step}.arkimet")


def add_recipe_test_cases(module_name, recipe_name):
    module = sys.modules[module_name]
    for model in ("IFS", "Cosmo"):
        for dispatch in ("Arkimet", "Eccodes"):
            cls_name = f"Test{recipe_name.upper()}{dispatch}{model}"

            dispatch_mixin = globals()[f"{dispatch}Mixin"]
            model_mixin = globals()[f"{model}Mixin"]
            test_mixin = getattr(module, f"{recipe_name.upper()}Mixin")

            test_case = type(
                    cls_name,
                    (dispatch_mixin, model_mixin, RecipeTestMixin, test_mixin, unittest.TestCase),
                    {"recipe_name": recipe_name})
            test_case.__module__ = module_name
            setattr(module, cls_name, test_case)
