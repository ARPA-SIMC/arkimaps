# from __future__ import annotations
from typing import List, Any, Dict

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

    def write_product(self):
        """
        Render the file and store the output file name into the order
        """
        self.macro.plot(
            self.output,
            *self.parts,
        )
