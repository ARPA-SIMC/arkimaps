# from __future__ import annotations

import datetime
import io
import json
import tarfile
import zipfile
from collections import Counter, defaultdict
from pathlib import Path
from typing import IO, TYPE_CHECKING, Any, Dict, List, NamedTuple, Optional, Sequence, Set

from .inputs import ModelStep

if TYPE_CHECKING:
    from .flavours import Flavour
    from .inputs import Input, Instant
    from .orders import Order
    from .recipes import Recipe


class InputSummary:
    """
    Summary about inputs useed in processing
    """

    def __init__(self) -> None:
        self.inputs: Dict[str, Dict[str, Any]] = {}

    def add(self, inp: "Input"):
        self.inputs[inp.name] = inp.stats.summarize()

    def serialize(self) -> bytes:
        """
        Serialize as a bytes object
        """
        return json.dumps(self.inputs, indent=1).encode()


class ReftimeOrders:
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
    def from_jsonable(cls, **kwargs) -> "ReftimeOrders":
        render_stats = kwargs.pop("render_stats")
        steps = kwargs.pop("steps")
        return cls(render_time_ns=render_stats["time_ns"], steps={ModelStep(k): v for k, v in steps.items()}, **kwargs)


class RecipeOrders:
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
            datetime.datetime.strptime(k, "%Y-%m-%d %H:%M:%S"): ReftimeOrders.from_jsonable(**v)
            for k, v in data.items()
        }
        return res


class ProductInfo:
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
    def from_jsonable(
        cls,
        *,
        recipe: Optional[str] = None,
        reftime: Optional[str] = None,
        step: Optional[int] = None,
        georef: Optional[Dict[str, Any]] = None,
    ):
        return cls(
            recipe=recipe,
            reftime=datetime.datetime.strptime(reftime, "%Y-%m-%d %H:%M:%S"),
            step=step,
            georef=georef,
        )


class Products:
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

    def serialize(self) -> bytes:
        """
        Serialize as a bytes object
        """
        return json.dumps(self.to_jsonable(), indent=1).encode()


class LogEntry(NamedTuple):
    """
    One serializable log entry
    """

    ts: float
    level: int
    msg: str
    name: str


class Log:
    """
    A collection of log entries
    """

    def __init__(self):
        self.entries: List[LogEntry] = []

    def append(self, *, ts: float, level: int, msg: str, name: str):
        """
        Add a log entry
        """
        self.entries.append(LogEntry(ts=ts, level=level, msg=msg, name=name))

    def serialize(self) -> bytes:
        """
        Serialize as a bytes object
        """
        return json.dumps(
            {
                "entries": [e._asdict() for e in self.entries],
            },
            indent=1,
        ).encode()


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
        summary = InputSummary()
        summary.inputs = self._load_json("inputs.json")
        return summary

    def log(self) -> Log:
        """
        Return the log information
        """
        data = self._load_json("log.json")
        res = Log()
        res.entries = [LogEntry(**e) for e in data["entries"]]
        return res

    def products(self) -> Products:
        """
        Return the products information
        """
        data = self._load_json("products.json")
        res = Products()
        res.flavour = data["flavour"]
        res.by_recipe = {k: RecipeOrders.from_jsonable(v) for k, v in data["recipes"].items()}
        res.by_path = {k: ProductInfo.from_jsonable(**v) for k, v in data["products"].items()}
        return res

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


class Writer:
    """
    Write functions for output bundles
    """

    def add_input_summary(self, input_summary: InputSummary):
        """
        Add inputs.json with a summary of inputs used
        """
        raise NotImplementedError(f"{self.__class__.__name__}.add_input_summary() not implemented")

    def add_log(self, entries: Log):
        """
        Add log.json with log entries generated during processing.

        If no log entries were generated, log.json is not added.
        """
        raise NotImplementedError(f"{self.__class__.__name__}.add_log() not implemented")

    def add_products(self, products: Products):
        """
        Add products.json with information about generated products
        """
        raise NotImplementedError(f"{self.__class__.__name__}.add_products() not implemented")

    def add_product(self, bundle_path: str, data: IO[bytes]):
        """
        Add a product
        """
        raise NotImplementedError(f"{self.__class__.__name__}.add_product() not implemented")

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

    def add_input_summary(self, input_summary: InputSummary):
        buf = input_summary.serialize()
        info = tarfile.TarInfo(name="inputs.json")
        info.size = len(buf)
        with io.BytesIO(buf) as fd:
            self.tarfile.addfile(tarinfo=info, fileobj=fd)

    def add_log(self, entries: Log):
        if not entries.entries:
            return
        # Add processing log
        buf = entries.serialize()
        info = tarfile.TarInfo(name="log.json")
        info.size = len(buf)
        with io.BytesIO(buf) as fd:
            self.tarfile.addfile(tarinfo=info, fileobj=fd)

    def add_products(self, products: Products):
        buf = products.serialize()
        info = tarfile.TarInfo(name="products.json")
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

    def add_input_summary(self, input_summary: InputSummary):
        self.zipfile.writestr("inputs.json", input_summary.serialize())

    def add_log(self, entries: Log):
        if not entries.entries:
            return
        self.zipfile.writestr("log.json", entries.serialize())

    def add_products(self, products: Products):
        self.zipfile.writestr("products.json", products.serialize())

    def add_product(self, bundle_path: str, data: IO[bytes]):
        self.zipfile.writestr(bundle_path, data.read())

    def add_artifact(self, bundle_path: str, data: IO[bytes]):
        # Currently same as add_product
        self.add_product(bundle_path, data)
