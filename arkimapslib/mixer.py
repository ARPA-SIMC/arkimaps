# from __future__ import annotations
from typing import Dict, Any, Optional, Type, List
import os
from .utils import ClassRegistry

# if TYPE_CHECKING:
#     from .recipes import Order
from .recipes import Recipe, Order
from .pantry import Pantry
from .inputs import InputFile
# Used for kwargs-style dicts
Kwargs = Dict[str, Any]


class Mixers(ClassRegistry["Mixer"]):
    """
    Registry of available Mixer implementations
    """
    registry: Dict[str, Type["Mixer"]] = {}

    @classmethod
    def for_order(cls, workdir: str, order: Order) -> "Mixer":
        try:
            mixer_cls = cls.by_name(order.mixer)
        except KeyError as e:
            raise KeyError(f"order requires unknown mixer {order.mixer}") from e
        return mixer_cls(workdir, order)

    @classmethod
    def make_orders(cls, recipe: Recipe, pantry: Pantry) -> List[Order]:
        """
        Scan a recipe and return a set with all the inputs it needs
        """
        mixer_cls = cls.by_name(recipe.mixer)
        return mixer_cls.make_orders(recipe, pantry)

    @classmethod
    def list_inputs(cls, recipe: Recipe) -> List[str]:
        """
        List the names of inputs used by a recipe
        """
        mixer_cls = cls.by_name(recipe.mixer)
        return mixer_cls.list_inputs(recipe)


@Mixers.register
class Mixer:
    NAME = "default"

    def __init__(self, workdir: str, order: Order):
        # Do not import Magics at toplevel to prevent accidentally importing it
        # in the main process. We only import Magics in working processes to
        # mitigate memory leaks
        from Magics import macro
        self.macro = macro
        self.output_pathname = os.path.join(workdir, order.basename)
        # Settings of the PNG output
        self.output = self.macro.output(
            output_formats=['png'],
            output_name=self.output_pathname,
            output_name_first_page_number="off",
        )
        # Loaded GRIB data
        self.gribs: Kwargs = {}
        # Order with the steps to execute
        self.order = order
        # Elements passed after output to macro.plot
        self.parts = []
        # Python script to reproduce this product
        self.py_lines = ["import os"]
        for name in ("MAGICS_STYLE_PATH", "MAGPLUS_QUIET"):
            if name in os.environ:
                self.py_lines.append(f"os.environ[{name!r}] = {os.environ[name]!r}")
        self.py_lines += [
            f"from Magics import macro",
            f"output = macro.output(output_formats=['png'], output_name={self.output_pathname!r},"
            f" output_name_first_page_number='off')",
            f"parts = []",
        ]

    @classmethod
    def list_inputs(cls, recipe: Recipe) -> List[str]:
        """
        List inputs used by this recipe.

        Inputs are listed in usage order, without duplicates
        """
        input_names = []

        # Collect the inputs needed for all steps
        for step_name, args in recipe.steps:
            if step_name == "add_grib":
                input_name = args["name"]
                if input_name in input_names:
                    continue
                input_names.append(input_name)

        return input_names

    @classmethod
    def make_orders(cls, recipe: Recipe, pantry: Pantry) -> List[Order]:
        inputs: Optional[Dict[str, Dict[str, InputFile]]] = None
        input_names = set()

        # Collect the inputs needed for all steps
        for step_name, args in recipe.steps:
            if step_name == "add_grib":
                input_name = args["name"]
                if input_name in input_names:
                    continue
                input_names.add(input_name)

                # Find available steps for this input
                steps = pantry.get_steps(input_name)

                # add_grib needs this input for all steps
                if inputs is None:
                    inputs = {}
                    for step, ifile in steps.items():
                        inputs[step] = {input_name: ifile}
                else:
                    steps_to_delete = []
                    for step, input_files in inputs.items():
                        if step not in steps:
                            # We miss an input for this step, so we cannot
                            # generate an order for it
                            steps_to_delete.append(step)
                        else:
                            input_files[input_name] = steps[step]
                    for step in steps_to_delete:
                        del inputs[step]

        res = []
        for step, input_files in inputs.items():
            res.append(Order(
                mixer=recipe.mixer,
                sources=input_files,
                recipe=recipe.name,
                step=step,
                steps=recipe.steps,
            ))

        return res

    def add_basemap(self, params: Kwargs):
        """
        Add a base map
        """
        self.parts.append(self.macro.mmap(**params))
        self.py_lines.append(f"parts.append(macro.mmap(**{params!r}))")

    def add_coastlines_bg(self):
        """
        Add background coastlines
        """
        self.parts.append(self.macro.mcoast(map_coastline_general_style="background"))
        self.py_lines.append(f"parts.append(macro.mcoast(map_coastline_general_style='background'))")

    def add_coastlines_fg(self):
        """
        Add foreground coastlines
        """
        self.parts.append(self.macro.mcoast(map_coastline_general_style="foreground"))
        args = {
            "map_coastline_sea_shade_colour": "#f2f2f2",
            "map_grid": "off",
            "map_coastline_sea_shade": "off",
            "map_label": "off",
            "map_coastline_colour": "#000000",
            "map_coastline_resolution": "medium",
        }
        self.parts.append(self.macro.mcoast(**args))
        self.py_lines.append(f"parts.append(macro.mcoast(map_coastline_general_style='foreground'))")
        self.py_lines.append(f"parts.append(macro.mcoast(**{args!r}))")

    def add_grib(self, name: str, params: Optional[Kwargs] = None):
        """
        Add a grib file
        """
        input_file = self.order.sources[name]
        source_input = input_file.info

        kwargs = {}
        if source_input.mgrib:
            kwargs.update(source_input.mgrib)
        if params is not None:
            kwargs.update(params)

        self.order.log.info("add_grib mgrib %r", kwargs)

        grib = self.macro.mgrib(grib_input_file_name=input_file.pathname, **kwargs)
        self.gribs[name] = grib
        self.parts.append(grib)
        self.py_lines.append(f"parts.append(macro.mgrib(grib_input_file_name={input_file.pathname!r}, **{kwargs!r}))")

    def add_contour(self, params: Optional[Kwargs] = None):
        """
        Add contouring of the previous data
        """
        if params is None:
            params = {"contour_automatic_setting": "ecmwf"}
        self.parts.append(
            self.macro.mcont(**params)
        )
        self.py_lines.append(f"parts.append(macro.mcont(**{params!r}))")

    def add_grid(self):
        """
        Add a coordinates grid
        """
        self.parts.append(
            self.macro.mcoast(map_coastline_general_style="grid"),
        )
        self.py_lines.append(f"parts.append(macro.mcoast(map_coastline_general_style='grid'))")

    def add_boundaries(self, params: Optional[Kwargs] = None):
        """
        Add a coordinates grid
        """
        self.parts.append(
            self.macro.mcoast(map_coastline_general_style="boundaries"),
        )
        self.py_lines.append(f"parts.append(macro.mcoast(map_coastline_general_style='boundaries'))")
        args = {
            'map_boundaries': "on",
            'map_boundaries_colour': "#504040",
            'map_administrative_boundaries_countries_list': ["ITA"],
            'map_administrative_boundaries_colour': "#504040",
            'map_administrative_boundaries_style': "solid",
            'map_administrative_boundaries': "on",
        }
        self.parts.append(self.macro.mcoast(**args))
        self.py_lines.append(f"parts.append(macro.mcoast(**{args!r}))")
        # FIX: group all mcoasts?
        if params is not None:
            self.parts.append(self.macro.mcoast(**params))
            self.py_lines.append(f"parts.append(macro.mcoast(**{params!r}))")

    def add_symbols(self):
        """
        Add symbols settings
        """
        self.parts.append(self.macro.msymb(
            symbol_type="marker",
            symbol_marker_index=15,
            legend="off",
            symbol_colour="black",
            symbol_height=0.28,
        ))

    def add_geopoints(self, params: Optional[Kwargs] = None):
        """
        Add geopoint file
        """
        if params is not None:
            self.parts.append(self.macro.mgeo(**params))

    def serve(self):
        """
        Render the file and store the output file name into the order
        """
        self.py_lines.append(f"macro.plot(output, *parts)")

        code = "\n".join(self.py_lines)
        try:
            from yapf.yapflib import yapf_api
            code, changed = yapf_api.FormatCode(code)
        except ModuleNotFoundError:
            pass
        with open(self.output_pathname + ".py", "wt") as fd:
            print(code, file=fd)

        self.macro.plot(
            self.output,
            *self.parts,
        )
        self.order.output = self.output_pathname + ".png"
