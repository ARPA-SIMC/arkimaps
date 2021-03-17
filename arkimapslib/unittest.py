# from __future__ import annotations
from typing import Dict, List, Any, Optional, Type
import unittest
import sys
import os
import pickle
import yaml
from .render import Renderer


class RecipeTestMixin:
    expected_basemap_args = {
        'page_id_line': False,
        'output_width': 1280,
        'subpage_map_projection': 'cylindrical',
        'subpage_lower_left_longitude': 2.5,
        'subpage_lower_left_latitude': 35.0,
        'subpage_upper_right_longitude': 20.0,
        'subpage_upper_right_latitude': 50.0,
        'map_grid': True,
        'map_grid_latitude_reference': 45.0,
        'map_grid_longitude_reference': 0.0,
        'map_grid_longitude_increment': 2.5,
        'map_grid_latitude_increment': 2.5,
        'map_grid_colour': 'grey',
        'map_grid_line_style': 'dash',
        'map_label_colour': 'black',
        'map_label_height': 0.4,
        'map_label_latitude_frequency': 1,
    }

    flavour_name = "default"

    @classmethod
    def setUpClass(cls):
        # There are cases in which Magics crashes, and they are outside our
        # control (see debian bugs #985137 and #985364, and arkimaps issues #69
        # and #71)
        #
        # If a .magics-crashes.yaml file is found, it is parsed and expect to
        # be a dict. The keys are test IDs, the values are records defining
        # when to skip a test.
        #
        # The values supported in the record are:
        #
        #  * hostname: skip the test when socket.gethostname() matches this
        #    value
        #
        import socket
        super().setUpClass()
        magic_crashes: List[Dict[str, Any]]
        try:
            with open(".magics-crashes.yaml", "rt") as fd:
                magics_crashes = yaml.load(fd)
        except FileNotFoundError:
            magics_crashes = {}

        cls.magics_crashes_skip_tests = set()
        for name, match in magics_crashes.items():
            hostname = match.get("hostname")
            if hostname is not None:
                if hostname == socket.gethostname():
                    cls.magics_crashes_skip_tests.add(name)

    def setUp(self):
        self.kitchen = self.kitchen_class()
        self.kitchen.__enter__()
        self.kitchen_recipes_loaded = False

    def tearDown(self):
        self.kitchen.__exit__(None, None, None)
        self.kitchen = None

    def make_orders(self, flavour_name=None):
        """
        Create all satisfiable orders from the currently tested recipe
        """
        if flavour_name is None:
            flavour_name = self.flavour_name

        recipe = self.kitchen.recipes.get(self.recipe_name)
        flavour = self.kitchen.flavours.get(flavour_name)
        orders = flavour.make_orders(recipe, self.kitchen.pantry)
        for o in orders:
            pickle.dumps(o)
        return orders

    def load_recipes(self, recipe_dirs=None):
        """
        Load recipes in the kitchen.

        It can be called multiple times in a test case, and only the first time
        will have any effect
        """
        if self.kitchen_recipes_loaded:
            return
        if recipe_dirs is None:
            recipe_dirs = ["recipes"]
        self.kitchen.load_recipes(recipe_dirs)
        self.kitchen_recipes_loaded = True

    def fill_pantry(self, step=12, recipe_dirs=None, expected=None, recipe_name=None, flavour_name=None):
        """
        Load recipes if needed, then fill the pantry with the inputs they require
        """
        if recipe_name is None:
            recipe_name = self.recipe_name
        if flavour_name is None:
            flavour_name = self.flavour_name
        self.load_recipes(recipe_dirs)
        flavour = self.kitchen.flavours.get(flavour_name)
        recipe = self.kitchen.recipes.get(recipe_name)

        # Import all test files available for the given recipe
        sample_dir = os.path.join("testdata", recipe_name)
        for fn in os.listdir(sample_dir):
            if not fn.endswith(".arkimet"):
                continue
            if not fn.startswith(self.model_name):
                continue
            self.kitchen.pantry.fill(path=os.path.join(sample_dir, fn))

        # Check that we imported the right files with the right names
        input_names = flavour.list_inputs(recipe)
        if expected is None:
            expected = []
            for name in input_names:
                inputs = self.kitchen.pantry.inputs.get(name)
                if inputs is None:
                    self.fail(f"No input found for {name}")
                for inp in inputs:
                    if inp.NAME != "default":
                        continue
                    if inp.model is None:
                        expected.append(f"{inp.name}+{step}.grib")
                    else:
                        expected.append(f"{self.model_name}_{inp.name}+{step}.grib")
        for fn in expected:
            self.assertIn(fn, os.listdir(os.path.join(self.kitchen.pantry.data_root)))

    def assertRenders(self, order, output_name=None):
        """
        Render an order, collecting a debug_trace of all steps invoked
        """
        if output_name is None:
            output_name = f"{self.recipe_name}+012.png"
        renderer = Renderer(self.kitchen.workdir)
        order.debug_trace = []

        # Stop testing at this point, if we know Magics would segfault or abort
        if self.id() in self.magics_crashes_skip_tests:
            raise unittest.SkipTest("disabled in .magics-crashes.yaml")

        renderer.render_one(order)
        self.assertIsNotNone(order.output)
        self.assertEqual(os.path.basename(order.output), output_name)
        add_basemap = self.get_step(order, "add_basemap")
        self.assertEqual(add_basemap.params.get("params", {}), self.expected_basemap_args)

    def assertMgribArgsEqual(self, order, cosmo=None, ifs=None):
        """
        Check that the mgrib arguments passed to add_grib match the given
        values. It has different expected values depending on the model used
        """
        step = self.get_step(order, "add_grib")
        expected_mgrib_args = {
            "cosmo": cosmo,
            "ifs": ifs,
        }
        self.assertEqual(step.params.get("params", {}), expected_mgrib_args[self.model_name])

    def get_step(self, order, step_name: str):
        """
        Return the debug trace arguments of the first step in the order's
        debug_trace log with the given name.

        Fails the test if not found
        """
        for step in order.order_steps:
            if step.name == step_name:
                return step
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


def add_recipe_test_cases(module_name, recipe_name, test_mixin: Optional[Type] = None):
    module = sys.modules[module_name]
    if test_mixin is None:
        test_name = recipe_name.upper()
        test_mixin = getattr(module, f"{recipe_name.upper()}Mixin")
    else:
        test_name = test_mixin.__name__
        if test_name.endswith("Mixin"):
            test_name = test_name[:-5]

    for model in ("IFS", "Cosmo"):
        for dispatch in ("Arkimet", "Eccodes"):
            cls_name = f"Test{test_name}{dispatch}{model}"

            dispatch_mixin = globals()[f"{dispatch}Mixin"]
            model_mixin = globals()[f"{model}Mixin"]

            test_case = type(
                    cls_name,
                    (test_mixin, dispatch_mixin, model_mixin, RecipeTestMixin, unittest.TestCase),
                    {"recipe_name": recipe_name})
            test_case.__module__ = module_name
            setattr(module, cls_name, test_case)
