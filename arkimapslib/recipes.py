# from __future__ import annotations
import inspect
import json
import logging
import os
from typing import TYPE_CHECKING, Any, Dict, Iterable, List, Optional, Set, TextIO, Type

from . import steps, toposort
from .config import Config
from .lint import Lint
from .models import BaseDataModel, pydantic
from .component import RootComponent, TypeRegistry
from .utils import setdefault_deep

if TYPE_CHECKING:
    from . import flavours, inputs, pantry

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


class RecipeStepSkipped(Exception):
    """
    Exception raised constructor to signal that the step should be skipped
    """

    pass


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
        step_class: Type[steps.Step],
        args: Dict[str, Any],
        id: Optional[str] = None,
    ):
        self.config = config
        self.name: str = name
        self.defined_in: str = defined_in
        self.step_class: Type[steps.Step] = step_class
        self.args: Dict[str, Any] = args
        self.id: Optional[str] = id

    def lint(self, lint: Lint) -> None:
        args = self.compile_args(lint.flavour)
        if bool(args.pop("skip", False)):
            return
        self.step_class.lint(lint, defined_in=self.defined_in, name=self.name, step=self.name, args=args)

    def create_step(self, flavour: "flavours.Flavour", input_files: Dict[str, "inputs.InputFile"]) -> steps.Step:
        """
        Instantiate the Step
        """
        args = self.compile_args(flavour)
        if bool(args.pop("skip", False)):
            raise RecipeStepSkipped()
        return self.step_class(
            config=self.config, name=self.name, defined_in=self.defined_in, args=args, sources=input_files
        )

    def get_input_names(self, flavour: "flavours.Flavour") -> Set[str]:
        """
        Get the names of inputs needed by this step
        """
        args = self.compile_args(flavour)
        if bool(args.pop("skip", False)):
            return set()
        return self.step_class.get_input_names(args)

    def compile_args(self, flavour: "flavours.Flavour") -> Dict[str, Any]:
        """
        Compute the set of arguments for this step, based on flavour
        information, arguments defined in the recipe, and step class defaults
        """
        flavour_step = flavour.step_config(self.name)

        # Take recipe-defined args
        res = self.args.copy()

        # Add missing bits from flavour
        for k, v in flavour_step.options.items():
            res.setdefault(k, v)

        # Add missing bits from step class defaults
        if self.step_class.DEFAULTS is not None:
            for k, v in self.step_class.DEFAULTS.items():
                res.setdefault(k, v)

        if self.step_class.DEEP_DEFAULTS is not None:
            setdefault_deep(res, self.step_class.DEEP_DEFAULTS)

        return res

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

    def document(self, flavour: "flavours.Flavour", file: TextIO):
        """
        Document this recipe step
        """
        args = self.compile_args(flavour)
        print(inspect.getdoc(self.step_class), file=file)
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

    @pydantic.validator("mixer")
    def mixer_in_registry(cls, value):
        from .mixers import mixers

        if value not in mixers.registry:
            raise ValueError(f"Unknown mixer: {value!r}. Use one of {', '.join(sorted(mixers.registry))}")
        return value


class Recipe(RootComponent[RecipeSpec]):
    """
    A parsed and validated recipe
    """

    __registry__ = TypeRegistry["Recipe"]()

    Spec = RecipeSpec

    def __init__(self, *, config: Config, name: str, defined_in: str, args: Dict[str, Any]) -> None:
        from .mixers import mixers

        super().__init__(config=config, name=name, defined_in=defined_in, args=args)

        # Parse the recipe steps
        self.steps: List[RecipeStep] = []
        step_collection = mixers.get_steps(self.spec.mixer)
        for s in self.spec.recipe:
            args = s.copy()
            step = args.pop("step", None)
            if step is None:
                raise RuntimeError("recipe step does not contain a 'step' name")
            step_class = step_collection.get(step)
            if step_class is None:
                raise RuntimeError(f"step {step} not found in mixer {self.spec.mixer}")
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

    def document(self, flavour: "flavours.Flavour", pantry: "pantry.Pantry", dest: str):
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        with open(dest, "w") as fd:
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
