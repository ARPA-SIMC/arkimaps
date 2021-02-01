from __future__ import annotations
from typing import TYPE_CHECKING, Dict, Any, Optional, NamedTuple, Type, List, Iterator
from collections import defaultdict
import os
import logging
from .utils import ClassRegistry

if TYPE_CHECKING:
    import arkimet
    from .recipes import Recipe

    # Used for kwargs-style dicts
    Kwargs = Dict[str, Any]

log = logging.getLogger("arkimaps.inputs")


class InputTypes(ClassRegistry["Input"]):
    """
    Registry of available Input implementations
    """
    registry: Dict[str, Type["Input"]] = {}


class Inputs:
    """
    Manage the input of a recipe inside its input directory
    """
    def __init__(
            self,
            recipe: Recipe,
            input_dir: str):
        """
        Look into the pantry filesystem storage and take note of what files are
        available
        """
        self.recipe = recipe
        self.input_dir = input_dir
        self.steps: Dict[int, List[InputFile]] = defaultdict(list)

        for input_file in self.read():
            self.steps[input_file.step].append(input_file)

    def read(self) -> Iterator["InputFile"]:
        for fname in os.listdir(self.input_dir):
            if not fname.endswith(".grib"):
                continue
            name, step = fname[:-5].rsplit("+", 1)
            model, name = name.split("_", 1)
            step = int(step)

            # Lookup the right Input in the recipe, by model name
            for i in self.recipe.inputs[name]:
                if i.name == model:
                    info = i
                    break
            else:
                continue

            yield InputFile(
                    pathname=os.path.join(self.input_dir, fname),
                    name=name,
                    step=step,
                    info=info)

    def for_step(self, step):
        """
        Return input files for the given step.

        Return None if some of the inputs are not satisfied for this step
        """
        res = {}
        for name, inputs in self.recipe.inputs.items():
            found = None
            # Try all input alternatives in order
            for i in inputs:
                found = i.select_file(self, name, step)
                # Stop at the first matching input alternative
                if found:
                    break
            if not found:
                log.debug("%s+%03d: data for input %s not found: skipping", self.recipe.name, step, name)
                return None
            res[name] = found

        return res


@InputTypes.register
class Input:
    NAME = "default"
    """
    An input element to a recipe
    """

    def __init__(
            self,
            name: str,
            arkimet: str,
            eccodes: str,
            mgrib: Optional[Kwargs] = None):
        # name, identifying this instance among other alternatives for this input
        self.name = name
        # arkimet matcher filter
        self.arkimet = arkimet
        # Compiled arkimet matcher, when available/used
        self.arkimet_matcher: Optional[arkimet.Matcher] = None
        # grib_filter if expression
        self.eccodes = eccodes
        # Extra arguments passed to mgrib on loading
        self.mgrib = mgrib

    @classmethod
    def create(cls, type: str = "default", **kw):
        """
        Instantiate an input by the ``type`` key in its recipe definition
        """
        try:
            impl_cls = InputTypes.by_name(type)
        except KeyError as e:
            raise KeyError(
                    f"recipe requires unknown input {type}. Available: {', '.join(InputTypes.registry.keys())}") from e
        return impl_cls(**kw)

    def __getstate__(self):
        # Don't pickle arkimet_matcher, which is unpicklable and undeeded
        return {
            "name": self.name,
            "arkimet": self.arkimet,
            "arkimet_matcher": None,
            "eccodes": self.eccodes,
            "mgrib": self.mgrib,
        }

    def select_file(self, inputs: Inputs, name: str, step: int) -> "InputFile":
        """
        Given a recipe input name, a step, and available input files for that
        step, select the input file (or generate a new one) that can be used as
        input for the recipe
        """
        input_files = inputs.steps.get(step)
        if input_files is None:
            return None

        # Look for files that satisfy this input
        for f in input_files:
            if f.name == name and f.info == self:
                return f
        return None

    def compile_arkimet_matcher(self, session: arkimet.Session):
        self.arkimet_matcher = session.matcher(self.arkimet)

    def document(self, file, indent=4):
        """
        Document the details about this input in Markdown
        """
        ind = " " * indent
        print(f"{ind}* **Arkimet matcher**: `{self.arkimet}`", file=file)
        print(f"{ind}* **grib_filter matcher**: `{self.eccodes}`", file=file)
        if self.mgrib:
            for k, v in self.mgrib.items():
                print(f"{ind}* **mgrib {{k}}**: `{v}`", file=file)


@InputTypes.register
class Decumulate(Input):
    """
    Decumulate inputs
    """
    NAME = "decumulate"

    def select_file(self, inputs: Inputs, name: str, step: int) -> "InputFile":
        """
        Given a recipe input name, a step, and available input files for that
        step, select the input file (or generate a new one) that can be used as
        input for the recipe
        """
        input_files = inputs.steps.get(step)
        if input_files is None:
            return None

        # Look for files that satisfy this input
        for f in input_files:
            if f.name == name and f.info == self:
                return f
        return None

    def document(self, file, indent=4):
        ind = " " * indent
        print(f"{ind}* **Preprocessing**: decumulation", file=file)
        super().document(file, indent)


class InputFile(NamedTuple):
    """
    An input file stored in the pantry
    """
    # Pathname to the file
    pathname: str
    # Input name in the recipe
    name: str
    # Forecast step
    step: int
    # Input with information about the file
    info: Input
