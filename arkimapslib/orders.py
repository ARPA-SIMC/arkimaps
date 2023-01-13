# from __future__ import annotations
import logging
import os
from collections import Counter, defaultdict
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Set

from .steps import StepSkipped, StepConfig, AddBasemap

if TYPE_CHECKING:
    import datetime

    from . import inputs, steps
    from .flavours import Flavour
    from .kitchen import Kitchen
    from .recipes import Recipe


class Order:
    """
    Serializable instructions to prepare a product, based on a recipe and its
    input files
    """
    def __init__(
            self, *,
            flavour: "Flavour",
            recipe: "Recipe",
            input_files: Dict[str, "inputs.InputFile"],
            instant: "inputs.Instant",
            output_options: Dict[str, Any],
            log: logging.Logger,
            ):
        # Reference to the flavour to use for summaries. It will be lost for
        # rendering, to avoid pickling the complex structure
        self.flavour: Optional["Flavour"] = flavour
        # Reference to the recipe to use for summaries. It will be lost for
        # rendering, to avoid pickling the complex structure
        self.recipe: Optional["Recipe"] = recipe
        # Name of the Mixer to use
        self.mixer = recipe.mixer
        # Dict mapping source names to pathnames of GRIB files
        self.input_files = input_files
        # Product instant
        self.instant = instant
        # List of recipe steps instantiated for this order
        self.order_steps: List["steps.Step"] = []

        # Destination directory inside the output
        self.relpath: str
        # Destination file name (without path or .png extension)
        self.basename: str
        # Output file name, set after the product has been rendered
        self.output: Optional[str] = None
        # Extra options to be passed to Magics' output() macro
        self.output_options = output_options

        # If this order generates a legend, this is information about the
        # legend to be forwarded to the summary
        self.legend_info: Optional[Dict[str, Any]] = None

        # Logger for this output
        self.log = log
        # Summary stats about the rendering
        self.render_time_ns: int = 0
        # Path to the rendering script
        self.render_script: Optional[str] = None

    def __str__(self):
        return self.basename

    def __repr__(self):
        return self.basename

    @classmethod
    def summarize_orders(cls, kitchen: "Kitchen", orders: List["Order"]) -> List[Dict[str, Any]]:
        """
        Summarize a list of orders into a json-able structure
        """
        result: List[Dict[str, Any]] = []

        by_fr: Dict[str, List[Order]] = defaultdict(list)

        # Group by flavour and recipe
        for order in orders:
            by_fr[(order.flavour.name, order.recipe.name)].append(order)

        for (flavour_name, recipe_name), orders_fr in by_fr.items():
            record = {
                "flavour": kitchen.flavours[flavour_name].summarize(),
                "recipe": kitchen.recipes.get(recipe_name).summarize(),
                "reftimes": {},
            }

            # Group orders by reftime
            by_rt: Dict[datetime.datetime, List[Order]] = defaultdict(list)
            for order in orders_fr:
                by_rt[order.instant.reftime].append(order)

            for reftime, orders in by_rt.items():
                inputs: Set[str] = set()
                steps: dict[int, int] = Counter()
                legend_info: Optional[Dict[str, Any]] = None
                render_time_ns: int = 0
                for order in orders:
                    inputs.update(order.input_files.keys())
                    steps[order.instant.step] += 1
                    if order.legend_info:
                        legend_info = order.legend_info
                    render_time_ns += order.render_time_ns
                record_rt = {
                    "inputs": sorted(inputs),
                    "steps": steps,
                    "legend_info": legend_info,
                    "render_stats": {
                        "time_ns": render_time_ns,
                    },
                }
                record["reftimes"][reftime.strftime("%Y-%m-%d %H:%M:%S")] = record_rt

            result.append(record)

        return result


class MapOrder(Order):
    def __init__(
            self, *,
            flavour: "Flavour",
            recipe: "Recipe",
            input_files: Dict[str, "inputs.InputFile"],
            instant: "inputs.Instant",
            output_options: Dict[str, Any],
            log: logging.Logger,
            ):
        super().__init__(
                flavour=flavour, recipe=recipe, input_files=input_files,
                instant=instant, output_options=output_options, log=log)
        self.relpath = f"{instant.reftime:%Y-%m-%dT%H:%M:%S}/{recipe.name}_{flavour.name}"
        self.basename = f"{os.path.basename(recipe.name)}+{instant.step:03d}"

        # Instantiate order steps from recipe steps
        for recipe_step in recipe.steps:
            try:
                step_config = flavour.step_config(recipe_step.name)
                s = recipe_step.step(recipe_step.name, step_config, recipe_step.args, input_files)
            except StepSkipped:
                self.log.debug("%s (skipped)", s.name)
                continue
            # self.log.debug("%s %r", step.name, step.get_params(mixer))
            self.order_steps.append(s)


class TileOrder(Order):
    def __init__(
            self, *,
            flavour: "Flavour",
            recipe: "Recipe",
            input_files: Dict[str, "inputs.InputFile"],
            instant: "inputs.Instant",
            order_steps: List["steps.Step"],
            output_options: Dict[str, Any],
            log: logging.Logger,
            z: int, x: int, y: int):
        super().__init__(
                flavour=flavour, recipe=recipe, input_files=input_files,
                instant=instant,
                output_options=output_options, log=log)
        self.relpath = (
            f"{instant.reftime:%Y-%m-%dT%H:%M:%S}/"
            f"{recipe.name}_{flavour.name}+{instant.step:03d}/"
            f"{z}/{x}/"
        )
        self.basename = f"{y}"
        self.order_steps.extend(order_steps)


class LegendOrder(Order):
    def __init__(
            self, *,
            flavour: "Flavour",
            recipe: "Recipe",
            input_files: Dict[str, "inputs.InputFile"],
            instant: "inputs.Instant",
            output_options: Dict[str, Any],
            log: logging.Logger,
            grib_step: Optional["steps.Step"],
            contour_step: "steps.Step"):
        super().__init__(
                flavour=flavour, recipe=recipe, input_files=input_files,
                instant=instant, output_options=output_options, log=log)
        self.relpath = f"{instant.reftime:%Y-%m-%dT%H:%M:%S}/"
        self.basename = f"{recipe.name}_{flavour.name}+legend"

        width_cm = 3
        height_cm = 21

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
        self.order_steps.append(AddBasemap("add_basemap", basemap_config, {}, input_files))

        if grib_step is not None:
            self.order_steps.append(grib_step)

        params = contour_step.params["params"]
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
        self.order_steps.append(contour_step)

        self.legend_info = {
            "params": params,
        }
