# from __future__ import annotations
from typing import BinaryIO, Optional, Union

import numpy

try:
    import eccodes
except ModuleNotFoundError:
    eccodes = None


if eccodes is None:

    class GRIB:
        def __init__(self, fname: str):
            raise RuntimeError("GRIB processing functionality is needed, but eccodes is not installed")

else:

    class GRIB:
        def __init__(self, fname: str):
            self.fname = fname
            self.fd: Optional[BinaryIO] = None
            self.gid: Optional[int] = None

        def __enter__(self):
            self.fd = open(self.fname, "rb")
            self.gid = eccodes.codes_grib_new_from_file(self.fd)
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            eccodes.codes_release(self.gid)
            self.fd.close()

        def get_long(self, k: str) -> int:
            return eccodes.codes_get_long(self.gid, k)

        def get_string(self, k: str) -> str:
            return eccodes.codes_get_string(self.gid, k)

        def get_double(self, k: str) -> float:
            return eccodes.codes_get_double(self.gid, k)

        def __setitem__(self, k: str, v: Union[int, float, str]):
            try:
                if isinstance(v, int):
                    eccodes.codes_set_long(self.gid, k, v)
                elif isinstance(v, float):
                    eccodes.codes_set_double(self.gid, k, v)
                elif isinstance(v, str):
                    eccodes.codes_set_string(self.gid, k, v)
                else:
                    raise RuntimeError(f"Cannot set {k}={v!r} (of type {type(v).__name__} in GRIB file")
            except eccodes.KeyValueNotFoundError as e:
                raise RuntimeError(f"Cannot set {k}={v!r} (of type {type(v).__name__} in GRIB file: {e}")

        @property
        def values(self) -> numpy.array:
            return eccodes.codes_get_values(self.gid)

        @values.setter
        def values(self, val: numpy.array):
            eccodes.codes_set_values(self.gid, val)

        def dumps(self) -> bytes:
            return eccodes.codes_get_message(self.gid)
