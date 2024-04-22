# from __future__ import annotations
from abc import ABC
from typing import Dict, Any, List, Optional, Set, Tuple, TYPE_CHECKING

from .models import BaseDataModel, pydantic

if TYPE_CHECKING:
    from . import inputs
    from .lint import Lint

# Used for kwargs-style dicts
Kwargs = Dict[str, Any]


class StepSpec(BaseDataModel):
    """
    Data model for Steps
    """


class Step(ABC):
    """
    One recipe step provided by a Mixer
    """

    Spec = StepSpec

    DEFAULTS: Optional[Dict[str, Any]] = None

    def __init__(self, *, name: str, args: Dict[str, Any], sources: Dict[str, "inputs.InputFile"]):
        self.name = name
        self.spec = self.Spec(**args)

    @classmethod
    def lint(cls, lint: "Lint", *, defined_in: str, name: str, step: str, args: Dict[str, Any]) -> Optional[StepSpec]:
        """
        Consistency check the given input arguments
        """
        try:
            return cls.Spec(**args)
        except pydantic.ValidationError as e:
            for line in str(e).splitlines():
                lint.warn_recipe(f"{step}: {line}", defined_in=defined_in, name=name)
            return None

    def as_magics_macro(self) -> Tuple[str, Dict[str, Any]]:
        """
        Return the name and arguments for a Magics macro that renders this step
        """
        raise NotImplementedError(f"{self.__class__.__name__}.as_magics_macro not implemented")

    @classmethod
    def apply_change(cls, data: Dict[str, Any], change: Dict[str, Any]):
        """
        Apply the given changeset to data.

        This is using when instantiating derived recipes
        """
        for name, value in change.items():
            if name == "params":
                old_params = data.get("params")
                if old_params is None:
                    old_params = {}
                    data["params"] = {}
                for k, v in value.items():
                    if v is None:
                        old_params.pop(k, None)
                    else:
                        old_params[k] = v
            else:
                data[name] = value

    @classmethod
    def get_input_names(cls, args: Dict[str, Any]) -> Set[str]:
        """
        Return the list of input names used by this step
        """
        return set()


class BaseMagicsParamsSpec(BaseDataModel):
    """
    Data model for MagicsMacro params
    """


class MagicsMacroSpec(BaseDataModel):
    """
    Data model for MagicsMacro Steps
    """

    params: BaseMagicsParamsSpec = pydantic.Field(default_factory=BaseMagicsParamsSpec)


class MagicsMacro(Step, ABC):
    """
    Run a Magics macro with optional default arguments
    """

    MACRO_NAME: str
    Step = MagicsMacroSpec

    def as_magics_macro(self) -> Tuple[str, Dict[str, Any]]:
        return self.MACRO_NAME, self.spec.params.dict(exclude_unset=True)


class LegendParamsSpec(BaseMagicsParamsSpec):
    legend: str = "off"
    legend_text_colour: str = "blue"
    legend_title: str = "off"
    legend_title_text: str = "legend"
    legend_title_orientation: str = "vertical"
    legend_title_font_size: float = -1
    legend_title_font_colour: str = "automatic"
    legend_title_position: str = "automatic"
    legend_title_position_ratio: float = 25
    legend_units_text: str = ""
    legend_user_minimum: str = "off"
    legend_user_minimum_text: str = ""
    legend_user_maximum: str = "off"
    legend_user_maximum_text: str = ""
    legend_display_type: str = "disjoint"
    legend_label_frequency: int = 1
    legend_histogram_border: str = "on"
    legend_histogram_border_colour: str = "black"
    legend_histogram_mean_value: str = "off"
    legend_histogram_mean_value_marker: int = 15
    legend_histogram_mean_value_marker_colour: str = "black"
    legend_histogram_mean_value_marker_size: float = 0.5
    legend_histogram_max_value: str = "on"
    legend_histogram_grid_colour: str = "black"
    legend_histogram_grid_line_style: str = "solid"
    legend_histogram_grid_thickness: float = 1
    legend_text_format: str = "(automatic)"
    legend_box_mode: str = "automatic"
    legend_automatic_position: str = "top"
    legend_text_font: str = "sansserif"
    legend_text_font_style: str = "normal"
    legend_text_font_size: float = 0.3
    legend_text_orientation: int = 0
    legend_user_lines: List[str] = pydantic.Field(default_factory=list)
    legend_column_count: int = 1
    legend_entry_plot_direction: str = "automatic"
    legend_entry_plot_orientation: str = "bottom_top"
    legend_text_composition: str = "automatic_text_only"
    legend_values_list: List[float] = pydantic.Field(default_factory=list)
    legend_symbol_height_factor: float = 1
    legend_box_x_position: float = -1
    legend_box_y_position: float = -1
    legend_box_x_length: float = -1
    legend_box_y_length: float = 0
    legend_box_blanking: str = "off"
    legend_border: str = "off"
    legend_border_line_style: str = "solid"
    legend_border_colour: str = "blue"
    legend_border_thickness: float = 1
    legend_entry_text_width: float = 60
    legend_entry_border: str = "on"
    legend_entry_border_colour: str = "black"


class AddBasemapParamsSpec(BaseMagicsParamsSpec):
    subpage_x_position: float = -1
    subpage_y_position: float = -1
    subpage_x_length: float = -1
    subpage_y_length: float = -1
    subpage_map_library_area: str = "off"
    subpage_map_area_name: str = "off"
    subpage_map_projection: str = "cylindrical"
    subpage_lower_left_latitude: float = -90.0
    subpage_lower_left_longitude: float = -180.0
    subpage_upper_right_latitude: float = 90.0
    subpage_upper_right_longitude: float = 180.0
    subpage_map_area_definition_polar: str = "corners"
    subpage_map_hemisphere: str = "north"
    subpage_map_vertical_longitude: float = 0.0
    subpage_map_centre_latitude: float = 90.0
    subpage_map_centre_longitude: float = 0.0
    subpage_map_scale: float = 50.0e6
    subpage_x_axis_type: str = "regular"
    subpage_y_axis_type: str = "regular"
    subpage_clipping: str = "off"
    subpage_background_colour: str = "white"
    subpage_frame: str = "on"
    subpage_frame_colour: str = "charcoal"
    subpage_frame_line_style: str = "solid"
    subpage_frame_thickness: float = 2
    subpage_vertical_axis_width: float = 1
    subpage_horizontal_axis_height: float = 0.5
    subpage_align_horizontal: str = "left"
    subpage_align_vertical: str = "bottom"


class AddBasemapSpec(MagicsMacroSpec):
    params: AddBasemapParamsSpec = pydantic.Field(default_factory=AddBasemapParamsSpec)


class AddBasemap(MagicsMacro):
    """
    Add a base map
    """

    MACRO_NAME = "mmap"
    Spec = AddBasemapSpec


class McoastParamsSpec(BaseMagicsParamsSpec):
    map_coastline_general_style: str = ""
    map_coastline: str = "on"
    map_coastline_resolution: str = "automatic"
    map_coastline_land_shade: str = "off"
    map_coastline_land_shade_colour: str = "green"
    map_coastline_sea_shade: str = "off"
    map_coastline_sea_shade_colour: str = "blue"
    map_boundaries: str = "off"
    map_boundaries_style: str = "solid"
    map_boundaries_colour: str = "grey"
    map_boundaries_thickness: int = 1
    map_disputed_boundaries: str = "on"
    map_disputed_boundaries_style: str = "dash"
    map_disputed_boundaries_colour: str = "automatic"
    map_disputed_boundaries_thickness: int = 1
    map_administrative_boundaries: str = "off"
    map_administrative_boundaries_countries_list: List[str] = pydantic.Field(default_factory=list)
    map_administrative_boundaries_style: str = "dash"
    map_administrative_boundaries_colour: str = "automatic"
    map_administrative_boundaries_thickness: int = 1
    map_cities: str = "off"
    map_cities_unit_system: str = "percent"
    map_cities_font: str = "sansserif"
    map_cities_font_style: str = "normal"
    map_cities_text_blanking: str = "on"
    map_cities_font_size: float = 2.5
    map_cities_font_colour: str = "navy"
    map_cities_name_position: str = "above"
    map_cities_marker: str = "plus"
    map_cities_marker_height: float = 0.7
    map_cities_marker_colour: str = "evergreen"
    map_rivers: str = "off"
    map_rivers_style: str = "solid"
    map_rivers_colour: str = "blue"
    map_rivers_thickness: int = 1
    # ...
    map_coastline_colour: str = "black"
    map_coastline_style: str = "solid"
    map_coastline_thickness: int = 1
    map_grid: str = "on"
    map_grid_latitude_reference: float = 0.0
    map_grid_latitude_increment: float = 10.0
    map_grid_longitude_reference: float = 0.0
    map_grid_longitude_increment: float = 20.0
    map_grid_line_style: str = "solid"
    map_grid_thickness: int = 1
    map_grid_colour: str = "black"
    map_grid_frame: str = "off"
    map_grid_frame_line_style: str = "solid"
    map_grid_frame_thickness: int = 1
    map_grid_frame_colour: str = "black"
    map_label: str = "on"
    map_label_font: str = "sansserif"
    map_label_font_style: str = "normal"
    map_label_colour: str = "black"
    map_label_height: float = 0.25
    map_label_blanking: str = "on"
    map_label_latitude_frequency: float = 1.0
    map_label_longitude_frequency: float = 1.0
    map_label_left: str = "on"
    map_label_right: str = "on"
    map_label_top: str = "on"
    map_label_bottom: str = "on"


class AddCoastlinesBgSpec(MagicsMacroSpec):
    params: McoastParamsSpec = pydantic.Field(default_factory=McoastParamsSpec)


class AddCoastlinesBg(MagicsMacro):
    """
    Add background coastlines
    """

    Spec = AddCoastlinesBgSpec

    MACRO_NAME = "mcoast"
    DEFAULTS = {
        "params": {
            "map_coastline_general_style": "background",
            "map_coastline_resolution": "high",
        },
    }


class AddSymbolsParamsSpec(LegendParamsSpec):
    symbol_type: str = "marker"
    symbol_marker_index: int = 15
    symbol_colour: str = "black"
    symbol_height: float = 0.28


class AddSymbolsSpec(MagicsMacroSpec):
    params: AddSymbolsParamsSpec = pydantic.Field(default_factory=AddSymbolsParamsSpec)


class AddSymbols(MagicsMacro):
    """
    Add symbols settings
    """

    Spec = AddSymbolsSpec

    MACRO_NAME = "msymb"
    DEFAULTS = {
        "params": {
            "symbol_type": "marker",
            "symbol_marker_index": 15,
            "legend": "off",
            "symbol_colour": "black",
            "symbol_height": 0.28,
        },
    }


class AddContourParamsSpec(LegendParamsSpec):
    contour: str = "on"
    contour_line_style: str = "solid"
    contour_line_thickness: float = 1.0
    contour_line_colour_rainbow: str = "off"
    contour_line_colour: str = "blue"
    contour_line_colour_rainbow_method: str = "calculate"
    contour_line_colour_rainbow_max_level_colour: str = "blue"
    contour_line_colour_rainbow_min_level_colour: str = "red"
    contour_line_colour_rainbow_direction: str = "anti_clockwise"
    contour_line_colour_rainbow_colour_list: List[str] = pydantic.Field(default_factory=list)
    contour_line_colour_rainbow_colour_list_policy: str = "lastone"
    contour_line_thickness_rainbow_list: List[str] = pydantic.Field(default_factory=list)
    contour_line_thickness_rainbow_list_policy: str = "lastone"
    contour_line_style_rainbow_list: List[str] = pydantic.Field(default_factory=list)
    contour_line_style_rainbow_list_policy: str = "lastone"
    contour_highlight: str = "on"
    contour_highlight_style: str = "solid"
    contour_reference_level: float = 0.0
    contour_highlight_colour: str = "blue"
    contour_highlight_thickness: float = 3
    contour_highlight_frequency: float = 4
    contour_level_selection_type: str = "count"
    contour_max_level: float = 1.0e21
    contour_min_level: float = -1.0e21
    contour_shade_max_level: float = 1.0e21
    contour_shade_min_level: float = -1.0e21
    contour_level_count: int = 10
    contour_level_tolerance: int = 2
    contour_interval: float = 8.0
    contour_level_list: List[float] = pydantic.Field(default_factory=list)
    contour_label: str = "on"
    contour_label_type: str = "number"
    contour_label_text: str = ""
    contour_label_height: float = 0.3
    contour_label_format: str = "(automatic)"
    contour_label_blanking: str = "on"
    contour_label_quality: str = "log"
    contour_label_font: str = "sansserif"
    contour_label_font_style: str = "normal"
    contour_label_colour: str = "contour_line_colour"
    contour_label_frequency: int = 2
    contour_shade: str = "off"
    contour_shade_technique: str = "polygon_shading"
    contour_shade_method: str = "dot"
    contour_shade_dot_size: float = 0.02
    contour_shade_max_level_density: float = 50.0
    contour_shade_min_level_density: float = 1.0
    contour_shade_hatch_index: int = 0
    contour_shade_hatch_thickness: int = 1
    contour_shade_hatch_density: float = 18.0
    contour_grid_shading_position: str = "middle"
    contour_shade_cell_resolution: int = 10
    contour_shade_cell_method: str = "nearest"
    contour_shade_cell_resolution_method: str = "classic"
    contour_shade_colour_table: List[str] = pydantic.Field(default_factory=list)
    contour_shade_height_table: List[str] = pydantic.Field(default_factory=list)
    contour_shade_marker_table_type: str = "index"
    contour_shade_marker_table: List[str] = pydantic.Field(default_factory=list)
    contour_shade_marker_name_table: List[str] = pydantic.Field(default_factory=list)
    contour_shade_colour_method: str = "calculate"
    contour_shade_max_level_colour: str = "blue"
    contour_shade_min_level_colour: str = "red"
    contour_shade_colour_direction: str = "anti_clockwise"
    contour_shade_colour_list: List[str] = pydantic.Field(default_factory=list)
    contour_shade_palette_name: str = ""
    contour_shade_palette_policy: str = "lastone"
    contour_legend_only: str = "off"
    contour_method: str = "automatic"
    contour_akima_x_resolution: float = 1.5
    contour_akima_y_resolution: float = 1.5
    # contour_interpolation_floor
    # contour_interpolation_ceiling
    contour_automatic_setting: str = "off"
    contour_hilo: str = "off"
    contour_hilo_type: str = "text"
    contour_hilo_height: float = 0.4
    contour_hilo_quality: str = "low"
    contour_hi_colour: str = "blue"
    contour_lo_colour: str = "blue"
    # ...

    @pydantic.root_validator
    def list_sync(cls, values):
        cll = values["contour_level_list"]
        cscl = values["contour_shade_colour_list"]
        if cll and cscl and len(cll) != len(cscl) + 1:
            raise ValueError(
                f"contour_level_list has {len(cll)} items while contour_shade_colour_list has {len(cscl)} items"
            )
        return values


class AddContourSpec(MagicsMacroSpec):
    params: AddContourParamsSpec = pydantic.Field(default_factory=AddContourParamsSpec)


class AddContour(MagicsMacro):
    """
    Add contouring of the previous data
    """

    Spec = AddContourSpec

    MACRO_NAME = "mcont"
    DEFAULTS = {
        "params": {
            "contour_automatic_setting": "ecmwf",
        },
    }


class AddWindParamsSpec(LegendParamsSpec):
    wind_field_type: str = "arrows"
    wind_legend_text: str = "vector"
    wind_advanced_method: str = "off"
    wind_advanced_colour_parameter: str = "speed"
    wind_advanced_colour_selection_type: str = "count"
    contour_max_level: float = 1.0e21
    contour_min_level: float = -1.0e21
    contour_shade_max_level: float = 1.0e21
    contour_shade_min_level: float = -1.0e21
    contour_level_count: int = 10
    contour_level_tolerance: int = 2
    contour_reference_level: float = 0.0
    contour_interval: float = 8.0
    contour_level_list: List[float] = pydantic.Field(default_factory=list)
    wind_advanced_colour_max_value: float = 1.0e21
    wind_advanced_colour_min_value: float = -1.0e21
    wind_advanced_colour_level_count: int = 10
    wind_advanced_colour_level_tolerance: int = 2
    wind_advanced_colour_reference_level: float = 0.0
    wind_advanced_colour_level_interval: float = 8.0
    wind_advanced_colour_level_list: List[float] = pydantic.Field(default_factory=list)
    wind_advanced_colour_table_colour_method: str = "calculate"
    contour_shade_max_level_colour: str = "blue"
    contour_shade_min_level_colour: str = "red"
    contour_shade_colour_direction: str = "anti_clockwise"
    wind_advanced_colour_max_level_colour: str = "blue"
    wind_advanced_colour_min_level_colour: str = "red"
    wind_advanced_colour_direction: str = "anti_clockwise"
    wind_advanced_colour_list: list[str] = pydantic.Field(default_factory=list)
    wind_advanced_colour_list_policy: str = "lastone"
    wind_flag_calm_indicator: str = "on"
    wind_flag_calm_indicator_size: float = 0.3
    wind_flag_calm_below: float = 0.5
    wind_flag_colour: str = "blue"
    wind_flag_length: float = 1.0
    wind_flag_max_speed: float = 1.0e21
    wind_flag_min_speed: float = -1.0e21
    wind_flag_mode: str = "normal"
    wind_flag_style: str = "solid"
    wind_flag_origin_marker: str = "circle"
    wind_flag_origin_marker_: float = 0.3
    wind_flag_thickness: int = 1
    wind_arrow_calm_indicator: str = "off"
    wind_arrow_calm_indicator_size: float = 0.3
    wind_arrow_calm_below: float = 0.5
    wind_arrow_colour: str = "blue"
    wind_arrow_cross_boundary: str = "on"
    wind_arrow_head_shape: int = 0
    wind_arrow_head_ratio: float = 0.3
    wind_arrow_max_speed: float = 1.0e21
    wind_arrow_min_speed: float = -1.0e21
    wind_arrow_origin_position: str = "tail"
    wind_arrow_thickness: int = 1
    wind_arrow_style: str = "solid"
    wind_arrow_unit_velocity: float = 25.0
    wind_arrow_legend_text: str = "m/s"
    wind_arrow_fixed_velocity: float = 0.0
    wind_thinning_factor: float = 2.0


class AddWindSpec(MagicsMacroSpec):
    params: AddWindParamsSpec = pydantic.Field(default_factory=AddWindParamsSpec)


class AddWind(MagicsMacro):
    """
    Add wind flag rendering of the previous data
    """

    MACRO_NAME = "mwind"
    Spec = AddWindSpec


class AddGridSpec(MagicsMacroSpec):
    params: McoastParamsSpec = pydantic.Field(default_factory=McoastParamsSpec)


class AddGrid(MagicsMacro):
    """
    Add a coordinates grid
    """

    Spec = AddGridSpec

    MACRO_NAME = "mcoast"
    DEFAULTS = {
        "params": {
            "map_coastline_general_style": "grid",
        },
    }


class AddCoastlinesFgSpec(MagicsMacroSpec):
    params: McoastParamsSpec = pydantic.Field(default_factory=McoastParamsSpec)


class AddCoastlinesFg(MagicsMacro):
    """
    Add foreground coastlines
    """

    Spec = AddCoastlinesFgSpec

    MACRO_NAME = "mcoast"
    DEFAULTS = {
        "params": {
            "map_coastline_sea_shade_colour": "#f2f2f2",
            "map_grid": "off",
            "map_coastline_sea_shade": "off",
            "map_label": "off",
            "map_coastline_colour": "#000000",
            "map_coastline_resolution": "high",
        },
    }


class AddBoundariesSpec(MagicsMacroSpec):
    params: McoastParamsSpec = pydantic.Field(default_factory=McoastParamsSpec)


class AddBoundaries(MagicsMacro):
    """
    Add political boundaries
    """

    Spec = AddBoundariesSpec

    MACRO_NAME = "mcoast"
    DEFAULTS = {
        "params": {
            "map_boundaries": "on",
            "map_boundaries_colour": "#504040",
            "map_administrative_boundaries_countries_list": ["ITA"],
            "map_administrative_boundaries_colour": "#504040",
            "map_administrative_boundaries_style": "solid",
            "map_administrative_boundaries": "on",
        },
    }


class AddGribParamsSpec(BaseMagicsParamsSpec):
    pass


class AddGribSpec(MagicsMacroSpec):
    params: AddGribParamsSpec = pydantic.Field(default_factory=AddGribParamsSpec)
    grib: str


class AddGrib(Step):
    """
    Add a grib file
    """

    Spec = AddGribSpec

    def __init__(self, step: str, params: Optional[Kwargs], sources: Dict[str, "inputs.InputFile"]):
        super().__init__(step, params, sources)
        inp = sources.get(self.spec.grib)
        if inp is None:
            raise KeyError(f"{self.name}: input {input_name} not found. Available: {', '.join(sources.keys())}")
        self.grib_input = inp

        for k, v in self.grib_input.info.spec.mgrib.items():
            setattr(self.spec.params, k, v)

    def as_magics_macro(self) -> Tuple[str, Dict[str, Any]]:
        params = self.spec.as_dict(exclude_unset=True)
        params["grib_input_file_name"] = str(self.grib_input.pathname)
        return "mgrib", params

    @classmethod
    def get_input_names(cls, args: Dict[str, Any]) -> Set[str]:
        res = super().get_input_names(args)
        spec = cls.Spec(**args)
        res.add(spec.grib)
        return res


class AddUserBoundariesParamsSpec(BaseMagicsParamsSpec):
    pass


class AddUserBoundariesSpec(MagicsMacroSpec):
    params: AddUserBoundariesParamsSpec = pydantic.Field(default_factory=AddUserBoundariesParamsSpec)
    shape: str


class AddUserBoundaries(Step):
    """
    Add user-defined boundaries from a shapefile
    """

    Spec = AddUserBoundariesSpec
    DEFAULTS = {
        "map_user_layer": "on",
        "map_user_layer_colour": "blue",
    }

    def __init__(self, *, name: str, args: Dict[str, Any], sources: Dict[str, "inputs.InputFile"]):
        super().__init__(name=name, args=args, sources=sources)
        inp = sources.get(self.spec.shape)
        if inp is None:
            raise KeyError(f"{self.name}: input {self.spec.name} not found. Available: {', '.join(sources.keys())}")
        self.shape = inp

    def _run_params(self):
        params = self.spec.params.dict(exclude_unset=True)
        params["map_user_layer_name"] = str(self.shape.pathname)
        return params

    def as_magics_macro(self) -> Tuple[str, Dict[str, Any]]:
        params = self._run_params()
        return "mcoast", params

    @classmethod
    def get_input_names(cls, args: Dict[str, Any]) -> Set[str]:
        res = super().get_input_names(args)
        spec = cls.Spec(**args)
        res.add(spec.shape)
        return res

    @classmethod
    def get_all_possible_input_names(cls, args: Kwargs) -> Set[str]:
        raise NotImplementedError()


class AddGeopointsParamsSpec(BaseMagicsParamsSpec):
    pass


class AddGeopointsSpec(MagicsMacroSpec):
    params: AddGeopointsParamsSpec
    params: AddGeopointsParamsSpec = pydantic.Field(default_factory=AddGeopointsParamsSpec)
    points: str


class AddGeopoints(Step):
    """
    Add geopoints
    """

    Spec = AddGeopointsSpec

    def __init__(self, *, name: str, args: Dict[str, Any], sources: Dict[str, "inputs.InputFile"]):
        super().__init__(name=name, args=args, sources=sources)
        inp = sources.get(self.spec.points)
        if inp is None:
            raise KeyError(f"{self.name}: input {self.spec.points} not found. Available: {', '.join(sources.keys())}")
        self.points = inp

    def as_magics_macro(self) -> Tuple[str, Dict[str, Any]]:
        params = self.spec.params.as_dict(exclude_unset=True)
        params["geo_input_file_name"] = str(self.points.pathname)
        return "mgeo", params

    @classmethod
    def get_input_names(cls, args: Dict[str, Any]) -> Set[str]:
        res = super().get_input_names(args)
        points = args.get("points")
        if points is not None:
            res.add(points)
        return res
