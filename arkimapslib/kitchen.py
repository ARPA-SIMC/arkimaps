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

# if TYPE_CHECKING:
    # Used for kwargs-style dicts
from .recipes import Order
Kwargs = Dict[str, Any]


class Kitchen:
    """
    Shared context for this arkimaps run
    """
    def __init__(self):
        from .recipes import Recipes
        from .pantry import Pantry
        self.pantry: Pantry
        self.recipes = Recipes()
        self.context_stack = contextlib.ExitStack()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return self.context_stack.__exit__(*args)

    def _build_input(self, name: str, filename: str, all_contents: Kwargs, input_contents: Kwargs):
        from .inputs import Input
        return Input.create(name=name, defined_in=filename, **input_contents)

    def _build_recipe(self, name: str, all_contents: Kwargs, recipe_contents: Kwargs):
        from .recipes import Recipe
        return Recipe(name, all_contents)

    def load_recipes(self, path: str):
        """
        Load recipes from the given directory
        """
        for fn in os.listdir(path):
            if not fn.endswith(".yaml"):
                continue
            with open(os.path.join(path, fn), "rt") as fd:
                recipe = yaml.load(fd, Loader=yaml.SafeLoader)
            inputs = recipe.get("inputs")
            if inputs is not None:
                for name, input_contents in inputs.items():
                    if isinstance(input_contents, list):
                        for ic in input_contents:
                            self.pantry.add_input(self._build_input(name, fn, recipe, ic))
                    else:
                        self.pantry.add_input(self._build_input(name, fn, recipe, input_contents))
            if "recipe" in recipe:
                self.recipes.add(self._build_recipe(fn[:-5], recipe, recipe["recipe"]))

    def make_orders(self) -> List[Order]:
        """
        Generate all possible orders for all available recipes
        """
        res = []
        from .mixer import Mixers
        for recipe in self.recipes.recipes:
            res.extend(Mixers.make_orders(recipe, self.pantry))
        return res


class EmptyKitchen(Kitchen):
    """
    Kitchen with an empty pantry, used only to load recipe and input
    information in order to generate documentation
    """
    def __init__(self):
        super().__init__()
        from .pantry import Pantry
        self.pantry: Pantry = Pantry()


class WorkingKitchen(Kitchen):
    def __init__(self, workdir: Optional[str] = None):
        """
        If no working directory is provided, it uses a temporary one
        """
        super().__init__()
        if workdir is None:
            self.tempdir = tempfile.TemporaryDirectory()
            self.workdir = self.context_stack.enter_context(self.tempdir)
        else:
            self.tempdir = None
            self.workdir = workdir


if arkimet is not None:
    class ArkimetRecipesMixin:
        def __init__(self, *args, **kw):
            super().__init__(*args, **kw)

            # Arkimet session
            #
            # Force directory segments so we can access each data by filesystem
            # path
            self.session = self.context_stack.enter_context(arkimet.dataset.Session(force_dir_segments=True))

    class ArkimetEmptyKitchen(ArkimetRecipesMixin, EmptyKitchen):
        """
        Arkimet-based kitchen used to load recipes but not prepare products
        """
        pass

    class ArkimetKitchen(ArkimetRecipesMixin, WorkingKitchen):
        def __init__(self, *args, **kw):
            super().__init__(*args, **kw)
            from .pantry import ArkimetPantry
            self.pantry = ArkimetPantry(root=self.workdir, session=self.session)


class EccodesEmptyKitchen(EmptyKitchen):
    """
    Eccodes-based kitchen used to load recipes but not prepare products
    """
    pass


class EccodesKitchen(WorkingKitchen):
    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        from .pantry import EccodesPantry
        self.pantry = EccodesPantry(root=self.workdir)
