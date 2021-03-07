# from __future__ import annotations
from typing import Dict, Any, List, Optional
import logging
from . import orders

# if TYPE_CHECKING:
from . import pantry
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


class Recipe:
    """
    A parsed and validated recipe
    """
    def __init__(self, name: str, defined_in: str, data: 'Kwargs'):
        self.name = name
        self.defined_in = defined_in

        # Name of the mixer to use
        self.mixer: str = data.get("mixer", "default")

        from .mixers import mixers
        step_collection = mixers.get_steps(self.mixer)

        # Get the recipe description
        self.description: str = data.get("description", "Unnamed recipe")

        # Get the recipe steps
        self.steps: List['steps.Step'] = []
        for s in data.get("recipe", ()):
            if not isinstance(s, dict):
                raise RuntimeError("recipe step is not a dict")
            step = s.pop("step", None)
            if step is None:
                raise RuntimeError("recipe step does not contain a 'step' name")
            step_cls = step_collection.get(step)
            if step_cls is None:
                raise RuntimeError(f"step {step} not found in mixer {self.mixer}")
            self.steps.append(step_cls(step=step, **s))

    def list_inputs(self) -> List[str]:
        """
        List the names of inputs used by this recipe

        Inputs are listed in usage order, without duplicates
        """
        input_names = []

        # Collect the inputs needed for all steps
        for step in self.steps:
            for input_name in step.get_input_names():
                if input_name in input_names:
                    continue
                input_names.append(input_name)
        return input_names

    def make_orders(self, pantry: "pantry.Pantry") -> List["orders.Order"]:
        """
        Scan a recipe and return a set with all the inputs it needs
        """
        from .inputs import InputFile
        inputs: Optional[Dict[str, Dict[str, InputFile]]] = None
        inputs_for_all_steps: Dict[str, InputFile] = {}
        input_names = set()

        # Collect the inputs needed for all steps
        for step in self.steps:
            for input_name in step.get_input_names():
                if input_name in input_names:
                    continue
                input_names.add(input_name)

                # Find available steps for this input
                steps = pantry.get_steps(input_name)
                any_step = steps.pop(None, None)
                if any_step is not None:
                    inputs_for_all_steps[input_name] = any_step
                if not steps:
                    continue

                # add_grib needs this input for all steps
                if inputs is None:
                    inputs = {}
                    for step, ifile in steps.items():
                        inputs[step] = {input_name: ifile}
                else:
                    steps_to_delete = []
                    for step, input_files in inputs.items():
                        if step not in steps:
                            # We miss an input for this step, so we cannot
                            # generate an order for it
                            steps_to_delete.append(step)
                        else:
                            input_files[input_name] = steps[step]
                    for step in steps_to_delete:
                        del inputs[step]

        if inputs_for_all_steps:
            for step, files in inputs.items():
                files.update(inputs_for_all_steps)

        res = []
        for step, input_files in inputs.items():
            res.append(orders.Order(
                mixer=self.mixer,
                sources=input_files,
                recipe=self,
                step=step,
            ))

        return res

    def document(self, p: "pantry.Pantry", dest: str):
        with open(dest, "wt") as fd:
            print(f"# {self.name}: {self.description}", file=fd)
            print(file=fd)
            print(f"Mixer: **{self.mixer}**", file=fd)
            print(file=fd)
            print("## Inputs", file=fd)
            print(file=fd)
            for name in p.list_all_inputs(self):
                inputs = p.inputs.get(name)
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
                print(f"### {name}", file=fd)
                print(file=fd)
                step.document(file=fd)
                print(file=fd)
