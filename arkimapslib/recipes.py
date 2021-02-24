# from __future__ import annotations
from typing import Dict, Any, List, Tuple, Optional
from collections import defaultdict
import os
import sys
import inspect
import json
import logging

# if TYPE_CHECKING:
#    import arkimet
try:
    import arkimet
except ModuleNotFoundError:
    arkimet = None

# Used for kwargs-style dicts
Kwargs = Dict[str, Any]

log = logging.getLogger("arkimaps.recipes")


class Recipes:
    """
    Repository of all known recipes
    """
    def __init__(self):
        self.recipes = []

    def get(self, name: str):
        """
        Return a recipe by name
        """
        for r in self.recipes:
            if r.name == name:
                return r
        raise KeyError(f"Recipe `{name}` does not exist")

    def document(self, path: str):
        """
        Generate markdown documentation for the recipes found in the given path
        """
        for recipe in self.recipes:
            dest = os.path.join(path, recipe.name) + '.md'
            recipe.document(dest)


class Recipe:
    """
    A parsed and validated recipe
    """
    def __init__(self, name: str, data: 'Kwargs'):
        from .inputs import Input

        self.name = name

        # Name of the mixer to use
        self.mixer: str = data.get("mixer", "default")

        # Get the recipe description
        self.description: str = data.get("description", "Unnamed recipe")

        # Get the list of input queries
        self.inputs: Dict[str, List[Input]] = defaultdict(list)
        for name, inputs in data.get("inputs", {}).items():
            for info in inputs:
                self.inputs[name].append(Input.create(**info))

        # Get the recipe steps
        self.steps: List[Tuple[str, 'Kwargs']] = []
        for s in data.get("recipe", ()):
            if not isinstance(s, dict):
                raise RuntimeError("recipe step is not a dict")
            step = s.pop("step", None)
            if step is None:
                raise RuntimeError("recipe step does not contain a 'step' name")
            self.steps.append((step, s))

    def document(self, dest: str):
        from .mixer import Mixers
        mixer = Mixers.registry[self.mixer]

        with open(dest, "wt") as fd:
            print(f"# {self.name}: {self.description}", file=fd)
            print(file=fd)
            print(f"Mixer: **{self.mixer}**", file=fd)
            print(file=fd)
            print("## Inputs", file=fd)
            print(file=fd)
            for name, inputs in self.inputs.items():
                print(f"* **{name}**:", file=fd)
                if len(inputs) == 1:
                    inputs[0].document(indent=4, file=fd)
                else:
                    for idx, i in enumerate(inputs, start=1):
                        print(f"    * **Option {idx}**:", file=fd)
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


class ArkimetRecipe(Recipe):
    def __init__(self, name: str, data: 'Kwargs', session: Optional['arkimet.dataset.Session']):
        super().__init__(name, data)
        for input_list in self.inputs.values():
            for i in input_list:
                i.compile_arkimet_matcher(session)


class EccodesRecipe(Recipe):
    pass


class Order:
    """
    Serializable instructions to prepare a product, based on a recipe and its
    input files
    """
    def __init__(
            self,
            mixer: str,
            sources: Dict[str, str],
            dest: str,
            basename: str,
            recipe: str,
            steps: List[Tuple[str, 'Kwargs']]):
        # Name of the Mixer to use
        self.mixer = mixer
        # Dict mapping source names to pathnames of GRIB files
        self.sources = sources
        # Destination file path (without .png extension)
        self.dest = dest
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

    def prepare(self):
        """
        Run all the steps of the recipe and render the resulting file
        """
        from arkimapslib.mixer import Mixers

        mixer = Mixers.for_order(self)
        for name, args in self.steps:
            self.log.info("%s %r", name, args)
            meth = getattr(mixer, name, None)
            if meth is None:
                raise RuntimeError("Recipe " + self.name + " uses unknown step " + name)
            meth(**args)

        mixer.serve()
