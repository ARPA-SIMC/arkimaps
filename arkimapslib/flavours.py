# from __future__ import annotations
from typing import Dict, Any

# if TYPE_CHECKING:
# from . import recipes
# from . import inputs
# Used for kwargs-style dicts
Kwargs = Dict[str, Any]


class Flavour:
    """
    Set of default settings used for generating a product
    """
    def __init__(self, name: str, defined_in: str, defaults: Kwargs = None, **kw):
        self.name = name
        self.defined_in = defined_in
        self.defaults: Kwargs
        if defaults is None:
            self.defaults = {}
        else:
            self.defaults = defaults
