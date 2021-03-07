# from __future__ import annotations
# from typing import Dict

# if TYPE_CHECKING:
# from . import recipes
# from . import inputs


class Flavour:
    """
    Set of default settings used for generating a product
    """
    def __init__(self, name: str, defined_in: str, **kw):
        self.name = name
        self.defined_in = defined_in
