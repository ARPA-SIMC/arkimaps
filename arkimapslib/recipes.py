# from __future__ import annotations
from typing import Dict, Any, List, Optional, Set, Type, TextIO
import inspect
import json
import logging
from . import steps
from . import inputs

# if TYPE_CHECKING:
# from . import flavours
# Used for kwargs-style dicts
Kwargs = Dict[str, Any]

log = logging.getLogger("arkimaps.recipes")


class Recipes:
    """
    Repository of all known recipes
    """
    def __init__(self):
        self.recipes = []

    def add(self, recipe: "Recipe"):
        """
        Add a recipe to this recipes collection
        """
        self.recipes.append(recipe)

    def get(self, name: str):
        """
        Return a recipe by name
        """
        for r in self.recipes:
            if r.name == name:
                return r
        raise KeyError(f"Recipe `{name}` does not exist")


class RecipeStep:
    """
    A step of a recipe
    """
    def __init__(self, name: str, step: Type[steps.Step], args: Kwargs):
        self.name = name
        self.step = step
        self.args = args

    def get_input_names(self, step_config: Optional[steps.StepConfig] = None) -> Set[str]:
        """
        Get the names of inputs needed by this step
        """
        if step_config is None:
            step_config = steps.StepConfig(self.name)
        return self.step.get_input_names(step_config, self.args)

    def document(self, file: TextIO):
        """
        Document this recipe step
        """
        args = self.step.compile_args(steps.StepConfig(self.name), self.args)
        print(inspect.getdoc(self.step), file=file)
        print(file=file)
        if args:
            print("With arguments:", file=file)
            print("```", file=file)
            # FIXME: dump as yaml?
            print(json.dumps(args, indent=2), file=file)
            print("```", file=file)


class Recipe:
    """
    A parsed and validated recipe
    """
    def __init__(self, name: str, defined_in: str, data: 'Kwargs'):
        from .mixers import mixers
        self.name = name
        self.defined_in = defined_in

        # Get the recipe description
        self.description: str = data.get("description", "Unnamed recipe")

        # Name of the mixer to use
        self.mixer: str = data.get("mixer", "default")

        # Parse the recipe steps
        self.steps: List[RecipeStep] = []
        step_collection = mixers.get_steps(self.mixer)
        for s in data.get("recipe", ()):
            if not isinstance(s, dict):
                raise RuntimeError("recipe step is not a dict")
            step = s.pop("step", None)
            if step is None:
                raise RuntimeError("recipe step does not contain a 'step' name")
            step_cls = step_collection.get(step)
            if step_cls is None:
                raise RuntimeError(f"step {step} not found in mixer {self.mixer}")
            self.steps.append(RecipeStep(step, step_cls, s))

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name

    def list_all_inputs(self, input_registry: inputs.InputRegistry) -> List[str]:
        """
        List inputs used by a recipe, and all their inputs, recursively
        """
        res: List[str] = []
        for input_name in self.list_inputs():
            for inp in input_registry.inputs[input_name]:
                inp.add_all_inputs(input_registry, res)
        return res

    def list_inputs(self, flavour: Optional["flavours.Flavour"] = None) -> List[str]:
        """
        List the names of inputs used by this recipe

        Inputs are listed in usage order, without duplicates
        """
        input_names: List[str] = []

        # Collect the inputs needed for all steps
        for step in self.steps:
            if flavour is None:
                step_config = steps.StepConfig(step.name)
            else:
                step_config = flavour.step_config(step.name)
            for input_name in step.get_input_names(step_config):
                if input_name in input_names:
                    continue
                input_names.append(input_name)
        return input_names

    def document(self, input_registry: inputs.InputRegistry, dest: str):
        with open(dest, "wt") as fd:
            print(f"# {self.name}: {self.description}", file=fd)
            print(file=fd)
            print(f"Mixer: **{self.mixer}**", file=fd)
            print(file=fd)
            print("## Inputs", file=fd)
            print(file=fd)
            # TODO: list only inputs explicitly required by the recipe
            for name in self.list_all_inputs(input_registry):
                inputs = input_registry.inputs.get(name)
                if inputs is None:
                    print(f"* **{name}** (input details are missing)", file=fd)
                else:
                    print(f"* **{name}**:", file=fd)
                    if len(inputs) == 1:
                        inputs[0].document(indent=4, file=fd)
                    else:
                        for i in inputs:
                            print(f"    * Model **{i.model}**:", file=fd)
                            inputs[0].document(indent=8, file=fd)
            print(file=fd)
            print("## Steps", file=fd)
            print(file=fd)
            for step in self.steps:
                print(f"### {step.name}", file=fd)
                print(file=fd)
                step.document(file=fd)
                print(file=fd)
