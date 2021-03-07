# from __future__ import annotations
from typing import Dict, Any, Optional, Type, Set
import functools

# if TYPE_CHECKING:
from . import mixer
# Used for kwargs-style dicts
Kwargs = Dict[str, Any]


class Step:
    """
    One recipe step provided by a Mixer
    """
    def __init__(self, doc: str):
        self.name = None
        self.doc = doc

    def __set_name__(self, owner: Type["Mixer"], name: str):
        owner.steps[name] = self
        self.name = name

    def __get__(self, instance, owner=None):
        return functools.partial(self.run, instance)

    def run(self, mixer: "mixer.Mixer"):
        raise NotImplementedError(f"{self.__class__.__name__}.run not implemented")

    def get_input_names(self, args: Optional[Kwargs] = None) -> Set[str]:
        """
        Return the list of input names used by this step
        """
        return set()


class MagicsMacro(Step):
    """
    Run a Magics macro with optional default arguments
    """
    def __init__(self, name: str, doc: str, params: Optional[Kwargs] = None):
        super().__init__(doc)
        self.macro_name = name
        self.params = params

    def run(self, mixer: "mixer.Mixer", params: Optional[Kwargs] = None):
        if params is None:
            params = self.params
        mixer.parts.append(getattr(mixer.macro, self.macro_name)(**params))
        mixer.py_lines.append(f"parts.append(macro.{self.macro_name}(**{params!r}))")


class AddGrib(Step):
    def __init__(self):
        super().__init__("Add a grib file")

    def run(self, mixer: "mixer.Mixer", name: str, params: Optional[Kwargs] = None):
        input_file = mixer.order.sources[name]
        source_input = input_file.info

        kwargs = {}
        if source_input.mgrib:
            kwargs.update(source_input.mgrib)
        if params is not None:
            kwargs.update(params)

        mixer.order.log.info("add_grib mgrib %r", kwargs)

        grib = mixer.macro.mgrib(grib_input_file_name=input_file.pathname, **kwargs)
        mixer.parts.append(grib)
        mixer.py_lines.append(f"parts.append(macro.mgrib(grib_input_file_name={input_file.pathname!r}, **{kwargs!r}))")

    def get_input_names(self, args: Optional[Kwargs] = None) -> Set[str]:
        res = super().get_input_names(args)
        name = args.get("name")
        if name is not None:
            res.add(name)
        return res


class AddUserBoundaries(Step):
    def __init__(self):
        super().__init__("Add user-defined boundaries from a shapefile")

    def run(self, mixer: "mixer.Mixer", shape: str, params: Optional[Kwargs] = None):
        input_file = mixer.order.sources[shape]

        args = {
            "map_user_layer": "on",
            "map_user_layer_colour": "blue",
        }
        if params is not None:
            args.update(params)

        args["map_user_layer_name"] = input_file.pathname

        mixer.parts.append(mixer.macro.mcoast(**args))
        mixer.py_lines.append(f"parts.append(macro.mcoast(**{args!r}))")

    def get_input_names(self, args: Optional[Kwargs] = None) -> Set[str]:
        res = super().get_input_names(args)
        name = args.get("shape")
        if name is not None:
            res.add(name)
        return res


class AddGeopoints(Step):
    def __init__(self):
        super().__init__("Add geopoints")

    def run(self, mixer: "mixer.Mixer", points: str, params: Optional[Kwargs] = None):
        input_file = mixer.order.sources[points]

        args = {}
        if params is not None:
            args.update(params)
        args["geo_input_file_name"] = input_file.pathname

        mixer.parts.append(mixer.macro.mgeo(**args))
        mixer.py_lines.append(f"parts.append(macro.mgeo(**{args!r}))")

    def get_input_names(self, args: Optional[Kwargs] = None) -> Set[str]:
        res = super().get_input_names(args)
        name = args.get("points")
        if name is not None:
            res.add(name)
        return res
