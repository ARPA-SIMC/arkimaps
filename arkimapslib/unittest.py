# from __future__ import annotations
import contextlib
import datetime
import fnmatch
import os
import re
import sys
import tempfile
import unittest
from pathlib import Path
from typing import TYPE_CHECKING, Any, Callable, ClassVar, Dict, List, Optional, Sequence, Set, Type, Union

import yaml

from .config import Config
from .definitions import Definitions
from .kitchen import Kitchen, WorkingKitchen
from .render import Renderer

if TYPE_CHECKING:
    from .orders import Order


config = Config()
cached_system_definitions: Optional[Definitions] = None


def system_definitions() -> Definitions:
    """
    Return loaded system definitions
    """
    global config
    global cached_system_definitions
    if cached_system_definitions is None:
        cached_system_definitions = Definitions(config=config)
        cached_system_definitions.load([Path("recipes")])
    return cached_system_definitions


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


class RecipeTestMixin(unittest.TestCase):
    expected_basemap_args = {
        "page_id_line": False,
        "page_x_length": 38,
        "page_y_length": 31,
        "output_width": 1280,
        "subpage_map_projection": "cylindrical",
        "subpage_lower_left_longitude": 2.5,
        "subpage_lower_left_latitude": 35.0,
        "subpage_upper_right_longitude": 20.0,
        "subpage_upper_right_latitude": 50.0,
        "subpage_x_length": 34,
        "subpage_x_position": 2,
        "subpage_y_length": 30,
        "subpage_y_position": 1,
        "super_page_x_length": 40,
        "super_page_y_length": 32,
        "map_grid": True,
        "map_grid_latitude_reference": 45.0,
        "map_grid_longitude_reference": 0.0,
        "map_grid_longitude_increment": 2.5,
        "map_grid_latitude_increment": 2.5,
        "map_grid_colour": "grey",
        "map_grid_line_style": "dash",
        "map_label_colour": "black",
        "map_label_height": 0.4,
        "map_label_latitude_frequency": 1,
    }

    flavour_name = "default"
    magics_crashes_skip_tests: ClassVar[Set[str]]
    kitchen_class: Type[WorkingKitchen]
    recipe_name: ClassVar[str]
    model_name: ClassVar[str]

    @classmethod
    def setUpClass(cls) -> None:
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
            with open(".magics-crashes.yaml") as fd:
                magics_crashes = yaml.load(fd, Loader=yaml.SafeLoader)
        except FileNotFoundError:
            magics_crashes = {}

        cls.magics_crashes_skip_tests = set()
        for name, match in magics_crashes.items():
            hostname = match.get("hostname")
            if hostname is not None:
                if hostname == socket.gethostname():
                    cls.magics_crashes_skip_tests.add(name)

    def setUp(self) -> None:
        self.defs = system_definitions()
        self.kitchen = self.kitchen_class(definitions=self.defs)
        self.kitchen.__enter__()

    def tearDown(self) -> None:
        self.kitchen.__exit__(None, None, None)
        delattr(self, "kitchen")

    def fill_pantry(
        self,
        reftime=datetime.datetime(2021, 1, 10),
        step=12,
        expected=None,
        flavour_name: Optional[str] = None,
        exclude=None,
        extra_sample_dirs: Sequence[Union[str, Path]] = (),
    ) -> None:
        """
        Load recipes if needed, then fill the pantry with the inputs they require
        """
        recipe_name = self.recipe_name
        if flavour_name is None:
            flavour_name = self.flavour_name
        flavour = self.kitchen.defs.flavours[flavour_name]
        recipe = self.kitchen.defs.recipes.get(recipe_name)

        # Import all test files available for the given recipe
        sample_dirs: List[Path] = [Path(os.path.basename(recipe_name))]
        sample_dirs += [Path(p) for p in extra_sample_dirs]
        for dirname in sample_dirs:
            sample_dir = Path("testdata") / dirname
            for fn in sample_dir.iterdir():
                if not fn.name.endswith(".arkimet"):
                    continue
                if not fn.name.startswith(self.model_name):
                    continue
                if exclude is not None and fnmatch.fnmatch(fn.name, exclude):
                    continue

                self.kitchen.pantry.fill(path=sample_dir / fn.name)

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
                    if inp.spec.model is not None and inp.spec.model != self.model_name:
                        continue
                    reftime_str = (
                        f"{reftime.year}_{reftime.month}_{reftime.day}"
                        f"_{reftime.hour}_{reftime.minute}_{reftime.second}"
                    )
                    if inp.spec.model is None:
                        expected.append(f"{inp.name}_{reftime_str}+{step}.grib")
                    else:
                        expected.append(f"{self.model_name}_{inp.name}_{reftime_str}+{step}.grib")
        for fn in expected:
            self.assertIn(fn, os.listdir(self.kitchen.pantry.data_root))

    def make_orders(self, flavour_name=None, recipe_name=None) -> List["Order"]:
        """
        Create all satisfiable orders from the currently tested recipe
        """
        if flavour_name is None:
            flavour_name = self.flavour_name
        if recipe_name is None:
            recipe_name = self.recipe_name

        recipe = self.kitchen.defs.recipes.get(recipe_name)
        flavour = self.kitchen.defs.flavours[flavour_name]
        orders = flavour.make_orders(recipe, self.kitchen.pantry)
        return orders

    def assertRenders(self, order, reftime=datetime.datetime(2021, 1, 10), step=12) -> None:
        """
        Render an order, collecting a debug_trace of all steps invoked
        """
        renderer = Renderer(self.kitchen.config, self.kitchen.workdir)

        # Stop testing at this point, if we know Magics would segfault or abort
        if self.id() in self.magics_crashes_skip_tests:
            raise unittest.SkipTest("disabled in .magics-crashes.yaml")

        res = OrderResult(renderer, order)

        # Generate magics parts for testing
        res.magics = []
        for order_step in order.order_steps:
            name, parms = order_step.as_magics_macro()
            res.magics.append((order_step.name, name, parms))

        add_basemap = self.get_step(order, "add_basemap")
        self.assertEqual(add_basemap.spec.params.dict(exclude_unset=True), self.expected_basemap_args)

        # Test rendering to Python
        script_pathname = renderer.write_render_script([order])

        # Check that the generated script compiles
        with open(script_pathname) as fd:
            compile(fd.read(), script_pathname, "exec")

        # Do not try to run Magics, which is slow: just check that the steps
        # are what we expect
        # # Test rendering with Magics
        # rendered = renderer.render_one(order)
        # self.assertIsNotNone(rendered)
        # output = rendered.output
        # self.assertEqual(
        #     output.relpath,
        #     f"{reftime:%Y-%m-%dT%H:%M:%S}/{self.recipe_name}_{self.flavour_name}/"
        #     f"{os.path.basename(self.recipe_name)}+{step:03d}.png",
        # )

    def assertProcessLogEqual(self, log: List[str]):
        """
        Check that the process log matches the given log template.

        It calls assertCountEqual between after preprocessing the process log,
        generating a string for each entry. Order is intentionally ignored
        because the order of processing may change between runs.

        The string will have the name of the input, its class name, and the
        message after removing all occurrencies of the pantry basename, all
        concatenated with colons.
        """
        re_size = re.compile(r"\b\d+b\b")
        simplified_log = []
        for e in self.kitchen.pantry.process_log:
            message = e.message.replace(str(self.kitchen.pantry.data_root) + "/", "")
            message = re_size.sub("xxxb", message)
            simplified_log.append(f"{e.input.name}:{e.input.__class__.__name__}:" + message)
        self.assertCountEqual(simplified_log, log)

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
        self.assertEqual(step.spec.params.dict(exclude_unset=True), expected_mgrib_args[self.model_name])

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


def recipe_tests(recipe_name, models: Sequence[str] = ("IFS", "Cosmo")) -> Callable[[Type], Type]:
    """
    Create test cases for the given recipe.

    Uses the provided class as a mixing to instantiate tests for each models.

    It generates dispatch- and model-specific test classes, combining a
    dispatch specific-mixin, a model-specific mixin, and a test-specific mixin.
    """

    def wrap(test_class: Type) -> Type:
        module = sys.modules[test_class.__module__]
        for dispatch in ("Arkimet", "Eccodes"):
            for model in models:
                test_name = test_class.__name__
                if test_name.endswith("Mixin"):
                    test_name = test_name[:-5]

                cls_name = f"Test{test_name}{dispatch}{model}"

                dispatch_mixin = globals()[f"{dispatch}Mixin"]
                model_mixin = globals()[f"{model}Mixin"]

                test_case = type(
                    cls_name,
                    (test_class, dispatch_mixin, model_mixin, RecipeTestMixin, unittest.TestCase),
                    {"recipe_name": recipe_name},
                )
                test_case.__module__ = test_class.__module__
                setattr(module, cls_name, test_case)
        return test_class

    return wrap


def scan_python_order(order: "Order") -> List[Dict[str, Any]]:
    parts = []
    for step in order.order_steps:
        name, parms = step.as_magics_macro()
        macro = {"__name__": name}
        for k, v in parms.items():
            macro[k] = v
        parts.append(macro)
    return parts


class Workdir(contextlib.ExitStack):
    def __init__(self, test_case: Optional[unittest.TestCase] = None):
        super().__init__()
        self.path = Path(self.enter_context(tempfile.TemporaryDirectory()))
        if test_case is not None:
            test_case.addCleanup(self.__exit__, None, None, None)

    def add_yaml_file(self, relpath: str, contents: Any):
        abspath = self.path / relpath
        abspath.parent.mkdir(parents=True, exist_ok=True)
        with abspath.open("wt") as fd:
            yaml.dump(contents, fd)

    def as_kitchen(self, kitchen_class: Union[str, Type[Kitchen]] = Kitchen) -> Kitchen:
        import arkimapslib.kitchen

        if kitchen_class == "arkimet":
            kitchen_class = arkimapslib.kitchen.ArkimetKitchen
        elif kitchen_class == "eccodes":
            kitchen_class = arkimapslib.kitchen.EccodesKitchen
        elif isinstance(kitchen_class, str):
            raise ValueError(f"Invalid kitchen_class {kitchen_class!r}")

        global config
        definitions = Definitions(config=config)
        definitions.load([self.path])
        kitchen = self.enter_context(kitchen_class(definitions=definitions))
        return kitchen

    def __str__(self):
        return self.workdir
