# from __future__ import annotations
import unittest
import sys
import os
import pickle
from .render import Renderer


class RecipeTestMixin:
    expected_basemap_args = {
        "subpage_map_projection": "cylindrical",
        "subpage_lower_left_longitude": -5.0,
        "subpage_lower_left_latitude": 30.0,
        "subpage_upper_right_longitude": 27.0,
        "subpage_upper_right_latitude": 55.0,
    }

    def make_orders(self, kitchen, flavour_names=None):
        """
        Create all satisfiable orders from the currently tested recipe
        """
        if flavour_names is None:
            flavour_names = "default"

        flavours = [kitchen.flavours.get(name) for name in flavour_names.split(",")]

        recipe = kitchen.recipes.get(self.recipe_name)
        orders = recipe.make_orders(kitchen.pantry, flavours=flavours)
        for o in orders:
            pickle.dumps(o)
        return orders

    def fill_pantry(self, kitchen, step=12, recipe_dirs=None, expected=None):
        if recipe_dirs is None:
            recipe_dirs = ["recipes"]
        kitchen.load_recipes(recipe_dirs)
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

    def assertRenders(self, kitchen, order):
        """
        Render an order, collecting a debug_trace of all steps invoked
        """
        renderer = Renderer(kitchen.workdir)
        order.debug_trace = []
        renderer.render_one(order)
        self.assertIsNotNone(order.output)
        self.assertEqual(os.path.basename(order.output), f"{self.recipe_name}+012.png")
        basemap_args = self.get_debug_trace(order, "add_basemap")
        self.assertEqual(basemap_args["params"], self.expected_basemap_args)

    def assertMgribArgsEqual(self, order, cosmo=None, ifs=None):
        """
        Check that the mgrib arguments passed to add_grib match the given
        values. It has different expected values depending on the model used
        """
        mgrib_args = self.get_debug_trace(order, "add_grib")
        expected_mgrib_args = {
            "cosmo": cosmo,
            "ifs": ifs,
        }
        self.assertEqual(mgrib_args["params"], expected_mgrib_args[self.model_name])

    def get_debug_trace(self, order, step_name: str):
        """
        Return the debug trace arguments of the first step in the order's
        debug_trace log with the given name.

        Fails the test if not found
        """
        for record in order.debug_trace:
            if record["name"] == step_name:
                return record
        self.fail(f"Step {step_name} not found in debug trace of order {order}")


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
                    (test_mixin, dispatch_mixin, model_mixin, RecipeTestMixin, unittest.TestCase),
                    {"recipe_name": recipe_name})
            test_case.__module__ = module_name
            setattr(module, cls_name, test_case)
