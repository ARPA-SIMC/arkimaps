# from __future__ import annotations
from typing import Dict, Any, Optional, List
import tempfile
import os
import yaml
import contextlib
try:
    import arkimet
except ModuleNotFoundError:
    arkimet = None
from .flavours import Flavour
from .recipes import Recipe
from . import pantry

# if TYPE_CHECKING:
# from .orders import Order
# Used for kwargs-style dicts
Kwargs = Dict[str, Any]


class Kitchen:
    """
    Shared context for this arkimaps run
    """
    def __init__(self):
        from .recipes import Recipes
        self.pantry: "pantry.Pantry"
        self.recipes = Recipes()
        self.flavours: Dict[str, Flavour] = {}
        self.context_stack = contextlib.ExitStack()

    def get_pantry(self) -> "pantry.Pantry":
        raise NotImplementedError(f"{self.__class__.__name__}.get_pantry() not implemented")

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return self.context_stack.__exit__(*args)

    def load_recipes(self, paths: List[str]):
        """
        Load recipes from the given list of directories
        """
        for path in paths:
            self.load_recipe_dir(path)

    def load_recipe_dir(self, path: str):
        """
        Load recipes from the given directory
        """
        from .inputs import Input
        from .recipes import Recipe
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

                inputs = recipe.get("inputs")
                if inputs is not None:
                    for name, input_contents in inputs.items():
                        if isinstance(input_contents, list):
                            for ic in input_contents:
                                self.pantry.add_input(Input.create(name=name, defined_in=relfn, **ic))
                        else:
                            self.pantry.add_input(Input.create(name=name, defined_in=relfn, **input_contents))

                flavours = recipe.get("flavours")
                if flavours is not None:
                    for flavour in flavours:
                        name = flavour.pop("name", None)
                        if name is None:
                            raise RuntimeError(f"{relfn}: found flavour without name")
                        old = self.flavours.get(name)
                        if old is not None:
                            raise RuntimeError(f"{relfn}: flavour {name} was already defined in {old.defined_in}")
                        self.flavours[name] = Flavour(name=name, defined_in=relfn, **flavour)

                if "recipe" in recipe:
                    self.recipes.add(Recipe(relfn[:-5], defined_in=relfn, data=recipe))

    def document_recipes(self, path: str):
        """
        Generate markdown documentation for all the recipes found.

        Write documentation to the given path
        """
        for recipe in self.recipes.recipes:
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

    def make_orders(self, flavour: Flavour) -> List["orders.Order"]:
        """
        Generate all possible orders for all available recipes
        """
        res: List["orders.Order"] = []
        for recipe in self.recipes.recipes:
            if not flavour.allows_recipe(recipe):
                continue
            res.extend(recipe.make_orders(self.pantry, flavour=flavour))
        return res

    def make_order(self, recipe: Recipe, step: int, flavour: Flavour) -> "orders.Order":
        """
        Generate all possible orders for all available recipes
        """
        for o in recipe.make_orders(self.pantry, flavour=flavour):
            if o.step == step:
                return o
        raise RuntimeError(f"not enough data to prepare {recipe.name}+{step:03d}")


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
            merged = None
            input_names = set()
            for r in self.recipes.recipes:
                input_names.update(self.pantry.list_all_inputs(r))
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
    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        self.pantry = pantry.EccodesPantry(root=self.workdir)
