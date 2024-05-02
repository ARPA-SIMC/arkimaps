# from __future__ import annotations
import contextlib
import datetime
import os
from pathlib import Path
import tempfile
from typing import Any, Dict, List, Optional, Set, Union

import yaml

try:
    import arkimet

    HAVE_ARKIMET = True
except ModuleNotFoundError:
    HAVE_ARKIMET = False

from . import orders, pantry
from .config import Config
from .flavours import Flavour
from .recipes import Recipe
from .inputs import Inputs
from .types import ModelStep
from .definitions import Definitions

# if TYPE_CHECKING:
# Used for kwargs-style dicts
Kwargs = Dict[str, Any]


class Kitchen:
    """
    Shared context for this arkimaps run
    """

    pantry: "pantry.Pantry"

    def __init__(self, *, definitions: Definitions):
        self.config = definitions.config
        self.defs = definitions
        self.context_stack = contextlib.ExitStack()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return self.context_stack.__exit__(*args)

    def list_inputs(self, flavours: List[Flavour]) -> Set[str]:
        """
        Filter the available of recipes according the flavours' recipe filters,
        and return the names of all possible inputs that can be used by the
        remaining recipes
        """
        all_inputs: Set[str] = set()
        for recipe in self.defs.recipes:
            for flavour in flavours:
                if not flavour.allows_recipe(recipe):
                    continue
                all_inputs.update(flavour.list_inputs_recursive(recipe, self.pantry))
        return all_inputs

    def document_recipes(self, flavour: Flavour, path: str):
        """
        Generate markdown documentation for all the recipes found.

        Write documentation to the given path
        """
        for recipe in self.defs.recipes:
            dest = os.path.join(path, recipe.name) + ".md"
            recipe.document(flavour, self.pantry, dest)


class WorkingKitchen(Kitchen):
    pantry: "pantry.DispatchPantry"

    def __init__(self, *, definitions: Definitions, workdir: Optional[Path] = None):
        """
        If no working directory is provided, it uses a temporary one
        """
        super().__init__(definitions=definitions)
        self.tempdir: Optional[tempfile.TemporaryDirectory]
        self.workdir: Path

        if workdir is None:
            self.tempdir = tempfile.TemporaryDirectory()
            self.workdir = Path(self.context_stack.enter_context(self.tempdir))
        else:
            self.tempdir = None
            self.workdir = workdir

    def fill_pantry(self, path: Optional[Path] = None, flavours: Optional[List[Flavour]] = None):
        """
        Fill the pantry from the given path or standard input
        """
        if not flavours:
            self.pantry.fill(path)
        else:
            all_inputs = self.list_inputs(flavours)
            self.pantry.fill(path, input_filter=all_inputs)

    def make_orders(self, flavour: Union[Flavour, str], recipe: Optional[str] = None) -> List[orders.Order]:
        """
        Generate all possible orders for all available recipes
        """
        if isinstance(flavour, str):
            flavour = self.defs.flavours[flavour]

        recipes: List[Recipe]
        if recipe is None:
            recipes = list(self.defs.recipes)
        else:
            recipes = [self.defs.recipes.get(recipe)]

        res: List[orders.Order] = []
        for rec in recipes:
            if not flavour.allows_recipe(rec):
                continue
            res.extend(flavour.make_orders(rec, self.pantry))
        return res

    def make_order(
        self,
        recipe: Recipe,
        flavour: Flavour,
        step: Union[None, int, str, ModelStep],
        reftime: Optional[datetime.datetime],
    ) -> orders.Order:
        """
        Generate all possible orders for all available recipes
        """
        selected = []
        for order in flavour.make_orders(recipe, self.pantry):
            if step is not None and order.instant.step != step:
                continue
            if reftime is not None and order.instant.reftime != reftime:
                continue
            selected.append(order)
        if not selected:
            raise RuntimeError(f"not enough data to prepare {recipe.name}")
        selected.sort(key=lambda x: x.instant)
        return selected[0]


class ArkimetRecipesMixin(Kitchen):
    pantry: "pantry.ArkimetBasePantry"

    def __init__(self, **kwargs):
        # Arkimet session
        #
        # Force directory segments so we can access each data by filesystem
        # path
        super().__init__(**kwargs)
        if HAVE_ARKIMET is False:
            raise RuntimeError("Arkimet processing functionality is needed, but arkimet is not installed")
        self.session = self.context_stack.enter_context(arkimet.dataset.Session(force_dir_segments=True))

    def get_merged_arki_query(self, flavours: List[Flavour]):
        input_names = set()
        for flavour in flavours:
            for recipe in self.defs.recipes:
                input_names.update(flavour.list_inputs_recursive(recipe, self.pantry))

        merged = None
        for input_name in input_names:
            for inp in self.defs.inputs[input_name]:
                matcher = self.pantry.arkimet_matcher(inp)
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

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.pantry = pantry.ArkimetEmptyPantry(self.session, inputs=self.defs.inputs)


class ArkimetKitchen(ArkimetRecipesMixin, WorkingKitchen):
    pantry: "pantry.ArkimetPantry"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        from .pantry import ArkimetPantry

        self.pantry = ArkimetPantry(root=self.workdir, session=self.session, inputs=self.defs.inputs)


class EccodesEmptyKitchen(Kitchen):
    """
    Eccodes-based kitchen used to load recipes but not prepare products
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.pantry = pantry.EmptyPantry(inputs=self.defs.inputs)


class EccodesKitchen(WorkingKitchen):
    def __init__(self, *, grib_input=False, **kwargs):
        super().__init__(**kwargs)
        self.pantry = pantry.EccodesPantry(root=self.workdir, grib_input=grib_input, inputs=self.defs.inputs)
