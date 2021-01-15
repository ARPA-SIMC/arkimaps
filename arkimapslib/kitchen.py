from __future__ import annotations
from typing import TYPE_CHECKING, Dict, Any, Optional
import tempfile
import os
import yaml
import contextlib
try:
    import arkimet
except ModuleNotFoundError:
    arkimet = None

if TYPE_CHECKING:
    # Used for kwargs-style dicts
    Kwargs = Dict[str, Any]


class Kitchen:
    """
    Shared context for this arkimaps run
    """
    def __init__(self):
        from .recipes import Recipes
        self.recipes = Recipes()
        self.context_stack = contextlib.ExitStack()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return self.context_stack.__exit__(*args)

    def _build_recipe(self, name: str, info: Kwargs):
        raise NotImplementedError(f"{self.__class__.__name__}._build_recipe() not implemented")

    def load_recipes(self, path: str):
        """
        Load recipes from the given directory
        """
        for fn in os.listdir(path):
            if not fn.endswith(".yaml"):
                continue
            with open(os.path.join(path, fn), "rt") as fd:
                recipe = yaml.load(fd, Loader=yaml.SafeLoader)
            self.recipes.recipes.append(self._build_recipe(fn[:-5], recipe))


class WorkingKitchen(Kitchen):
    def __init__(self, workdir: Optional[str] = None):
        """
        If no working directory is provided, it uses a temporary one
        """
        super().__init__()
        from .pantry import Pantry
        if workdir is None:
            self.tempdir = tempfile.TemporaryDirectory()
            self.workdir = self.context_stack.enter_context(self.tempdir)
        else:
            self.tempdir = None
            self.workdir = workdir
        self.pantry: Pantry = self._build_pantry(self.workdir)

    def _build_pantry(self, workdir: str):
        raise NotImplementedError(f"{self.__class__.__name__}._build_pantry() not implemented")


if arkimet is not None:
    class ArkimetRecipesMixin:
        def __init__(self, *args, **kw):
            super().__init__(*args, **kw)

            # Arkimet session
            #
            # Force directory segments so we can access each data by filesystem
            # path
            self.session = self.context_stack.enter_context(arkimet.dataset.Session(force_dir_segments=True))

        def _build_recipe(self, name: str, info: Kwargs):
            from .recipes import ArkimetRecipe
            return ArkimetRecipe(name, info, self.session)

    class ArkimetEmptyKitchen(ArkimetRecipesMixin, Kitchen):
        """
        Arkimet-based kitchen used to load recipes but not prepare products
        """
        pass

    class ArkimetKitchen(ArkimetRecipesMixin, WorkingKitchen):
        def _build_pantry(self, workdir: str):
            from .pantry import ArkimetPantry
            return ArkimetPantry(self, workdir)


class EccodesRecipesMixin:
    def _build_recipe(self, name: str, info: Kwargs):
        from .recipes import EccodesRecipe
        return EccodesRecipe(name, info)


class EccodesEmptyKitchen(EccodesRecipesMixin, Kitchen):
    """
    Eccodes-based kitchen used to load recipes but not prepare products
    """
    pass


class EccodesKitchen(EccodesRecipesMixin, WorkingKitchen):
    def _build_pantry(self, workdir: str):
        from .pantry import EccodesPantry
        return EccodesPantry(self, workdir)
