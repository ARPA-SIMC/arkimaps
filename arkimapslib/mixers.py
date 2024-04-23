# from __future__ import annotations
from typing import Dict, Any, Type
from . import steps

# if TYPE_CHECKING:
# Used for kwargs-style dicts
Kwargs = Dict[str, Any]


class Mixers:
    """
    Registry of available Mixer implementations (collection of named steps)
    """

    def __init__(self) -> None:
        self.registry: Dict[str, Dict[str, Type["steps.Step"]]] = {}

    def register(self, name: str, steps: Dict[str, Type["steps.Step"]]) -> None:
        """
        Add a named set of steps to the mixers collection
        """
        if name in self.registry:
            raise RuntimeError(f"Mixer steps {name} alredy registered")
        self.registry[name] = steps

    def get_steps(self, name: str) -> Dict[str, Type["steps.Step"]]:
        """
        Get a collection of steps, by name
        """
        return self.registry[name]


mixers = Mixers()

mixers.register(
    "default",
    {
        "add_basemap": steps.AddBasemap,
        "add_coastlines_bg": steps.AddCoastlinesBg,
        "add_coastlines_fg": steps.AddCoastlinesFg,
        "add_grib": steps.AddGrib,
        "add_contour": steps.AddContour,
        "add_grid": steps.AddGrid,
        "add_wind": steps.AddWind,
        "add_boundaries": steps.AddBoundaries,
        "add_user_boundaries": steps.AddUserBoundaries,
        "add_symbols": steps.AddSymbols,
        "add_geopoints": steps.AddGeopoints,
    },
)
