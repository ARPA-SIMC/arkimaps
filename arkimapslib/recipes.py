# from __future__ import annotations
import inspect
import json
import logging
import os
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Sequence, Set, TextIO, Type

from . import steps, toposort
from .config import Config
from .lint import Lint
from .models import BaseDataModel, pydantic

if TYPE_CHECKING:
    from . import pantry

log = logging.getLogger("arkimaps.recipes")


class Recipes:
    """
    Repository of all known recipes
    """

    def __init__(self) -> None:
        self.recipes: Dict[str, "Recipe"] = {}
        # Temporary storage for derived recipes not yet instantiated
        self.new_derived: Dict[str, Dict[str, Any]] = {}

    def __iter__(self):
        return self.recipes.values().__iter__()

    def add(self, *, lint: Optional[Lint] = None, **kwargs):
        """
        Add a recipe to this recipes collection
        """
        if lint:
            Recipe.lint(lint, **kwargs)
        recipe = Recipe(**kwargs)
        old = self.recipes.get(recipe.name)
        if old is not None:
            raise RuntimeError(f"{recipe.name} is defined both in {old.defined_in!r} and in {recipe.defined_in!r}")
        self.recipes[recipe.name] = recipe

    def add_derived(self, *, name: str, extends: str, defined_in: str, lint: Optional[Lint] = None, **kwargs):
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

    def resolve_derived(self, *, lint: Optional[Lint] = None):
        """
        Instantiate all recipes in new_derived
        """
        if not self.new_derived:
            return

        # Sort the postponed recipes topologically, so we can instantiate them
        # in dependency order

        # Start with the existing recipes, that have no dependencies
        deps = {name: {} for name in self.recipes}

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
            if lint:
                Recipe.lint(lint, **kwargs)
            self.recipes[name] = Recipe(**kwargs)

    def get(self, name: str):
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

    def __init__(self, name: str, step: Type[steps.Step], args: dict[str, Any], id: Optional[str] = None):
        self.name: str = name
        self.step: Type[steps.Step] = step
        self.args: dict[str, Any] = args
        self.id: Optional[str] = id

    def get_input_names(self, step_config: steps.FlavourStep) -> Set[str]:
        """
        Get the names of inputs needed by this step
        """
        return self.step.get_input_names(step_config, self.args)

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
        self.step.apply_change(res, change)
        res["step"] = self.name
        if self.id is not None:
            res["id"] = self.id
        return res

    def document(self, file: TextIO):
        """
        Document this recipe step
        """
        args = self.step.compile_args(steps.FlavourStep(self.name), self.args)
        print(inspect.getdoc(self.step), file=file)
        print(file=file)
        if args:
            print("With arguments:", file=file)
            print("```", file=file)
            # FIXME: dump as yaml?
            print(json.dumps(args, indent=2), file=file)
            print("```", file=file)


class RecipeSpec(BaseDataModel):
    """
    Data model for Recipes
    """

    #: Optional notes for the documentation
    notes: Optional[str] = None
    #: Long description for the recipe
    description: str = "Unnamed recipe"
    #: Name of the mixer to use
    mixer: str = "default"
    #: Informational fields about the recipe
    info: Optional[Dict[str, Any]] = None
    #: Unparsed recipe steps
    recipe: List[Dict[str, Any]] = pydantic.Field(default_factory=list)


class Recipe:
    """
    A parsed and validated recipe
    """

    Spec = RecipeSpec

    def __init__(
        self,
        *,
        name: str,
        defined_in: str,
        **kwargs,
    ):
        from .mixers import mixers

        # Name of the recipe
        self.name = name
        # File where the recipe was defined
        self.defined_in = defined_in
        # Input data as specified in the recipe
        self.spec = self.Spec(**kwargs)

        # Parse the recipe steps
        self.steps: List[RecipeStep] = []
        step_collection = mixers.get_steps(self.spec.mixer)
        for s in self.spec.recipe:
            args = s.copy()
            step = args.pop("step", None)
            if step is None:
                raise RuntimeError("recipe step does not contain a 'step' name")
            step_cls = step_collection.get(step)
            if step_cls is None:
                raise RuntimeError(f"step {step} not found in mixer {self.spec.mixer}")
            id = args.pop("id", None)
            self.steps.append(RecipeStep(name=step, step=step_cls, args=args, id=id))

    @classmethod
    def lint(
        cls,
        lint: Lint,
        *,
        name: str,
        defined_in: str,
        notes: Optional[str] = None,
        description: str = "Unnamed recipe",
        mixer: str = "default",
        info: Optional[Dict[str, Any]] = None,
        recipe: Sequence[Dict[str, Any]] = (),
        **kwargs: Any,
    ):
        for k, v in kwargs.items():
            lint.warn_recipe(f"Unknown parameter: {k!r}", defined_in=defined_in, name=name)

        from .mixers import mixers

        if mixer not in mixers.registry:
            lint.warn_recipe(f"Unknown mixer: {mixer!r}", defined_in=defined_in, name=name)
        else:
            step_collection = mixers.get_steps(mixer)
            for s in recipe:
                if not isinstance(s, dict):
                    lint.warn_recipe(f"Recipe step {s!r} is not a dict", defined_in=defined_in, name=name)
                    continue
                s = s.copy()
                step = s.pop("step", None)
                if step is None:
                    lint.warn_recipe(f"Recipe step {s!r} does not contain 'step'", defined_in=defined_in, name=name)
                    continue
                step_cls = step_collection.get(step)
                if step_cls is None:
                    lint.warn_recipe(
                        f"Recipe step {s!r} contains invalid step={step!r}", defined_in=defined_in, name=name
                    )
                    continue
                step_cls.lint(lint, defined_in=defined_in, name=name, step=step, **s)

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
        kwargs.setdefault("mixer", parent.spec.mixer)

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
        return kwargs

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
            "info": self.spec.info,
        }

    def document(self, pantry: "pantry.Pantry", dest: str):
        from .flavours import Flavour

        empty_flavour = Flavour(config=Config(), name="default", defined_in=__file__)
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        with open(dest, "wt") as fd:
            print(f"# {self.name}: {self.spec.description}", file=fd)
            print(file=fd)
            print(f"Mixer: **{self.spec.mixer}**", file=fd)
            print(file=fd)
            if self.spec.notes:
                print("## Notes", file=fd)
                print(file=fd)
                print(self.spec.notes, file=fd)
                print(file=fd)
            print("## Inputs", file=fd)
            print(file=fd)
            # TODO: list only inputs explicitly required by the recipe
            for name in empty_flavour.list_inputs_recursive(self, pantry):
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
                step.document(file=fd)
                print(file=fd)
