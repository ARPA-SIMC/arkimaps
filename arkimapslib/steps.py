# from __future__ import annotations
from typing import Dict, Any, Optional, Set, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from . import inputs
    from .lint import Lint

# Used for kwargs-style dicts
Kwargs = Dict[str, Any]


class StepSkipped(Exception):
    """
    Exception raised in Step constructor to signal that the step should be skipped
    """

    pass


class StepConfig:
    """
    Flavour configuration for a step
    """

    def __init__(self, name: str, options: Optional[Kwargs] = None, **kw):
        self.name = name
        self.options: Kwargs = options if options is not None else {}

    def get_param(self, name: str) -> Any:
        return self.options.get(name)


class Step:
    """
    One recipe step provided by a Mixer
    """

    defaults: Optional[Kwargs] = None

    def __init__(
        self, step: str, step_config: StepConfig, params: Optional[Kwargs], sources: Dict[str, "inputs.InputFile"]
    ):
        self.name = step
        self.params = self.compile_args(step_config, params if params is not None else {})
        if bool(self.params.get("skip")):
            raise StepSkipped()

    @classmethod
    def lint(cls, lint: "Lint", *, defined_in: str, name: str, step: str, **kwargs):
        """
        Consistency check the given input arguments
        """
        for k, v in kwargs.items():
            lint.warn_recipe_step(f"Unknown parameter: {k!r}", defined_in=defined_in, name=name, step=step)

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
    def compile_args(cls, step_config: StepConfig, args: Kwargs) -> Kwargs:
        """
        Compute the set of arguments for this step, based on flavour
        information and arguments defined in the recipe
        """
        # take args
        res = dict(args)

        # add missing bits from step_config
        for k, v in step_config.options.items():
            res.setdefault(k, v)

        # add missing bits from class config
        if cls.defaults is not None:
            for k, v in cls.defaults.items():
                res.setdefault(k, v)

        return res

    @classmethod
    def get_input_names(cls, step_config: StepConfig, args: Kwargs) -> Set[str]:
        """
        Return the list of input names used by this step
        """
        return set()


class MagicsMacro(Step):
    """
    Run a Magics macro with optional default arguments
    """

    macro_name: str

    @classmethod
    def lint(cls, lint: "Lint", **kwargs):
        kwargs.pop("params", None)
        super().lint(lint, **kwargs)

    def as_magics_macro(self) -> Tuple[str, Dict[str, Any]]:
        return self.macro_name, self.params.get("params", {})


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
    defaults = {
        "params": {
            "map_coastline_general_style": "background",
            "map_coastline_resolution": "high",
        },
    }


class AddSymbols(MagicsMacro):
    """
    Add symbols settings
    """

    macro_name = "msymb"
    defaults = {
        "params": {
            "symbol_type": "marker",
            "symbol_marker_index": 15,
            "legend": "off",
            "symbol_colour": "black",
            "symbol_height": 0.28,
        },
    }


class AddContour(MagicsMacro):
    """
    Add contouring of the previous data
    """

    macro_name = "mcont"
    defaults = {
        "params": {
            "contour_automatic_setting": "ecmwf",
        },
    }

    @classmethod
    def lint(cls, lint: "Lint", **kwargs):
        super().lint(lint, **kwargs)
        params = kwargs.get("params", None)
        if params is None:
            lint.warn_recipe_step("missing 'params'", **kwargs)
            return
        cll = params.get("contour_level_list")
        cscl = params.get("contour_shade_colour_list")
        if cll is not None and cscl is not None:
            ok = True
            if not isinstance(cll, list):
                lint.warn_recipe_step(f"contour_level_list {cll!r} is not a list", **kwargs)
                ok = False
            if not isinstance(cscl, list):
                lint.warn_recipe_step(f"contour_level_list {cll!r} is not a list", **kwargs)
                ok = False
            if ok:
                if len(cll) != len(cscl) + 1:
                    lint.warn_recipe_step(
                        f"contour_level_list has {len(cll)} items while"
                        f" contour_shade_colour_list has {len(cscl)} items",
                        **kwargs,
                    )


class AddWind(MagicsMacro):
    """
    Add wind flag rendering of the previous data
    """

    macro_name = "mwind"


class AddGrid(MagicsMacro):
    """
    Add a coordinates grid
    """

    macro_name = "mcoast"
    defaults = {
        "params": {
            "map_coastline_general_style": "grid",
        },
    }


class AddCoastlinesFg(MagicsMacro):
    """
    Add foreground coastlines
    """

    macro_name = "mcoast"
    defaults = {
        "params": {
            "map_coastline_sea_shade_colour": "#f2f2f2",
            "map_grid": "off",
            "map_coastline_sea_shade": "off",
            "map_label": "off",
            "map_coastline_colour": "#000000",
            "map_coastline_resolution": "high",
        },
    }


class AddBoundaries(MagicsMacro):
    """
    Add political boundaries
    """

    macro_name = "mcoast"
    defaults = {
        "params": {
            "map_boundaries": "on",
            "map_boundaries_colour": "#504040",
            "map_administrative_boundaries_countries_list": ["ITA"],
            "map_administrative_boundaries_colour": "#504040",
            "map_administrative_boundaries_style": "solid",
            "map_administrative_boundaries": "on",
        },
    }


class AddGrib(Step):
    """
    Add a grib file
    """

    def __init__(
        self, step: str, step_config: StepConfig, params: Optional[Kwargs], sources: Dict[str, "inputs.InputFile"]
    ):
        super().__init__(step, step_config, params, sources)
        input_name = self.params.get("grib")
        if input_name is None:
            raise KeyError(f"{self.name}: missing 'grib' key")
        if not isinstance(input_name, str):
            raise KeyError(f"{self.name}: 'grib' must be a string")
        inp = sources.get(input_name)
        if inp is None:
            raise KeyError(f"{self.name}: input {input_name} not found. Available: {', '.join(sources.keys())}")
        self.grib_input = inp

        if self.grib_input.info.spec.mgrib:
            params = self.params.get("params")
            if params is None:
                self.params["params"] = params = {}
            for k, v in self.grib_input.info.spec.mgrib.items():
                params.setdefault(k, v)

    @classmethod
    def lint(cls, lint: "Lint", **kwargs):
        kwargs.pop("params", None)

        grib = kwargs.pop("grib", None)
        if grib is None:
            lint.warn_recipe_step("missing 'grib'", **kwargs)
        if not isinstance(grib, str):
            lint.warn_recipe_step("'grib' must be a string", **kwargs)

        super().lint(lint, **kwargs)

    def as_magics_macro(self) -> Tuple[str, Dict[str, Any]]:
        params = dict(self.params.get("mgrib", {}))
        params.update(self.params.get("params", {}))
        params["grib_input_file_name"] = str(self.grib_input.pathname)
        return "mgrib", params

    @classmethod
    def get_input_names(cls, step_config: StepConfig, args: Kwargs) -> Set[str]:
        res = super().get_input_names(step_config, args)
        args = cls.compile_args(step_config, args)
        grib_name = args.get("grib")
        if grib_name is not None:
            res.add(grib_name)
        return res


class AddUserBoundaries(Step):
    """
    Add user-defined boundaries from a shapefile
    """

    def __init__(
        self, step: str, step_config: StepConfig, params: Optional[Kwargs], sources: Dict[str, "inputs.InputFile"]
    ):
        super().__init__(step, step_config, params, sources)
        input_name = self.params.get("shape")
        if input_name is None:
            raise KeyError(f"{self.name}: missing 'shape'")
        if not isinstance(input_name, str):
            raise KeyError(f"{self.name}: 'shape' must be a string")
        inp = sources.get(input_name)
        if inp is None:
            raise KeyError(f"{self.name}: input {input_name} not found. Available: {', '.join(sources.keys())}")
        self.shape = inp

    @classmethod
    def lint(cls, lint: "Lint", **kwargs):
        kwargs.pop("shape", None)
        # Shape may be defined by the flavour
        # if shape is None:
        #     lint.warn_recipe_step("missing 'shape'", **kwargs)
        # if not isinstance(shape, str):
        #     lint.warn_recipe_step("'shape' must be a string", **kwargs)
        super().lint(lint, **kwargs)

    def _run_params(self):
        params = {
            "map_user_layer": "on",
            "map_user_layer_colour": "blue",
        }
        params.update(self.params.get("params", {}))
        params["map_user_layer_name"] = str(self.shape.pathname)
        return params

    def as_magics_macro(self) -> Tuple[str, Dict[str, Any]]:
        params = self._run_params()
        return "mcoast", params

    @classmethod
    def get_input_names(cls, step_config: StepConfig, args: Kwargs) -> Set[str]:
        res = super().get_input_names(step_config, args)
        args = cls.compile_args(step_config, args)
        shape = args.get("shape")
        if shape is not None:
            res.add(shape)
        return res

    @classmethod
    def get_all_possible_input_names(cls, args: Kwargs) -> Set[str]:
        raise NotImplementedError()


class AddGeopoints(Step):
    """
    Add geopoints
    """

    def __init__(
        self, step: str, step_config: StepConfig, params: Optional[Kwargs], sources: Dict[str, "inputs.InputFile"]
    ):
        super().__init__(step, step_config, params, sources)
        input_name = self.params.get("points")
        if input_name is None:
            raise KeyError(f"{self.name}: missing 'points'")
        if not isinstance(input_name, str):
            raise KeyError(f"{self.name}: 'points' must be a string")
        inp = sources.get(input_name)
        if inp is None:
            raise KeyError(f"{self.name}: input {input_name} not found. Available: {', '.join(sources.keys())}")
        self.points = inp

    @classmethod
    def lint(cls, lint: "Lint", **kwargs):
        kwargs.pop("points", None)
        # Points may be defined by the flavour
        # if points is None:
        #     lint.warn_recipe_step("missing 'points'", **kwargs)
        # if not isinstance(points, str):
        #     lint.warn_recipe_step("'points' must be a string", **kwargs)
        super().lint(lint, **kwargs)

    def as_magics_macro(self) -> Tuple[str, Dict[str, Any]]:
        params = dict(self.params.get("params", {}))
        params["geo_input_file_name"] = str(self.points.pathname)
        return "mgeo", params

    @classmethod
    def get_input_names(cls, step_config: StepConfig, args: Kwargs) -> Set[str]:
        res = super().get_input_names(step_config, args)
        args = cls.compile_args(step_config, args)
        points = args.get("points")
        if points is not None:
            res.add(points)
        return res
