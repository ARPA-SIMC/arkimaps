# from __future__ import annotations
import contextlib
import datetime
import logging
import os
import shlex
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, Generator, List, NamedTuple, Optional, Set, Type, Union

import eccodes
import numpy

from .config import Config
from .grib import GRIB
from .lint import Lint
from .models import BaseDataModel
from .outputbundle import InputProcessingStats
from .utils import perf_counter_ns, TypeRegistry
from .types import ModelStep, Instant

if TYPE_CHECKING:
    from . import pantry
    from .recipes import Recipe

    try:
        import arkimet
    except ModuleNotFoundError:
        pass

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


class InputTypes(TypeRegistry["Input"]):
    """
    Registry of available Input implementations
    """

    pass


input_types = InputTypes()


class InputSpec(BaseDataModel):
    """
    Data model common for all inputs
    """

    #: model, identifying this instance among other alternatives for this input
    model: Optional[str] = None
    #: Extra arguments passed to mgrib on loading
    mgrib: Optional[Dict[str, Any]] = None
    #: Optional notes for the documentation
    notes: Optional[str] = None


class Input:
    """
    An input element to a recipe.

    All arguments to the constructor besides `name` and `defined_in` are taken
    from the YAML input definition
    """

    NAME: str
    Spec: Type[InputSpec] = InputSpec

    def __init__(
        self,
        *,
        config: Config,
        name: str,
        defined_in: str,
        **kwargs,
    ):
        # Configuration for this run
        self.config = config
        # Name of the input in the recipe
        self.name = name
        # file name where this input was defined
        self.defined_in = defined_in
        # Input data as specified in the recipe
        self.spec = self.Spec(**kwargs)
        # Processing statistics
        self.stats = InputProcessingStats()

    @classmethod
    def create(cls, *, lint: Optional[Lint] = None, type: str = "default", **kw):
        """
        Instantiate an input by the ``type`` key in its recipe definition
        """
        try:
            impl_cls = input_types.by_name(type)
        except KeyError as e:
            raise KeyError(
                f"recipe requires unknown input {type}. Available: {', '.join(input_types.registry.keys())}"
            ) from e
        if lint:
            impl_cls.lint(lint, **kw)
        return impl_cls(**kw)

    @classmethod
    def lint(
        cls,
        lint: Lint,
        *,
        config: Config,
        name: str,
        defined_in: str,
        model: Optional[str] = None,
        mgrib: Optional["Kwargs"] = None,
        notes: Optional[str] = None,
        **kwargs,
    ):
        """
        Consistency check the given input arguments
        """
        for k, v in kwargs.items():
            lint.warn_input(f"Unknown parameter: {k!r}", defined_in=defined_in, name=name)

    @contextlib.contextmanager
    def _collect_stats(self, pantry: "pantry.Pantry", what: str) -> Generator[None, None, None]:
        """
        Collect statistics about processing done to generate this input
        """
        start = perf_counter_ns()
        try:
            yield
        finally:
            elapsed = perf_counter_ns() - start
            self.stats.add_computation_log(elapsed, what)
            pantry.log_input_processing(self, what)

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

    def add_instant(self, instant: Instant):
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

    def get_instants(self, pantry: "pantry.DiskPantry") -> Dict[Optional[Instant], "InputFile"]:
        """
        Scan the pantry to check what input files are available for this input.

        Return a dict mapping available steps to corresponding InputFile
        objects
        """
        return {}

    def compile_arkimet_matcher(self, session: "arkimet.Session"):
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
        if self.spec.notes:
            print(f"{ind}**Note**: {self.spec.notes}", file=file)
        if self.spec.mgrib:
            for k, v in self.spec.mgrib.items():
                print(f"{ind}* **mgrib {{k}}**: `{v}`", file=file)


class StaticInputSpec(InputSpec):
    """
    Data model for Static inputs
    """

    path: Path


@input_types.register
class Static(Input):
    """
    An input that refers to static files distributed with arkimaps
    """

    # TODO: in newer pythons, use importlib.resources.Resource and copy to
    # workdir in get_instants
    NAME = "static"

    def __init__(self, *, path: str, **kw):
        super().__init__(**kw)
        abspath, path = self.clean_path(path)
        self.abspath = abspath
        self.path = path

    @classmethod
    def lint(cls, lint: Lint, *, path: str, **kwargs):
        super().lint(lint, **kwargs)

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
        for static_dir in self.config.static_dir:
            if not os.path.isdir(static_dir):
                continue
            abspath = os.path.abspath(os.path.join(static_dir, path))
            cp = os.path.commonpath((abspath, static_dir))
            if not os.path.samefile(cp, static_dir):
                raise RuntimeError(f"{path} leads outside the static directory")
            if not os.path.exists(abspath):
                continue
            return abspath, os.path.relpath(abspath, static_dir)
        raise RuntimeError(f"{path} does not exist inside {self.config.static_dir}")

    def document(self, file, indent=4):
        ind = " " * indent
        print(f"{ind}* **Path**: `{self.path}`", file=file)
        super().document(file, indent)

    def get_instants(self, pantry: "pantry.DiskPantry") -> Dict[Optional[Instant], "InputFile"]:
        return {None: InputFile(self.abspath, self, None)}


@input_types.register
class Shape(Static):
    """
    A special instance of static that deals with shapefiles
    """

    # TODO: in newer pythons, use importlib.resources.Resource and copy to
    # workdir in get_instants
    NAME = "shape"

    def clean_path(self, path: str):
        """
        Resolve path into an absolute path, and turn it into a clean relative
        path inside it.

        Also perform any validation expected on this kind of static input paths
        """
        for static_dir in self.config.static_dir:
            if not os.path.isdir(static_dir):
                continue
            abspath = os.path.abspath(os.path.join(static_dir, path))
            cp = os.path.commonpath((abspath, static_dir))
            if not os.path.samefile(cp, static_dir):
                raise RuntimeError(f"{path} leads outside the static directory")
            if not os.path.exists(abspath + ".shp"):
                continue
            return abspath, os.path.relpath(abspath, static_dir)
        raise RuntimeError(f"{path}.shp does not exist inside {self.config.static_dir}")


@input_types.register
class Source(Input):
    """
    An input that is data straight out of a model
    """

    NAME = "default"

    def __init__(self, *, arkimet: Optional[str] = None, eccodes: Optional[str] = None, **kw):
        super().__init__(**kw)
        # arkimet matcher filter
        self.arkimet = arkimet
        # Compiled arkimet matcher, when available/used
        self.arkimet_matcher: Optional[arkimet.Matcher] = None
        # grib_filter if expression
        self.eccodes = eccodes
        # set of available steps
        self.instants: Set[Instant] = set()
        # set of steps for which the data in the pantry contains multiple
        # elements and needs to be truncated
        self.instants_to_truncate: Set[Instant] = set()

    @classmethod
    def lint(cls, lint: Lint, *, arkimet: Optional[str] = None, eccodes: Optional[str] = None, **kwargs):
        super().lint(lint, **kwargs)
        if not arkimet and not eccodes:
            lint.warn_input("neither `arkimet` nor `eccodes` were defined for the input", **kwargs)

        if eccodes:
            with tempfile.NamedTemporaryFile(mode="wt") as tf:
                print(f"if ({eccodes}) {{", file=tf)
                print('print "";', file=tf)
                print("}", file=tf)
                tf.flush()
                cmd = ["grib_filter", tf.name, "-", "/dev/null"]
                res = subprocess.run(cmd, input=b"GRIB7777", stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                if res.stderr != b"no messages found in /dev/null\n":
                    errors: List[str] = []
                    header = "ECCODES ERROR   :  "
                    for line in res.stderr.decode().splitlines():
                        if line.startswith(header):
                            errors.append(line[len(header) :])
                    lint.warn_input(f"eccodes match {eccodes!r} cannot be parsed: {errors}", **kwargs)

    def __repr__(self):
        return f"Source:{self.spec.model}:{self.name}"

    def to_dict(self):
        res = super().to_dict()
        res["arkimet"] = self.arkimet
        res["eccodes"] = self.eccodes
        return res

    def add_instant(self, instant: Instant):
        if instant in self.instants:
            log.warning("%s: multiple data found for %s", self.name, instant)
            self.instants_to_truncate.add(instant)
        self.instants.add(instant)

    def on_pantry_filled(self, pantry: "pantry.DiskPantry"):
        # If some steps had duplicate data, truncate them
        for instant in self.instants_to_truncate:
            fname = pantry.get_fullname(self, instant)
            keep_only_first_grib(fname)
        self.instants_to_truncate = set()

    def get_instants(self, pantry: "pantry.DiskPantry") -> Dict[Optional[Instant], "InputFile"]:
        # FIXME: this hardcodes .grib as extension. We can either rename
        # 'Source' to 'GRIB' and default that, or allow to specify a different
        # extension, leaving '.grib' as a default
        res: Dict[Optional[Instant], "InputFile"] = {}
        for instant in self.instants:
            res[instant] = pantry.get_input_file(self, instant)
        return res

    def compile_arkimet_matcher(self, session: "arkimet.Session"):
        if self.arkimet is None or self.arkimet == "skip":
            self.arkimet_matcher = None
        else:
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

    def __init__(self, *, inputs: Union[str, List[str]] = None, **kw):
        if inputs is None:
            raise RuntimeError(f"inputs must be present for '{self.NAME}' inputs")
        super().__init__(**kw)
        self.inputs: List[str] = [inputs] if isinstance(inputs, str) else [str(x) for x in inputs]
        # set of available steps
        self.instants: Set[Instant] = set()

    @classmethod
    def lint(cls, lint: Lint, *, inputs: Union[str, List[str]] = None, **kwargs):
        super().lint(lint, **kwargs)

    def to_dict(self):
        res = super().to_dict()
        res["inputs"] = self.inputs
        return res

    def get_all_inputs(self) -> List[str]:
        res = super().get_all_inputs()
        res.extend(self.inputs)
        return res

    def add_instant(self, instant: Instant):
        if instant in self.instants:
            log.warning("%s: multiple data generated for instant %s", self.name, instant)
        self.instants.add(instant)

    def generate(self, pantry: "pantry.DiskPantry"):
        """
        Generate derived products from inputs
        """
        raise NotImplementedError(f"{self.__class__.__name__}.generate() not implemented")

    def get_instants(self, pantry: "pantry.DiskPantry") -> Dict[Optional[Instant], "InputFile"]:
        # Check if flagfile exists, in which case skip generation
        flagfile = pantry.get_accessory_fullname(self, "processed")
        if not os.path.exists(flagfile):
            self.generate(pantry)
            # Create the flagfile to mark that all steps have been generated
            with open(flagfile, "wb"):
                pass

        res: Dict[Optional[Instant], "InputFile"] = {}
        for instant in self.instants:
            res[instant] = pantry.get_input_file(self, instant)
        return res

    def document(self, file, indent=4):
        ind = " " * indent
        print(f"{ind}* **Preprocessing**: {self.NAME}", file=file)
        print(f"{ind}* **Inputs**: {', '.join(self.inputs)}", file=file)
        super().document(file, indent)


class VG6DStatProcMixin:
    def __init__(
        self,
        *,
        step: int = None,
        comp_stat_proc: str,
        comp_frac_valid: float = 0,
        comp_full_steps: Optional[bool] = None,
        **kw,
    ):
        if step is None:
            raise RuntimeError("step must be present for 'decumulate' inputs")
        super().__init__(**kw)
        self.step = int(step)
        if len(self.inputs) != 1:
            raise RuntimeError(
                f"input {self.name}: {self.NAME} has inputs {', '.join(self.inputs)} and should have only one"
            )
        self.comp_stat_proc = comp_stat_proc
        self.comp_frac_valid = comp_frac_valid
        self.comp_full_steps: bool
        if comp_full_steps is not None:
            self.comp_full_steps = bool(comp_full_steps)
        else:
            self.comp_full_steps = self.step != 24

    @classmethod
    def lint(
        cls,
        lint: Lint,
        *,
        step: int = None,
        comp_stat_proc: str,
        comp_frac_valid: float = 0,
        comp_full_steps: Optional[bool] = None,
        **kwargs,
    ):
        super().lint(lint, **kwargs)

    def to_dict(self):
        res = super().to_dict()
        res["step"] = self.step
        return res

    def generate(self, pantry: "pantry.DiskPantry"):
        # Get the instants of our source input
        source_instants = pantry.get_instants(self.inputs[0])

        # TODO: check that they match the instant

        # Don't run preprocessing if we don't have data to preprocess
        if not source_instants:
            log.info("input %s: missing source data", self.name)
            return

        log.info("input %s: generating from %r", self.name, self.inputs)

        # Generate derived input
        grib_filter_rules = pantry.get_accessory_fullname(self, "grib_filter_rules.txt")
        with open(grib_filter_rules, "wt") as fd:
            print('print "s:[year],[month],[day],[hour],[minute],[second],[endStep]";', file=fd)
            print(f'write "{pantry.get_eccodes_fullname(self)}";', file=fd)

        # We could pipe the output of vg6d_transform directly into grib_filter,
        # but grib_filter errors in case of empty input with the same exit code
        # as having a nonexisting file as input, so we can't tell the ok
        # situation in which vg6d_transform doesn't find enough data, from a
        # bug causing a wrong invocation.
        # As a workaround, we need a temporary file, so we can check if it's
        # empty before passing it to grib_filter
        decumulated_data = pantry.get_accessory_fullname(self, "decumulated.grib")
        if os.path.exists(decumulated_data):
            os.unlink(decumulated_data)

        cmd = [
            "vg6d_transform",
            f"--comp-step=0 {self.step:02d}",
            f"--comp-stat-proc={self.comp_stat_proc}",
            f"--comp-frac-valid={self.comp_frac_valid}",
        ]
        if self.comp_full_steps:
            cmd.append("--comp-full-steps")
        cmd += ["-", decumulated_data]
        with self._collect_stats(pantry, " ".join(shlex.quote(c) for c in cmd)):
            v6t = subprocess.Popen(cmd, stdin=subprocess.PIPE, env={"LOG4C_PRIORITY": "debug"})
            for input_file in source_instants.values():
                with open(input_file.pathname, "rb") as src:
                    shutil.copyfileobj(src, v6t.stdin)
            v6t.stdin.close()
            v6t.wait()
            if v6t.returncode != 0:
                raise RuntimeError(f"vg6d_transform exited with code {v6t.returncode}")

        try:
            if os.path.exists(decumulated_data):
                size = os.path.getsize(decumulated_data)
            else:
                size = None
            if size is None or size == 0:
                log.warning("%s: vg6d_transform generated empty output", self.name)
                return

            with self._collect_stats(pantry, f"grib_filter {size}b"):
                res = subprocess.run(
                    ["grib_filter", grib_filter_rules, decumulated_data], stdout=subprocess.PIPE, check=True
                )
                for line in res.stdout.splitlines():
                    if not line.startswith(b"s:"):
                        return
                    ye, mo, da, ho, mi, se, step = line[2:].split(b",")
                    instant = Instant(
                        datetime.datetime(int(ye), int(mo), int(da), int(ho), int(mi), int(se)), int(step)
                    )
                    if instant in self.instants:
                        log.warning(
                            "%s: vg6d_transform generated multiple GRIB data for instant %s. Note that truncation"
                            " to only the first data produced is not supported yet!",
                            self.name,
                            instant,
                        )
                    self.add_instant(instant)
        finally:
            if os.path.exists(decumulated_data):
                os.unlink(decumulated_data)


@input_types.register
class Decumulate(VG6DStatProcMixin, Derived):
    """
    Decumulate inputs
    """

    NAME = "decumulate"

    def __init__(self, **kw):
        kw.setdefault("comp_stat_proc", "1")
        super().__init__(**kw)

    @classmethod
    def lint(cls, lint: Lint, **kwargs):
        kwargs.setdefault("comp_stat_proc", "1")
        super().lint(lint, **kwargs)

    def document(self, file, indent=4):
        ind = " " * indent
        print(f"{ind}* **Decumulation step**: {self.step}", file=file)
        super().document(file, indent)


@input_types.register
class Average(VG6DStatProcMixin, Derived):
    """
    Average inputs
    """

    NAME = "average"

    def __init__(self, **kw):
        kw.setdefault("comp_stat_proc", "254:0")
        super().__init__(**kw)

    @classmethod
    def lint(cls, lint: Lint, **kwargs):
        kwargs.setdefault("comp_stat_proc", "254:0")
        super().lint(lint, **kwargs)

    def document(self, file, indent=4):
        ind = " " * indent
        print(f"{ind}* **Averaging step**: {self.step}", file=file)
        super().document(file, indent)


class AlignInstantsMixin:
    def align_instants(self, pantry: "pantry.DiskPantry") -> Dict[Optional[Instant], List["InputFile"]]:
        # Get the steps for each of our inputs
        available_instants: Optional[Dict[Optional[Instant], List[InputFile]]] = None
        for input_name in self.inputs:
            input_instants = pantry.get_instants(input_name, model=self.spec.model)
            # Intersect the steps to get only those for which we have all inputs
            if available_instants is None:
                available_instants = {k: [v] for k, v in input_instants.items()}
            else:
                instants_to_delete = []
                for instant, inputs in available_instants.items():
                    input_file = input_instants.get(instant)
                    if input_file is None:
                        instants_to_delete.append(instant)
                    else:
                        inputs.append(input_file)
                for instant in instants_to_delete:
                    log.info("input %s: dropping instant %s missing in source input %s", self.name, instant, input_name)
                    del available_instants[instant]

        # Don't run preprocessing if we don't have data to preprocess
        if not available_instants:
            log.info("input %s: missing source data", self.name)
            return {}

        return available_instants


@input_types.register
class VG6DTransform(AlignInstantsMixin, Derived):
    """
    Process inputs with vg6d_transform
    """

    NAME = "vg6d_transform"

    def __init__(self, *, args: Union[str, List[str]] = None, **kw):
        if args is None:
            raise RuntimeError(f"args must be present for '{self.NAME}' inputs")
        super().__init__(**kw)
        self.args = [args] if isinstance(args, str) else [str(x) for x in args]

    @classmethod
    def lint(cls, lint: Lint, *, args: Union[str, List[str]] = None, **kwargs):
        super().lint(lint, **kwargs)

    def to_dict(self):
        res = super().to_dict()
        res["args"] = self.args
        return res

    def generate(self, pantry: "pantry.DiskPantry"):
        # Get the steps for each of our inputs
        available_instants = self.align_instants(pantry)
        if not available_instants:
            return

        # For each step, run vg6d_transform to generate its output
        for instant, input_files in available_instants.items():
            output_name = pantry.get_basename(self, instant)
            log.info("input %s: generating instant %s as %s", self.name, instant, output_name)
            for f in input_files:
                log.info("input %s: generating from %s", self.name, f.pathname)

            output_pathname = os.path.join(pantry.data_root, output_name)
            cmd = ["vg6d_transform"] + self.args + ["-", output_pathname]
            log.debug("running %s", " ".join(shlex.quote(x) for x in cmd))

            with self._collect_stats(pantry, " ".join(shlex.quote(c) for c in cmd)):
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

            self.add_instant(instant)

    def document(self, file, indent=4):
        ind = " " * indent
        print(f"{ind}* **vg6d_transform arguments**: {' '.join(shlex.quote(arg) for arg in self.args)}", file=file)
        super().document(file, indent)


@input_types.register
class Cat(AlignInstantsMixin, Derived):
    """
    Concatenate inputs
    """

    NAME = "cat"

    def generate(self, pantry: "pantry.DiskPantry"):
        # Get the instants for each of our inputs
        available_instants = self.align_instants(pantry)
        if not available_instants:
            return

        # For each instant, concatenate all inputs to generate the output
        for instant, input_files in available_instants.items():
            output_name = pantry.get_basename(self, instant)
            log.info("input %s: generating instant %s as %s", self.name, instant, output_name)
            output_pathname = os.path.join(pantry.data_root, output_name)
            with self._collect_stats(
                pantry, "cat " + ",".join(shlex.quote(i.pathname) for i in input_files) + " " + output_name
            ):
                with open(output_pathname, "wb") as out:
                    for input_file in input_files:
                        with open(input_file.pathname, "rb") as fd:
                            shutil.copyfileobj(fd, out)

            self.add_instant(instant)


@input_types.register
class Or(Derived):
    """
    Represents the first of the inputs listed that has data for a step
    """

    NAME = "or"

    def generate(self, pantry: "pantry.DiskPantry"):
        available_instants: Dict[Instant, InputFile] = {}
        for input_name in self.inputs:
            for instant, input_file in pantry.get_instants(input_name).items():
                available_instants.setdefault(instant, input_file)

        # For each instant, concatenate all inputs to generate the output
        for instant, input_file in available_instants.items():
            output_name = pantry.get_basename(self, instant)
            log.info("input %s: using %s for instant %s as %s", self.name, input_file.info.name, instant, output_name)
            output_pathname = os.path.join(pantry.data_root, output_name)
            with self._collect_stats(pantry, input_file.pathname + " as " + output_name):
                os.link(input_file.pathname, output_pathname)
            self.add_instant(instant)


class GribSetMixin:
    """
    Mixin used for inputs that take a `grib_set` argument
    """

    def __init__(self, *, grib_set: Optional[Dict[str, Any]] = None, clip: Optional[str] = None, **kw):
        super().__init__(**kw)
        self.grib_set = grib_set if grib_set is not None else {}
        self.clip = clip
        self.clip_fn = compile(clip, filename=self.defined_in, mode="exec") if clip is not None else None

    @classmethod
    def lint(cls, lint: Lint, *, grib_set: Optional[Dict[str, Any]] = None, clip: Optional[str] = None, **kwargs):
        super().lint(lint, **kwargs)

    def to_dict(self):
        res = super().to_dict()
        res["grib_set"] = self.grib_set
        res["clip"] = self.clip
        return res

    def apply_grib_set(self, grib: GRIB):
        """
        Set key=value entries in the given grib from the `grib_set` input
        definition
        """
        for k, v in self.grib_set.items():
            grib[k] = v

    def apply_clip(self, values: Dict[str, numpy.array]) -> numpy.array:
        """
        Evaluate the clip expression using the keyword arguments as locals.

        Returns values[self.name], which might be a different array than what
        is in values when the function was called, in case the expression
        creates a new array for it.
        """
        if self.clip_fn is not None:
            eval(self.clip_fn, values)
        return values[self.name]


@input_types.register
class GroundToMSL(GribSetMixin, Derived):
    """
    Convert heights above ground to heights above mean sea level, by adding
    ground geopotential.

    It takes two inputs: the ground geopotential, and the value to convert, in
    that order.
    """

    NAME = "groundtomsl"

    def generate(self, pantry: "pantry.DiskPantry"):
        if len(self.inputs) != 2:
            raise RuntimeError(f"{self.name} has {len(self.inputs)} inputs instead of 2")

        z_input: InputFile
        for instant, input_file in pantry.get_instants(self.inputs[0]).items():
            if not instant.step.is_zero():
                log.warning(
                    "input %s: ignoring input %s with step %s instead of 0",
                    self.name,
                    input_file.info.name,
                    instant.step_suffix(),
                )
            z_input = input_file
            break
        else:
            log.info("input %s: missing z data", self.name)
            return

        with GRIB(z_input.pathname) as z_grib:
            # Read z_input into a numpy matrix
            z = z_grib.values
            # Convert to meters
            z /= 9.80665

        has_output = False
        for instant, input_file in pantry.get_instants(self.inputs[1]).items():
            output_name = pantry.get_basename(self, instant)
            with self._collect_stats(
                pantry,
                " ".join(("groundtomsl", shlex.quote(z_input.pathname), shlex.quote(input_file.pathname), output_name)),
            ):
                with GRIB(input_file.pathname) as val_grib:
                    # Add z
                    vals = val_grib.values
                    vals += z
                    vals = self.apply_clip({self.name: vals, "z": z})
                    self.apply_grib_set(val_grib)
                    val_grib.values = vals

                    # Write output
                    log.info("input %s: generating instant %s as %s", self.name, instant, output_name)
                    output_pathname = os.path.join(pantry.data_root, output_name)
                    with open(output_pathname, "wb") as out:
                        out.write(val_grib.dumps())
                    self.add_instant(instant)
                    has_output = True

        if not has_output:
            log.info("input %s: missing source data", self.name)


@input_types.register
class Expr(AlignInstantsMixin, GribSetMixin, Derived):
    """
    Compute the result using a Python expression of the input values, as numpy
    arrays.

    The first input GRIB is used as a template for the output GRIB, so all its
    metadata is copied to the output as-is, unless amended by ``grib_set``.
    """

    NAME = "expr"

    def __init__(self, *, expr: str, **kw):
        super().__init__(**kw)
        self.expr = expr
        self.expr_fn = compile(expr, filename=self.defined_in, mode="exec")

    @classmethod
    def lint(cls, lint: Lint, **kwargs):
        expr = kwargs.pop("expr", None)
        if expr is None:
            lint.warn_input("missing 'expr'", **kwargs)
        if not isinstance(expr, str):
            lint.warn_input("'expr' is not a string", **kwargs)
        super().lint(lint, **kwargs)

    def to_dict(self):
        res = super().to_dict()
        res["expr"] = self.expr
        return res

    def generate(self, pantry: "pantry.DiskPantry"):
        available_instants = self.align_instants(pantry)
        if not available_instants:
            return

        # For each instant, run the expression
        for instant, input_files in available_instants.items():
            output_name = pantry.get_basename(self, instant)
            with self._collect_stats(
                pantry, "expr " + ",".join(shlex.quote(i.pathname) for i in input_files) + " " + output_name
            ):
                with contextlib.ExitStack() as stack:
                    # Open all input GRIBs
                    gribs: Dict[str, GRIB] = {}
                    template: Optional[GRIB] = None
                    for f in input_files:
                        grib = stack.enter_context(GRIB(f.pathname))
                        gribs[f.info.name] = grib
                        if template is None:
                            template = grib

                    # Build the variable dict to use to evaluate self.expr_fn
                    values = {name: grib.values for name, grib in gribs.items()}

                    # Evaluate the expression
                    eval(self.expr_fn, values)

                    # Extract the result
                    result = values.get(self.name)
                    if result is None:
                        log.warning("input %s: the expression did not set %s: skipping step", self.name, self.name)
                        continue

                    # Apply clip
                    result = self.apply_clip(values)

                    # Fill the template
                    self.apply_grib_set(template)
                    template.values = result

                    # Write output
                    log.info("input %s: generating instant %s as %s", self.name, instant, output_name)
                    output_pathname = os.path.join(pantry.data_root, output_name)
                    with open(output_pathname, "wb") as out:
                        out.write(template.dumps())

                    self.add_instant(instant)


@input_types.register
class SFFraction(AlignInstantsMixin, GribSetMixin, Derived):
    """
    Compute snow fraction percentage based on formulas documented in #38

    It takes two inputs: the first is total precipitation, the second is total
    snow precipitation.
    """

    NAME = "sffraction"

    def generate(self, pantry: "pantry.DiskPantry"):
        if len(self.inputs) != 2:
            raise RuntimeError(f"{self.name} has {len(self.inputs)} inputs instead of 2")

        available_instants = self.align_instants(pantry)
        if not available_instants:
            return

        # For each instant, run the expression
        for instant, input_files in available_instants.items():
            output_name = pantry.get_basename(self, instant)
            with self._collect_stats(
                pantry, "sffraction " + ",".join(shlex.quote(i.pathname) for i in input_files) + " " + output_name
            ):
                with GRIB(input_files[0].pathname) as grib_tp:
                    template = grib_tp
                    with GRIB(input_files[1].pathname) as grib_snow:
                        snow = grib_snow.values
                        tp = grib_tp.values

                        units = grib_tp.get_string("units")
                        if units == "m":
                            threshold = 0.0005
                        elif units == "kg m**-2":
                            threshold = 0.5
                        else:
                            log.warning("Unsupported unit %s for tp input in sffraction processing", units)
                            threshold = 0.5

                        snow[tp <= threshold] = 0
                        tp[tp == 0] = 1
                        sffraction = snow * 100 / tp
                        sffraction.clip(0, 100, out=sffraction)

                    # Apply clip
                    sffraction = self.apply_clip({self.name: sffraction})

                    # Fill the template
                    self.apply_grib_set(template)
                    template.values = sffraction

                    # Write output
                    log.info("input %s: generating instant %s as %s", self.name, instant, output_name)
                    output_pathname = os.path.join(pantry.data_root, output_name)
                    with open(output_pathname, "wb") as out:
                        out.write(template.dumps())

                    self.add_instant(instant)


class InputFile(NamedTuple):
    """
    An input file stored in the pantry
    """

    # Pathname to the file
    pathname: str
    # Input with information about the file
    info: Input
    # Forecast step (if None, this input file is valid for all steps)
    instant: Optional[Instant]

    def __str__(self):
        return self.pathname
