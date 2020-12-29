from __future__ import annotations
from typing import TYPE_CHECKING, Dict, Any, List, Tuple, Iterator, Optional
from collections import defaultdict
import os
import inspect
import json
import yaml

if TYPE_CHECKING:
    import arkimet


class Recipes:
    """
    Repository of all known recipes
    """
    def __init__(self):
        self.recipes = []

    def load(self, session: Optional[arkimet.dataset.Session], path: str):
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
        for recipe in self.recipes:
            dest = os.path.join(path, recipe.name) + '.yaml.md'
            recipe.document(dest)


class Recipe:
    """
    A parsed and validated recipe
    """
    def __init__(self, name: str, session: Optional[arkimet.dataset.Session], data: Dict[str, Any]):
        self.name = name

        # Name of the chef to use
        self.chef: str = data.get("chef", "default")

        # Get the recipe description
        self.description: str = data.get("description", "Unnamed recipe")

        # Get the list of input queries
        self.inputs: List[Tuple[str, arkimet.Matcher]] = []
        for name, query in data.get("inputs", {}).items():
            self.inputs.append((name, session.matcher(query) if session else query))
        if len(self.inputs) > 1:
            raise RuntimeError("Recipes with multiple inputs are not supported yet")

        # Get the list of grib_filter input queries
        self.inputs_grib: List[Tuple[str, str]] = []
        for name, query in data.get("inputs_grib", {}).items():
            self.inputs_grib.append((name, query))
        if len(self.inputs_grib) > 1:
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

    def make_orders_from_arkimet(self, reader: arkimet.dataset.Reader, workdir: str) -> Iterator["Order"]:
        for name, query in self.inputs:
            for md in reader.query_data(query):
                source = md.to_python("source")
                pathname = os.path.join(source["basedir"], source["file"], f"{source['offset']:06d}.grib")
                sources = {name: pathname}

                trange = md.to_python("timerange")
                basename = f"{self.name}+{trange['p1']:03d}"
                dest = os.path.join(workdir, basename)

                yield Order(
                    chef=self.chef,
                    sources=sources,
                    dest=dest,
                    basename=basename,
                    recipe=self.name,
                    steps=self.steps,
                )

    def make_orders_from_grib(self, workdir: str) -> Iterator["Order"]:
        input_dir = os.path.join(workdir, self.name)

        # Read all available input files in a dict indexed by inputs_grib name
        # and step: {input_name: {step: filename}}
        files = defaultdict(dict)
        for fname in os.listdir(input_dir):
            if not fname.endswith(".grib"):
                continue
            name, step = fname[:-5].rsplit("+")
            files[name][int(step)] = fname

        # Build orders for each step of each input grib found
        for name, query in self.inputs_grib:
            for step, fname in files[name].items():
                pathname = os.path.join(input_dir, fname)
                sources = {name: pathname}

                basename = f"{self.name}+{step}"
                dest = os.path.join(workdir, basename)

                yield Order(
                    chef=self.chef,
                    sources=sources,
                    dest=dest,
                    basename=basename,
                    recipe=self.name,
                    steps=self.steps,
                )

    def document(self, dest: str):
        from .chef import Chefs
        chef = Chefs.registry[self.chef]

        with open(dest, "wt") as fd:
            print(f"# {self.name}: {self.description}", file=fd)
            print(file=fd)
            print(f"Chef: **{self.chef}**", file=fd)
            print(file=fd)
            print("## Inputs", file=fd)
            print(file=fd)
            for name, matcher in self.inputs:
                print(f"* **{name}**: [arkimet] `{matcher}`", file=fd)
            for name, expr in self.inputs_grib:
                print(f"* **{name}**: [grib_filter] `{expr}`", file=fd)
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


class Order:
    """
    Serializable instructions to prepare a product, based on a recipe and its
    input files
    """
    def __init__(
            self,
            chef: str,
            sources: Dict[str, str],
            dest: str,
            basename: str,
            recipe: str,
            steps: List[Tuple[str, Dict[str, Any]]]):
        # Name of the Chef to use
        self.chef = chef
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

    def prepare(self):
        """
        Run all the steps of the recipe and render the resulting file
        """
        from arkimapslib.chef import Chefs

        chef = Chefs.for_order(self)
        for name, args in self.steps:
            meth = getattr(chef, name, None)
            if meth is None:
                raise RuntimeError("Recipe " + self.name + " uses unknown step " + name)
            meth(**args)

        chef.serve()
