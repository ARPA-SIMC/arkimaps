# from __future__ import annotations
from typing import TYPE_CHECKING, Dict, List, Any, Optional, Type, Sequence, Tuple
import datetime
import os
import pickle
import sys
import unittest
import yaml
from .render import Renderer

if TYPE_CHECKING:
    from .orders import Order


class OrderResult:
    """
    Encapsulate the results of rendering an order, to be used for inspecting
    details of rendering
    """
    def __init__(self, renderer, order):
        self.renderer = renderer
        self.order = order
        self.magics = None
        self.python_code = None

    def get_step(self, step_name: str):
        """
        Return the arguments passed to Magics for the given step
        debug_trace log with the given name.
        """
        for name, macro_name, params in self.magics:
            if name == step_name:
                return macro_name, params
        raise KeyError(f"Step {step_name} not found in debug trace of order {self.order}")


class RecipeTestMixin:
    expected_basemap_args = {
        'page_id_line': False,
        'page_x_length': 38,
        'page_y_length': 31,
        'output_width': 1280,
        'subpage_map_projection': 'cylindrical',
        'subpage_lower_left_longitude': 2.5,
        'subpage_lower_left_latitude': 35.0,
        'subpage_upper_right_longitude': 20.0,
        'subpage_upper_right_latitude': 50.0,
        'subpage_x_length': 34,
        'subpage_x_position': 2,
        'subpage_y_length': 30,
        'subpage_y_position': 1,
        'super_page_x_length': 40,
        'super_page_y_length': 32,
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
                magics_crashes = yaml.load(fd, Loader=yaml.SafeLoader)
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

    def make_orders(self, flavour_name=None, recipe_name=None):
        """
        Create all satisfiable orders from the currently tested recipe
        """
        if flavour_name is None:
            flavour_name = self.flavour_name
        if recipe_name is None:
            recipe_name = self.recipe_name

        recipe = self.kitchen.recipes.get(recipe_name)
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

    def fill_pantry(
            self,
            reftime=datetime.datetime(2021, 1, 10),
            step=12,
            recipe_dirs=None,
            expected=None,
            recipe_name=None,
            flavour_name=None):
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
                    if inp.model is not None and inp.model != self.model_name:
                        continue
                    reftime_str = (f"{reftime.year}_{reftime.month}_{reftime.day}"
                                   f"_{reftime.hour}_{reftime.minute}_{reftime.second}")
                    if inp.model is None:
                        expected.append(f"{inp.name}_{reftime_str}+{step}.grib")
                    else:
                        expected.append(f"{self.model_name}_{inp.name}_{reftime_str}+{step}.grib")
        for fn in expected:
            self.assertIn(fn, os.listdir(os.path.join(self.kitchen.pantry.data_root)))

    def assertRenders(self, order, reftime=datetime.datetime(2021, 1, 10), step=12):
        """
        Render an order, collecting a debug_trace of all steps invoked
        """
        self.assertEqual(order.relpath, f"{reftime:%Y-%m-%dT%H:%M:%S}/{self.recipe_name}_{self.flavour_name}")
        self.assertEqual(order.basename, f"{self.recipe_name}+{step:03d}")
        renderer = Renderer(self.kitchen.workdir)

        # Stop testing at this point, if we know Magics would segfault or abort
        if self.id() in self.magics_crashes_skip_tests:
            raise unittest.SkipTest("disabled in .magics-crashes.yaml")

        res = OrderResult(renderer, order)

        # Generate magics parts for testing
        res.magics = []
        for step in order.order_steps:
            name, parms = step.as_magics_macro()
            res.magics.append((step.name, name, parms))

        add_basemap = self.get_step(order, "add_basemap")
        self.assertEqual(add_basemap.params.get("params", {}), self.expected_basemap_args)

        # Test rendering to Python
        res.python_code = renderer.render_one_to_python(order)

        # Test rendering with Magics
        rendered = renderer.render_one(order)
        self.assertIsNotNone(rendered)
        self.assertIsNotNone(rendered.output)
        self.assertEqual(os.path.basename(rendered.output), order.basename + ".png")

    def order_to_python(self, order) -> str:
        """
        Render an order to a Python trace file only.

        This is useful to reproduce a test case if Magics aborts on it.

        Returns the name of the file with the Python trace>
        """
        renderer = Renderer(self.kitchen.workdir)
        return renderer.render_one_to_python(order)

    def assertProcessLogEqual(self, log: List[str]):
        """
        Check that the process log matches the given log template.

        It calls assertEquals a list comparison after preprocessing the process
        log, generating a string for each entry.

        The string will have the name of the input, its class name, and the
        message after removing all occurrencies of the pantry basename, all
        concatenated with colons.
        """
        simplified_log = []
        for e in self.kitchen.pantry.process_log:
            simplified_log.append(
                    f"{e.input.name}:{e.input.__class__.__name__}:"
                    f"{e.message.replace(self.kitchen.pantry.data_root + '/', '')}")
        self.assertEqual(simplified_log, log)

    def assertMgribArgsEqual(self, order, cosmo=None, ifs=None, erg5=None):
        """
        Check that the mgrib arguments passed to add_grib match the given
        values. It has different expected values depending on the model used
        """
        step = self.get_step(order, "add_grib")
        expected_mgrib_args = {
            "cosmo": cosmo,
            "ifs": ifs,
            "erg5": erg5,
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


class ERG5Mixin:
    model_name = "erg5"

    def get_sample_path(self, input_name, step):
        return os.path.join("testdata", self.recipe_name, f"erg5_{input_name}+{step}.arkimet")


def add_recipe_test_cases(
        module_name, recipe_name,
        test_mixin: Optional[Type] = None,
        models: Sequence[str] = ("IFS", "Cosmo")):
    """
    Create test cases for the given recipe.

    Looks in the module ``module_name`` for a mixin class that it will

    It generates dispatch- and model-specific test classes, combining a
    dispatch specific-mixin, a model-specific mixin, and a test-specific mixin.

    The test-specific mixin is the class passed as ``test_mixin``.

    If ``test_mixin`` is not provided, it defaults to
    ``{recipe_name.upper()}{model}Mixin`` or ``{recipe_name.upper()}Mixin``
    looked up in module ``module_name``.
    """
    module = sys.modules[module_name]
    for dispatch in ("Arkimet", "Eccodes"):
        for model in models:
            # Find mixin with the test methods
            if test_mixin is None:
                _test_mixin = getattr(module, f"{recipe_name.upper()}{model}Mixin", None)
                if _test_mixin is None:
                    _test_mixin = getattr(module, f"{recipe_name.upper()}Mixin")
            else:
                _test_mixin = test_mixin

            if test_mixin is not None:
                test_name = _test_mixin.__name__
                if test_name.endswith("Mixin"):
                    test_name = test_name[:-5]
            else:
                test_name = recipe_name.upper()

            cls_name = f"Test{test_name}{dispatch}{model}"

            dispatch_mixin = globals()[f"{dispatch}Mixin"]
            model_mixin = globals()[f"{model}Mixin"]

            test_case = type(
                    cls_name,
                    (_test_mixin, dispatch_mixin, model_mixin, RecipeTestMixin, unittest.TestCase),
                    {"recipe_name": recipe_name})
            test_case.__module__ = module_name
            setattr(module, cls_name, test_case)


class MockMacro:
    def plot(self, *args):
        pass

    def __getattr__(self, key: str):
        def to_dict(**kw):
            res = {"__name__": key}
            res.update(**kw)
            return res
        return to_dict


mock_macro = MockMacro()


def scan_python_order(order: "Order") -> List[Dict[str, Any]]:
    renderer = Renderer("/")
    py_order = renderer.render_one_to_python(order, testing=True)
    py_order_globals = {}
    exec(py_order, py_order_globals)
    return py_order_globals["parts"]
