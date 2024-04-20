# from __future__ import annotations
import io
import logging
import math
import os
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Dict, Generator, List, NamedTuple, Optional, Tuple

from PIL import Image

from . import outputbundle
from .steps import StepSkipped
from .pygen import PyGen

if TYPE_CHECKING:
    from . import inputs, steps
    from .flavours import Flavour
    from .recipes import Recipe

log = logging.getLogger("orders")

TILE_WIDTH_CM = 256 / 40.0
TILE_HEIGHT_CM = 256 / 40.0
TILE_WIDTH_PX = 256
TILE_HEIGHT_PX = 256


class Output(NamedTuple):
    """
    Information about an output generated by a Python render function
    """

    name: str
    relpath: str
    magics_output: str


class Order(ABC):
    """
    Serializable instructions to prepare a product, based on a recipe and its
    input files
    """

    def __init__(
        self,
        *,
        flavour: "Flavour",
        recipe: "Recipe",
        input_files: Dict[str, "inputs.InputFile"],
        instant: "inputs.Instant",
    ):
        # Reference to the flavour to use for summaries
        self.flavour: "Flavour" = flavour
        # Reference to the recipe to use for summaries
        self.recipe: "Recipe" = recipe
        # Name of the Mixer to use
        self.mixer = recipe.spec.mixer
        # Dict mapping source names to pathnames of GRIB files
        self.input_files = input_files
        # Product instant
        self.instant = instant
        # List of recipe steps instantiated for this order
        self.order_steps: List["steps.Step"] = []
        # Extra options to be passed to Magics' output() macro
        self.output_options: Dict[str, Any] = {}

        # Output file name, set after the product has been rendered
        self.output: Optional[Output] = None

        # Summary stats about the rendering
        self.render_time_ns: int = 0

    @abstractmethod
    def print_python_function(self, function_name: str, gen: PyGen):
        """
        Print a function that renders this order
        """

    def set_output(self, output: Output, timing: int = 0):
        """
        Add a rendered output to this order
        """
        if self.output is not None:
            log.error("%s: output already set to %s and set again to %s", self, self.output, output)
        self.output = output
        self.render_time_ns += timing

    def add_to_bundle(self, workdir: str, bundle: outputbundle.Writer):
        """
        Add render results to a tarball
        """
        if self.output is None:
            raise AssertionError(f"{self}: product has not been rendered")
        log.info("Rendered %s to %s", self, self.output.relpath)

        # Move the generated image to the output bundle
        path = os.path.join(workdir, self.output.relpath)
        with open(path, "rb") as data:
            bundle.add_product(self.output.relpath, data)
        os.unlink(path)

    def georeference(self) -> Optional[Dict[str, Any]]:
        """
        Return a dict with georeferencing information for the image produced by
        this order.

        Returns None of this order produces an image that cannot be
        georeferenced.

        In the case of an order that produces a larger tile that will then get
        cut into a grid to produce the actual requested tiles, the
        georeferencing refers to the image with the larger tile
        """
        for step in self.order_steps:
            if step.name == "add_basemap":
                try:
                    params = step.params["params"]
                    projection = params["subpage_map_projection"]
                    lllon = params["subpage_lower_left_longitude"]
                    lllat = params["subpage_lower_left_latitude"]
                    urlon = params["subpage_upper_right_longitude"]
                    urlat = params["subpage_upper_right_latitude"]
                except KeyError:
                    continue
                break
        else:
            log.info("%s: Order has no add_basemap step", self)
            return None

        if projection.startswith("EPSG:"):
            epsg = int(projection[5:])
        elif projection == "cylindrical":
            epsg = 4326
        else:
            log.info("%s: Order has still unsupported projection %s", self, projection)
            return None

        return {
            "projection": "EPSG",
            "epsg": epsg,
            "bbox": [min(lllon, urlon), min(lllat, urlat), max(lllon, urlon), max(lllat, urlat)],
        }

    def summarize_outputs(self, products_info: outputbundle.Products):
        """
        Add information about the images producted by this order to the
        products information of an output bundle
        """
        if self.output is None:
            raise AssertionError(f"{self}: product has not been rendered")

        products_info.by_path[self.output.relpath].add_recipe(self.recipe)
        products_info.by_path[self.output.relpath].add_instant(self.instant)

        georef = self.georeference()
        if georef is not None:
            products_info.by_path[self.output.relpath].add_georef(georef)


class MapOrder(Order):
    def __init__(
        self,
        *,
        flavour: "Flavour",
        recipe: "Recipe",
        input_files: Dict[str, "inputs.InputFile"],
        instant: "inputs.Instant",
    ):
        super().__init__(flavour=flavour, recipe=recipe, input_files=input_files, instant=instant)

        # Instantiate order steps from recipe steps
        for recipe_step in recipe.steps:
            try:
                s = recipe_step.create_step(flavour, input_files)
            except StepSkipped:
                log.debug("%s: %s (skipped)", self, recipe_step.name)
                continue
            self.order_steps.append(s)

    def __str__(self):
        return f"{os.path.basename(self.recipe.name)}{self.instant.step_suffix()}"

    def __repr__(self):
        return f"{self.__class__.__name__}({os.path.basename(self.recipe.name)}{self.instant.step_suffix()})"

    def print_python_function(self, function_name: str, gen: PyGen):
        """
        Print a function that renders this order
        """
        # Destination directory inside the output
        relpath = f"{self.instant.reftime:%Y-%m-%dT%H:%M:%S}/{self.recipe.name}_{self.flavour.name}"
        # Destination file name (without path or .png extension)
        basename = f"{os.path.basename(self.recipe.name)}{self.instant.step_suffix()}"
        gen.magics_renderer(function_name, self, relpath, basename)


def num2deg(xtile: int, ytile: int, zoom: int) -> Tuple[float, float]:
    """
    Compute the geographical coordinates of the northwest point of the tile
    """
    n = 2.0**zoom
    lon_deg = xtile / n * 360.0 - 180.0
    lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * ytile / n)))
    lat_deg = math.degrees(lat_rad)
    return (lon_deg, lat_deg)


def deg2num(lon_deg: float, lat_deg: float, zoom: int) -> Tuple[int, int]:
    """
    Compute the tile coordinates of the tile that contain the given point
    """
    # See https://towardsdatascience.com/map-tiles-locating-areas-nested-parent-tiles-coordinates-and-bounding-boxes-e54de570d0bd  # noqa
    lat_rad = math.radians(lat_deg)
    n = 2.0**zoom
    xtile = int((lon_deg + 180.0) / 360.0 * n)
    ytile = int((1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * n)
    return (xtile, ytile)


class TileOrder(Order):
    def __init__(
        self,
        *,
        flavour: "Flavour",
        recipe: "Recipe",
        input_files: Dict[str, "inputs.InputFile"],
        instant: "inputs.Instant",
        z: int,
        x: int,
        y: int,
        w: int = 1,
        h: int = 1,
    ):
        super().__init__(flavour=flavour, recipe=recipe, input_files=input_files, instant=instant)
        self.x = x
        self.y = y
        self.z = z
        # Width, in number of tiles, of the rendering cluster
        self.width = w
        # Height, in number of tiles, of the rendering cluster
        self.height = h

        min_lon, max_lat = num2deg(x, y, z)
        max_lon, min_lat = num2deg(x + self.width, y + self.height, z)

        self.output_options["output_cairo_transparent_background"] = True
        # TODO: if we eventually do rectangular renderings, see
        #       if there is also output_height
        self.output_options["output_width"] = TILE_WIDTH_PX * self.width

        # Instantiate order steps from recipe steps
        for recipe_step in recipe.steps:
            try:
                compiled_step = recipe_step.create_step(flavour, input_files)
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
                        page_x_length=TILE_WIDTH_CM * self.width,
                        page_y_length=TILE_HEIGHT_CM * self.height,
                        super_page_x_length=TILE_WIDTH_CM * self.width,
                        super_page_y_length=TILE_HEIGHT_CM * self.height,
                        subpage_x_length=TILE_WIDTH_CM * self.width,
                        subpage_y_length=TILE_HEIGHT_CM * self.height,
                        subpage_x_position=0.0,
                        subpage_y_position=0.0,
                        subpage_frame="off",
                        output_width=TILE_WIDTH_PX * self.width,
                        page_frame="off",
                        skinny_mode="on",
                        page_id_line="off",
                    )
                elif recipe_step.name == "add_contour":
                    # Strip legend from add_contour
                    params = compiled_step.params.get("params")
                    if params is not None:
                        compiled_step.params["params"] = {k: v for k, v in params.items() if not k.startswith("legend")}
            except StepSkipped:
                log.debug("%s: %s (skipped)", self, compiled_step.name)
                continue
            self.order_steps.append(compiled_step)

    def __str__(self):
        return (
            f"{os.path.basename(self.recipe.name)}{self.instant.step_suffix()}/"
            f"{self.z}/{self.x}/{self.y}+w{self.width}h{self.height}"
        )

    def __repr__(self):
        return f"{self.__class__.__name__}({str(self)})"

    def print_python_function(self, function_name: str, gen: PyGen):
        """
        Print a function that renders this order
        """
        relpath = (
            f"{self.instant.reftime:%Y-%m-%dT%H:%M:%S}/"
            f"{self.recipe.name}_{self.flavour.name}{self.instant.step_suffix()}/"
            f"{self.z}"
        )
        basename = f"{self.x}-{self.y}-{self.width}-{self.height}"
        gen.magics_renderer(function_name, self, relpath, basename)

    def add_to_bundle(self, workdir: str, bundle: outputbundle.Writer):
        """
        Add render results to a tarball
        """
        relpath, basename = os.path.split(self.output.relpath)

        start_x, start_y, width, height = (int(x) for x in basename[:-4].split("-"))

        rendered = Image.open(os.path.join(workdir, self.output.relpath), mode="r")
        # Requires PIL >= 8.0.0
        # rendered = Image.open(os.path.join(workdir, self.output.relpath), mode='r', formats=('PNG',))

        # Slice the tile and add it to the bundle
        for x in range(width):
            for y in range(height):
                tile = rendered.crop(
                    (x * TILE_WIDTH_PX, y * TILE_HEIGHT_PX, (x + 1) * TILE_WIDTH_PX, (y + 1) * TILE_HEIGHT_PX)
                )
                with io.BytesIO() as buf:
                    tile.save(buf, "PNG")
                    buf.seek(0)
                    bundle_path = os.path.join(relpath, str(x + start_x), f"{y + start_y}.png")
                    bundle.add_product(bundle_path, buf)
                    log.info("Rendered %s to %s", self, bundle_path)

    def summarize_outputs(self, products_info: outputbundle.Products):
        """
        Add information about the images producted by this order to the
        products information of an output bundle
        """
        if self.output is None:
            raise AssertionError(f"{self}: product has not been rendered")

        relpath, basename = os.path.split(self.output.relpath)

        start_x, start_y, width, height = (int(x) for x in basename[:-4].split("-"))

        georef = self.georeference()
        if georef is not None:
            lonmin, latmin, lonmax, latmax = georef["bbox"]
            lon_width = (lonmax - lonmin) / width
            lat_height = (latmax - latmin) / height

        # Add information about each tile slice
        for x in range(width):
            for y in range(height):
                bundle_path = os.path.join(relpath, str(x + start_x), f"{y + start_y}.png")
                products_info.by_path[bundle_path].add_recipe(self.recipe)
                products_info.by_path[bundle_path].add_instant(self.instant)

                if georef is None:
                    continue

                tile_georef = georef.copy()
                tile_georef["bbox"] = [
                    lonmin + x * lon_width,
                    latmin + y * lat_height,
                    lonmin + (x + 1) * lon_width,
                    latmin + (y + 1) * lat_height,
                ]
                products_info.by_path[bundle_path].add_georef(tile_georef)

    @classmethod
    def make_orders(
        cls,
        *,
        flavour: "Flavour",
        recipe: "Recipe",
        input_files: Dict[str, "inputs.InputFile"],
        instant: "inputs.Instant",
        lat_min: float,
        lat_max: float,
        lon_min: float,
        lon_max: float,
        zoom_min: int,
        zoom_max: int,
    ) -> Generator["TileOrder", None, None]:
        for z in range(zoom_min, zoom_max + 1):
            x_min, y_min = deg2num(lon_min, lat_min, z)
            x_max, y_max = deg2num(lon_max, lat_max, z)
            x_min, x_max = sorted((x_min, x_max))
            y_min, y_max = sorted((y_min, y_max))
            for x, y, w, h in cls.tessellate(x_min, x_max + 1, y_min, y_max + 1, flavour.config.tile_group_width):
                yield cls(
                    flavour=flavour,
                    recipe=recipe,
                    input_files=input_files,
                    instant=instant,
                    z=z,
                    x=x,
                    y=y,
                    w=w,
                    h=h,
                )

    @classmethod
    def tessellate(
        cls, x_min: int, x_max: int, y_min: int, y_max: int, max_side: int
    ) -> Generator[Tuple[int, int, int, int], None, None]:
        """
        Generate a sequence of (x, y, width, height) rectangles covering the
        given surface. Each rectangle's area will not exceed max_side**2, and
        the tiling will try to make square tiles
        """
        # print("Tessellate", x_min, x_max, y_min, y_max, max_side)
        width = x_max - x_min
        height = y_max - y_min
        if width == 0 or height == 0:
            # print("      stop", width, height)
            return

        # Carve a horizontal stripe as large as we can go
        tile_height = min(height, max_side)
        tile_width = min(width, max_side * max_side // tile_height)
        # print("     tw th", tile_width, tile_height, "iterate", width, "step=", tile_width)
        for x in range(0, width, tile_width):
            # print("       gen", x_min + x, y_min, min(tile_width, x_max - x_min - x), tile_height)
            yield x_min + x, y_min, min(tile_width, x_max - x_min - x), tile_height

        y_min += tile_height
        if y_min == y_max:
            # print("     done!")
            return
        # print("   recurse", x_min, x_max, y_min, y_max, max_side)
        yield from cls.tessellate(x_min, x_max, y_min, y_max, max_side)


class LegendOrder(Order):
    def __init__(
        self,
        *,
        flavour: "Flavour",
        recipe: "Recipe",
        input_files: Dict[str, "inputs.InputFile"],
        instant: "inputs.Instant",
        order_steps: list["steps.Step"],
    ):
        super().__init__(flavour=flavour, recipe=recipe, input_files=input_files, instant=instant)
        self.order_steps.extend(order_steps)

    def __str__(self):
        return f"{os.path.basename(self.recipe.name)}{self.instant.step_suffix()}/legend"

    def __repr__(self):
        return f"{self.__class__.__name__}({str(self)})"

    def print_python_function(self, function_name: str, gen: PyGen):
        """
        Print a function that renders this order
        """
        # Destination directory inside the output
        relpath = f"{self.instant.reftime:%Y-%m-%dT%H:%M:%S}/"
        # Destination file name (without path or .png extension)
        basename = f"{self.recipe.name}_{self.flavour.name}+legend"
        gen.magics_renderer(function_name, self, relpath, basename)
