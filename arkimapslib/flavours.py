# from __future__ import annotations
import fnmatch
import itertools
import logging
import math
import re
from typing import TYPE_CHECKING, Dict, Any, Optional, List, Set, Tuple

from .steps import StepConfig, Step, StepSkipped, AddBasemap
from . import recipes
from . import orders
from . import inputs

if TYPE_CHECKING:
    from . import pantry
    from .inputs import InputFile

# Used for kwargs-style dicts
Kwargs = Dict[str, Any]


log = logging.getLogger("arkimaps.flavours")


def deg2num(lon_deg: float, lat_deg: float, zoom: int) -> Tuple[int, int]:
    lat_rad = math.radians(lat_deg)
    n = 2.0 ** zoom
    xtile = int((lon_deg + 180.0) / 360.0 * n)
    ytile = int((1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * n)
    return (xtile, ytile)


def num2deg(xtile: int, ytile: int, zoom: int) -> Tuple[float, float]:
    n = 2.0 ** zoom
    lon_deg = xtile / n * 360.0 - 180.0
    lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * ytile / n)))
    lat_deg = math.degrees(lat_rad)
    return (lon_deg, lat_deg)


class Flavour:
    """
    Set of default settings used for generating a product
    """
    def __init__(self,
                 name: str,
                 defined_in: str,
                 steps: Kwargs = None,
                 recipes_filter: Optional[List[str]] = None,
                 **kw):
        self.name = name
        self.defined_in = defined_in

        self.recipes_filter: List[re.compile] = []
        if recipes_filter is not None:
            if not isinstance(recipes_filter, list):
                raise ValueError(f"{defined_in}: recipes_filter is {type(recipes_filter).__name__} instead of list")
            for expr in recipes_filter:
                self.recipes_filter.append(
                        re.compile(fnmatch.translate(expr)))

        self.steps: Dict[str, StepConfig] = {}
        if steps is not None:
            for name, options in steps.items():
                self.steps[name] = StepConfig(name, options)

    def __str__(self):
        return self.name

    def summarize(self) -> Dict[str, Any]:
        """
        Return a structure describing this Flavour, to use for the render order
        summary
        """
        return {
            "name": self.name,
            "defined_in": self.defined_in,
        }

    @classmethod
    def create(cls,
               name: str,
               defined_in: str,
               steps: Kwargs = None,
               recipes_filter: Optional[List[str]] = None,
               **kw):
        if 'tile' in kw:
            return TiledFlavour(name, defined_in, steps, recipes_filter, **kw)
        else:
            return SimpleFlavour(name, defined_in, steps, recipes_filter, **kw)

    def allows_recipe(self, recipe: "recipes.Recipe"):
        """
        Check if a recipe should be generated for this flavour
        """
        if not self.recipes_filter:
            return True
        for regex in self.recipes_filter:
            if regex.match(recipe.name):
                return True
        return False

    def step_config(self, name: str) -> StepConfig:
        """
        Return a StepConfig object for the given step name
        """
        res = self.steps.get(name)
        if res is None:
            res = StepConfig(name)
        return res

    def list_inputs_recursive(self, recipe: "recipes.Recipe", pantry: "pantry.Pantry") -> List[str]:
        """
        List inputs used by a recipe, and all their inputs, recursively
        """
        res: List[str] = []
        for input_name in self.list_inputs(recipe):
            for inp in pantry.inputs[input_name]:
                inp.add_all_inputs(pantry, res)
        return res

    def list_inputs(self, recipe: "recipes.Recipe") -> List[str]:
        """
        List the names of inputs used by this recipe

        Inputs are listed in usage order, without duplicates
        """
        input_names: List[str] = []

        # Collect the inputs needed for all steps
        for recipe_step in recipe.steps:
            step_config = self.step_config(recipe_step.name)
            for input_name in recipe_step.get_input_names(step_config):
                if input_name in input_names:
                    continue
                input_names.append(input_name)
        return input_names

    def get_inputs_for_recipe(self, recipe: "recipes.Recipe") -> Set[str]:
        """
        Return a list with the names of all inputs used by a recipe in this
        flavour
        """
        input_names: Set[str] = set()
        for recipe_step in recipe.steps:
            step_config = self.step_config(recipe_step.name)
            for input_name in recipe_step.get_input_names(step_config):
                input_names.add(input_name)
        return input_names

    def make_orders(self,
                    recipe: "recipes.Recipe",
                    pantry: "pantry.DiskPantry") -> List["orders.Order"]:
        """
        Scan a recipe and return a set with all the inputs it needs
        """
        # For each output instant, map inputs names to InputFile structures
        inputs: Optional[Dict["inputs.Instant", Dict[str, "inputs.InputFile"]]] = None
        # Collection of input name to InputFile mappings used by all output steps
        inputs_for_all_instants: Dict[str, "inputs.InputFile"] = {}

        input_names = self.get_inputs_for_recipe(recipe)
        log.debug("flavour %s: recipe %s uses inputs: %r", self.name, recipe.name, input_names)

        # Find the intersection of all steps available for all inputs needed
        for input_name in input_names:
            # Find available steps for this input
            output_instants: Dict[Optional["inputs.Instant"], "InputFile"]
            output_instants = pantry.get_instants(input_name)

            # Special handling for inputs that are not step-specific and
            # are valid for all steps, like maps or orography
            any_instant = output_instants.pop(None, None)
            if any_instant is not None:
                log.debug("flavour %s: recipe %s inputs %s available for any step", self.name, recipe.name, input_name)
                inputs_for_all_instants[input_name] = any_instant
                # This input is valid for all steps and does not
                # introduce step limitations
                if not output_instants:
                    continue
            else:
                log.debug("flavour %s: recipe %s inputs %s available for instants %r",
                          self.name, recipe.name, input_name, output_instants.keys())

            # Intersect the output instants for the recipe input list
            if inputs is None:
                # The first time this output_instant has been seen, populate
                # the `inputs` mapping with all available inputs
                inputs = {}
                for output_instant, ifile in output_instants.items():
                    inputs[output_instant] = {input_name: ifile}
            else:
                # The subsequent times this output_instant is seen, intersect
                instants_to_delete: List[int] = []
                for output_instant, input_files in inputs.items():
                    if output_instant not in output_instants:
                        # We miss an input for this instant, so we cannot
                        # generate an order for it
                        instants_to_delete.append(output_instant)
                    else:
                        input_files[input_name] = output_instants[output_instant]
                for output_instant in instants_to_delete:
                    del inputs[output_instant]

        return self.inputs_to_orders(recipe, inputs, inputs_for_all_instants)

    def inputs_to_orders(
            self,
            recipe: "recipes.Recipe",
            inputs: Optional[Dict["inputs.Instant", Dict[str, "inputs.InputFile"]]],
            inputs_for_all_instants: Dict[str, "inputs.InputFile"]) -> List["orders.Order"]:
        raise NotImplementedError(f"{self.__class__}.inputs_to_orders not implemented")


class SimpleFlavour(Flavour):
    def instantiate_order_step(
            self,
            recipe_step: "recipes.RecipeStep",
            input_files: Dict[str, inputs.InputFile]) -> Step:
        """
        Instantiate the step class with the given flavour config
        """
        step_config = self.step_config(recipe_step.name)
        return recipe_step.step(recipe_step.name, step_config, recipe_step.args, input_files)

    def inputs_to_orders(
            self,
            recipe: "recipes.Recipe",
            inputs: Optional[Dict["inputs.Instant", Dict[str, "inputs.InputFile"]]],
            inputs_for_all_instants: Dict[str, "inputs.InputFile"]) -> List["orders.Order"]:
        res: List["orders.Order"] = []
        if inputs is None:
            return res

        # For each instant we found, build an order
        for output_instant, input_files in inputs.items():
            if inputs_for_all_instants:
                input_files.update(inputs_for_all_instants)

            logger = logging.getLogger(
                    f"arkimaps.render.{self.name}.{recipe.name}{output_instant.product_suffix()}")

            # Instantiate order steps from recipe steps
            order_steps: List[Step] = []
            for recipe_step in recipe.steps:
                try:
                    s = self.instantiate_order_step(recipe_step, input_files)
                except StepSkipped:
                    logger.debug("%s (skipped)", s.name)
                    continue
                # self.log.debug("%s %r", step.name, step.get_params(mixer))
                order_steps.append(s)

            res.append(orders.MapOrder(
                flavour=self,
                recipe=recipe,
                input_files=input_files,
                instant=output_instant,
                order_steps=order_steps,
                output_options={},
                log=logger,
            ))
        return res


class TiledFlavour(Flavour):
    """
    Flavour that generates tiled output.

    ``tile`` in the flavour is a dictionary defining the requested tiling, with
    these fields:
     * ``zoom_min: Int = 3``: minimum zoom level to generate
     * ``zoom_max: Int = 5``: maximum zoom level to generate
     * ``lat_min: Float``: minimum latitude
     * ``lat_max: Float``: maximum latitude
     * ``lon_min: Float``: minimum longitude
     * ``lon_max: Float``: maximum longitude
    """
    def __init__(self, *args, tile: Dict[str, Any] = None, **kw):
        super().__init__(*args, **kw)
        self.zoom_min = int(tile.get("zoom_min", 3))
        self.zoom_max = int(tile.get("zoom_max", 5))
        self.lat_min = float(tile["lat_min"])
        self.lat_max = float(tile["lat_max"])
        self.lon_min = float(tile["lon_min"])
        self.lon_max = float(tile["lon_max"])
        self.width = 256
        self.height = 256
        self.width_cm = self.width / 40.
        self.height_cm = self.height / 40.

    def summarize(self) -> Dict[str, Any]:
        res = super().summarize()
        for name in ("zoom", "lat", "lon"):
            res[f"{name}_min"] = getattr(self, f"{name}_min")
            res[f"{name}_max"] = getattr(self, f"{name}_max")
        return res

    def instantiate_order_step(
            self,
            recipe_step: "recipes.RecipeStep",
            input_files: Dict[str, inputs.InputFile],
            min_lat: float, max_lat: float,
            min_lon: float, max_lon: float) -> Step:
        """
        Instantiate the step class with the given flavour config
        """
        step_config = self.step_config(recipe_step.name)
        compiled_step = recipe_step.step(recipe_step.name, step_config, recipe_step.args, input_files)
        if recipe_step.name == "add_basemap":
            params = compiled_step.params.get("params")
            if params is None:
                params = {}
            else:
                params = params.copy()
            compiled_step.params["params"] = params
            params.update(
                subpage_map_projection="EPSG:3857",
                subpage_lower_left_latitude=min_lat,
                subpage_lower_left_longitude=min_lon,
                subpage_upper_right_latitude=max_lat,
                subpage_upper_right_longitude=max_lon,
                page_x_length=self.width_cm,
                page_y_length=self.height_cm,
                super_page_x_length=self.width_cm,
                super_page_y_length=self.height_cm,
                subpage_x_length=self.width_cm,
                subpage_y_length=self.height_cm,
                subpage_x_position=0.,
                subpage_y_position=0.,
                subpage_frame='off',
                output_width=self.width,
                page_frame='off',
                skinny_mode="on",
                page_id_line='off',
            )
        elif recipe_step.name == "add_contour":
            # Strip legend from add_contour
            params = compiled_step.params.get("params")
            if params is not None:
                compiled_step.params["params"] = {k: v for k, v in params.items() if not k.startswith("legend")}
        return compiled_step

    def make_order_for_legend(
            self,
            recipe: "recipes.Recipe",
            input_files: Dict[str, "inputs.InputFile"],
            output_instant: "inputs.Instant"):
        """
        Create an order to generate the legend for a tileset
        """
        logger = logging.getLogger(
                f"arkimaps.render.{self.name}.{recipe.name}.legend")

        width_cm = 3
        height_cm = 21

        # Instantiate order steps from recipe steps
        order_steps: List[Step] = []

        # Configure the basemap to be just a canvas for the legend
        basemap_config = StepConfig("add_basemap", options={
            "params": {
                "subpage_frame": "off",
                "page_x_length": width_cm,
                "page_y_length": height_cm,
                "super_page_x_length": width_cm,
                "super_page_y_length": height_cm,
                "subpage_x_length": width_cm,
                "subpage_y_length": height_cm,
                "subpage_x_position": 0.0,
                "subpage_y_position": 0.0,
                "subpage_gutter_percentage": 20.,
                "page_frame": "off",
                "page_id_line": "off"
            },
        })
        order_steps.append(AddBasemap("add_basemap", basemap_config, {}, input_files))

        legend_step = None
        for recipe_step in recipe.steps:
            if recipe_step.name not in ("add_grib", "add_contour"):
                continue
            try:
                step_config = self.step_config(recipe_step.name)
                s = recipe_step.step(recipe_step.name, step_config, recipe_step.args, input_files)
                if not legend_step and recipe_step.name == "add_contour":
                    params = s.params.get("params")
                    if params is None:
                        params = {}
                        s.params["params"] = params
                    # Skip add_contour levels with `legend: off`
                    if not params.get("legend", False):
                        continue
                    params["legend"] = "on"
                    params["legend_text_font_size"] = '25%'
                    params["legend_border_thickness"] = 4
                    params["legend_only"] = "on"
                    params["legend_box_mode"] = "positional"
                    params["legend_box_x_position"] = 0.00
                    params["legend_box_y_position"] = 0.00
                    params["legend_box_x_length"] = width_cm
                    params["legend_box_y_length"] = height_cm
                    params["legend_box_blanking"] = False
                    params.pop("legend_title_font_size", None)
                    params.pop("legend_automatic_position", None)
                    legend_step = s
            except StepSkipped:
                logger.debug("%s (skipped)", s.name)
                continue
            order_steps.append(s)

        if not legend_step:
            return None

        order = orders.LegendOrder(
            flavour=self,
            recipe=recipe,
            input_files=input_files,
            instant=output_instant,
            order_steps=order_steps,
            output_options={
                # "output_cairo_transparent_background": True,
                # "output_width": self.width,
            },
            log=logger,
        )
        order.legend_info = {
            "params": legend_step.params["params"],
        }
        return order

    def inputs_to_orders(
            self,
            recipe: "recipes.Recipe",
            inputs: Optional[Dict["inputs.Instant", Dict[str, "inputs.InputFile"]]],
            inputs_for_all_instants: Dict[str, "inputs.InputFile"]) -> List["orders.Order"]:
        res: List["orders.Order"] = []
        if inputs is not None:
            # For each instant we found, build an order
            for idx, (output_instant, input_files) in enumerate(inputs.items()):
                if inputs_for_all_instants:
                    input_files.update(inputs_for_all_instants)

                for z in range(self.zoom_min, self.zoom_max + 1):
                    x_min, y_min = deg2num(self.lon_min, self.lat_min, z)
                    x_max, y_max = deg2num(self.lon_max, self.lat_max, z)
                    x_min, x_max = sorted((x_min, x_max))
                    y_min, y_max = sorted((y_min, y_max))
                    for x, y in itertools.product(
                                range(x_min, x_max + 1),
                                range(y_min, y_max + 1),
                            ):
                        min_lon, max_lat = num2deg(x, y, z)
                        max_lon, min_lat = num2deg(x + 1, y + 1, z)

                        logger = logging.getLogger(
                                f"arkimaps.render.{self.name}.{recipe.name}"
                                f"{output_instant.product_suffix()}.{z}.{x}.{y}")

                        # Instantiate order steps from recipe steps
                        order_steps: List[Step] = []
                        for recipe_step in recipe.steps:
                            try:
                                s = self.instantiate_order_step(
                                        recipe_step, input_files, min_lat, max_lat, min_lon, max_lon)
                            except StepSkipped:
                                logger.debug("%s (skipped)", s.name)
                                continue
                            # self.log.debug("%s %r", step.name, step.get_params(mixer))
                            order_steps.append(s)

                        res.append(orders.TileOrder(
                            flavour=self,
                            recipe=recipe,
                            input_files=input_files,
                            instant=output_instant,
                            order_steps=order_steps,
                            output_options={
                                "output_cairo_transparent_background": True,
                                "output_width": self.width,
                            },
                            log=logger,
                            z=z, x=x, y=y
                        ))

                if idx == 0:
                    order = self.make_order_for_legend(recipe, input_files, output_instant)
                    if order is not None:
                        res.append(order)

        return res
