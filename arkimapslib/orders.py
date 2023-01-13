# from __future__ import annotations
import itertools
import logging
import math
import os
from collections import Counter, defaultdict
from typing import TYPE_CHECKING, Any, Dict, Generator, IO, List, Optional, Set, Tuple

from .steps import StepSkipped, StepConfig, AddBasemap

if TYPE_CHECKING:
    import datetime

    from . import inputs, steps
    from .flavours import Flavour
    from .kitchen import Kitchen
    from .recipes import Recipe


LEGEND_WIDTH_CM = 3
LEGEND_HEIGHT_CM = 21
TILE_WIDTH_CM = 256 / 40.
TILE_HEIGHT_CM = 256 / 40.
TILE_WIDTH_PX = 256
TILE_HEIGHT_PX = 256


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
        self.output_options: Dict[str, Any] = {}

        # If this order generates a legend, this is information about the
        # legend to be forwarded to the summary
        self.legend_info: Optional[Dict[str, Any]] = None

        # Logger for this output
        self.log: logging.Logger
        # Summary stats about the rendering
        self.render_time_ns: int = 0
        # Path to the rendering script
        self.render_script: Optional[str] = None

    def __str__(self):
        return self.basename

    def __repr__(self):
        return self.basename

    def print_python_function(self, name: str, timings=False, file: Optional[IO[str]] = None):
        """
        Print a function that renders this order
        """
        print(f"def {name}(workdir: str):", file=file)
        if timings:
            print("    start = perf_counter_ns()", file=file)

        output_pathname = os.path.join(self.relpath, self.basename)
        order_args = "".join([f", {k}={v!r}" for k, v in self.output_options.items()])
        print(f"    output_name=os.path.join(workdir, {output_pathname!r})", file=file)
        print(f"    parts = [macro.output(output_formats=['png'], output_name=output_name,"
              f" output_name_first_page_number='off'{order_args})]", file=file)

        for step in self.order_steps:
            name, parms = step.as_magics_macro()
            py_parms = []
            for k, v in parms.items():
                py_parms.append(f"{k}={v!r}")
            print(f"    parts.append(macro.{name}({', '.join(py_parms)}))", file=file)

        print("    res = {'output': output_name}", file=file)

        print("    with contextlib.redirect_stdout(io.StringIO()) as out:", file=file)
        print("        macro.plot(*parts)", file=file)
        print("        res['magics_output'] = out.getvalue()", file=file)

        # Return result
        if timings:
            print("    res['time'] = perf_counter_ns() - start", file=file)
        print("    return [res]", file=file)

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
            ):
        super().__init__(
                flavour=flavour, recipe=recipe, input_files=input_files,
                instant=instant)
        self.relpath = f"{instant.reftime:%Y-%m-%dT%H:%M:%S}/{recipe.name}_{flavour.name}"
        self.basename = f"{os.path.basename(recipe.name)}+{instant.step:03d}"
        self.log = logging.getLogger(
                f"arkimaps.render.{flavour.name}.{recipe.name}{instant.product_suffix()}")

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


def num2deg(xtile: int, ytile: int, zoom: int) -> Tuple[float, float]:
    n = 2.0 ** zoom
    lon_deg = xtile / n * 360.0 - 180.0
    lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * ytile / n)))
    lat_deg = math.degrees(lat_rad)
    return (lon_deg, lat_deg)


def deg2num(lon_deg: float, lat_deg: float, zoom: int) -> Tuple[int, int]:
    lat_rad = math.radians(lat_deg)
    n = 2.0 ** zoom
    xtile = int((lon_deg + 180.0) / 360.0 * n)
    ytile = int((1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * n)
    return (xtile, ytile)


class TileOrder(Order):
    def __init__(
            self, *,
            flavour: "Flavour",
            recipe: "Recipe",
            input_files: Dict[str, "inputs.InputFile"],
            instant: "inputs.Instant",
            z: int, x: int, y: int):
        super().__init__(
                flavour=flavour, recipe=recipe, input_files=input_files,
                instant=instant)
        self.relpath = (
            f"{instant.reftime:%Y-%m-%dT%H:%M:%S}/"
            f"{recipe.name}_{flavour.name}+{instant.step:03d}/"
            f"{z}/{x}/"
        )
        self.basename = f"{y}"
        self.log = logging.getLogger(
                f"arkimaps.render.{flavour.name}.{recipe.name}"
                f"{instant.product_suffix()}.{z}.{x}.{y}")

        min_lon, max_lat = num2deg(x, y, z)
        max_lon, min_lat = num2deg(x + 1, y + 1, z)

        self.output_options["output_cairo_transparent_background"] = True
        self.output_options["output_width"] = TILE_WIDTH_PX

        # Instantiate order steps from recipe steps
        for recipe_step in recipe.steps:
            try:
                step_config = flavour.step_config(recipe_step.name)
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
                        page_x_length=TILE_WIDTH_CM,
                        page_y_length=TILE_HEIGHT_CM,
                        super_page_x_length=TILE_WIDTH_CM,
                        super_page_y_length=TILE_HEIGHT_CM,
                        subpage_x_length=TILE_WIDTH_CM,
                        subpage_y_length=TILE_HEIGHT_CM,
                        subpage_x_position=0.,
                        subpage_y_position=0.,
                        subpage_frame='off',
                        output_width=TILE_WIDTH_PX,
                        page_frame='off',
                        skinny_mode="on",
                        page_id_line='off',
                    )
                elif recipe_step.name == "add_contour":
                    # Strip legend from add_contour
                    params = compiled_step.params.get("params")
                    if params is not None:
                        compiled_step.params["params"] = {k: v for k, v in params.items() if not k.startswith("legend")}
            except StepSkipped:
                self.log.debug("%s (skipped)", compiled_step.name)
                continue
            # self.log.debug("%s %r", step.name, step.get_params(mixer))
            self.order_steps.append(compiled_step)

    @classmethod
    def make_orders(
            cls, *,
            flavour: "Flavour",
            recipe: "Recipe",
            input_files: Dict[str, "inputs.InputFile"],
            instant: "inputs.Instant",
            lat_min: float, lat_max: float,
            lon_min: float, lon_max: float,
            zoom_min: int, zoom_max: int) -> Generator["TileOrder", None, None]:

        for z in range(zoom_min, zoom_max + 1):
            x_min, y_min = deg2num(lon_min, lat_min, z)
            x_max, y_max = deg2num(lon_max, lat_max, z)
            x_min, x_max = sorted((x_min, x_max))
            y_min, y_max = sorted((y_min, y_max))
            for x, y in itertools.product(
                        range(x_min, x_max + 1),
                        range(y_min, y_max + 1),
                    ):
                yield cls(
                    flavour=flavour,
                    recipe=recipe,
                    input_files=input_files,
                    instant=instant,
                    z=z, x=x, y=y
                )


class LegendOrder(Order):
    def __init__(
            self, *,
            flavour: "Flavour",
            recipe: "Recipe",
            input_files: Dict[str, "inputs.InputFile"],
            instant: "inputs.Instant",
            grib_step: Optional["steps.Step"],
            contour_step: "steps.Step"):
        super().__init__(
                flavour=flavour, recipe=recipe, input_files=input_files,
                instant=instant)
        self.relpath = f"{instant.reftime:%Y-%m-%dT%H:%M:%S}/"
        self.basename = f"{recipe.name}_{flavour.name}+legend"

        self.log = logging.getLogger(f"arkimaps.render.{flavour.name}.{recipe.name}.legend")

        # Configure the basemap to be just a canvas for the legend
        basemap_config = StepConfig("add_basemap", options={
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
        params["legend_box_x_length"] = LEGEND_WIDTH_CM
        params["legend_box_y_length"] = LEGEND_HEIGHT_CM
        params["legend_box_blanking"] = False
        params.pop("legend_title_font_size", None)
        params.pop("legend_automatic_position", None)
        self.order_steps.append(contour_step)

        self.legend_info = {
            "params": params,
        }
