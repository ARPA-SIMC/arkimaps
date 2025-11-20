# from __future__ import annotations
import contextlib
import datetime
import logging
import os
import re
import shlex
import shutil
import subprocess
import tempfile
from abc import ABC
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, Generator, Iterable, List, NamedTuple, Optional, Tuple, Type, TypeVar

from .config import Config
from .grib import GRIB
from .lint import Lint
from .models import BaseDataModel, pydantic
from .types import Instant
from .component import RootComponent, TypeRegistry
from .utils import perf_counter_ns

if TYPE_CHECKING:
    from numpy.typing import NDArray

    from . import pantry, outputbundle, orders

log = logging.getLogger("arkimaps.inputs")


class Inputs:
    """
    Repository of all known inputs
    """

    def __init__(self) -> None:
        # List of input definitions, indexed by name
        self.inputs: Dict[str, List["Input"]] = {}

    def __getitem__(self, key: str) -> List["Input"]:
        """
        Lookup an input by name
        """
        return self.inputs[key]

    def get(self, name: str, model: Optional[str] = None) -> List["Input"]:
        """
        Lookup an input by name, optionally filtered by model
        """
        inputs = self.inputs.get(name) or []
        if model is not None:
            inputs = [inp for inp in inputs if inp.spec.model is None or model == inp.spec.model]
        return inputs

    def values(self) -> Iterable[List["Input"]]:
        """
        Return all the inputs in the repository
        """
        return self.inputs.values()

    def add(self, inp: "Input"):
        """
        Add an Input definition
        """
        old = self.inputs.get(inp.name)
        if old is None:
            # First time we see this input: add it
            self.inputs[inp.name] = [inp]
            return

        if len(old) == 1 and old[0].spec.model is None:
            # We had an input for model=None (all models)
            # so we refuse to add more
            raise RuntimeError(
                f"{inp.defined_in}: input {inp.name} for (any model) already defined in {old[0].defined_in}"
            )

        for i in old:
            if i.spec.model == inp.spec.model:
                # We already had an input for this model name
                raise RuntimeError(
                    f"{inp.defined_in}: input {inp.name} (model {inp.spec.model}) already defined in {i.defined_in}"
                )

        # Input for a new model: store it
        old.append(inp)

    def summarize(self, pantry: "pantry.Pantry", orders: List["orders.Order"], summary: "outputbundle.InputSummary"):
        """
        Return a JSON-serializable summary about input processing
        """
        # Collect which inputs have been used by which recipes
        for order in orders:
            for input_file in order.input_files.values():
                pantry.input_stats[input_file.info].used_by.add(order.recipe.name)

        for inps in self.inputs.values():
            for inp in inps:
                stats = pantry.input_stats[inp]
                if stats.used_by or stats.computation_log:
                    summary.add(inp.name, stats)

    def add_inputs_recursive(self, name: str, res: List[str]) -> None:
        """
        Add to res the name of this input, and all inputs of this input, and
        their inputs, recursively
        """
        if name in res:
            return
        res.append(name)
        for inp in self[name]:
            for other in inp.get_all_inputs():
                for inp in self[other]:
                    self.add_inputs_recursive(other, res)


class InputSpec(BaseDataModel):
    """
    Data model common for all inputs
    """

    #: model, identifying this instance among other alternatives for this input
    model: Optional[str] = None
    #: Extra arguments passed to mgrib on loading
    mgrib: Dict[str, Any] = pydantic.Field(default_factory=dict)
    #: Optional notes for the documentation
    notes: Optional[str] = None


SPEC = TypeVar("SPEC", bound=InputSpec)


class Input(RootComponent[SPEC], ABC):
    """
    An input element to a recipe.

    All arguments to the constructor besides `name` and `defined_in` are taken
    from the YAML input definition
    """

    __registry__ = TypeRegistry["Input"]()
    lookup = __registry__.lookup

    NAME: str

    @classmethod
    def create(cls, *, config: Config, name: str, defined_in: str, type: str = "default", args: Dict[str, Any]):
        """
        Instantiate an input by the ``type`` key in its recipe definition
        """
        impl_cls = cls.lookup(type)
        return impl_cls(config=config, name=name, defined_in=defined_in, args=args)

    def lint(self, lint: Lint) -> None:
        """
        Expensive consistency checks of the input configuration
        """
        pass

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
            pantry.input_stats[self].add_computation_log(elapsed, what)
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
            "model": self.spec.model,
            "defined_in": self.defined_in,
            "mgrib": self.spec.mgrib,
            "notes": self.spec.notes,
        }

    def get_all_inputs(self) -> List[str]:
        """
        Return all names of inputs used by this input
        """
        return []

    def get_instants(self, pantry: "pantry.DiskPantry") -> Dict[Optional[Instant], "InputFile"]:
        """
        Scan the pantry to check what input files are available for this input.

        Return a dict mapping available steps to corresponding InputFile
        objects
        """
        return {}

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


class Static(Input[StaticInputSpec]):
    """
    An input that refers to static files distributed with arkimaps
    """

    # TODO: in newer pythons, use importlib.resources.Resource and copy to
    # workdir in get_instants
    NAME = "static"
    Spec = StaticInputSpec

    def __init__(self, **kw):
        super().__init__(**kw)
        abspath, path = self.clean_path(self.spec.path)
        self.abspath = abspath
        self.spec.path = path

    def to_dict(self):
        res = super().to_dict()
        res["abspath"] = self.abspath.as_posix()
        res["path"] = self.spec.path.as_posix()
        return res

    def clean_path(self, path: Path) -> Tuple[Path, Path]:
        """
        Resolve path into an absolute path, and turn it into a clean relative
        path inside it.

        Also perform any validation expected on this kind of static input paths
        """
        for static_dir in self.config.static_dir:
            if not static_dir.is_dir():
                continue
            abspath = (static_dir / path).absolute()
            cp = Path(os.path.commonpath((abspath, static_dir)))
            if not cp.samefile(static_dir):
                raise RuntimeError(f"{path} leads outside the static directory")
            if not abspath.exists():
                continue
            return abspath, abspath.relative_to(static_dir)
        raise RuntimeError(f"{path} does not exist inside {self.config.static_dir}")

    def document(self, file, indent=4):
        ind = " " * indent
        print(f"{ind}* **Path**: `{self.spec.path}`", file=file)
        super().document(file, indent)

    def get_instants(self, pantry: "pantry.DiskPantry") -> Dict[Optional[Instant], "InputFile"]:
        return {None: InputFile(self.abspath, self, None)}


class Shape(Static):
    """
    A special instance of static that deals with shapefiles
    """

    # TODO: in newer pythons, use importlib.resources.Resource and copy to
    # workdir in get_instants
    NAME = "shape"
    Spec = StaticInputSpec

    def clean_path(self, path: Path):
        """
        Resolve path into an absolute path, and turn it into a clean relative
        path inside it.

        Also perform any validation expected on this kind of static input paths
        """
        for static_dir in self.config.static_dir:
            if not static_dir.is_dir():
                continue
            abspath = (static_dir / path).absolute()
            cp = Path(os.path.commonpath((abspath, static_dir)))
            if not cp.samefile(static_dir):
                raise RuntimeError(f"{path} leads outside the static directory")
            if not abspath.with_suffix(".shp").exists():
                continue
            return abspath, abspath.relative_to(static_dir)
        raise RuntimeError(f"{path}.shp does not exist inside {self.config.static_dir}")


class SourceInputSpec(InputSpec):
    """
    Data model for Source inputs
    """

    #: arkimet matcher filter
    arkimet: Optional[str] = None
    #: grib_filter if expression
    eccodes: Optional[str] = None


class Source(Input[SourceInputSpec]):
    """
    An input that is data straight out of a model
    """

    NAME = "default"
    Spec = SourceInputSpec

    def lint(self, lint: Lint):
        super().lint(lint)
        if not self.spec.arkimet and not self.spec.eccodes:
            lint.warn_input(
                "neither `arkimet` nor `eccodes` were defined for the input", defined_in=self.defined_in, name=self.name
            )

        if self.spec.eccodes:
            with tempfile.NamedTemporaryFile(mode="wt") as tf:
                print(f"if ({self.spec.eccodes}) {{", file=tf)
                print('print "";', file=tf)
                print("}", file=tf)
                tf.flush()
                cmd = ["grib_filter", tf.name, "-", "/dev/null"]
                res = subprocess.run(cmd, input=b"GRIB7777", stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                stderr = res.stderr.decode()
                if re.match(r"^(?:grib_filter:\s*)?[Nn]o messages found in /dev/null\s*$", stderr):
                    return
                errors: List[str] = []
                header = "ECCODES ERROR   :  "
                for line in stderr.splitlines():
                    if line.startswith(header):
                        errors.append(line[len(header) :])
                lint.warn_input(
                    f"eccodes match {self.spec.eccodes!r} cannot be parsed: {errors}",
                    defined_in=self.defined_in,
                    name=self.name,
                )

    def __repr__(self):
        return f"Source:{self.spec.model}:{self.name}"

    def to_dict(self):
        res = super().to_dict()
        res["arkimet"] = self.spec.arkimet
        res["eccodes"] = self.spec.eccodes
        return res

    def get_instants(self, pantry: "pantry.DiskPantry") -> Dict[Optional[Instant], "InputFile"]:
        # FIXME: this hardcodes .grib as extension. We can either rename
        # 'Source' to 'GRIB' and default that, or allow to specify a different
        # extension, leaving '.grib' as a default
        res: Dict[Optional[Instant], "InputFile"] = {}
        for instant in pantry.input_instants[self]:
            res[instant] = pantry.get_input_file(self, instant)
        return res

    def document(self, file, indent=4):
        ind = " " * indent
        print(f"{ind}* **Arkimet matcher**: `{self.spec.arkimet}`", file=file)
        print(f"{ind}* **grib_filter matcher**: `{self.spec.eccodes}`", file=file)
        super().document(file, indent)


class DerivedInputSpec(InputSpec):
    """
    Data model for Derived inputs
    """

    inputs: List[str] = pydantic.Field(default_factory=list, min_items=1)

    @pydantic.validator("inputs", pre=True, allow_reuse=True)
    def string_to_list(cls, value):
        if isinstance(value, str):
            return [value]
        return value


DSPEC = TypeVar("DSPEC", bound=DerivedInputSpec)


class Derived(Input[DSPEC], ABC):
    """
    Base class for inputs derives from other inputs
    """

    def to_dict(self):
        res = super().to_dict()
        res["inputs"] = self.spec.inputs
        return res

    def get_all_inputs(self) -> List[str]:
        res = super().get_all_inputs()
        res.extend(self.spec.inputs)
        return res

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
        for instant in pantry.input_instants[self]:
            res[instant] = pantry.get_input_file(self, instant)
        return res

    def document(self, file, indent=4):
        ind = " " * indent
        print(f"{ind}* **Preprocessing**: {self.NAME}", file=file)
        print(f"{ind}* **Inputs**: {', '.join(self.spec.inputs)}", file=file)
        super().document(file, indent)


class VG6DStatProDerivedcInputSpec(DerivedInputSpec, ABC):
    """
    Data model for VG6DStatProc inputs
    """

    step: int
    comp_stat_proc: str
    comp_frac_valid: float = 0.0
    comp_full_steps: bool

    @pydantic.root_validator(pre=True, allow_reuse=True)
    def default_comp_full_steps(cls, values):
        val = values.get("comp_full_steps")
        if val is None:
            val = int(values["step"]) != 24
        else:
            val = bool(val)
        values["comp_full_steps"] = val
        return values

    @pydantic.validator("inputs", allow_reuse=True)
    def only_one_input(cls, value):
        if len(value) != 1:
            raise RuntimeError("only one source in put allowed")
        return value


class VG6DStatProcMixin(Derived[VG6DStatProDerivedcInputSpec], ABC):
    def to_dict(self):
        res = super().to_dict()
        res["step"] = self.spec.step
        return res

    def generate(self, pantry: "pantry.DiskPantry"):
        # Get the instants of our source input
        source_instants = pantry.get_instants(self.spec.inputs[0])

        # TODO: check that they match the instant

        # Don't run preprocessing if we don't have data to preprocess
        if not source_instants:
            log.info("input %s: missing source data", self.name)
            return

        log.info("input %s: generating from %r", self.name, self.spec.inputs)

        # Generate derived input
        grib_filter_rules = pantry.get_accessory_fullname(self, "grib_filter_rules.txt")
        with open(grib_filter_rules, "w") as fd:
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
            f"--comp-step=0 {self.spec.step:02d}",
            f"--comp-stat-proc={self.spec.comp_stat_proc}",
            f"--comp-frac-valid={self.spec.comp_frac_valid:g}",
        ]
        if self.spec.comp_full_steps:
            cmd.append("--comp-full-steps")
        cmd += ["-", str(decumulated_data)]
        with self._collect_stats(pantry, " ".join(shlex.quote(c) for c in cmd)):
            v6t = subprocess.Popen(cmd, stdin=subprocess.PIPE, env={"LOG4C_PRIORITY": "debug"})
            # With the above invocation stdin should always be set, this lets
            # mypy know
            assert v6t.stdin is not None
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
                    ["grib_filter", grib_filter_rules, decumulated_data],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    check=True,
                )
                for line in res.stderr.splitlines():
                    log.debug("%s: grib_filter stderr: %s", self.name, line)
                for line in res.stdout.splitlines():
                    if not line.startswith(b"s:"):
                        return
                    ye, mo, da, ho, mi, se, step = line[2:].split(b",")
                    instant = Instant(
                        datetime.datetime(int(ye), int(mo), int(da), int(ho), int(mi), int(se)), int(step)
                    )
                    if instant in pantry.input_instants[self]:
                        log.warning(
                            "%s: vg6d_transform generated multiple GRIB data for instant %s. Note that truncation"
                            " to only the first data produced is not supported yet!",
                            self.name,
                            instant,
                        )
                    pantry.add_instant(self, instant)
        finally:
            if os.path.exists(decumulated_data):
                os.unlink(decumulated_data)


class Decumulate(VG6DStatProcMixin):
    """
    Decumulate inputs
    """

    NAME = "decumulate"
    Spec = VG6DStatProDerivedcInputSpec

    def __init__(self, args: Dict[str, Any], **kwargs):
        args.setdefault("comp_stat_proc", "1")
        super().__init__(args=args, **kwargs)

    def document(self, file, indent=4):
        ind = " " * indent
        print(f"{ind}* **Decumulation step**: {self.spec.step}", file=file)
        super().document(file, indent)


class Average(VG6DStatProcMixin):
    """
    Average inputs
    """

    NAME = "average"
    Spec = VG6DStatProDerivedcInputSpec

    def __init__(self, args: Dict[str, Any], **kwargs):
        args.setdefault("comp_stat_proc", "254:0")
        super().__init__(args=args, **kwargs)

    def document(self, file, indent=4):
        ind = " " * indent
        print(f"{ind}* **Averaging step**: {self.spec.step}", file=file)
        super().document(file, indent)


class AlignInstants(Derived[DSPEC], ABC):
    def align_instants(self, pantry: "pantry.DiskPantry") -> Dict[Optional[Instant], List["InputFile"]]:
        # Get the steps for each of our inputs
        available_instants: Optional[Dict[Optional[Instant], List[InputFile]]] = None
        for input_name in self.spec.inputs:
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


class VG6DTransformInputSpec(DerivedInputSpec):
    """
    Data model for VG6DTransform inputs
    """

    args: List[str] = pydantic.Field(default_factory=list, min_items=1)

    @pydantic.validator("args", pre=True, allow_reuse=True)
    def args_string_to_list(cls, value):
        if isinstance(value, str):
            return [value]
        return value


class VG6DTransform(AlignInstants[VG6DTransformInputSpec]):
    """
    Process inputs with vg6d_transform
    """

    NAME = "vg6d_transform"
    Spec = VG6DTransformInputSpec

    def to_dict(self):
        res = super().to_dict()
        res["args"] = self.spec.args
        return res

    def generate(self, pantry: "pantry.DiskPantry"):
        # Get the steps for each of our inputs
        available_instants = self.align_instants(pantry)
        if not available_instants:
            return

        # For each step, run vg6d_transform to generate its output
        for instant, input_files in available_instants.items():
            assert instant is not None
            output_name = pantry.get_basename(self, instant)
            log.info("input %s: generating instant %s as %s", self.name, instant, output_name)
            for f in input_files:
                log.info("input %s: generating from %s", self.name, f.pathname)

            output_pathname = os.path.join(pantry.data_root, output_name)
            cmd = ["vg6d_transform"] + self.spec.args + ["-", output_pathname]
            log.debug("running %s", " ".join(shlex.quote(x) for x in cmd))

            with self._collect_stats(pantry, " ".join(shlex.quote(c) for c in cmd)):
                v6t = subprocess.Popen(cmd, stdin=subprocess.PIPE, env={"LOG4C_PRIORITY": "debug"})
                assert v6t.stdin is not None
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

            pantry.add_instant(self, instant)

    def document(self, file, indent=4):
        ind = " " * indent
        print(f"{ind}* **vg6d_transform arguments**: {' '.join(shlex.quote(arg) for arg in self.spec.args)}", file=file)
        super().document(file, indent)


class Cat(AlignInstants[DerivedInputSpec]):
    """
    Concatenate inputs
    """

    NAME = "cat"
    Spec = DerivedInputSpec

    def generate(self, pantry: "pantry.DiskPantry"):
        # Get the instants for each of our inputs
        available_instants = self.align_instants(pantry)
        if not available_instants:
            return

        # For each instant, concatenate all inputs to generate the output
        for instant, input_files in available_instants.items():
            assert instant is not None
            output_name = pantry.get_basename(self, instant)
            log.info("input %s: generating instant %s as %s", self.name, instant, output_name)
            output_pathname = os.path.join(pantry.data_root, output_name)
            with self._collect_stats(
                pantry, "cat " + ",".join(shlex.quote(str(i.pathname)) for i in input_files) + " " + str(output_name)
            ):
                with open(output_pathname, "wb") as out:
                    for input_file in input_files:
                        with open(input_file.pathname, "rb") as fd:
                            shutil.copyfileobj(fd, out)

            pantry.add_instant(self, instant)


class Or(Derived[DerivedInputSpec]):
    """
    Represents the first of the inputs listed that has data for a step
    """

    NAME = "or"
    Spec = DerivedInputSpec

    def generate(self, pantry: "pantry.DiskPantry"):
        available_instants: Dict[Instant, InputFile] = {}
        for input_name in self.spec.inputs:
            for instant, input_file in pantry.get_instants(input_name).items():
                assert instant is not None
                available_instants.setdefault(instant, input_file)

        # For each instant, concatenate all inputs to generate the output
        for instant, input_file in available_instants.items():
            output_name = pantry.get_basename(self, instant)
            log.info("input %s: using %s for instant %s as %s", self.name, input_file.info.name, instant, output_name)
            output_pathname = os.path.join(pantry.data_root, output_name)
            with self._collect_stats(pantry, f"{input_file.pathname} as {output_name}"):
                os.link(input_file.pathname, output_pathname)
            pantry.add_instant(self, instant)


class GribSetInputSpec(DerivedInputSpec):
    """
    Data model for GribSet inputs
    """

    grib_set: Dict[str, Any] = pydantic.Field(default_factory=dict)
    clip: Optional[str] = None


GSPEC = TypeVar("GSPEC", bound=GribSetInputSpec)


class GribSetMixin(Derived[GSPEC], ABC):
    """
    Mixin used for inputs that take a `grib_set` argument
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.clip_fn = (
            compile(self.spec.clip, filename=self.defined_in, mode="exec") if self.spec.clip is not None else None
        )

    def to_dict(self):
        res = super().to_dict()
        res["grib_set"] = self.spec.grib_set
        res["clip"] = self.spec.clip
        return res

    def apply_grib_set(self, grib: GRIB):
        """
        Set key=value entries in the given grib from the `grib_set` input
        definition
        """
        for k, v in self.spec.grib_set.items():
            grib[k] = v

    def apply_clip(self, values: Dict[str, "NDArray"]) -> "NDArray":
        """
        Evaluate the clip expression using the keyword arguments as locals.

        Returns values[self.name], which might be a different array than what
        is in values when the function was called, in case the expression
        creates a new array for it.
        """
        if self.clip_fn is not None:
            eval(self.clip_fn, values)
        return values[self.name]


class GroundToMSL(GribSetMixin[GribSetInputSpec]):
    """
    Convert heights above ground to heights above mean sea level, by adding
    ground geopotential.

    It takes two inputs: the ground geopotential, and the value to convert, in
    that order.
    """

    NAME = "groundtomsl"
    Spec = GribSetInputSpec

    def __str__(self) -> str:
        return f"groundtomsl({', '.join(self.get_all_inputs())})"

    def generate(self, pantry: "pantry.DiskPantry"):
        if len(self.spec.inputs) != 2:
            raise RuntimeError(f"{self.name} has {len(self.spec.inputs)} inputs instead of 2")

        z_input: InputFile
        for instant, input_file in pantry.get_instants(self.spec.inputs[0]).items():
            assert instant is not None
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
        for instant, input_file in pantry.get_instants(self.spec.inputs[1]).items():
            assert instant is not None
            output_name = pantry.get_basename(self, instant)
            with self._collect_stats(
                pantry,
                " ".join(
                    (
                        "groundtomsl",
                        shlex.quote(str(z_input.pathname)),
                        shlex.quote(str(input_file.pathname)),
                        str(output_name),
                    )
                ),
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
                    pantry.add_instant(self, instant)
                    has_output = True

        if not has_output:
            log.info("input %s: missing source data", self.name)


class ExprInputSpec(GribSetInputSpec):
    """
    Data model for Expr inputs
    """

    expr: str


class Expr(GribSetMixin[ExprInputSpec], AlignInstants[ExprInputSpec]):
    """
    Compute the result using a Python expression of the input values, as numpy
    arrays.

    The first input GRIB is used as a template for the output GRIB, so all its
    metadata is copied to the output as-is, unless amended by ``grib_set``.
    """

    NAME = "expr"
    Spec = ExprInputSpec

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.expr_fn = compile(self.spec.expr, filename=self.defined_in, mode="exec")

    def to_dict(self):
        res = super().to_dict()
        res["expr"] = self.spec.expr
        return res

    def generate(self, pantry: "pantry.DiskPantry"):
        available_instants = self.align_instants(pantry)
        if not available_instants:
            return

        # For each instant, run the expression
        for instant, input_files in available_instants.items():
            assert instant is not None
            output_name = pantry.get_basename(self, instant)
            with self._collect_stats(
                pantry, "expr " + ",".join(shlex.quote(str(i.pathname)) for i in input_files) + f" {output_name}"
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
                    assert template is not None

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

                    pantry.add_instant(self, instant)


class SFFraction(GribSetMixin[GribSetInputSpec], AlignInstants[GribSetInputSpec]):
    """
    Compute snow fraction percentage based on formulas documented in #38

    It takes two inputs: the first is total precipitation, the second is total
    snow precipitation.
    """

    NAME = "sffraction"
    Spec = GribSetInputSpec

    def generate(self, pantry: "pantry.DiskPantry"):
        if len(self.spec.inputs) != 2:
            raise RuntimeError(f"{self.name} has {len(self.spec.inputs)} inputs instead of 2")

        available_instants = self.align_instants(pantry)
        if not available_instants:
            return

        # For each instant, run the expression
        for instant, input_files in available_instants.items():
            assert instant is not None
            output_name = pantry.get_basename(self, instant)
            with self._collect_stats(
                pantry,
                "sffraction " + ",".join(shlex.quote(str(i.pathname)) for i in input_files) + " " + str(output_name),
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

                    pantry.add_instant(self, instant)


class InputFile(NamedTuple):
    """
    An input file stored in the pantry
    """

    # Pathname to the file
    pathname: Path
    # Input with information about the file
    info: Input
    # Forecast step (if None, this input file is valid for all steps)
    instant: Optional[Instant]

    def __str__(self):
        return self.pathname
