# from __future__ import annotations
from typing import Dict, Any, Optional, NamedTuple, Type, List, Union
import os
import re
import subprocess
import shutil
import shlex
import logging
from .utils import ClassRegistry

# if TYPE_CHECKING:
#     import arkimet
try:
    import arkimet
except ModuleNotFoundError:
    pass
# from .recipes import Recipe
from . import pantry

# Used for kwargs-style dicts
Kwargs = Dict[str, Any]

log = logging.getLogger("arkimaps.inputs")


class InputTypes(ClassRegistry["Input"]):
    """
    Registry of available Input implementations
    """
    registry: Dict[str, Type["Input"]] = {}


class Input:
    """
    An input element to a recipe
    """

    def __init__(self, name: str, defined_in: str, model: Optional[str] = None, mgrib: Optional['Kwargs'] = None):
        # Name of the input in the recipe
        self.name = name
        # model, identifying this instance among other alternatives for this input
        self.model = model
        # file name where this input was defined
        self.defined_in = defined_in
        # Extra arguments passed to mgrib on loading
        self.mgrib = mgrib
        # Basename of files for this input in the pantry
        # This has no path, and no +step.ext suffix
        if self.model is None:
            self.pantry_basename = self.name
        else:
            self.pantry_basename = f"{self.model}_{self.name}"

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
        return {
            "mgrib": self.mgrib,
        }

    def get_steps(self, p: "pantry.Pantry") -> Dict[int, "InputFile"]:
        """
        Scan the pantry to check what input files are available for this input.

        Return a dict mapping available steps to corresponding InputFile
        objects
        """
        fn_match = re.compile(rf"{re.escape(self.pantry_basename)}\+(\d+)\.\w+")
        res = {}
        for fn in os.listdir(p.data_root):
            mo = fn_match.match(fn)
            if not mo:
                continue
            step = int(mo.group(1))
            res[step] = InputFile(os.path.join(p.data_root, fn), self, step)
        return res

    def compile_arkimet_matcher(self, session: 'arkimet.Session'):
        """
        Hook to allow inputs to compile arkimet matchers
        """
        # Does nothing by default
        pass

    def document(self, file, indent=4):
        """
        Document the details about this input in Markdown
        """
        ind = " " * indent
        if self.mgrib:
            for k, v in self.mgrib.items():
                print(f"{ind}* **mgrib {{k}}**: `{v}`", file=file)


@InputTypes.register
class Source(Input):
    """
    An input that is data straight out of a model
    """
    NAME = "default"

    def __init__(self, arkimet: str, eccodes: str, **kw):
        super().__init__(**kw)
        # arkimet matcher filter
        self.arkimet = arkimet
        # Compiled arkimet matcher, when available/used
        self.arkimet_matcher: Optional[arkimet.Matcher] = None
        # grib_filter if expression
        self.eccodes = eccodes

    def compile_arkimet_matcher(self, session: 'arkimet.Session'):
        self.arkimet_matcher = session.matcher(self.arkimet)

    def document(self, file, indent=4):
        ind = " " * indent
        print(f"{ind}* **Arkimet matcher**: `{self.arkimet}`", file=file)
        print(f"{ind}* **grib_filter matcher**: `{self.eccodes}`", file=file)
        super().document(file, indent)


class Derived(Input):
    """
    Base class for inputs derives from other inputs
    """
    def __init__(self, inputs: Union[str, List[str]] = None, **kw):
        if inputs is None:
            raise RuntimeError(f"inputs must be present for '{self.NAME}' inputs")
        super().__init__(**kw)
        self.inputs = [inputs] if isinstance(inputs, str) else [str(x) for x in inputs]

    def generate(self, p: "pantry.Pantry"):
        """
        Generate derived products from inputs
        """
        raise NotImplementedError(f"{self.__class__.__name__}.generate() not implemented")

    def get_steps(self, p: "pantry.Pantry") -> Dict[int, "InputFile"]:
        # Check if flagfile exists, in which case skip generation
        flagfile = os.path.join(p.data_root, f"{self.pantry_basename}.processed")
        if not os.path.exists(flagfile):
            self.generate(p)
            # Create the flagfile to mark that all steps have been generated
            with open(flagfile, "wb"):
                pass
        # Rescan pantry
        return super().get_steps(p)

    def document(self, file, indent=4):
        ind = " " * indent
        print(f"{ind}* **Preprocessing**: {self.NAME}", file=file)
        print(f"{ind}* **Inputs**: {', '.join(self.inputs)}", file=file)
        super().document(file, indent)


@InputTypes.register
class Decumulate(Derived):
    """
    Decumulate inputs
    """
    NAME = "decumulate"

    def __init__(self, step: int = None, **kw):
        if step is None:
            raise RuntimeError("step must be present for 'decumulate' inputs")
        super().__init__(**kw)
        self.step = int(step)

    def generate(self, p: "pantry.Pantry"):
        if len(self.inputs) != 1:
            raise RuntimeError(f"input {self.name}: {self.NAME} has inputs {', '.join(self.inputs)} ")

        # Get the steps of our source input
        source_steps = p.get_steps(self.inputs[0])

        # TODO: check that they match the step

        # Don't run preprocessing if we don't have data to preprocess
        if not source_steps:
            return

        # Generate derived input
        grib_filter_rules = os.path.join(p.data_root, f"{self.pantry_basename}.grib_filter_rules")
        with open(grib_filter_rules, "wt") as fd:
            print(f'write "{p.data_root}/{self.pantry_basename}+[endStep].grib";', file=fd)

        # We could pipe the output of vg6d_transform directly into grib_filter,
        # but grib_filter errors in case of empty input with the same exit code
        # as having a nonexisting file as input, so we can't tell the ok
        # situation in which vg6d_transform doesn't find enough data, from a
        # bug causing a wrong invocation.
        # As a workaround, we need a temporary file, so we can check if it's
        # empty before passing it to grib_filter
        decumulated_data = os.path.join(p.data_root, f"{self.pantry_basename}-decumulated.grib")
        if os.path.exists(decumulated_data):
            os.unlink(decumulated_data)

        cmd = ["vg6d_transform", "--comp-stat-proc=1",
               f"--comp-step=0 {self.step:02d}", "--comp-frac-valid=0"]
        if self.step != 24:
            cmd.append("--comp-full-steps")
        cmd += ["-", decumulated_data]
        v6t = subprocess.Popen(cmd, stdin=subprocess.PIPE, env={"LOG4C_PRIORITY": "debug"})
        for step, input_file in source_steps.items():
            with open(input_file.pathname, "rb") as fd:
                shutil.copyfileobj(fd, v6t.stdin)
        v6t.stdin.close()
        v6t.wait()
        if v6t.returncode != 0:
            raise RuntimeError(f"vg6d_transform exited with code {v6t.returncode}")

        if not os.path.exists(decumulated_data) or os.path.getsize(decumulated_data) == 0:
            return

        subprocess.run(["grib_filter", grib_filter_rules, decumulated_data], check=True)

        os.unlink(decumulated_data)

#    def preprocess(self, inputs: Inputs):
#        """
#        Run preprocessing commands if needed by this input type
#        """
#        super().preprocess(inputs)
#
#        # List inputs that need preprocessing
#        sources = []
#        for input_files in inputs.steps.values():
#            for f in input_files:
#                if f.info != self:
#                    continue
#                sources.append(f)
#
#        # Don't run preprocessing if we don't have data to preprocess
#        if not sources:
#            return
#
#        data_dir = os.path.join(inputs.input_dir, self.dirname)
#        stamp_file = os.path.join(data_dir, "done")
#        if os.path.exists(stamp_file):
#            return
#
#        os.makedirs(data_dir, exist_ok=True)
#
#        grib_filter_rules = os.path.join(data_dir, "filter_rules")
#        with open(grib_filter_rules, "wt") as fd:
#            print(f'write "{data_dir}/[endStep].grib";', file=fd)
#
#        # We could pipe the output of vg6d_transform directly into grib_filter,
#        # but grib_filter errors in case of empty input with the same exit code
#        # as having a nonexisting file as input, so we can't tell the ok
#        # situation in which vg6d_transform doesn't find enough data, from a
#        # bug causing a wrong invocation.
#        # As a workaround, we need a temporary file, so we can check if it's
#        # empty before passing it to grib_filter
#        decumulated_data = os.path.join(data_dir, "decumulated.grib")
#        if os.path.exists(decumulated_data):
#            os.unlink(decumulated_data)
#
#        cmd = ["vg6d_transform", "--comp-stat-proc=1",
#               f"--comp-step=0 {self.step:02d}", "--comp-frac-valid=0"]
#        if self.step != 24:
#            cmd.append("--comp-full-steps")
#        cmd += ["-", decumulated_data]
#        v6t = subprocess.Popen(cmd, stdin=subprocess.PIPE, env={"LOG4C_PRIORITY": "debug"})
#        for f in sources:
#            with open(f.pathname, "rb") as fd:
#                shutil.copyfileobj(fd, v6t.stdin)
#        v6t.stdin.close()
#        v6t.wait()
#        if v6t.returncode != 0:
#            raise RuntimeError(f"vg6d_transform exited with code {v6t.returncode}")
#
#        if not os.path.exists(decumulated_data) or os.path.getsize(decumulated_data) == 0:
#            return
#
#        subprocess.run(["grib_filter", grib_filter_rules, decumulated_data], check=True)
#
#        with open(stamp_file, "wb"):
#            pass
#
#    def select_file(self, inputs: Inputs, name: str, step: int) -> "InputFile":
#        """
#        Given a recipe input model, a step, and available input files for that
#        step, select the input file (or generate a new one) that can be used as
#        input for the recipe
#        """
#        f = os.path.join(inputs.input_dir, self.dirname, f"{step}.grib")
#        if os.path.exists(f):
#            return InputFile(
#                    pathname=f,
#                    name=name,
#                    step=step,
#                    info=self)
#        return None

#    def preprocess(self, inputs: Inputs):
#        """
#        Run preprocessing commands if needed by this input type
#        """
#        # Default implementation is no preprocessing
#        pass
#
#    def select_file(self, inputs: Inputs, name: str, step: int) -> "InputFile":
#        """
#        Given a recipe input name, a step, and available input files for that
#        step, select the input file (or generate a new one) that can be used as
#        input for the recipe
#        """
#        input_files = inputs.steps.get(step)
#        if input_files is None:
#            return None
#
#        # Look for files that satisfy this input
#        for f in input_files:
#            if f.name == name and f.info == self:
#                return f
#        return None

    def document(self, file, indent=4):
        ind = " " * indent
        print(f"{ind}* **Decumulation step**: {self.step}", file=file)
        super().document(file, indent)


@InputTypes.register
class VG6DTransform(Derived):
    """
    Process inputs with vg6d_transform
    """
    NAME = "vg6d_transform"

    def __init__(self, args: Union[str, List[str]] = None, **kw):
        if args is None:
            raise RuntimeError(f"inputs must be present for '{self.NAME}' inputs")
        super().__init__(**kw)
        self.args = [args] if isinstance(args, str) else [str(x) for x in args]

#    def preprocess(self, inputs: Inputs):
#        """
#        Run preprocessing commands if needed by this input type
#        """
#        super().preprocess(inputs)
#
#        # TODO: Find available files for each input for this model
#        # TODO: match them by step
#        # TODO: when a step has len(self.inputs) inputs, generate an output
#
#        # List inputs that need preprocessing
#        sources = []
#        for input_files in inputs.steps.values():
#            for f in input_files:
#                if f.info != self:
#                    continue
#                sources.append(f)
#
#        # Don't run preprocessing if we don't have data to preprocess
#        if not sources:
#            return
#
#        data_dir = os.path.join(inputs.input_dir, self.dirname)
#        stamp_file = os.path.join(data_dir, "done")
#        if os.path.exists(stamp_file):
#            return
#
#        os.makedirs(data_dir, exist_ok=True)
#
#        grib_filter_rules = os.path.join(data_dir, "filter_rules")
#        with open(grib_filter_rules, "wt") as fd:
#            print(f'write "{data_dir}/[endStep].grib";', file=fd)
#
#        # We could pipe the output of vg6d_transform directly into grib_filter,
#        # but grib_filter errors in case of empty input with the same exit code
#        # as having a nonexisting file as input, so we can't tell the ok
#        # situation in which vg6d_transform doesn't find enough data, from a
#        # bug causing a wrong invocation.
#        # As a workaround, we need a temporary file, so we can check if it's
#        # empty before passing it to grib_filter
#        decumulated_data = os.path.join(data_dir, "decumulated.grib")
#        if os.path.exists(decumulated_data):
#            os.unlink(decumulated_data)
#
#        cmd = ["vg6d_transform", "--comp-stat-proc=1",
#               f"--comp-step=0 {self.step:02d}", "--comp-frac-valid=0"]
#        if self.step != 24:
#            cmd.append("--comp-full-steps")
#        cmd += ["-", decumulated_data]
#        v6t = subprocess.Popen(cmd, stdin=subprocess.PIPE, env={"LOG4C_PRIORITY": "debug"})
#        for f in sources:
#            with open(f.pathname, "rb") as fd:
#                shutil.copyfileobj(fd, v6t.stdin)
#        v6t.stdin.close()
#        v6t.wait()
#        if v6t.returncode != 0:
#            raise RuntimeError(f"vg6d_transform exited with code {v6t.returncode}")
#
#        if not os.path.exists(decumulated_data) or os.path.getsize(decumulated_data) == 0:
#            return
#
#        subprocess.run(["grib_filter", grib_filter_rules, decumulated_data], check=True)
#
#        with open(stamp_file, "wb"):
#            pass
#
#    def select_file(self, inputs: Inputs, name: str, step: int) -> "InputFile":
#        """
#        Given a recipe input model, a step, and available input files for that
#        step, select the input file (or generate a new one) that can be used as
#        input for the recipe
#        """
#        f = os.path.join(inputs.input_dir, self.dirname, f"{name}+{step}.grib")
#        if os.path.exists(f):
#            return InputFile(
#                    pathname=f,
#                    name=name,
#                    step=step,
#                    info=self)
#        return None
#
    def document(self, file, indent=4):
        ind = " " * indent
        print(f"{ind}* **vg6d_transform arguments**: {' '.join(shlex.quote(arg) for arg in self.args)}", file=file)
        super().document(file, indent)

# class Inputs:
#    """
#    Manage the input of a recipe inside its input directory
#    """
#    def __init__(
#            self,
#            recipe: 'Recipe',
#            input_dir: str):
#        """
#        Look into the pantry filesystem storage and take note of what files are
#        available
#        """
#        self.recipe = recipe
#        self.input_dir = input_dir
#        self.steps: Dict[int, List[InputFile]] = defaultdict(list)
#
#        for input_file in self.read():
#            self.steps[input_file.step].append(input_file)
#
#    def read(self) -> Iterator["InputFile"]:
#        """
#        Scan an input directory in the pantry and generate InputFile objects
#        for each input found
#        """
#        for fname in os.listdir(self.input_dir):
#            if not fname.endswith(".grib"):
#                continue
#            name, step = fname[:-5].rsplit("+", 1)
#            model, name = name.split("_", 1)
#            step = int(step)
#
#            # Lookup the corresponding Input in the recipe, by input name and
#            # model name, and associate it with this input
#            for i in self.recipe.inputs[name]:
#                if i.model == model:
#                    info = i
#                    break
#            else:
#                continue
#
#            yield InputFile(
#                    pathname=os.path.join(self.input_dir, fname),
#                    name=name,
#                    step=step,
#                    info=info)
#
#    def preprocess(self):
#        """
#        Hook into inputs to run preprocessors if needed
#        """
#        for name, inputs in self.recipe.inputs.items():
#            for i in inputs:
#                i.preprocess(self)
#
#    def for_step(self, step):
#        """
#        Return available input files for the given step.
#
#        Return None if some of the inputs are not satisfied for this step
#        """
#        res = {}
#        # For each of the recipe required inputs...
#        for name, inputs in self.recipe.inputs.items():
#            found = None
#            # ...try all its alternatives in order...
#            for i in inputs:
#                # ...and see if we have data for it
#                found = i.select_file(self, name, step)
#                # Stop at the first matching input alternative
#                if found:
#                    break
#            # One of the required inputs for this recipe has no data for this
#            # step: give up
#            if not found:
#                log.debug("%s+%03d: data for input %s not found: skipping", self.recipe.name, step, name)
#                return None
#            res[name] = found
#
#        return res


class InputFile(NamedTuple):
    """
    An input file stored in the pantry
    """
    # Pathname to the file
    pathname: str
    # Input with information about the file
    info: Input
    # Forecast step
    step: int
