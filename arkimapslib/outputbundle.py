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
from .models import BaseDataModel, pydantic
from .types import ModelStep

if TYPE_CHECKING:
    from .flavours import Flavour
    from .inputs import Input, Instant
    from .orders import Order
    from .recipes import Recipe
    from .kitchen import Kitchen

log = logging.getLogger("outputbundle")


class Serializable(BaseDataModel):
    """
    Base for classes that can be serialized to JSON
    """

    def to_jsonable(self) -> Dict[str, Any]:
        """
        Return a version of this object that can be serialized to JSON, and
        deserialized with from_jsonable()
        """
        return self.dict(by_alias=True)

    @classmethod
    def from_jsonable(cls, data: Dict[str, Any]):
        """
        Recreate an object serialized by to_jsonable
        """
        # TODO: from 3.11 we can type the return value as Self
        return cls.parse_obj(data)


class InputProcessingStats(Serializable):
    """
    Statistics collected while processing inputs
    """

    #: List of strings describing computation steps, and the time they took in nanoseconds
    computation_log: List[Tuple[int, str]] = pydantic.Field(default_factory=list)
    #: List of recipes that used this input to generate products
    used_by: Set[str] = pydantic.Field(default_factory=set)

    def add_computation_log(self, elapsed: int, what: str) -> None:
        """
        Add an entry to the computation log.

        :param elapsed: elapsed time in nanoseconds
        :param what: description of the computation
        """
        self.computation_log.append((elapsed, what))

    def dict(self, *args: Any, **kwargs: Any) -> dict[str, Any]:
        res = super().dict(*args, **kwargs)
        res["used_by"] = sorted(res["used_by"])
        res["computation"] = res.pop("computation_log")
        return res

    @pydantic.root_validator(pre=True)
    def fix_layout(cls, values: Any) -> Any:
        if isinstance(values, dict) and "computation" in values:
            values["computation_log"] = values.pop("computation")
        return values


class InputSummary(Serializable):
    """
    Summary about inputs useed in processing
    """

    #: Per-input processing information indexed by input name
    inputs: Dict[str, InputProcessingStats] = pydantic.Field(default_factory=dict)

    def add(self, name: str, stats: InputProcessingStats):
        self.inputs[name] = stats

    def dict(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        res = super().dict(*args, **kwargs)
        return res["inputs"]

    @pydantic.root_validator(pre=True)
    def fix_layout(cls, values: Any) -> Any:
        return {"inputs": values}


class ReftimeOrders(Serializable):
    """
    Information and statistics for all orders for a given reftime
    """

    #: Names of inputs used
    inputs: Set[str] = pydantic.Field(default_factory=set)
    #: Numer of products produced for each step
    steps: Dict[ModelStep, int] = pydantic.Field(default_factory=Counter)
    #: Total processing time in nanoseconds
    render_time_ns: int = 0

    def add(self, order: "Order"):
        self.inputs.update(order.input_files.keys())
        self.steps[order.instant.step] += 1
        self.render_time_ns += order.render_time_ns

    def dict(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        res = super().dict(*args, **kwargs)
        res["inputs"] = sorted(res["inputs"])
        res["steps"] = {str(k): v for k, v in res["steps"].items()}
        return res


class RecipeOrders(Serializable):
    """
    Information and statistics for all orders generated from one recipe
    """

    #: Summary of all products produced for this recipe at this reference time
    by_reftime: Dict[datetime.datetime, ReftimeOrders] = pydantic.Field(
        default_factory=lambda: defaultdict(ReftimeOrders)
    )
    #: Legend information for products produced from this recipe
    legend_info: Optional[Dict[str, Any]] = None

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

    #: Name of the recipe used for this product
    recipe: Optional[str] = None
    #: Reference time
    reftime: Optional[datetime.datetime] = None
    #: Step
    step: Optional[ModelStep]
    #: Georeferencing information
    georef: Dict[str, Any] = pydantic.Field(default_factory=dict)

    def add_recipe(self, recipe: "Recipe"):
        self.recipe = recipe.name

    def add_georef(self, georef: Dict[str, Any]):
        self.georef = georef

    def add_instant(self, instant: "Instant"):
        self.reftime = instant.reftime
        self.step = instant.step

    def to_jsonable(self) -> Dict[str, Any]:
        if self.recipe is None or self.reftime is None or self.step is None:
            raise RuntimeError("Cannot write ProductInfo without filling it first")
        res: Dict[str, Any] = {
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

    #: Information about the flavour used
    flavour: Optional[Dict[str, Any]] = None
    #: Recipes used, indexed by name
    by_recipe: Dict[str, RecipeOrders] = pydantic.Field(default_factory=lambda: defaultdict(RecipeOrders))
    #: Products generated, indexed by their path
    by_path: Dict[str, ProductInfo] = pydantic.Field(default_factory=lambda: defaultdict(ProductInfo))

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


class LogEntry(Serializable):
    """
    One serializable log entry
    """

    #: Timestamp in seconds
    ts: float
    #: Log level
    level: int
    #: Log message
    msg: str
    #: Logger name
    name: str


class Log(Serializable):
    """
    A collection of log entries.

    Iterate :py:attr:`Log.entries` for a list of all log entries generated
    during processing.
    """

    #: List of all log entries
    entries: List[LogEntry] = pydantic.Field(default_factory=list)

    def append(self, *, ts: float, level: int, msg: str, name: str):
        """
        Add a log entry
        """
        self.entries.append(LogEntry(ts=ts, level=level, msg=msg, name=name))

    def dict(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        res = super().dict(*args, **kwargs)
        return res["entries"]

    @pydantic.root_validator(pre=True)
    def fix_layout(cls, values: Any) -> Any:
        if not values:
            return {"entries": []}
        if isinstance(values, dict):
            return values
        return {"entries": values}

    @classmethod
    def parse_obj(cls, obj: Any) -> "Log":
        if isinstance(obj, list):
            return super().parse_obj({"entries": obj})
        return super().parse_obj(obj)


class Reader(ABC):
    """
    Read functions for output bundles
    """

    @abstractmethod
    def __enter__(self): ...

    @abstractmethod
    def __exit__(self, exc_type, exc_value, traceback): ...

    @abstractmethod
    def version(self) -> str:
        """
        Return the bundle version information
        """

    @abstractmethod
    def _load_json(self, path: str) -> Dict[str, Any]:
        """
        Load the contents of a JSON file
        """

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
        self.path = path

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.tarfile.close()

    def _extract(self, path: str) -> IO[bytes]:
        reader = self.tarfile.extractfile(path)
        if reader is None:
            raise ValueError(f"{path} does not identify a valid file in {self.path}")
        return reader

    def _load_json(self, path: str) -> Dict[str, Any]:
        with self._extract(path) as fd:
            return json.load(fd)

    def version(self) -> str:
        with self._extract("version.txt") as fd:
            return fd.read().strip().decode()

    def load_product(self, bundle_path: str) -> bytes:
        with self._extract(bundle_path) as fd:
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
    def __enter__(self): ...

    @abstractmethod
    def __exit__(self, exc_type, exc_value, traceback): ...

    @abstractmethod
    def _add_serializable(self, name: str, value: Serializable) -> None:
        """
        Add a serializable object to the bundle, using the given file name
        """

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

    @abstractmethod
    def add_artifact(self, bundle_path: str, data: IO[bytes]):
        """
        Add a processing artifact
        """


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
