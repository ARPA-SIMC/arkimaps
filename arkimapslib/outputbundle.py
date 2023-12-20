# from __future__ import annotations

import datetime
import io
import json
import tarfile
import zipfile
from abc import ABC, abstractmethod
from collections import Counter, defaultdict
from pathlib import Path
from typing import IO, TYPE_CHECKING, Any, Dict, List, NamedTuple, Optional, Sequence, Set

from .types import ModelStep

if TYPE_CHECKING:
    from .flavours import Flavour
    from .inputs import Input, Instant
    from .orders import Order
    from .recipes import Recipe


class Serializable(ABC):
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

    def __init__(self) -> None:
        # List of strings describing computation steps, and the time they took
        # in nanoseconds
        self.computation_log: List[Tuple[int, str]] = []
        # List of recipes that used this input to generate products
        self.used_by: Set[str] = set()

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
        res.computation_log = [tuple(i) for i in data["computation"]]
        res.used_by = set(data["used_by"])
        return res


class InputSummary(Serializable):
    """
    Summary about inputs useed in processing
    """

    def __init__(self) -> None:
        self.inputs: Dict[str, InputProcessingStats] = {}

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

    def __init__(
        self,
        *,
        inputs: Optional[Sequence[str]] = None,
        steps: Optional[Dict[ModelStep, int]] = None,
        legend_info: Optional[Dict[str, Any]] = None,
        render_time_ns: int = 0,
    ):
        self.inputs: Set[str] = set(inputs) if inputs else set()
        self.steps: Dict[ModelStep, int] = Counter()
        if steps:
            self.steps.update(steps)
        self.legend_info: Optional[Dict[str, Any]] = legend_info
        self.render_time_ns: int = render_time_ns

    def add(self, order: "Order"):
        self.inputs.update(order.input_files.keys())
        self.steps[order.instant.step] += 1
        if order.legend_info:
            self.legend_info = order.legend_info
        self.render_time_ns += order.render_time_ns

    def to_jsonable(self) -> Dict[str, Any]:
        return {
            "inputs": sorted(self.inputs),
            "steps": {str(s): c for s, c in self.steps.items()},
            "legend_info": self.legend_info,
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
            legend_info=data.get("legend_info"),
        )


class RecipeOrders(Serializable):
    """
    Information and statistics for all orders generated from one recipe
    """

    def __init__(self):
        self.by_reftime: Dict[datetime.datetime, ReftimeOrders] = defaultdict(ReftimeOrders)

    def add(self, orders: List["Order"]):
        for order in orders:
            self.by_reftime[order.instant.reftime].add(order)

    def to_jsonable(self) -> Dict[str, Any]:
        return {
            reftime.strftime("%Y-%m-%d %H:%M:%S"): stats.to_jsonable() for reftime, stats in self.by_reftime.items()
        }

    @classmethod
    def from_jsonable(cls, data: Dict[str, Any]):
        res = cls()
        res.by_reftime = {
            datetime.datetime.strptime(k, "%Y-%m-%d %H:%M:%S"): ReftimeOrders.from_jsonable(v) for k, v in data.items()
        }
        return res


class ProductInfo(Serializable):
    """
    Information about a generated product image
    """

    def __init__(
        self,
        *,
        recipe: Optional[str] = None,
        reftime: Optional[datetime.datetime] = None,
        step: Optional[ModelStep] = None,
        georef: Optional[Dict[str, Any]] = None,
    ):
        self.recipe: Optional[str] = recipe
        self.reftime: Optional[datetime.datetime] = reftime
        self.step: Optional[ModelStep] = step
        self.georef: Dict[str, Any] = georef if georef is not None else {}

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

    def __init__(self) -> None:
        self.flavour: Optional[Dict[str, Any]] = None
        self.by_recipe: Dict[str, RecipeOrders] = defaultdict(RecipeOrders)
        self.by_path: Dict[str, ProductInfo] = defaultdict(ProductInfo)

    def add_flavour(self, flavour: "Flavour"):
        self.flavour = flavour.summarize()

    def add_orders(self, recipe: "Recipe", orders: List["Order"]):
        self.by_recipe[recipe.name].add(orders)

        for order in orders:
            order.summarize_outputs(self)

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
    level: int
    msg: str
    name: str


class Log(Serializable):
    """
    A collection of log entries
    """

    def __init__(self) -> None:
        self.entries: List[LogEntry] = []

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


class Reader:
    """
    Read functions for output bundles
    """

    def version(self) -> str:
        """
        Return the bundle version information
        """
        raise NotImplementedError(f"{self.__class__.__name__}.version() not implemented")

    def _load_json(self, path: str) -> Dict[str, Any]:
        """
        Load the contents of a JSON file
        """
        raise NotImplementedError(f"{self.__class__.__name__}.load_json() not implemented")

    def input_summary(self) -> InputSummary:
        """
        Return the input summary information
        """
        return InputSummary.from_jsonable(self._load_json("inputs.json"))

    def log(self) -> Log:
        """
        Return the log information
        """
        return Log.from_jsonable(self._load_json("log.json"))

    def products(self) -> Products:
        """
        Return the products information
        """
        return Products.from_jsonable(self._load_json("products.json"))

    def find(self) -> List[str]:
        """
        List all paths in the bundle
        """
        raise NotImplementedError(f"{self.__class__.__name__}.find() not implemented")


class TarReader(Reader):
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

    def find(self) -> List[str]:
        """
        List all paths in the bundle
        """
        return self.tarfile.getnames()


class ZipReader(Reader):
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
