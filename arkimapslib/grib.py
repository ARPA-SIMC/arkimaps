# from __future__ import annotations
from typing import TYPE_CHECKING, BinaryIO, Optional, Union

if TYPE_CHECKING:
    from numpy.typing import NDArray

try:
    import eccodes

    HAVE_ECCODES = True
except ModuleNotFoundError:
    HAVE_ECCODES = False


class GRIB:
    def __init__(self, fname: str):
        self.fname = fname
        self.fd: Optional[BinaryIO] = None
        self.gid: Optional[int] = None

    def __enter__(self):
        if not HAVE_ECCODES:
            raise RuntimeError("GRIB processing functionality is needed, but eccodes is not installed")

        self.fd = open(self.fname, "rb")
        self.gid = eccodes.codes_grib_new_from_file(self.fd)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        eccodes.codes_release(self.gid)
        self.fd.close()

    def get_long(self, k: str) -> int:
        assert self.gid is not None
        return eccodes.codes_get_long(self.gid, k)

    def get_string(self, k: str) -> str:
        assert self.gid is not None
        return eccodes.codes_get_string(self.gid, k)

    def get_double(self, k: str) -> float:
        assert self.gid is not None
        return eccodes.codes_get_double(self.gid, k)

    def __setitem__(self, k: str, v: Union[int, float, str]):
        assert self.gid is not None
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
    def values(self) -> "NDArray":
        assert self.gid is not None
        return eccodes.codes_get_values(self.gid)

    @values.setter
    def values(self, val: "NDArray"):
        assert self.gid is not None
        eccodes.codes_set_values(self.gid, val)

    def dumps(self) -> bytes:
        assert self.gid is not None
        return eccodes.codes_get_message(self.gid)
