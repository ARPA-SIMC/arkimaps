# from __future__ import annotations
from typing import Dict, Any, Type, List
import os
from . import steps

# if TYPE_CHECKING:
#     from .recipes import Order
from .orders import Order
# Used for kwargs-style dicts
Kwargs = Dict[str, Any]


class Mixers:
    """
    Registry of available Mixer implementations (collection of named steps)
    """
    def __init__(self):
        self.registry: Dict[str, Dict[str, Type["steps.Step"]]] = {}

    def register(self, name: str, steps: Dict[str, Type["steps.Step"]]):
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

mixers.register("default", {
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
})


class Mixer:
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
        # Order with the steps to execute
        self.order = order
        # Elements passed after output to macro.plot
        self.parts: List[Any] = []
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
