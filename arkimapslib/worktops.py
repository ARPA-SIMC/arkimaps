# from __future__ import annotations
from typing import List, Any, Dict

# if TYPE_CHECKING:
from . import inputs


class Worktop:
    """
    Holding area for intermediate values during rendering of a recipe
    """
    def __init__(self, input_files: Dict[str, inputs.InputFile]):
        # Do not import Magics at toplevel to prevent accidentally importing it
        # in the main process. We only import Magics in working processes to
        # mitigate memory leaks
        from Magics import macro
        self.macro = macro

        # Input files used to render this product
        self.input_files = input_files

        # Elements passed after output to macro.plot
        self.parts: List[Any] = []
