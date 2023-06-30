# from __future__ import annotations

import io
import json
import tarfile
import zipfile
from pathlib import Path
from typing import IO, Any, Dict, List, NamedTuple


class InputSummary:
    def __init__(self, summary: Dict[str, Any]):
        self.summary = summary


class Products:
    def __init__(self, summary: List[Dict[str, Any]]):
        self.summary = summary


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
        self.entries.append(
                LogEntry(ts=ts, level=level, msg=msg, name=name))

    def serialize(self) -> bytes:
        """
        Serialize as a bytes object
        """
        serializable = [e._asdict() for e in self.entries]
        return json.dumps(serializable, indent=1).encode()


class Reader:
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

    def find(self) -> List[str]:
        """
        List all paths in the bundle
        """
        return self.zipfile.namelist()


class Writer:
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

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.tarfile.close()

    def add_input_summary(self, input_summary: InputSummary):
        with io.BytesIO(json.dumps(input_summary.summary, indent=1).encode()) as buf:
            info = tarfile.TarInfo(name="inputs.json")
            info.size = len(buf.getvalue())
            self.tarfile.addfile(tarinfo=info, fileobj=buf)

    def add_log(self, entries: Log):
        if not entries.entries:
            return
        # Add processing log
        buf = entries.entries.serialize()
        info = tarfile.TarInfo(name="log.json")
        info.size = len(buf)
        with io.BytesIO(buf) as fd:
            self.tarfile.addfile(tarinfo=info, fileobj=fd)

    def add_products(self, products: Products):
        # Add products summary
        with io.BytesIO(json.dumps(products.summary, indent=1).encode()) as buf:
            info = tarfile.TarInfo(name="products.json")
            info.size = len(buf.getvalue())
            self.tarfile.addfile(tarinfo=info, fileobj=buf)

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

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.zipfile.close()

    def add_input_summary(self, input_summary: InputSummary):
        self.zipfile.writestr("inputs.json", json.dumps(input_summary.summary, indent=1))

    def add_log(self, entries: Log):
        if not entries.entries:
            return
        self.zipfile.writestr("log.json", entries.serialize())

    def add_products(self, products: Products):
        self.zipfile.writestr("products.json", json.dumps(products.summary, indent=1))

    def add_product(self, bundle_path: str, data: IO[bytes]):
        self.zipfile.writestr(bundle_path, data.read())

    def add_artifact(self, bundle_path: str, data: IO[bytes]):
        # Currently same as add_product
        self.add_product(bundle_path, data)
