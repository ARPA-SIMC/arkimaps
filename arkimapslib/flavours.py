# from __future__ import annotations
import fnmatch
import logging
import re
from typing import TYPE_CHECKING, Dict, Any, Optional, List, Set

from .steps import StepConfig, Step, StepSkipped
from . import recipes
from . import orders
from . import inputs
from .config import Config

if TYPE_CHECKING:
    from . import pantry
    from .inputs import InputFile

# Used for kwargs-style dicts
Kwargs = Dict[str, Any]


log = logging.getLogger("arkimaps.flavours")


class Flavour:
    """
    Set of default settings used for generating a product
    """
    def __init__(self,
                 config: Config,
                 name: str,
                 defined_in: str,
                 steps: Kwargs = None,
                 recipes_filter: Optional[List[str]] = None,
                 **kw):
        self.config = config
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
               config: Config,
               name: str,
               defined_in: str,
               steps: Kwargs = None,
               recipes_filter: Optional[List[str]] = None,
               **kw):
        if 'tile' in kw:
            return TiledFlavour(config, name, defined_in, steps, recipes_filter, **kw)
        else:
            return SimpleFlavour(config, name, defined_in, steps, recipes_filter, **kw)

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

            res.append(orders.MapOrder(
                flavour=self,
                recipe=recipe,
                input_files=input_files,
                instant=output_instant,
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

    def summarize(self) -> Dict[str, Any]:
        res = super().summarize()
        for name in ("zoom", "lat", "lon"):
            res[f"{name}_min"] = getattr(self, f"{name}_min")
            res[f"{name}_max"] = getattr(self, f"{name}_max")
        return res

    def make_order_for_legend(
            self,
            recipe: "recipes.Recipe",
            input_files: Dict[str, "inputs.InputFile"],
            output_instant: "inputs.Instant"):
        """
        Create an order to generate the legend for a tileset
        """
        # Identify relevant steps for legend generation
        grib_step: Optional[Step] = None
        contour_step: Optional[Step] = None

        for recipe_step in recipe.steps:
            try:
                if recipe_step.name == "add_grib":
                    step_config = self.step_config(recipe_step.name)
                    grib_step = recipe_step.step(recipe_step.name, step_config, recipe_step.args, input_files)
                elif recipe_step.name == "add_contour":
                    step_config = self.step_config(recipe_step.name)
                    step = recipe_step.step(recipe_step.name, step_config, recipe_step.args, input_files)
                    params = step.params.get("params")
                    if params is None:
                        params = {}
                        step.params["params"] = params
                    if params.get("legend", False):
                        contour_step = step
                        break
                else:
                    # Ignore all other steps
                    pass
            except StepSkipped:
                continue

        if not contour_step:
            return None

        return orders.LegendOrder(
            flavour=self,
            recipe=recipe,
            input_files=input_files,
            instant=output_instant,
            grib_step=grib_step,
            contour_step=contour_step,
        )

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

                res.extend(orders.TileOrder.make_orders(
                            flavour=self,
                            recipe=recipe,
                            input_files=input_files,
                            instant=output_instant,
                            lat_min=self.lat_min, lat_max=self.lat_max,
                            lon_min=self.lon_min, lon_max=self.lon_max,
                            zoom_min=self.zoom_min, zoom_max=self.zoom_max))

                if idx == 0:
                    order = self.make_order_for_legend(recipe, input_files, output_instant)
                    if order is not None:
                        res.append(order)

        return res
