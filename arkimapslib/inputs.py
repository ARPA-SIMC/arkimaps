#from __future__ import annotations
from typing import TYPE_CHECKING, Dict, Any, Optional, NamedTuple, Type, List, Iterator
from collections import defaultdict
import os
import sys
import subprocess
import shutil
import logging
from .utils import ClassRegistry

def type_check():
    return (sys.version_info[0] == 3 and sys.version_info[1] < 7) or TYPE_CHECKING

if type_check():
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

    def preprocess(self):
        """
        Hook into inputs to run preprocessors if needed
        """
        for name, inputs in self.recipe.inputs.items():
            for i in inputs:
                i.preprocess(self)

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

    def preprocess(self, inputs: Inputs):
        """
        Run preprocessing commands if needed by this input type
        """
        # Default implementation is no preprocessing
        pass

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

    def __init__(self, step: int = None, **kw):
        if step is None:
            raise RuntimeError("step must be present for 'decumulate' inputs")
        super().__init__(**kw)
        self.step = int(step)
        self.dirname = f"{self.name}_decumulate_{self.step}"

    def preprocess(self, inputs: Inputs):
        """
        Run preprocessing commands if needed by this input type
        """
        super().preprocess(inputs)

        # List inputs that need preprocessing
        sources = []
        for input_files in inputs.steps.values():
            for f in input_files:
                if f.info != self:
                    continue
                sources.append(f)

        # Don't run preprocessing if we don't have data to preprocess
        if not sources:
            return

        data_dir = os.path.join(inputs.input_dir, self.dirname)
        stamp_file = os.path.join(data_dir, "done")
        if os.path.exists(stamp_file):
            return

        os.makedirs(data_dir, exist_ok=True)

        grib_filter_rules = os.path.join(data_dir, "filter_rules")
        with open(grib_filter_rules, "wt") as fd:
            print(f'write "{data_dir}/[endStep].grib";', file=fd)

        # We could pipe the output of vg6d_transform directly into grib_filter,
        # but grib_filter errors in case of empty input with the same exit code
        # as having a nonexisting file as input, so we can't tell the ok
        # situation in which vg6d_transform doesn't find enough data, from a
        # bug causing a wrong invocation.
        # As a workaround, we need a temporary file, so we can check if it's
        # empty before passing it to grib_filter
        decumulated_data = os.path.join(data_dir, "decumulated.grib")
        if os.path.exists(decumulated_data):
            os.unlink(decumulated_data)

        cmd = ["vg6d_transform", "--comp-stat-proc=1",
               f"--comp-step=0 {self.step:02d}", "--comp-frac-valid=0"]
        if self.step != 24:
            cmd.append("--comp-full-steps")
        cmd += ["-", decumulated_data]
        v6t = subprocess.Popen(cmd, stdin=subprocess.PIPE, env={"LOG4C_PRIORITY": "debug"})
        for f in sources:
            with open(f.pathname, "rb") as fd:
                shutil.copyfileobj(fd, v6t.stdin)
        v6t.stdin.close()
        v6t.wait()
        if v6t.returncode != 0:
            raise RuntimeError(f"vg6d_transform exited with code {v6t.returncode}")

        if not os.path.exists(decumulated_data) or os.path.getsize(decumulated_data) == 0:
            return

        subprocess.run(["grib_filter", grib_filter_rules, decumulated_data], check=True)

        with open(stamp_file, "wb"):
            pass

    def select_file(self, inputs: Inputs, name: str, step: int) -> "InputFile":
        """
        Given a recipe input name, a step, and available input files for that
        step, select the input file (or generate a new one) that can be used as
        input for the recipe
        """
        f = os.path.join(inputs.input_dir, self.dirname, f"{step}.grib")
        if os.path.exists(f):
            return InputFile(
                    pathname=f,
                    name=name,
                    step=step,
                    info=self)
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
