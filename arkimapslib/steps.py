# from __future__ import annotations
from typing import Dict, Any, Optional, Set, TextIO
import inspect
import json

# if TYPE_CHECKING:
from . import mixers
# Used for kwargs-style dicts
Kwargs = Dict[str, Any]


class Step:
    """
    One recipe step provided by a Mixer
    """
    default_params: Optional[Kwargs] = None

    def __init__(self, step: str, params: Optional[Kwargs] = None):
        self.name = step
        self.params = params

    def get_params(self, mixer: "mixers.Mixer"):
        if self.params:
            return self.params

        flavour_config = mixer.order.flavour.step_config(self.name)
        flavour_params = flavour_config.get_params()
        if flavour_params is not None:
            return flavour_params

        if self.default_params:
            return self.default_params

        return {}

    def run(self, mixer: "mixers.Mixer"):
        raise NotImplementedError(f"{self.__class__.__name__}.run not implemented")

    def get_input_names(self) -> Set[str]:
        """
        Return the list of input names used by this step
        """
        return set()

    def document(self, file: TextIO):
        print(inspect.getdoc(self), file=file)
        print(file=file)
        if self.params:
            print("With arguments:", file=file)
            print("```", file=file)
            # FIXME: dump as yaml?
            print(json.dumps(self.params, indent=2), file=file)
            print("```", file=file)


class MagicsMacro(Step):
    """
    Run a Magics macro with optional default arguments
    """
    macro_name: str

    def run(self, mixer: "mixers.Mixer"):
        params = self.get_params(mixer)
        mixer.parts.append(getattr(mixer.macro, self.macro_name)(**params))
        mixer.py_lines.append(f"parts.append(macro.{self.macro_name}(**{params!r}))")
        if mixer.order.debug_trace is not None:
            mixer.order.debug_trace.append((self.name, params))


class AddBasemap(MagicsMacro):
    """
    Add a base map
    """
    macro_name = "mmap"


class AddCoastlinesBg(MagicsMacro):
    """
    Add background coastlines
    """
    macro_name = "mcoast"
    default_params = {
        "map_coastline_general_style": "background",
    }


class AddSymbols(MagicsMacro):
    """
    Add symbols settings
    """
    macro_name = "msymb"
    default_params = {
        "symbol_type": "marker",
        "symbol_marker_index": 15,
        "legend": "off",
        "symbol_colour": "black",
        "symbol_height": 0.28,
    }


class AddContour(MagicsMacro):
    """
    Add contouring of the previous data
    """
    macro_name = "mcont"
    default_params = {
        "contour_automatic_setting": "ecmwf",
    }


class AddGrid(MagicsMacro):
    """
    Add a coordinates grid
    """
    macro_name = "mcoast"
    default_params = {
        "map_coastline_general_style": "grid",
    }


class AddCoastlinesFg(Step):
    """
    Add foreground coastlines
    """
    default_params = {
        "map_coastline_sea_shade_colour": "#f2f2f2",
        "map_grid": "off",
        "map_coastline_sea_shade": "off",
        "map_label": "off",
        "map_coastline_colour": "#000000",
        "map_coastline_resolution": "medium",
    }

    def run(self, mixer: "mixers.Mixer"):
        params = self.get_params(mixer)

        mixer.parts.append(mixer.macro.mcoast(map_coastline_general_style="foreground"))
        mixer.py_lines.append(f"parts.append(macro.mcoast(map_coastline_general_style='foreground'))")

        mixer.parts.append(mixer.macro.mcoast(**params))
        mixer.py_lines.append(f"parts.append(macro.mcoast(**{params!r}))")

        if mixer.order.debug_trace is not None:
            mixer.order.debug_trace.append((self.name, params))


class AddBoundaries(Step):
    """
    Add political boundaries
    """
    default_params = {
        'map_boundaries': "on",
        'map_boundaries_colour': "#504040",
        'map_administrative_boundaries_countries_list': ["ITA"],
        'map_administrative_boundaries_colour': "#504040",
        'map_administrative_boundaries_style': "solid",
        'map_administrative_boundaries': "on",
    }

    def run(self, mixer: "mixers.Mixer"):
        params = self.get_params(mixer)

        mixer.parts.append(
            mixer.macro.mcoast(map_coastline_general_style="boundaries"),
        )
        mixer.py_lines.append(f"parts.append(macro.mcoast(map_coastline_general_style='boundaries'))")

        mixer.parts.append(mixer.macro.mcoast(**params))
        mixer.py_lines.append(f"parts.append(macro.mcoast(**{params!r}))")

        if mixer.order.debug_trace is not None:
            mixer.order.debug_trace.append((self.name, params))


class AddGrib(Step):
    """
    Add a grib file
    """
    def __init__(self, name: str, **kwargs):
        super().__init__(**kwargs)
        self.grib_name = name

    def run(self, mixer: "mixers.Mixer"):
        input_file = mixer.order.sources[self.grib_name]
        source_input = input_file.info

        params = {}
        if source_input.mgrib:
            params.update(source_input.mgrib)
        params.update(self.get_params(mixer))

        mixer.order.log.debug("add_grib mgrib %r", params)

        grib = mixer.macro.mgrib(grib_input_file_name=input_file.pathname, **params)
        mixer.parts.append(grib)
        mixer.py_lines.append(f"parts.append(macro.mgrib(grib_input_file_name={input_file.pathname!r}, **{params!r}))")

        if mixer.order.debug_trace is not None:
            mixer.order.debug_trace.append((self.name, params))

    def get_input_names(self) -> Set[str]:
        res = super().get_input_names()
        res.add(self.grib_name)
        return res


class AddUserBoundaries(Step):
    """
    Add user-defined boundaries from a shapefile
    """
    def __init__(self, shape: str, **kwargs):
        super().__init__(**kwargs)
        self.shape = shape

    def run(self, mixer: "mixers.Mixer"):
        input_file = mixer.order.sources[self.shape]

        params = {
            "map_user_layer": "on",
            "map_user_layer_colour": "blue",
        }
        params.update(self.get_params(mixer))

        params["map_user_layer_name"] = input_file.pathname

        mixer.parts.append(mixer.macro.mcoast(**params))
        mixer.py_lines.append(f"parts.append(macro.mcoast(**{params!r}))")

        if mixer.order.debug_trace is not None:
            mixer.order.debug_trace.append((self.name, params))

    def get_input_names(self) -> Set[str]:
        res = super().get_input_names()
        res.add(self.shape)
        return res


class AddGeopoints(Step):
    """
    Add geopoints
    """
    def __init__(self, points: str, **kwargs):
        super().__init__(**kwargs)
        self.points = points

    def run(self, mixer: "mixers.Mixer"):
        input_file = mixer.order.sources[self.points]

        params = dict(self.get_params(mixer))
        params["geo_input_file_name"] = input_file.pathname

        mixer.parts.append(mixer.macro.mgeo(**params))
        mixer.py_lines.append(f"parts.append(macro.mgeo(**{params!r}))")

        if mixer.order.debug_trace is not None:
            mixer.order.debug_trace.append((self.name, params))

    def get_input_names(self) -> Set[str]:
        res = super().get_input_names()
        res.add(self.points)
        return res
