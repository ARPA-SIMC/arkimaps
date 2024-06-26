from typing import Any, BinaryIO, Callable, Dict, List, Optional, Union, overload

from . import dataset

class Metadata:
    @overload
    @classmethod
    def read_bundle(cls, str: Union[bytes, BinaryIO], dest: Callable[["Metadata"], bool]) -> bool: ...
    @overload
    @classmethod
    def read_bundle(cls, str: Union[bytes, BinaryIO]) -> List["Metadata"]: ...
    def to_python(self, type: Optional[str]) -> Dict[str, Any]: ...
    @property
    def data(self) -> bytes: ...

class Matcher: ...
