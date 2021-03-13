# from __future__ import annotations
from typing import Dict, Any, Optional, List
import re
import fnmatch

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
    def __init__(self,
                 name: str,
                 defined_in: str,
                 steps: Kwargs = None,
                 recipes_filter: Optional[List[str]] = None,
                 **kw):
        self.name = name
        self.defined_in = defined_in

        self.recipes_filter: List[re.compile] = []
        if recipes_filter is not None:
            for expr in recipes_filter:
                self.recipes_filter.append(
                        re.compile(fnmatch.translate(expr)))

        self.steps = {}
        if steps is not None:
            for name, options in steps.items():
                self.steps[name] = StepConfig(name, options)

    def allows_recipe(self, recipe: "recipes.Recipe"):
        """
        Check if a recipe should be generated for this flavour
        """
        if not self.recipes_filter:
            return True
        for regex in self.recipes_filter:
            if regex.match(recipe.name):
                return True
        return False

    def step_config(self, name: str) -> StepConfig:
        """
        Return a StepConfig object for the given step name
        """
        res = self.steps.get(name)
        if res is None:
            res = StepConfig(name)
        return res
