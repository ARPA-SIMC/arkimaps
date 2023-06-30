# from __future__ import annotations

import io
import json
import tarfile
from pathlib import Path
from typing import IO, Any, Dict, List


class InputSummary:
    def __init__(self, summary: Dict[str, Any]):
        self.summary = summary


class Products:
    def __init__(self, summary: List[Dict[str, Any]]):
        self.summary = summary


class Log:
    def __init__(self, entries: List[Dict[str, Any]]):
        self.entries = entries

    def write(self, out: IO[bytes]):
        with io.BytesIO(json.dumps(self.entries, indent=1).encode()) as buf:
            out.write(buf.getvalue().encode())


class Reader:
    def __init__(self, path: Path):
        """
        Read an existing output bundle
        """
        raise NotImplementedError()


class Writer:
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
        """
        Add inputs.json with a summary of inputs used
        """
        with io.BytesIO(json.dumps(input_summary.summary, indent=1).encode()) as buf:
            info = tarfile.TarInfo(name="inputs.json")
            info.size = len(buf.getvalue())
            self.tarfile.addfile(tarinfo=info, fileobj=buf)

    def add_log(self, entries: Log):
        """
        Add log.json with log entries generated during processing.

        If no log entries were generated, log.json is not added.
        """
        if not entries.entries:
            return
        # Add processing log
        with io.BytesIO(json.dumps(entries.entries, indent=1).encode()) as buf:
            info = tarfile.TarInfo(name="log.json")
            info.size = len(buf.getvalue())
            self.tarfile.addfile(tarinfo=info, fileobj=buf)

    def add_products(self, products: Products):
        """
        Add products.json with information about generated products
        """
        # Add products summary
        with io.BytesIO(json.dumps(products.summary, indent=1).encode()) as buf:
            info = tarfile.TarInfo(name="products.json")
            info.size = len(buf.getvalue())
            self.tarfile.addfile(tarinfo=info, fileobj=buf)

    def add_product(self, bundle_path: str, data: IO[bytes]):
        """
        Add a product
        """
        info = tarfile.TarInfo(bundle_path)
        data.seek(0, io.SEEK_END)
        info.size = data.tell()
        data.seek(0)
        self.tarfile.addfile(info, data)

    def add_artifact(self, bundle_path: str, data: IO[bytes]):
        """
        Add a processing artifact
        """
        # Currently same as add_product
        self.add_product(bundle_path, data)
