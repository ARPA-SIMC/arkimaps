# from __future__ import annotations
from typing import List, Any, Optional, Dict
import os

# if TYPE_CHECKING:
from . import inputs


class Worktop:
    """
    Holding area for intermediate values during rendering of a recipe
    """
    def __init__(self, output_pathname: str, input_files: Dict[str, inputs.InputFile]):
        # Do not import Magics at toplevel to prevent accidentally importing it
        # in the main process. We only import Magics in working processes to
        # mitigate memory leaks
        from Magics import macro
        self.macro = macro

        # Pathname of the output file without .png extension
        self.output_pathname = output_pathname

        # Input files used to render this product
        self.input_files = input_files

        # Settings of the PNG output
        self.output = self.macro.output(
            output_formats=['png'],
            output_name=self.output_pathname,
            output_name_first_page_number="off",
        )

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

    def write_python_trace(self, fname: Optional[str] = None):
        """
        Write the python trace of this run to the given file
        """
        if fname is None:
            fname = self.output_pathname + ".py"
        self.py_lines.append(f"macro.plot(output, *parts)")

        code = "\n".join(self.py_lines)
        try:
            from yapf.yapflib import yapf_api
            code, changed = yapf_api.FormatCode(code)
        except ModuleNotFoundError:
            pass
        with open(fname, "wt") as fd:
            print(code, file=fd)

    def write_product(self):
        """
        Render the file and store the output file name into the order
        """
        self.macro.plot(
            self.output,
            *self.parts,
        )
