from __future__ import annotations
from typing import TYPE_CHECKING, Dict, Any, List, Tuple, Type
import os
import inspect
import json
import yaml
from Magics import macro
import arkimet

if TYPE_CHECKING:
    from .chef import Chef


class Recipe:
    """
    A parsed and validated recipe
    """
    def __init__(self, name: str, session: arkimet.dataset.Session, data: Dict[str, Any]):
        self.name = name

        # Get the recipe description
        self.description: str = data.get("description", "Unnamed recipe")

        # Get the list of input queries
        self.inputs: List[Tuple[str, arkimet.Matcher]] = []
        for name, query in data.get("inputs", {}).items():
            self.inputs.append((name, session.matcher(query)))
        if len(self.inputs) > 1:
            raise RuntimeError("Recipes with multiple inputs are not supported yet")

        # Get the recipe steps
        self.steps: List[Tuple[str, Dict[str, Any]]] = []
        for s in data.get("recipe", ()):
            if not isinstance(s, dict):
                raise RuntimeError("recipe step is not a dict")
            step = s.pop("step", None)
            if step is None:
                raise RuntimeError("recipe step does not contain a 'step' name")
            self.steps.append((step, s))

    def matches(self, path: str):
        """
        Check if the given path matches one of the recipe input regexps
        """
        # TODO: change this logic for multi-source recipes
        for name, glob, input_re in self.inputs:
            if input_re.match(path):
                return True
        return False

    def start_dish(self, src: str, dest: str):
        """
        Start an output for this recipe and the given source
        """
        dish = Dish(dest)
        # TODO: change this logic for multi-source recipes
        dish.sources[self.inputs[0][0]] = src
        return dish

    def prepare(self, chef: Type[Chef], dish: "Dish"):
        """
        Run all the steps of the recipe
        """
        chef = chef(dish)

        for name, args in self.steps:
            meth = getattr(chef, name, None)
            if meth is None:
                raise RuntimeError("Recipe " + self.name + " uses unknown step " + name)
            meth(**args)

        chef.serve()

    def document(self, chef: Type[Chef], dest: str):
        with open(dest, "wt") as fd:
            print(f"# {self.name}: {self.description}", file=fd)
            print(file=fd)
            print("## Inputs", file=fd)
            print(file=fd)
            for name, glob, input_re in self.inputs:
                print(f"* **{name}**: `{glob}`", file=fd)
            print(file=fd)
            print("## Steps", file=fd)
            print(file=fd)
            for name, args in self.steps:
                print(f"### {name}", file=fd)
                print(file=fd)
                print(inspect.getdoc(getattr(chef, name)), file=fd)
                print(file=fd)
                if args:
                    print("With arguments:", file=fd)
                    print("```", file=fd)
                    # FIXME: dump as yaml?
                    print(json.dumps(args, indent=2), file=fd)
                    print("```", file=fd)
                print(file=fd)


class Recipes:
    """
    Repository of all known recipes
    """
    def __init__(self):
        self.recipes = []

    def load(self, session: arkimet.dataset.Session, path: str):
        """
        Load recipes from the given directory
        """
        for fn in os.listdir(path):
            if not fn.endswith(".yaml"):
                continue
            with open(os.path.join(path, fn), "rt") as fd:
                recipe = yaml.load(fd)
            self.recipes.append(Recipe(fn[:-5], session, recipe))

    def document(self, path: str):
        """
        Generate markdown documentation for the recipes found in the given path
        """
        for fn in os.listdir(path):
            if not fn.endswith(".yaml"):
                continue
            with open(os.path.join(path, fn), "rt") as fd:
                recipe = yaml.load(fd)
            recipe = Recipe(recipe)
            recipe.document(os.path.join(path, fn) + ".md")

    def for_path(self, path: str):
        """
        Generate all recipes matching the given path
        """
        for recipe in self.recipes:
            if recipe.matches(path):
                yield recipe


class Dish:
    """
    Object holding the final output and intermediate data while the recipes are
    executed
    """
    def __init__(self, fname: str):
        # Settings of the PNG output
        self.output = macro.output(
            output_formats=['png'],
            output_name=fname,
            output_name_first_page_number="off",
        )
        # List of source paths by name
        self.sources: Dict[str, str] = {}
        # Loaded GRIB data
        self.gribs: Dict[str, Any] = {}
        # Elements passed after output to macro.plot
        self.parts = []

        # Destination file name
        self.output_file_name = fname + ".png"
