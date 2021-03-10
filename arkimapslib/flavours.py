# from __future__ import annotations
from typing import Dict, Any, Optional

# if TYPE_CHECKING:
# from . import recipes
# from . import inputs
# Used for kwargs-style dicts
Kwargs = Dict[str, Any]


class StepConfig:
    """
    Flavour configuration for a step
    """
    def __init__(self, name: str, options: Optional[Kwargs] = None, **kw):
        self.name = name
        self.options: Kwargs = options if options is not None else {}

    def get_param(self, name: str) -> Kwargs:
        return self.options.get(name)


class Flavour:
    """
    Set of default settings used for generating a product
    """
    def __init__(self, name: str, defined_in: str, steps: Kwargs = None, **kw):
        self.name = name
        self.defined_in = defined_in
        self.steps = {
            name: StepConfig(name, options)
            for name, options in steps.items()
        }

    def step_config(self, name: str) -> StepConfig:
        """
        Return a StepConfig object for the given step name
        """
        res = self.steps.get(name)
        if res is None:
            res = StepConfig(name)
        return res
