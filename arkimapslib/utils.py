# from __future__ import annotations

import time
from typing import Dict, Generic, Type, TypeVar

if hasattr(time, "perf_counter_ns"):
    perf_counter_ns = time.perf_counter_ns
else:
    # Polyfill for Python < 3.7
    def perf_counter_ns() -> int:
        return int(time.perf_counter() * 1000000000)


T = TypeVar("T")


class TypeRegistry(Generic[T]):
    """
    Registry of type objects by name
    """
    def __init__(self):
        self.registry: Dict[str, Type[T]] = {}

    def register(self, impl_cls: Type[T]):
        """
        Add a class to the registry
        """
        name = getattr(impl_cls, "NAME", None)
        if name is None:
            name = impl_cls.__name__.lower()
        self.registry[name] = impl_cls
        return impl_cls

    def by_name(self, name: str) -> Type[T]:
        """
        Lookup a class by name
        """
        return self.registry[name.lower()]
