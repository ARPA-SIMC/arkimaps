# from __future__ import annotations
import contextlib
import datetime
import os
import tempfile
from typing import Any, Dict, List, Optional, Union

import yaml

try:
    import arkimet
except ModuleNotFoundError:
    arkimet = None
from . import orders, pantry
from .config import Config
from .flavours import Flavour
from .lint import Lint
from .recipes import Recipe
from .inputs import ModelStep

# if TYPE_CHECKING:
# Used for kwargs-style dicts
Kwargs = Dict[str, Any]


class Kitchen:
    """
    Shared context for this arkimaps run
    """
    def __init__(self, config: Optional[Config] = None):
        from .recipes import Recipes
        if config is None:
            self.config = Config()
        else:
            self.config = config
        self.pantry: "pantry.Pantry"
        self.recipes = Recipes()
        self.flavours: Dict[str, Flavour] = {}
        self.context_stack = contextlib.ExitStack()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return self.context_stack.__exit__(*args)

    def load_recipes(self, paths: List[str], *, lint: Optional[Lint] = None):
        """
        Load recipes from the given list of directories
        """
        for path in paths:
            self.load_recipe_dir(path, lint=lint)

        self.recipes.resolve_derived(lint=lint)

    def load_recipe_dir(self, path: str, *, lint: Optional[Lint] = None):
        """
        Load recipes from the given directory
        """
        from .inputs import Input

        path = os.path.abspath(path)
        if path not in self.config.static_dir:
            self.config.static_dir.insert(0, os.path.join(path, "static"))

        for dirpath, dirnames, fnames in os.walk(path):
            relpath = os.path.relpath(dirpath, start=path)
            for fn in fnames:
                if not fn.endswith(".yaml"):
                    continue
                with open(os.path.join(dirpath, fn), "rt") as fd:
                    recipe = yaml.load(fd, Loader=yaml.SafeLoader)
                if relpath == ".":
                    relfn = fn
                else:
                    relfn = os.path.join(relpath, fn)

                inputs = recipe.pop("inputs", None)
                if inputs is not None:
                    for name, input_contents in inputs.items():
                        if "_" in name:
                            raise RuntimeError(f"{relfn}: '_' not allowed in input name {name!r}")
                        if isinstance(input_contents, list):
                            for ic in input_contents:
                                self.pantry.add_input(
                                    Input.create(config=self.config, name=name, defined_in=relfn, lint=lint, **ic))
                        else:
                            self.pantry.add_input(
                                Input.create(
                                    config=self.config, name=name, defined_in=relfn, lint=lint, **input_contents))

                flavours = recipe.pop("flavours", None)
                if flavours is not None:
                    for flavour in flavours:
                        name = flavour.pop("name", None)
                        if name is None:
                            raise RuntimeError(f"{relfn}: found flavour without name")
                        old = self.flavours.get(name)
                        if old is not None:
                            raise RuntimeError(f"{relfn}: flavour {name} was already defined in {old.defined_in}")
                        self.flavours[name] = Flavour.create(
                            config=self.config, name=name, defined_in=relfn, lint=lint, **flavour)

                recipe["name"] = relfn[:-5]
                recipe["defined_in"] = relfn

                if "recipe" in recipe:
                    self.recipes.add(lint=lint, **recipe)

                if "extends" in recipe:
                    self.recipes.add_derived(lint=lint, **recipe)

    def document_recipes(self, path: str):
        """
        Generate markdown documentation for all the recipes found.

        Write documentation to the given path
        """
        for recipe in self.recipes:
            dest = os.path.join(path, recipe.name) + '.md'
            recipe.document(self.pantry, dest)


class WorkingKitchen(Kitchen):
    def __init__(self, workdir: Optional[str] = None):
        """
        If no working directory is provided, it uses a temporary one
        """
        super().__init__()
        self.pantry: "pantry.DiskPantry"
        self.tempdir: Optional[tempfile.TemporaryDirectory]
        self.workdir: str

        if workdir is None:
            self.tempdir = tempfile.TemporaryDirectory()
            self.workdir = self.context_stack.enter_context(self.tempdir)
        else:
            self.tempdir = None
            self.workdir = workdir

    def make_orders(self, flavour: Union[Flavour, str], recipe: Optional[str] = None) -> List[orders.Order]:
        """
        Generate all possible orders for all available recipes
        """
        if isinstance(flavour, str):
            flavour = self.flavours.get(flavour)

        if recipe is None:
            recipes = self.recipes
        else:
            recipes = [self.recipes.get(recipe)]

        res: List[orders.Order] = []
        for recipe in recipes:
            if not flavour.allows_recipe(recipe):
                continue
            res.extend(flavour.make_orders(recipe, self.pantry))
        return res

    def make_order(
            self,
            recipe: Recipe,
            flavour: Flavour,
            step: Union[None, int, str, ModelStep],
            reftime: Optional[datetime.datetime]) -> orders.Order:
        """
        Generate all possible orders for all available recipes
        """
        selected = []
        for o in flavour.make_orders(recipe, self.pantry):
            if step is not None and o.instant.step != step:
                continue
            if reftime is not None and o.instant.reftime != reftime:
                continue
            selected.append(o)
        if not selected:
            raise RuntimeError(f"not enough data to prepare {recipe.name}")
        selected.sort(key=lambda x: x.instant)
        return selected[0]


if arkimet is not None:
    class ArkimetRecipesMixin:
        def __init__(self, *args, **kw):
            # Arkimet session
            #
            # Force directory segments so we can access each data by filesystem
            # path
            super().__init__(*args, **kw)
            self.session = self.context_stack.enter_context(
                    arkimet.dataset.Session(force_dir_segments=True))

        def get_merged_arki_query(self):
            empty_flavour = Flavour(config=self.config, name="default", defined_in=__file__)
            merged = None
            input_names = set()
            for recipe in self.recipes:
                input_names.update(empty_flavour.list_inputs_recursive(recipe, self.pantry))
            for input_name in input_names:
                for inp in self.pantry.inputs[input_name]:
                    matcher = getattr(inp, "arkimet_matcher", None)
                    if matcher is None:
                        continue
                    if merged is None:
                        merged = matcher
                    else:
                        merged = merged.merge(matcher)
            return merged

    class ArkimetEmptyKitchen(ArkimetRecipesMixin, Kitchen):
        """
        Arkimet-based kitchen used to load recipes but not prepare products
        """
        def __init__(self, *args, **kw):
            super().__init__(*args, **kw)
            self.pantry = pantry.ArkimetEmptyPantry(self.session)

    class ArkimetKitchen(ArkimetRecipesMixin, WorkingKitchen):
        def __init__(self, *args, **kw):
            super().__init__(*args, **kw)
            from .pantry import ArkimetPantry
            self.pantry = ArkimetPantry(root=self.workdir, session=self.session)


class EccodesEmptyKitchen(Kitchen):
    """
    Eccodes-based kitchen used to load recipes but not prepare products
    """
    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        self.pantry = pantry.EmptyPantry()


class EccodesKitchen(WorkingKitchen):
    def __init__(self, *args, grib_input=False, **kw):
        super().__init__(*args, **kw)
        self.pantry = pantry.EccodesPantry(root=self.workdir, grib_input=grib_input)
