# Workaround for https://github.com/pydantic/pydantic/issues/11613
# from __future__ import annotations

import inspect
import json
import logging
import os
from typing import TYPE_CHECKING, Any, Dict, Iterable, List, Optional, TextIO, Type

from . import steps, toposort
from .config import Config
from .lint import Lint
from .models import BaseDataModel, pydantic
from .component import RootComponent, TypeRegistry
from .steps import Step

if TYPE_CHECKING:
    from . import flavours, pantry

log = logging.getLogger("arkimaps.recipes")


class Recipes:
    """
    Repository of all known recipes
    """

    def __init__(self, config: Config) -> None:
        self.config = config
        self.recipes: Dict[str, "Recipe"] = {}
        # Temporary storage for derived recipes not yet instantiated
        self.new_derived: Dict[str, Dict[str, Any]] = {}

    def __iter__(self):
        return self.recipes.values().__iter__()

    def add(self, name: str, defined_in: str, args: Dict[str, Any]) -> None:
        """
        Add a recipe to this recipes collection
        """
        recipe = Recipe(config=self.config, name=name, defined_in=defined_in, args=args)
        old = self.recipes.get(recipe.name)
        if old is not None:
            raise RuntimeError(f"{recipe.name} is defined both in {old.defined_in!r} and in {recipe.defined_in!r}")
        self.recipes[recipe.name] = recipe

    def add_derived(self, *, name: str, defined_in: str, extends: str, **kwargs: Any) -> None:
        """
        Add the definition of a derived recipe to be instantiated later
        """
        if extends is None:
            raise RuntimeError(f"{name} in {defined_in!r} does not contain an 'extends' entry")

        old = self.recipes.get(name)
        if old is not None:
            raise RuntimeError(f"{name} is defined both in {old.defined_in!r} and in {defined_in!r}")

        old_derived = self.new_derived.get(name)
        if old_derived is not None:
            raise RuntimeError(f"{name} is defined both in {old_derived['defined_in']!r} and in {defined_in!r}")

        self.new_derived[name] = {
            "defined_in": defined_in,
            "extends": extends,
            **kwargs,
        }

    def resolve_derived(self) -> None:
        """
        Instantiate all recipes in new_derived
        """
        if not self.new_derived:
            return

        # Sort the postponed recipes topologically, so we can instantiate them
        # in dependency order

        # Start with the existing recipes, that have no dependencies
        deps: Dict[str, Iterable[str]] = {name: () for name in self.recipes}

        # Add the derived recipes in the queue
        for name, info in self.new_derived.items():
            deps[name] = (info["extends"],)

        # Instantiate recipes topologically sorted by dependencies
        for name in toposort.sort(deps):
            if name in self.recipes:
                continue

            info = self.new_derived.pop(name)
            parent = self.recipes[info.pop("extends")]
            kwargs = Recipe.inherit(name=name, parent=parent, **info)
            recipe = Recipe(config=self.config, **kwargs)
            self.recipes[name] = recipe

    def get(self, name: str) -> "Recipe":
        """
        Return a recipe by name
        """
        res = self.recipes.get(name)
        if res is None:
            raise KeyError(f"Recipe `{name}` does not exist")
        return res


class RecipeStep:
    """
    A step of a recipe, as defined in the recipe file.

    This does not contain the full information for the step, as it can be
    integrated with Step class defaults and step overrides from the flavour
    """

    def __init__(
        self,
        *,
        config: Config,
        name: str,
        defined_in: str,
        step_class: Type[steps.Step[Any, Any]],
        args: Dict[str, Any],
        id: Optional[str] = None,
    ):
        self.config = config
        self.name: str = name
        self.defined_in: str = defined_in
        self.step_class: Type[steps.Step[Any, Any]] = step_class
        self.args: Dict[str, Any] = args
        self.id: Optional[str] = id

    def lint(self, lint: Lint) -> None:
        self.step_class.lint(lint, defined_in=self.defined_in, name=self.name, step=self.name, args=self.args)

    def derive(self) -> Dict[str, Any]:
        """
        Create a raw recipe step definition based on this step
        """
        res = dict(self.args)
        res["step"] = self.name
        if self.id is not None:
            res["id"] = self.id
        return res

    def change(self, change: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a raw recipe step definition based on this step, plus the given
        changeset
        """
        res = dict(self.args)
        self.step_class.apply_change(res, change)
        res["step"] = self.name
        if self.id is not None:
            res["id"] = self.id
        return res

    def document(self, flavour: "flavours.Flavour[Any]", file: TextIO) -> None:
        """
        Document this recipe step
        """
        print(inspect.getdoc(self.step_class), file=file)
        print(file=file)
        if self.args:
            print("With arguments:", file=file)
            print("```", file=file)
            # FIXME: dump as yaml?
            print(json.dumps(self.args, indent=2), file=file)
            print("```", file=file)


class RecipeSpec(BaseDataModel):
    """
    Data model for Recipes
    """

    #: Optional notes for the documentation
    notes: Optional[str] = None
    #: Long description for the recipe
    description: str = "Unnamed recipe"
    #: Informational fields about the recipe
    info: Optional[Dict[str, Any]] = None
    #: Unparsed recipe steps
    recipe: List[Dict[str, Any]] = pydantic.Field(default_factory=list)


class Recipe(RootComponent[RecipeSpec]):
    """
    A parsed and validated recipe
    """

    __registry__ = TypeRegistry["Recipe"]()
    lookup = __registry__.lookup
    Spec = RecipeSpec

    def __init__(self, *, config: Config, name: str, defined_in: str, args: Dict[str, Any]) -> None:
        super().__init__(config=config, name=name, defined_in=defined_in, args=args)

        # Parse the recipe steps
        self.steps: List[RecipeStep] = []
        for s in self.spec.recipe:
            args = s.copy()
            step = args.pop("step", None)
            if step is None:
                raise RuntimeError("recipe step does not contain a 'step' name")
            step_class = Step.step_by_name(step)
            if step_class is None:
                raise RuntimeError(f"step {step} not found")
            id = args.pop("id", None)
            self.steps.append(
                RecipeStep(
                    config=self.config, name=step, defined_in=defined_in, step_class=step_class, args=args, id=id
                )
            )

    def lint(self, lint: Lint) -> None:
        """
        Consistency check the recipe configuration
        """
        for recipe_step in self.steps:
            recipe_step.lint(lint)

    @classmethod
    def inherit(
        cls, *, name: str, defined_in: str, parent: "Recipe", change: Optional[Dict[str, Any]] = None, **kwargs: Any
    ) -> Dict[str, Any]:
        """
        Compute recipe arguments deriving them from an existing one
        """
        # Get list of steps to change
        changes = change if change is not None else {}

        # If elements aren't specified, use those from the parent recipe
        kwargs.setdefault("notes", parent.spec.notes)
        kwargs.setdefault("description", parent.spec.description)

        # Build the new list of steps, based on the parent list
        steps: List[Dict[str, Any]] = []
        for recipe_step in parent.steps:
            if recipe_step.id in changes:
                step = recipe_step.change(changes[recipe_step.id])
            else:
                step = recipe_step.derive()
            steps.append(step)
        kwargs["recipe"] = steps
        kwargs["name"] = name
        kwargs["defined_in"] = defined_in
        return {"name": kwargs.pop("name"), "defined_in": kwargs.pop("defined_in"), "args": kwargs}

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return self.name

    def summarize(self) -> Dict[str, Any]:
        """
        Return a structure describing this Recipe, to use for the render order
        summary
        """
        return {
            "name": self.name,
            "defined_in": self.defined_in,
            "description": self.spec.description,
            "info": self.spec.info or {},
        }

    def document(self, flavour: "flavours.Flavour[Any]", pantry: "pantry.Pantry", dest: str) -> None:
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        with open(dest, "w") as fd:
            print(f"# {self.name}: {self.spec.description}", file=fd)
            print(file=fd)
            if self.spec.notes:
                print("## Notes", file=fd)
                print(file=fd)
                print(self.spec.notes, file=fd)
                print(file=fd)
            print("## Inputs", file=fd)
            print(file=fd)
            # TODO: list only inputs explicitly required by the recipe
            for name in flavour.list_inputs_recursive(self, pantry):
                inputs = pantry.inputs.get(name)
                if inputs is None:
                    print(f"* **{name}** (input details are missing)", file=fd)
                else:
                    print(f"* **{name}**:", file=fd)
                    if len(inputs) == 1:
                        inputs[0].document(indent=4, file=fd)
                    else:
                        for i in inputs:
                            print(f"    * Model **{i.spec.model}**:", file=fd)
                            i.document(indent=8, file=fd)
            print(file=fd)
            print("## Steps", file=fd)
            print(file=fd)
            for step in self.steps:
                print(f"### {step.name}", file=fd)
                print(file=fd)
                step.document(flavour, file=fd)
                print(file=fd)
