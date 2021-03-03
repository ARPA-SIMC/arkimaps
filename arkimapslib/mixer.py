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
        List inputs used by a recipe
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
                            input_files[input_name] = ifile
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

#    def make_orders(
#            self,
#            recipe: 'Recipe',
#            workdir: str,
#            output_steps: Optional[List[int]] = None) -> Iterator["Order"]:
#        """
#        Look at what input files are available for the given recipe, and
#        generate a sequence of orders for all steps for which there are enough
#        inputs to make the order
#        """
#        # List the data files in the pantry
#        input_dir = os.path.join(workdir, recipe.name)
#        inputs = Inputs(recipe, input_dir)
#
#        # Run preprocessors if needed
#        inputs.preprocess()
#
#        # Generate orders based on the data we found
#        count_generated = 0
#        for step, files in inputs.steps.items():
#            if output_steps is not None and step not in output_steps:
#                continue
#            sources = inputs.for_step(step)
#            if sources is None:
#                continue
#            basename = f"{recipe.name}+{step:03d}"
#            dest = os.path.join(workdir, basename)
#            count_generated += 1
#            yield Order(
#                mixer=recipe.mixer,
#                sources=sources,
#                dest=dest,
#                basename=basename,
#                recipe=recipe.name,
#                steps=recipe.steps,
#            )
#
#        log.info("%s: %d orders created", recipe.name, count_generated)

        return res

    def add_basemap(self, params: Kwargs):
        """
        Add a base map
        """
        self.parts.append(self.macro.mmap(**params))

    def add_coastlines_bg(self):
        """
        Add background coastlines
        """
        self.parts.append(self.macro.mcoast(map_coastline_general_style="background"))

    def add_coastlines_fg(self):
        """
        Add foreground coastlines
        """
        self.parts.append(self.macro.mcoast(map_coastline_general_style="foreground"))
        self.parts.append(self.macro.mcoast(
            map_coastline_sea_shade_colour="#f2f2f2",
            map_grid="off",
            map_coastline_sea_shade="off",
            map_label="off",
            map_coastline_colour="#000000",
            map_coastline_resolution="medium",
        ))

    def add_grib(self, name: str, params: Optional[Kwargs] = None):
        """
        Add a grib file
        """
        input_file = self.order.sources[name]
        source_input = input_file.info

        # TODO: if source_input has preprocessing steps, apply them here
        # source_input: Input
        # source_info["source"]: source file

        kwargs = {}
        if source_input.mgrib:
            kwargs.update(source_input.mgrib)
        if params is not None:
            kwargs.update(params)

        self.order.log.info("add_grib mgrib %r", kwargs)

        grib = self.macro.mgrib(grib_input_file_name=input_file.pathname, **kwargs)
        self.gribs[name] = grib
        self.parts.append(grib)

    def add_contour(self, params: Optional[Kwargs] = None):
        """
        Add contouring of the previous data
        """
        if params is None:
            params = {"contour_automatic_setting": "ecmwf"}
        self.parts.append(
            self.macro.mcont(**params)
        )

    def add_grid(self):
        """
        Add a coordinates grid
        """
        self.parts.append(
            self.macro.mcoast(map_coastline_general_style="grid"),
        )

    def add_boundaries(self, params: Optional[Kwargs] = None):
        """
        Add a coordinates grid
        """
        self.parts.append(
            self.macro.mcoast(map_coastline_general_style="boundaries"),
        )
        self.parts.append(self.macro.mcoast(
            map_boundaries="on",
            map_boundaries_colour="#504040",
            map_administrative_boundaries_countries_list=["ITA"],
            map_administrative_boundaries_colour="#504040",
            map_administrative_boundaries_style="solid",
            map_administrative_boundaries="on",
        ))
        # FIX: group all mcoasts?
        if params is not None:
            self.parts.append(self.macro.mcoast(**params))

    def serve(self):
        """
        Render the file and store the output file name into the order
        """
        self.macro.plot(
            self.output,
            *self.parts,
        )
        self.order.output = self.output_pathname + ".png"
