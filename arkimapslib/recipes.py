# from __future__ import annotations
import inspect
import json
import logging
import os
from typing import TYPE_CHECKING, Any, Dict, List, Set, TextIO, Type, Optional

from . import steps

if TYPE_CHECKING:
    from . import pantry

# if TYPE_CHECKING:
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
    def __init__(self, name: str, step: Type[steps.Step], args: Kwargs, id: Optional[str] = None):
        self.name = name
        self.step = step
        self.args = args
        self.id = id

    def get_input_names(self, step_config: steps.StepConfig) -> Set[str]:
        """
        Get the names of inputs needed by this step
        """
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
        # Name of the recipe
        self.name = name
        # File where the recipe was defined
        self.defined_in = defined_in
        # Optional notes for the documentation
        self.notes = data.get("notes")

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
            id = s.pop("id", None)
            self.steps.append(RecipeStep(name=step, step=step_cls, args=s, id=id))

    @classmethod
    def inherit(self, name: str, defined_in: str, parent: "Recipe", data: 'Kwargs') -> "Recipe":
        """
        Create a recipe derived from an existing one
        """
        changes = data.pop("change", {})
        data.setdefault("notes", parent.notes)
        data.setdefault("description", parent.description)
        data.setdefault("mixer", parent.mixer)
        steps: List[Dict[str, Any]] = []
        for recipe_step in parent.steps:
            step = {"step": recipe_step.name, "id": recipe_step.id}
            step.update(recipe_step.args)
            if recipe_step.id in changes:
                step.update(changes[recipe_step.id])
            steps.append(step)
        data["recipe"] = steps
        return Recipe(name, defined_in, data)

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name

    def summarize(self) -> Dict[str, Any]:
        """
        Return a structure describing this Recipe, to use for the render order
        summary
        """
        return {
            "name": self.name,
            "defined_in": self.defined_in,
            "description": self.description,
        }

    def document(self, pantry: "pantry.Pantry", dest: str):
        from .flavours import Flavour
        empty_flavour = Flavour("default", defined_in=__file__)
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        with open(dest, "wt") as fd:
            print(f"# {self.name}: {self.description}", file=fd)
            print(file=fd)
            print(f"Mixer: **{self.mixer}**", file=fd)
            print(file=fd)
            if self.notes:
                print("## Notes", file=fd)
                print(file=fd)
                print(self.notes, file=fd)
                print(file=fd)
            print("## Inputs", file=fd)
            print(file=fd)
            # TODO: list only inputs explicitly required by the recipe
            for name in empty_flavour.list_inputs_recursive(self, pantry):
                inputs = pantry.inputs.get(name)
                if inputs is None:
                    print(f"* **{name}** (input details are missing)", file=fd)
                else:
                    print(f"* **{name}**:", file=fd)
                    if len(inputs) == 1:
                        inputs[0].document(indent=4, file=fd)
                    else:
                        for i in inputs:
                            print(f"    * Model **{i.model}**:", file=fd)
                            i.document(indent=8, file=fd)
            print(file=fd)
            print("## Steps", file=fd)
            print(file=fd)
            for step in self.steps:
                print(f"### {step.name}", file=fd)
                print(file=fd)
                step.document(file=fd)
                print(file=fd)
