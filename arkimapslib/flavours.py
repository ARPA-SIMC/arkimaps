# from __future__ import annotations
import fnmatch
import logging
import re
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Set, Type, cast, TypeVar

from . import inputs, orders
from .config import Config
from .lint import Lint
from .models import BaseDataModel, pydantic
from .postprocess import Postprocessor
from .component import RootComponent, TypeRegistry

if TYPE_CHECKING:
    from . import pantry, recipes
    from .inputs import InputFile, Instant

# Used for kwargs-style dicts
Kwargs = Dict[str, Any]


log = logging.getLogger("arkimaps.flavours")

# TODO: move these to flavour arguments
LEGEND_WIDTH_CM = 3
LEGEND_HEIGHT_CM = 21


class FlavourStep:
    """
    Flavour configuration for a step
    """

    def __init__(self, name: str, options: Optional[Kwargs] = None, **kw):
        self.name = name
        self.options: Kwargs = options if options is not None else {}

    def get_param(self, name: str) -> Any:
        return self.options.get(name)


class FlavourSpec(BaseDataModel):
    """
    Data model for Flavours
    """

    steps: Dict[str, Any] = pydantic.Field(default_factory=dict)
    postprocess: List[Dict[str, Any]] = pydantic.Field(default_factory=list)
    recipes_filter: List[str] = pydantic.Field(default_factory=list)


SPEC = TypeVar("SPEC", bound=FlavourSpec)


class Flavour(RootComponent[SPEC], spec=FlavourSpec):
    """
    Set of default settings used for generating a product
    """

    __registry__ = TypeRegistry["Flavour"]()
    lookup = __registry__.lookup

    def __init__(
        self,
        *,
        config: Config,
        name: str,
        defined_in: str,
        args: Dict[str, Any],
    ):
        super().__init__(config=config, name=name, defined_in=defined_in, args=args)

        self.recipes_filter: List[re.Pattern] = []
        for expr in self.spec.recipes_filter:
            self.recipes_filter.append(re.compile(fnmatch.translate(expr)))

        self.steps: Dict[str, FlavourStep] = {}
        for name, options in self.spec.steps.items():
            self.steps[name] = FlavourStep(name, options)

        self.postprocessors: List[Postprocessor] = []
        for desc in self.spec.postprocess:
            desc = desc.copy()
            name = desc.pop("type", None)
            if name is None:
                raise ValueError(f"{defined_in}: postprocessor listed without 'type'")
            self.postprocessors.append(Postprocessor.create(name=name, config=config, defined_in=defined_in, args=desc))

    def lint(self, lint: Lint) -> None:
        """
        Consistency check the given input arguments
        """
        for postproc in self.postprocessors:
            postproc.lint(lint=lint)

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
    def create(cls, *, args=Dict[str, Any], **kwargs: Any) -> "Flavour":
        tile_cls: Type[Flavour]
        if "tile" in args:
            tile_cls = cls.lookup("tiled")
        else:
            tile_cls = cls.lookup("simple")
        return tile_cls(args=args, **kwargs)

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

    def step_config(self, name: str) -> FlavourStep:
        """
        Return a FlavourStep object for the given step name
        """
        res = self.steps.get(name)
        if res is None:
            res = FlavourStep(name)
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
            for input_name in recipe_step.get_input_names(self):
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
            for input_name in recipe_step.get_input_names(self):
                input_names.add(input_name)
        return input_names

    def make_orders(self, recipe: "recipes.Recipe", pantry: "pantry.DiskPantry") -> List["orders.Order"]:
        """
        Scan a recipe and return a set with all the inputs it needs
        """
        # For each output instant, map inputs names to InputFile structures
        inputs: Optional[Dict["Instant", Dict[str, "InputFile"]]] = None
        # Collection of input name to InputFile mappings used by all output steps
        inputs_for_all_instants: Dict[str, "InputFile"] = {}

        input_names = self.get_inputs_for_recipe(recipe)
        log.debug("flavour %s: recipe %s uses inputs: %r", self.name, recipe.name, input_names)

        # Find the intersection of all steps available for all inputs needed
        for input_name in input_names:
            # Find available steps for this input
            output_instants: Dict[Optional["Instant"], "InputFile"]
            output_instants = pantry.get_instants(input_name)

            # Special handling for inputs that are not step-specific and
            # are valid for all steps, like maps or orography
            any_instant = output_instants.pop(None, None)
            if any_instant is not None:
                log.debug("flavour %s: recipe %s input %s available for any step", self.name, recipe.name, input_name)
                inputs_for_all_instants[input_name] = any_instant
                # This input is valid for all steps and does not
                # introduce step limitations
                if not output_instants:
                    continue
            elif output_instants:
                log.debug(
                    "flavour %s: recipe %s input %s available for instants %s",
                    self.name,
                    recipe.name,
                    input_name,
                    ", ".join(str(i) for i in output_instants.keys()),
                )
            else:
                log.debug(
                    "flavour %s: recipe %s input %s not available",
                    self.name,
                    recipe.name,
                    input_name,
                )

            # Intersect the output instants for the recipe input list
            if inputs is None:
                # The first time this output_instant has been seen, populate
                # the `inputs` mapping with all available inputs
                inputs = {}
                for output_instant, ifile in output_instants.items():
                    # None was popped earlier
                    assert output_instant is not None
                    inputs[output_instant] = {input_name: ifile}
            else:
                # The subsequent times this output_instant is seen, intersect
                instants_to_delete: List[Instant] = []
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
        inputs_for_all_instants: Dict[str, "inputs.InputFile"],
    ) -> List["orders.Order"]:
        raise NotImplementedError(f"{self.__class__}.inputs_to_orders not implemented")


class Simple(Flavour[FlavourSpec], spec=FlavourSpec):
    def inputs_to_orders(
        self,
        recipe: "recipes.Recipe",
        inputs: Optional[Dict["inputs.Instant", Dict[str, "inputs.InputFile"]]],
        inputs_for_all_instants: Dict[str, "inputs.InputFile"],
    ) -> List["orders.Order"]:
        res: List["orders.Order"] = []
        if inputs is None:
            return res

        # For each instant we found, build an order
        for output_instant, input_files in inputs.items():
            if inputs_for_all_instants:
                input_files.update(inputs_for_all_instants)

            res.append(
                orders.MapOrder(
                    flavour=self,
                    recipe=recipe,
                    input_files=input_files,
                    instant=output_instant,
                )
            )
        return res


class TileSpec(BaseDataModel):
    """
    Tile definition for TiledSpec
    """

    #: minimum zoom level to generate
    zoom_min: int = 3
    #: maximum zoom level to generate
    zoom_max: int = 5
    #: minimum latitude
    lat_min: float
    #: maximum latitude
    lat_max: float
    #: minimum longitude
    lon_min: float
    #: maximum longitude
    lon_max: float


class TiledSpec(FlavourSpec):
    """
    Data model for Flavours
    """

    #: Definition of the tiling requested
    tile: TileSpec


class Tiled(Flavour[TiledSpec], spec=TiledSpec):
    """
    Flavour that generates tiled output.

    """

    def summarize(self) -> Dict[str, Any]:
        res = super().summarize()
        for name in ("zoom", "lat", "lon"):
            res[f"{name}_min"] = getattr(self.spec.tile, f"{name}_min")
            res[f"{name}_max"] = getattr(self.spec.tile, f"{name}_max")
        return res

    def make_order_for_legend(
        self, recipe: "recipes.Recipe", input_files: Dict[str, "inputs.InputFile"], output_instant: "inputs.Instant"
    ):
        """
        Create an order to generate the legend for a tileset
        """
        from .mixers import mixers
        from .recipes import RecipeStepSkipped
        from .steps import AddGrib, AddContour

        # Identify relevant steps for legend generation
        grib_step: Optional[AddGrib] = None
        contour_step: Optional[AddContour] = None

        for recipe_step in recipe.steps:
            try:
                if recipe_step.name == "add_grib":
                    grib_step = cast(AddGrib, recipe_step.create_step(self, input_files))
                elif recipe_step.name == "add_contour":
                    step = cast(AddContour, recipe_step.create_step(self, input_files))
                    if step.spec.params.legend:
                        contour_step = step
                else:
                    # Ignore all other steps
                    pass
            except RecipeStepSkipped:
                continue

        if not contour_step:
            return None

        order_steps = []

        step_collection = mixers.get_steps(recipe.spec.mixer)
        add_basemap_class = step_collection.get("add_basemap")
        if add_basemap_class is None:
            raise RuntimeError(f"step add_basemap not found in mixer {recipe.spec.mixer}")

        # Configure the basemap to be just a canvas for the legend
        order_steps.append(
            add_basemap_class(
                config=self.config,
                # Allow to configure add_legend_basemap in flavour differently from
                # add_basemap
                # TODO: document this
                name="add_legend_basemap",
                defined_in=self.defined_in,
                args={
                    "params": {
                        "subpage_frame": "off",
                        "page_x_length": LEGEND_WIDTH_CM,
                        "page_y_length": LEGEND_HEIGHT_CM,
                        "super_page_x_length": LEGEND_WIDTH_CM,
                        "super_page_y_length": LEGEND_HEIGHT_CM,
                        "subpage_x_length": LEGEND_WIDTH_CM,
                        "subpage_y_length": LEGEND_HEIGHT_CM,
                        "subpage_x_position": 0.0,
                        "subpage_y_position": 0.0,
                        "subpage_gutter_percentage": 20.0,
                        "page_frame": "off",
                        "page_id_line": "off",
                    }
                },
                sources=input_files,
            )
        )

        if grib_step is not None:
            order_steps.append(grib_step)

        params = contour_step.spec.params
        params.legend = True
        params.legend_text_font_size = "25%"
        params.legend_border_thickness = 4
        params.legend_only = True
        params.legend_box_mode = "positional"
        params.legend_box_x_position = 0.00
        params.legend_box_y_position = 0.00
        params.legend_box_x_length = LEGEND_WIDTH_CM
        params.legend_box_y_length = LEGEND_HEIGHT_CM
        params.legend_box_blanking = False
        params.legend_title_font_size = -1
        params.legend_automatic_position = "top"
        order_steps.append(contour_step)

        return orders.LegendOrder(
            flavour=self,
            recipe=recipe,
            input_files=input_files,
            instant=output_instant,
            order_steps=order_steps,
        )

    def inputs_to_orders(
        self,
        recipe: "recipes.Recipe",
        inputs: Optional[Dict["inputs.Instant", Dict[str, "inputs.InputFile"]]],
        inputs_for_all_instants: Dict[str, "inputs.InputFile"],
    ) -> List["orders.Order"]:
        res: List["orders.Order"] = []
        if inputs is not None:
            # For each instant we found, build an order
            for idx, (output_instant, input_files) in enumerate(inputs.items()):
                if inputs_for_all_instants:
                    input_files.update(inputs_for_all_instants)

                res.extend(
                    orders.TileOrder.make_orders(
                        flavour=self,
                        recipe=recipe,
                        input_files=input_files,
                        instant=output_instant,
                        lat_min=self.spec.tile.lat_min,
                        lat_max=self.spec.tile.lat_max,
                        lon_min=self.spec.tile.lon_min,
                        lon_max=self.spec.tile.lon_max,
                        zoom_min=self.spec.tile.zoom_min,
                        zoom_max=self.spec.tile.zoom_max,
                    )
                )

                if idx == 0:
                    order = self.make_order_for_legend(recipe, input_files, output_instant)
                    if order is not None:
                        res.append(order)

        return res
