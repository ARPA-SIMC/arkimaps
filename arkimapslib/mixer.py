from __future__ import annotations
from typing import TYPE_CHECKING, Dict, Any, Type, Optional

if TYPE_CHECKING:
    from .recipes import Order

    # Used for kwargs-style dicts
    Kwargs = Dict[str, Any]


class Mixers:
    registry: Dict[str, Type["Mixer"]] = {}

    @classmethod
    def register(cls, mixer_cls: Type["Mixer"]):
        """
        Add a mixer class to the registry
        """
        name = getattr(mixer_cls, "NAME", None)
        if name is None:
            name = str(mixer_cls)

        cls.registry[name] = mixer_cls

    @classmethod
    def for_order(cls, order: Order) -> "Mixer":
        mixer_cls = cls.registry.get(order.mixer)
        if mixer_cls is None:
            raise KeyError(f"order requires unknown mixer {order.mixer}")
        return mixer_cls(order)


@Mixers.register
class Mixer:
    NAME = "default"

    def __init__(self, order: Order):
        # Do not import Magics at toplevel to prevent accidentally importing it
        # in the main process. We only import Magics in working processes to
        # mitigate memory leaks
        from Magics import macro
        self.macro = macro
        # Settings of the PNG output
        self.output = self.macro.output(
            output_formats=['png'],
            output_name=order.dest,
            output_name_first_page_number="off",
        )
        # Loaded GRIB data
        self.gribs: Kwargs = {}
        # Order with the steps to execute
        self.order = order
        # Elements passed after output to macro.plot
        self.parts = []

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

    def add_boundaries(self):
        """
        Add a coordinates grid
        """
        self.parts.append(
            self.macro.mcoast(map_coastline_general_style="boundaries"),
        )

    def serve(self):
        """
        Render the file and store the output file name into the order
        """
        self.macro.plot(
            self.output,
            *self.parts,
        )
        self.order.output = self.order.dest + ".png"