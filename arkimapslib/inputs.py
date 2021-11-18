# from __future__ import annotations
from typing import TYPE_CHECKING, Dict, Any, Optional, NamedTuple, Type, List, Union, Set
import logging
import os
import shlex
import shutil
import subprocess

import eccodes
try:
    import arkimet
except ModuleNotFoundError:
    pass

if TYPE_CHECKING:
    from . import pantry

# Used for kwargs-style dicts
Kwargs = Dict[str, Any]

log = logging.getLogger("arkimaps.inputs")


def keep_only_first_grib(fname: str):
    with open(fname, "r+b") as infd:
        gid = eccodes.codes_grib_new_from_file(infd)
        try:
            if eccodes.codes_get_message_offset(gid) != 0:
                raise RuntimeError(f"{fname}: first grib does not start at offset 0")
            infd.truncate(eccodes.codes_get_message_size(gid))
        finally:
            eccodes.codes_release(gid)


class InputTypes:
    """
    Registry of available Input implementations
    """
    registry: Dict[str, Type["Input"]] = {}

    @classmethod
    def register(cls, impl_cls: Type["Input"]):
        """
        Add an input class to the registry
        """
        name = getattr(impl_cls, "NAME", None)
        if name is None:
            name = impl_cls.__name__.lower()
        cls.registry[name] = impl_cls
        return impl_cls

    @classmethod
    def by_name(cls, name: str) -> Type["Input"]:
        return cls.registry[name.lower()]


class Input:
    """
    An input element to a recipe
    """
    NAME: str

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

    def to_dict(self):
        """
        Return data about this input in a jsonable dict
        """
        return {
            "name": self.name,
            "type": self.NAME,
            "model": self.model,
            "defined_in": self.defined_in,
            "mgrib": self.mgrib,
            "pantry_basename": self.pantry_basename,
        }

    def get_all_inputs(self) -> List[str]:
        """
        Return all names of inputs used by this input
        """
        return []

    def add_all_inputs(self, pantry: "pantry.Pantry", res: List[str]):
        """
        Add to res the name of this input, and all inputs of this input, and
        their inputs, recursively
        """
        if self.name in res:
            return
        res.append(self.name)
        for name in self.get_all_inputs():
            for inp in pantry.inputs[name]:
                inp.add_all_inputs(pantry, res)

    def add_step(self, step: int):
        """
        Notify that the pantry contains data for this input for the given step
        """
        pass

    def on_pantry_filled(self, pantry: "pantry.DiskPantry"):
        """
        Hook called on all inputs after the pantry is filled with the initial
        data.

        This is called once for every Pantry.fill() invocation.
        """
        pass

    def get_steps(self, pantry: "pantry.DiskPantry") -> Dict[Optional[int], "InputFile"]:
        """
        Scan the pantry to check what input files are available for this input.

        Return a dict mapping available steps to corresponding InputFile
        objects
        """
        return {}

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
class Static(Input):
    """
    An input that refers to static files distributed with arkimaps
    """
    # TODO: in newer pythons, use importlib.resources.Resource and copy to
    # workdir in get_steps
    NAME = "static"

    static_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "static"))

    def __init__(self, path: str, **kw):
        super().__init__(**kw)
        abspath, path = self.clean_path(path)
        self.abspath = abspath
        self.path = path

    def to_dict(self):
        res = super().to_dict()
        res["abspath"] = self.abspath
        res["path"] = self.path
        return res

    def clean_path(self, path: str):
        """
        Resolve path into an absolute path, and turn it into a clean relative
        path inside it.

        Also perform any validation expected on this kind of static input paths
        """
        abspath = os.path.abspath(os.path.join(self.static_dir, path))
        cp = os.path.commonpath((abspath, self.static_dir))
        if not os.path.samefile(cp, self.static_dir):
            raise RuntimeError(f"{path} leads outside the static directory")
        if not os.path.exists(abspath):
            raise RuntimeError(f"{path} does not exist inside {self.static_dir}")
        return abspath, os.path.relpath(abspath, self.static_dir)

    def document(self, file, indent=4):
        ind = " " * indent
        print(f"{ind}* **Path**: `{self.path}`", file=file)
        super().document(file, indent)

    def get_steps(self, pantry: "pantry.DiskPantry") -> Dict[Optional[int], "InputFile"]:
        return {None: InputFile(self.abspath, self, None)}


@InputTypes.register
class Shape(Static):
    """
    A special instance of static that deals with shapefiles
    """
    # TODO: in newer pythons, use importlib.resources.Resource and copy to
    # workdir in get_steps
    NAME = "shape"

    def clean_path(self, path: str):
        """
        Resolve path into an absolute path, and turn it into a clean relative
        path inside it.

        Also perform any validation expected on this kind of static input paths
        """
        abspath = os.path.abspath(os.path.join(self.static_dir, path))
        cp = os.path.commonpath((abspath, self.static_dir))
        if not os.path.samefile(cp, self.static_dir):
            raise RuntimeError(f"{path} leads outside the static directory")
        if not os.path.exists(abspath + ".shp"):
            raise RuntimeError(f"{path}.shp does not exist inside {self.static_dir}")
        return abspath, os.path.relpath(abspath, self.static_dir)


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
        # set of available steps
        self.steps: Set[int] = set()
        # set of steps for which the data in the pantry contains multiple
        # elements and needs to be truncated
        self.steps_to_truncate: Set[int] = set()

    def to_dict(self):
        res = super().to_dict()
        res["arkimet"] = self.arkimet
        res["eccodes"] = self.eccodes
        return res

    def add_step(self, step: int):
        if step in self.steps:
            log.warning("%s: multiple data found for step +%d", self.name, step)
            self.steps_to_truncate.add(step)
        self.steps.add(step)

    def on_pantry_filled(self, pantry: "pantry.DiskPantry"):
        # If some steps had duplicate data, truncate them
        for step in self.steps_to_truncate:
            fname = os.path.join(pantry.data_root, self.pantry_basename + f"+{step}.grib")
            keep_only_first_grib(fname)
        self.steps_to_truncate = set()

    def get_steps(self, pantry: "pantry.DiskPantry") -> Dict[Optional[int], "InputFile"]:
        # FIXME: this hardcodes .grib as extension. We can either rename
        # 'Source' to 'GRIB' and default that, or allow to specify a different
        # extension, leaving '.grib' as a default
        res: Dict[Optional[int], "InputFile"] = {}
        for step in self.steps:
            res[step] = InputFile(os.path.join(pantry.data_root, self.pantry_basename + f"+{step}.grib"), self, step)
        return res

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
        # set of available steps
        self.steps: Set[int] = set()

    def to_dict(self):
        res = super().to_dict()
        res["inputs"] = self.inputs
        return res

    def get_all_inputs(self) -> List[str]:
        res = super().get_all_inputs()
        res.extend(self.inputs)
        return res

    def add_step(self, step: int):
        if step in self.steps:
            log.warning("%s: multiple data generated for step +%d", self.name, step)
        self.steps.add(step)

    def generate(self, pantry: "pantry.DiskPantry"):
        """
        Generate derived products from inputs
        """
        raise NotImplementedError(f"{self.__class__.__name__}.generate() not implemented")

    def get_steps(self, pantry: "pantry.DiskPantry") -> Dict[Optional[int], "InputFile"]:
        # Check if flagfile exists, in which case skip generation
        flagfile = os.path.join(pantry.data_root, f"{self.pantry_basename}.processed")
        if not os.path.exists(flagfile):
            self.generate(pantry)
            # Create the flagfile to mark that all steps have been generated
            with open(flagfile, "wb"):
                pass

        res: Dict[Optional[int], "InputFile"] = {}
        for step in self.steps:
            res[step] = InputFile(os.path.join(pantry.data_root, self.pantry_basename + f"+{step}.grib"), self, step)
        return res

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
        if len(self.inputs) != 1:
            raise RuntimeError(
                    f"input {self.name}: {self.NAME} has inputs {', '.join(self.inputs)} and should have only one")

    def to_dict(self):
        res = super().to_dict()
        res["step"] = self.step
        return res

    def generate(self, pantry: "pantry.DiskPantry"):
        # Get the steps of our source input
        source_steps = pantry.get_steps(self.inputs[0])

        # TODO: check that they match the step

        # Don't run preprocessing if we don't have data to preprocess
        if not source_steps:
            log.info("input %s: missing source data", self.name)
            return

        log.info("input %s: generating from %r", self.name, self.inputs)

        # Generate derived input
        grib_filter_rules = os.path.join(pantry.data_root, f"{self.pantry_basename}.grib_filter_rules")
        with open(grib_filter_rules, "wt") as fd:
            print('print "s:[endStep]";', file=fd)
            print(f'write "{pantry.data_root}/{self.pantry_basename}+[endStep].grib";', file=fd)

        # We could pipe the output of vg6d_transform directly into grib_filter,
        # but grib_filter errors in case of empty input with the same exit code
        # as having a nonexisting file as input, so we can't tell the ok
        # situation in which vg6d_transform doesn't find enough data, from a
        # bug causing a wrong invocation.
        # As a workaround, we need a temporary file, so we can check if it's
        # empty before passing it to grib_filter
        decumulated_data = os.path.join(pantry.data_root, f"{self.pantry_basename}-decumulated.grib")
        if os.path.exists(decumulated_data):
            os.unlink(decumulated_data)

        cmd = ["vg6d_transform", "--comp-stat-proc=1",
               f"--comp-step=0 {self.step:02d}", "--comp-frac-valid=0"]
        if self.step != 24:
            cmd.append("--comp-full-steps")
        cmd += ["-", decumulated_data]
        v6t = subprocess.Popen(cmd, stdin=subprocess.PIPE, env={"LOG4C_PRIORITY": "debug"})
        for step, input_file in source_steps.items():
            with open(input_file.pathname, "rb") as src:
                shutil.copyfileobj(src, v6t.stdin)
        v6t.stdin.close()
        v6t.wait()
        try:
            if v6t.returncode != 0:
                raise RuntimeError(f"vg6d_transform exited with code {v6t.returncode}")

            if not os.path.exists(decumulated_data) or os.path.getsize(decumulated_data) == 0:
                return

            res = subprocess.run(
                    ["grib_filter", grib_filter_rules, decumulated_data],
                    stdout=subprocess.PIPE,
                    check=True)
            for line in res.stdout.splitlines():
                if not line.startswith(b"s:"):
                    return
                step = int(line[2:])
                if step in self.steps:
                    log.warning(
                        "%s: vg6d_transform generated multiple GRIB data for step +%d. Note that truncation to only the"
                        " first data produced is not supported yet!", self.name, step)
                self.add_step(step)
        finally:
            if os.path.exists(decumulated_data):
                os.unlink(decumulated_data)

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
            raise RuntimeError(f"args must be present for '{self.NAME}' inputs")
        super().__init__(**kw)
        self.args = [args] if isinstance(args, str) else [str(x) for x in args]

    def to_dict(self):
        res = super().to_dict()
        res["args"] = self.args
        return res

    def generate(self, pantry: "pantry.DiskPantry"):
        # Get the steps for each of our inputs
        available_steps: Optional[Dict[Optional[int], List[InputFile]]] = None
        for input_name in self.inputs:
            input_steps = pantry.get_steps(input_name)
            # Intersect the steps to get only those for which we have all inputs
            if available_steps is None:
                available_steps = {k: [v] for k, v in input_steps.items()}
            else:
                steps_to_delete = []
                for step, inputs in available_steps.items():
                    input_file = input_steps.get(step)
                    if input_file is None:
                        steps_to_delete.append(step)
                    else:
                        inputs.append(input_file)
                for step in steps_to_delete:
                    log.info("input %s: dropping step %d missing in source input %s", self.name, step, input_name)
                    del available_steps[step]

        # Don't run preprocessing if we don't have data to preprocess
        if not available_steps:
            log.info("input %s: missing source data", self.name)
            return

        # For each step, run vg6d_transform to generate its output
        for step, input_files in available_steps.items():
            output_name = f"{self.pantry_basename}+{step}.grib"

            log.info("input %s: generating step %d as %s", self.name, step, output_name)

            output_pathname = os.path.join(pantry.data_root, output_name)
            cmd = ["vg6d_transform"] + self.args + ["-", output_pathname]
            log.debug("running %s", ' '.join(shlex.quote(x) for x in cmd))

            v6t = subprocess.Popen(cmd, stdin=subprocess.PIPE, env={"LOG4C_PRIORITY": "debug"})
            for input_file in input_files:
                with open(input_file.pathname, "rb") as fd:
                    shutil.copyfileobj(fd, v6t.stdin)
            v6t.stdin.close()
            v6t.wait()
            if v6t.returncode != 0:
                raise RuntimeError(f"vg6d_transform exited with code {v6t.returncode}")

            if not os.path.exists(output_pathname):
                log.warning("input %s: %s not found after running vg6d_transform", self.name, output_name)
                pass
            if os.path.getsize(output_pathname) == 0:
                log.warning("input %s: %s is empty after running vg6d_transform", self.name, output_name)
                os.unlink(output_pathname)

            self.add_step(step)

    def document(self, file, indent=4):
        ind = " " * indent
        print(f"{ind}* **vg6d_transform arguments**: {' '.join(shlex.quote(arg) for arg in self.args)}", file=file)
        super().document(file, indent)


@InputTypes.register
class Cat(Derived):
    """
    Concatenate inputs
    """
    NAME = "cat"

    def generate(self, pantry: "pantry.DiskPantry"):
        # Get the steps for each of our inputs
        available_steps: Optional[Dict[Optional[int], List[InputFile]]] = None
        for input_name in self.inputs:
            input_steps = pantry.get_steps(input_name)
            # Intersect the steps to get only those for which we have all inputs
            if available_steps is None:
                available_steps = {k: [v] for k, v in input_steps.items()}
            else:
                steps_to_delete = []
                for step, inputs in available_steps.items():
                    input_file = input_steps.get(step)
                    if input_file is None:
                        steps_to_delete.append(step)
                    else:
                        inputs.append(input_file)
                for step in steps_to_delete:
                    log.info("input %s: dropping step %d missing in source input %s", self.name, step, input_name)
                    del available_steps[step]

        # Don't run preprocessing if we don't have data to preprocess
        if not available_steps:
            log.info("input %s: missing source data", self.name)
            return

        # For each step, concatenate all inputs to generate the output
        for step, input_files in available_steps.items():
            output_name = f"{self.pantry_basename}+{step}.grib"

            log.info("input %s: generating step %d as %s", self.name, step, output_name)

            output_pathname = os.path.join(pantry.data_root, output_name)
            with open(output_pathname, "wb") as out:
                for input_file in input_files:
                    with open(input_file.pathname, "rb") as fd:
                        shutil.copyfileobj(fd, out)

            self.add_step(step)


class InputFile(NamedTuple):
    """
    An input file stored in the pantry
    """
    # Pathname to the file
    pathname: str
    # Input with information about the file
    info: Input
    # Forecast step (if None, this input file is valid for all steps)
    step: Optional[int]
