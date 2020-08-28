from __future__ import annotations
from typing import TYPE_CHECKING, Dict, Any

if TYPE_CHECKING:
    from .recipes import Order


class Chef:
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
        self.gribs: Dict[str, Any] = {}
        # Order with the steps to execute
        self.order = order
        # Elements passed after output to macro.plot
        self.parts = []

    def add_basemap(self, params: Dict[str, Any]):
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
            map_coastline_sea_shade="on",
            map_label="off",
            map_coastline_colour="#f2f2f2",
            map_coastline_resolution="medium",
        ))

    def add_grib(self, name: str):
        """
        Add a grib file
        """
        fname = self.order.sources[name]
        grib = self.macro.mgrib(grib_input_file_name=fname)
        self.gribs[name] = grib
        self.parts.append(grib)

    def add_contour(self):
        """
        Add contouring of the previous data
        """
        self.parts.append(
            self.macro.mcont(
                contour_automatic_setting="ecmwf",
            )
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
