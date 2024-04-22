# from __future__ import annotations

"""
Read/write arkimaps output bundles.

An output bundle is a zip or tar file with the output products of an arkimaps
run, and their associated metadata.

The main entry points for reading an output bundle are :py:class:`ZipReader` and
:py:class:`TarReader`.

Example program to show all products in a zip bundle::

    #!/usr/bin/python3

    import json
    import sys

    from arkimapslib.outputbundle import ZipReader


    reader = ZipReader(sys.argv[1])
    products = reader.products()
    for path, info in products.by_path.items():
        georef = info.georef
        recipe_info = products.by_recipe[info.recipe]
        legend_info = recipe_info.legend_info
        print(json.dumps({"path": path, "georef": georef, "legend": legend_info}, indent=1))
"""

import datetime
import io
import json
import logging
import tarfile
import zipfile
from abc import ABC, abstractmethod
from collections import Counter, defaultdict
from pathlib import Path
from typing import IO, TYPE_CHECKING, Any, Dict, List, NamedTuple, Optional, Sequence, Set, Tuple

from . import steps
from .types import ModelStep

if TYPE_CHECKING:
    from .flavours import Flavour
    from .inputs import Input, Instant
    from .orders import Order
    from .recipes import Recipe
    from .kitchen import Kitchen

log = logging.getLogger("outputbundle")


class Serializable(ABC):
    """
    Base for classes that can be serialized to JSON
    """

    @abstractmethod
    def to_jsonable(self) -> Dict[str, Any]:
        """
        Return a version of this object that can be serialized to JSON, and
        deserialized with from_jsonable()
        """
        ...

    @classmethod
    @abstractmethod
    def from_jsonable(cls, data: Dict[str, Any]):
        """
        Recreate an object serialized by to_jsonable
        """
        # TODO: from 3.11 we can type the return value as Self
        ...


class InputProcessingStats(Serializable):
    """
    Statistics collected while processing inputs
    """

    computation_log: List[Tuple[int, str]]
    """List of strings describing computation steps, and the time they took in nanoseconds"""
    used_by: Set[str]
    """List of recipes that used this input to generate products"""

    def __init__(self) -> None:
        self.computation_log = []
        self.used_by = set()

    def add_computation_log(self, elapsed: int, what: str) -> None:
        """
        Add an entry to the computation log.

        :param elapsed: elapsed time in nanoseconds
        :param what: description of the computation
        """
        self.computation_log.append((elapsed, what))

    def to_jsonable(self) -> Dict[str, Any]:
        """
        Produce a JSON-serializable summary about this input
        """
        return {
            "used_by": sorted(self.used_by),
            "computation": self.computation_log,
        }

    @classmethod
    def from_jsonable(cls, data: Dict[str, Any]):
        res = cls()
        res.computation_log = [(elapsed, what) for elapsed, what in data["computation"]]
        res.used_by = set(data["used_by"])
        return res


class InputSummary(Serializable):
    """
    Summary about inputs useed in processing
    """

    inputs: Dict[str, InputProcessingStats]
    """Per-input processing information indexed by input name"""

    def __init__(self) -> None:
        self.inputs = {}

    def add(self, inp: "Input"):
        self.inputs[inp.name] = inp.stats

    def to_jsonable(self) -> Dict[str, Any]:
        # TODO: return {"inputs": self.inputs}
        return {name: stats.to_jsonable() for name, stats in self.inputs.items()}

    @classmethod
    def from_jsonable(cls, data: Dict[str, Any]):
        res = cls()
        for k, v in data.items():
            res.inputs[k] = InputProcessingStats.from_jsonable(v)
        return res


class ReftimeOrders(Serializable):
    """
    Information and statistics for all orders for a given reftime
    """

    inputs: Set[str]
    """Names of inputs used"""
    steps: Dict[ModelStep, int]
    """Numer of products produced for each step"""
    render_time_ns: int
    """Total processing time in nanoseconds"""

    def __init__(
        self,
        *,
        inputs: Optional[Sequence[str]] = None,
        steps: Optional[Dict[ModelStep, int]] = None,
        render_time_ns: int = 0,
    ):
        self.inputs = set(inputs) if inputs else set()
        self.steps = Counter()
        if steps:
            self.steps.update(steps)
        self.render_time_ns = render_time_ns

    def add(self, order: "Order"):
        self.inputs.update(order.input_files.keys())
        self.steps[order.instant.step] += 1
        self.render_time_ns += order.render_time_ns

    def to_jsonable(self) -> Dict[str, Any]:
        return {
            "inputs": sorted(self.inputs),
            "steps": {str(s): c for s, c in self.steps.items()},
            "render_stats": {
                "time_ns": self.render_time_ns,
            },
        }

    @classmethod
    def from_jsonable(cls, data: Dict[str, Any]) -> "ReftimeOrders":
        render_stats = data["render_stats"]
        steps = data["steps"]
        return cls(
            render_time_ns=render_stats["time_ns"],
            steps={ModelStep(k): v for k, v in steps.items()},
            inputs=data.get("inputs"),
        )


class RecipeOrders(Serializable):
    """
    Information and statistics for all orders generated from one recipe
    """

    by_reftime: Dict[datetime.datetime, ReftimeOrders]
    """Summary of all products produced for this recipe at this reference time"""
    legend_info: Optional[Dict[str, Any]]
    """Legend information for products produced from this recipe"""

    def __init__(self) -> None:
        self.by_reftime = defaultdict(ReftimeOrders)
        self.legend_info = None

    def add(self, order: "Order"):
        self.by_reftime[order.instant.reftime].add(order)
        if self.legend_info is None:
            for step in order.order_steps:
                if isinstance(step, steps.AddContour):
                    self.legend_info = step.spec.params.dict(exclude_unset=True)

    def to_jsonable(self) -> Dict[str, Any]:
        return {
            "reftimes": {
                reftime.strftime("%Y-%m-%d %H:%M:%S"): stats.to_jsonable() for reftime, stats in self.by_reftime.items()
            },
            "legend_info": self.legend_info,
        }

    @classmethod
    def from_jsonable(cls, data: Dict[str, Any]):
        res = cls()
        res.by_reftime = {
            datetime.datetime.strptime(k, "%Y-%m-%d %H:%M:%S"): ReftimeOrders.from_jsonable(v)
            for k, v in data["reftimes"].items()
        }
        res.legend_info = data.get("legend_info")
        return res


class ProductInfo(Serializable):
    """
    Information about a generated product image
    """

    recipe: Optional[str]
    """Name of the recipe used for this product"""
    reftime: Optional[datetime.datetime]
    """Reference time"""
    step: Optional[ModelStep]
    """Step"""
    georef: Dict[str, Any]
    """Georeferencing information"""

    def __init__(
        self,
        *,
        recipe: Optional[str] = None,
        reftime: Optional[datetime.datetime] = None,
        step: Optional[ModelStep] = None,
        georef: Optional[Dict[str, Any]] = None,
    ):
        self.recipe = recipe
        self.reftime = reftime
        self.step = step
        self.georef = georef if georef is not None else {}

    def add_recipe(self, recipe: "Recipe"):
        self.recipe = recipe.name

    def add_georef(self, georef: Dict[str, Any]):
        self.georef = georef

    def add_instant(self, instant: "Instant"):
        self.reftime = instant.reftime
        self.step = instant.step

    def to_jsonable(self) -> Dict[str, Any]:
        res = {
            "recipe": self.recipe,
            "reftime": self.reftime.strftime("%Y-%m-%d %H:%M:%S"),
            "step": str(self.step),
        }
        if self.georef:
            res["georef"] = self.georef
        return res

    @classmethod
    def from_jsonable(cls, data: Dict[str, Any]):
        return cls(
            recipe=data["recipe"],
            reftime=datetime.datetime.strptime(data["reftime"], "%Y-%m-%d %H:%M:%S"),
            step=data["step"],
            georef=data.get("georef", None),
        )


class Products(Serializable):
    """
    Information about the products present in the bundle
    """

    flavour: Optional[Dict[str, Any]]
    """Information about the flavour used"""
    by_recipe: Dict[str, RecipeOrders]
    """Recipes used, indexed by name"""
    by_path: Dict[str, ProductInfo]
    """Products generated, indexed by their path"""

    def __init__(self) -> None:
        self.flavour = None
        self.by_recipe = defaultdict(RecipeOrders)
        self.by_path = defaultdict(ProductInfo)

    def add_order(self, order: "Order") -> None:
        """
        Add information from this order to the products summary
        """
        # Add flavour information
        if self.flavour is None:
            self.flavour = order.flavour.summarize()
        elif self.flavour["name"] != order.flavour.name:
            log.error("Found different flavours %s and %s", self.flavour["name"], order.flavour.name)

        order.summarize_outputs(self)
        self.by_recipe[order.recipe.name].add(order)

    def to_jsonable(self) -> Dict[str, Any]:
        return {
            "flavour": self.flavour,
            "recipes": {k: v.to_jsonable() for k, v in self.by_recipe.items()},
            "products": {k: v.to_jsonable() for k, v in self.by_path.items()},
        }

    @classmethod
    def from_jsonable(cls, data: Dict[str, Any]):
        res = cls()
        res.flavour = data["flavour"]
        res.by_recipe = {k: RecipeOrders.from_jsonable(v) for k, v in data["recipes"].items()}
        res.by_path = {k: ProductInfo.from_jsonable(v) for k, v in data["products"].items()}
        return res


class LogEntry(NamedTuple):
    """
    One serializable log entry
    """

    ts: float
    """Timestamp in seconds"""
    level: int
    """Log level"""
    msg: str
    """Log message"""
    name: str
    """Logger name"""


class Log(Serializable):
    """
    A collection of log entries.

    Iterate :py:attr:`Log.entries` for a list of all log entries generated
    during processing.
    """

    entries: List[LogEntry]
    """List of all log entries"""

    def __init__(self) -> None:
        self.entries = []

    def append(self, *, ts: float, level: int, msg: str, name: str):
        """
        Add a log entry
        """
        self.entries.append(LogEntry(ts=ts, level=level, msg=msg, name=name))

    def to_jsonable(self) -> Dict[str, Any]:
        return {
            "entries": [e._asdict() for e in self.entries],
        }

    @classmethod
    def from_jsonable(cls, data: Dict[str, Any]):
        entries: List[Dict[str, Any]] = data["entries"]
        res = cls()
        res.entries = [LogEntry(**e) for e in entries]
        return res


class Reader(ABC):
    """
    Read functions for output bundles
    """

    @abstractmethod
    def version(self) -> str:
        """
        Return the bundle version information
        """
        raise NotImplementedError(f"{self.__class__.__name__}.version() not implemented")

    @abstractmethod
    def _load_json(self, path: str) -> Dict[str, Any]:
        """
        Load the contents of a JSON file
        """
        raise NotImplementedError(f"{self.__class__.__name__}.load_json() not implemented")

    def input_summary(self) -> InputSummary:
        """
        Return summary of all inputs used during processing
        """
        return InputSummary.from_jsonable(self._load_json("inputs.json"))

    def log(self) -> Log:
        """
        Return the log generated during processing
        """
        return Log.from_jsonable(self._load_json("log.json"))

    def products(self) -> Products:
        """
        Return metadata for all products
        """
        return Products.from_jsonable(self._load_json("products.json"))

    @abstractmethod
    def find(self) -> List[str]:
        """
        List all paths in the bundle
        """
        raise NotImplementedError(f"{self.__class__.__name__}.find() not implemented")

    @abstractmethod
    def load_product(self, bundle_path: str) -> bytes:
        """
        Load a product by its path.

        Return the raw PNG image data
        """

    @abstractmethod
    def load_artifact(self, bundle_path: str) -> bytes:
        """
        Load processing artifact.

        Return the raw file data
        """


class TarReader(Reader):
    """
    Read an output bundle from a tar file

    Usage::

        with TarReader(path) as reader:
            for name in reader.find():
                if name.endswith(".png"):
                    print(name)

    See :py:class:`Reader` for the full method list
    """

    def __init__(self, path: Path):
        """
        Read an existing output bundle
        """
        self.tarfile = tarfile.open(path, mode="r")

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.tarfile.close()

    def _load_json(self, path: str) -> Dict[str, Any]:
        with self.tarfile.extractfile(path) as fd:
            return json.load(fd)

    def version(self) -> str:
        with self.tarfile.extractfile("version.txt") as fd:
            return fd.read().strip().decode()

    def load_product(self, bundle_path: str) -> bytes:
        with self.tarfile.extractfile(bundle_path) as fd:
            return fd.read()

    def load_artifact(self, bundle_path: str) -> bytes:
        return self.load_product(bundle_path)

    def find(self) -> List[str]:
        """
        List all paths in the bundle
        """
        return self.tarfile.getnames()


class ZipReader(Reader):
    """
    Read an output bundle from a zip file

    Usage::

        with ZipReader(path) as reader:
            for name in reader.find():
                if name.endswith(".png"):
                    print(name)

    See :py:class:`Reader` for the full method list
    """

    def __init__(self, path: Path):
        """
        Read an existing output bundle
        """
        self.zipfile = zipfile.ZipFile(path, mode="r")

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.zipfile.close()

    def _load_json(self, path: str) -> Dict[str, Any]:
        return json.loads(self.zipfile.read(path))

    def version(self) -> str:
        return self.zipfile.read("version.txt").strip().decode()

    def load_product(self, bundle_path: str) -> bytes:
        return self.zipfile.read(bundle_path)

    def load_artifact(self, bundle_path: str) -> bytes:
        return self.load_product(bundle_path)

    def find(self) -> List[str]:
        """
        List all paths in the bundle
        """
        return self.zipfile.namelist()


class Writer(ABC):
    """
    Write functions for output bundles
    """

    @abstractmethod
    def _add_serializable(self, name: str, value: Serializable) -> None:
        """
        Add a serializable object to the bundle, using the given file name
        """
        ...

    def add_input_summary(self, input_summary: InputSummary):
        """
        Add inputs.json with a summary of inputs used
        """
        self._add_serializable("inputs.json", input_summary)

    def add_log(self, entries: Log):
        """
        Add log.json with log entries generated during processing.

        If no log entries were generated, log.json is not added.
        """
        if not entries.entries:
            return
        self._add_serializable("log.json", entries)

    def add_products(self, products: Products):
        """
        Add products.json with information about generated products
        """
        self._add_serializable("products.json", products)

    @abstractmethod
    def add_product(self, bundle_path: str, data: IO[bytes]):
        """
        Add a product
        """
        raise NotImplementedError(f"{self.__class__.__name__}.add_product() not implemented")

    @abstractmethod
    def add_artifact(self, bundle_path: str, data: IO[bytes]):
        """
        Add a processing artifact
        """
        raise NotImplementedError(f"{self.__class__.__name__}.add_artifact() not implemented")


class TarWriter(Writer):
    """
    Write an output bundle as a tar file.
    """

    def __init__(self, out: IO[bytes]):
        """
        Create a new output bundle, written to the given file descriptor
        """
        self.tarfile = tarfile.open(mode="w|", fileobj=out)
        with io.BytesIO() as buf:
            buf.write(b"1\n")
            buf.seek(0)
            self.add_artifact("version.txt", buf)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.tarfile.close()

    def _add_serializable(self, name: str, value: Serializable) -> None:
        as_json = value.to_jsonable()
        buf = json.dumps(as_json, indent=1).encode()
        info = tarfile.TarInfo(name=name)
        info.size = len(buf)
        with io.BytesIO(buf) as fd:
            self.tarfile.addfile(tarinfo=info, fileobj=fd)

    def add_product(self, bundle_path: str, data: IO[bytes]):
        info = tarfile.TarInfo(bundle_path)
        data.seek(0, io.SEEK_END)
        info.size = data.tell()
        data.seek(0)
        self.tarfile.addfile(info, data)

    def add_artifact(self, bundle_path: str, data: IO[bytes]):
        # Currently same as add_product
        self.add_product(bundle_path, data)


class ZipWriter(Writer):
    """
    Write an output bundle as a zip file.
    """

    def __init__(self, out: IO[bytes]):
        """
        Create a new output bundle, written to the given file descriptor
        """
        self.zipfile = zipfile.ZipFile(out, mode="w", compression=zipfile.ZIP_STORED)
        self.zipfile.writestr("version.txt", "1\n")

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.zipfile.close()

    def _add_serializable(self, name: str, value: Serializable) -> None:
        as_json = value.to_jsonable()
        buf = json.dumps(as_json, indent=1).encode()
        self.zipfile.writestr(name, buf)

    def add_product(self, bundle_path: str, data: IO[bytes]):
        self.zipfile.writestr(bundle_path, data.read())

    def add_artifact(self, bundle_path: str, data: IO[bytes]):
        # Currently same as add_product
        self.add_product(bundle_path, data)
