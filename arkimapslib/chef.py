from __future__ import annotations
from typing import TYPE_CHECKING, Dict, Any
from Magics import macro

if TYPE_CHECKING:
    from .recipes import Dish


class Chef:
    def __init__(self, dish: Dish):
        self.dish = dish

    def add_basemap(self, params: Dict[str, Any]):
        """
        Add a base map
        """
        self.dish.parts.append(macro.mmap(**params))

    def add_coastlines_bg(self):
        """
        Add background coastlines
        """
        self.dish.parts.append(macro.mcoast(map_coastline_general_style="background"))

    def add_coastlines_fg(self):
        """
        Add foreground coastlines
        """
        self.dish.parts.append(macro.mcoast(map_coastline_general_style="foreground"))
        self.dish.parts.append(macro.mcoast(
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
        fname = self.dish.sources[name]
        grib = macro.mgrib(grib_input_file_name=fname)
        self.dish.gribs[name] = grib
        self.dish.parts.append(grib)

    def add_contour(self):
        """
        Add contouring of the previous data
        """
        self.dish.parts.append(
            macro.mcont(
                contour_automatic_setting="ecmwf",
            )
        )

    def add_grid(self):
        """
        Add a coordinates grid
        """
        self.dish.parts.append(
            macro.mcoast(map_coastline_general_style="grid"),
        )

    def add_boundaries(self):
        """
        Add a coordinates grid
        """
        self.dish.parts.append(
            macro.mcoast(map_coastline_general_style="boundaries"),
        )

    def serve(self):
        macro.plot(
            self.dish.output,
            *self.dish.parts,
        )
