# from __future__ import annotations
from typing import Dict, Any, List, Tuple
import inspect
import json
import logging

# Used for kwargs-style dicts
from . import pantry
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
    def __init__(self, name: str, data: 'Kwargs'):
        self.name = name

        # Name of the mixer to use
        self.mixer: str = data.get("mixer", "default")

        # Get the recipe description
        self.description: str = data.get("description", "Unnamed recipe")

        # Get the recipe steps
        self.steps: List[Tuple[str, 'Kwargs']] = []
        for s in data.get("recipe", ()):
            if not isinstance(s, dict):
                raise RuntimeError("recipe step is not a dict")
            step = s.pop("step", None)
            if step is None:
                raise RuntimeError("recipe step does not contain a 'step' name")
            self.steps.append((step, s))

    def document(self, p: "pantry.Pantry", dest: str):
        from .mixer import Mixers
        mixer = Mixers.registry[self.mixer]

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
            for name, args in self.steps:
                print(f"### {name}", file=fd)
                print(file=fd)
                print(inspect.getdoc(getattr(mixer, name)), file=fd)
                print(file=fd)
                if args:
                    print("With arguments:", file=fd)
                    print("```", file=fd)
                    # FIXME: dump as yaml?
                    print(json.dumps(args, indent=2), file=fd)
                    print("```", file=fd)
                print(file=fd)


class Order:
    """
    Serializable instructions to prepare a product, based on a recipe and its
    input files
    """
    def __init__(
            self,
            mixer: str,
            sources: Dict[str, str],
            basename: str,
            recipe: str,
            steps: List[Tuple[str, 'Kwargs']]):
        # Name of the Mixer to use
        self.mixer = mixer
        # Dict mapping source names to pathnames of GRIB files
        self.sources = sources
        # Destination file name (without path or .png extension)
        self.basename = basename
        # Recipe name
        self.recipe = recipe
        # Recipe steps
        self.steps = steps
        # Output file name, set after the product has been rendered
        self.output = None
        # Logger for this output
        self.log = logging.getLogger(f"arkimaps.order.{basename}")

    def __getstate__(self):
        state = self.__dict__.copy()
        # logger objects don't pickle correctly on python 3.6
        del state['log']
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)
        self.log = logging.getLogger(f"arkimaps.order.{self.basename}")

    def __str__(self):
        return self.basename

    def __repr__(self):
        return self.basename

    def prepare(self, workdir: str):
        """
        Run all the steps of the recipe and render the resulting file
        """
        from arkimapslib.mixer import Mixers

        mixer = Mixers.for_order(workdir, self)
        for name, args in self.steps:
            self.log.info("%s %r", name, args)
            meth = getattr(mixer, name, None)
            if meth is None:
                raise RuntimeError("Recipe " + self.name + " uses unknown step " + name)
            meth(**args)

        mixer.serve()
