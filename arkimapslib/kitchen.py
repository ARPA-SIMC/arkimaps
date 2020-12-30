from __future__ import annotations
from typing import TYPE_CHECKING, Dict, Any
import os
import yaml
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
    def __init__(self, workdir: str):
        from .recipes import Recipes
        from .pantry import Pantry
        self.workdir = workdir
        self.recipes = Recipes()
        self.pantry: Pantry = self._build_pantry(workdir)

    def _build_pantry(self, workdir: str):
        raise NotImplementedError(f"{self.__class__.__name__}._build_pantry() not implemented")

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


if arkimet is not None:
    class ArkimetKitchen(Kitchen):
        def __init__(self, workdir: str):
            super().__init__(workdir)

            # Arkimet session
            #
            # Force directory segments so we can access each data by filesystem
            # path
            self.session = arkimet.dataset.Session(force_dir_segments=True)

        def _build_pantry(self, workdir: str):
            from .pantry import ArkimetPantry
            return ArkimetPantry(self, workdir)

        def _build_recipe(self, name: str, info: Kwargs):
            from .recipes import ArkimetRecipe
            return ArkimetRecipe(name, info, self.session)


class EccodesKitchen(Kitchen):
    def _build_pantry(self, workdir: str):
        from .pantry import EccodesPantry
        return EccodesPantry(self, workdir)

    def _build_recipe(self, name: str, info: Kwargs):
        from .recipes import EccodesRecipe
        return EccodesRecipe(name, info)
