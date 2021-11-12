# from __future__ import annotations
from typing import TYPE_CHECKING, Dict, Any, Optional, List, Set
import re
import fnmatch
import logging
from .steps import StepConfig, Step, StepSkipped

from . import recipes
from . import orders
from . import inputs

if TYPE_CHECKING:
    from . import pantry

# Used for kwargs-style dicts
Kwargs = Dict[str, Any]


log = logging.getLogger("arkimaps.flavours")


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

        self.steps: Dict[str, StepConfig] = {}
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

    def list_inputs_recursive(self, recipe: "recipes.Recipe", pantry: "pantry.Pantry") -> List[str]:
        """
        List inputs used by a recipe, and all their inputs, recursively
        """
        res: List[str] = []
        for input_name in self.list_inputs(recipe):
            for inp in pantry.inputs[input_name]:
                inp.add_all_inputs(pantry, res)
        return res

    def list_inputs(self, recipe: "recipes.Recipe") -> List[str]:
        """
        List the names of inputs used by this recipe

        Inputs are listed in usage order, without duplicates
        """
        input_names: List[str] = []

        # Collect the inputs needed for all steps
        for recipe_step in recipe.steps:
            step_config = self.step_config(recipe_step.name)
            for input_name in recipe_step.get_input_names(step_config):
                if input_name in input_names:
                    continue
                input_names.append(input_name)
        return input_names

    def instantiate_order_step(
            self,
            recipe_step: "recipes.RecipeStep",
            input_files: Dict[str, inputs.InputFile]) -> Step:
        """
        Instantiate the step class with the given flavour config
        """
        step_config = self.step_config(recipe_step.name)
        return recipe_step.step(recipe_step.name, step_config, recipe_step.args, input_files)

    def get_inputs_for_recipe(self, recipe: "recipes.Recipe") -> Set[str]:
        """
        Return a list with the names of all inputs used by a recipe in this
        flavour
        """
        input_names: Set[str] = set()
        for recipe_step in recipe.steps:
            step_config = self.step_config(recipe_step.name)
            for input_name in recipe_step.get_input_names(step_config):
                input_names.add(input_name)
        return input_names

    def make_orders(self,
                    recipe: "recipes.Recipe",
                    input_storage: "pantry.DiskPantry") -> List["orders.Order"]:
        """
        Scan a recipe and return a set with all the inputs it needs
        """
        from .inputs import InputFile
        # For each output step, map inputs names to InputFile structures
        inputs: Optional[Dict[int, Dict[str, InputFile]]] = None
        # Collection of input name to InputFile mappings used by all output steps
        inputs_for_all_steps: Dict[str, InputFile] = {}

        input_names = self.get_inputs_for_recipe(recipe)
        log.debug("flavour %s: recipe %s uses inputs: %r", self.name, recipe.name, input_names)

        # Find the intersection of all steps available for all inputs needed
        for input_name in input_names:
            # Find available steps for this input
            output_steps: Dict[Optional[int], "InputFile"]
            output_steps = input_storage.get_steps(input_name)

            # Special handling for inputs that are not step-specific and
            # are valid for all steps, like maps or orography
            any_step = output_steps.pop(None, None)
            if any_step is not None:
                log.debug("flavour %s: recipe %s inputs %s available for any step", self.name, recipe.name, input_name)
                inputs_for_all_steps[input_name] = any_step
                # This input is valid for all steps and does not
                # introduce step limitations
                if not output_steps:
                    continue
            else:
                log.debug("flavour %s: recipe %s inputs %s available for steps %r",
                          self.name, recipe.name, input_name, output_steps.keys())

            # Intersect the output steps for the recipe input list
            if inputs is None:
                # The first time this output_step has been seen, populate
                # the `inputs` mapping with all available inputs
                inputs = {}
                for output_step, ifile in output_steps.items():
                    inputs[output_step] = {input_name: ifile}
            else:
                # The subsequent times this output_step is seen, intersect
                steps_to_delete: List[int] = []
                for output_step, input_files in inputs.items():
                    if output_step not in output_steps:
                        # We miss an input for this step, so we cannot
                        # generate an order for it
                        steps_to_delete.append(output_step)
                    else:
                        input_files[input_name] = output_steps[output_step]
                for output_step in steps_to_delete:
                    del inputs[output_step]

        res: List["orders.Order"] = []
        if inputs is not None:
            # For each step we found, build an order
            for output_step, input_files in inputs.items():
                if inputs_for_all_steps:
                    input_files.update(inputs_for_all_steps)

                logger = logging.getLogger(f"arkimaps.render.{self.name}.{recipe.name}+{output_step:03d}")

                # Instantiate order steps from recipe steps
                order_steps: List[Step] = []
                for recipe_step in recipe.steps:
                    try:
                        s = self.instantiate_order_step(recipe_step, input_files)
                    except StepSkipped:
                        logger.debug("%s (skipped)", s.name)
                        continue
                    # self.log.debug("%s %r", step.name, step.get_params(mixer))
                    order_steps.append(s)

                res.append(orders.Order(
                    mixer=recipe.mixer,
                    input_files=input_files,
                    recipe_name=recipe.name,
                    step=output_step,
                    order_steps=order_steps,
                    log=log,
                ))

        return res
