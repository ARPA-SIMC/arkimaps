# from __future__ import annotations

from abc import ABC
import time
from typing import Any, Dict, Generic, Type, TypeVar, TYPE_CHECKING

from .models import BaseDataModel

if TYPE_CHECKING:
    from .config import Config

if hasattr(time, "perf_counter_ns"):
    perf_counter_ns = time.perf_counter_ns
else:
    # Polyfill for Python < 3.7
    def perf_counter_ns() -> int:
        return int(time.perf_counter() * 1000000000)


T = TypeVar("T", bound="Component[Any]")
SPEC = TypeVar("SPEC", bound=BaseDataModel)


class TypeRegistry(Generic[T]):
    """
    Registry of type objects by name
    """

    def __init__(self) -> None:
        self.registry: Dict[str, Type[T]] = {}

    def register(self, impl_cls: Type[T]) -> Type[T]:
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


class Component(Generic[T], ABC):
    """
    Base class for components class hierarchies.

    Components support being defined by a dict structure parsed from JSON or
    YAML, from a registry of subclass types.
    """

    NAME: str
    __component_label__: str
    __registry__: TypeRegistry[T]

    def __init_subclass__(cls, **kwargs: Any) -> None:
        """
        Maintain the subclass registry
        """
        # The first subclass found defines the root registry for that type
        if not hasattr(cls, "__registry__"):
            cls.__registry__ = TypeRegistry[T]()
            cls.__component_label__ = cls.__name__.lower()

        if ABC in cls.__bases__:
            # Do not register abstract classes
            return

        cls.__registry__.register(cls)

    @classmethod
    def lookup(cls, name: str) -> Type[T]:
        """
        Lookup a component class by name
        """
        try:
            return cls.__registry__.by_name(name)
        except KeyError as e:
            raise KeyError(f"unknown input {name}. Available: {', '.join(cls.__registry__.registry.keys())}") from e

    def __init__(self, *, config: "Config", name: str, defined_in: str) -> None:
        """
        Common initialization for all components
        """
        # Configuration for this run
        self.config = config
        # Name of the input in the recipe
        self.name = name
        # File name where this input was defined
        self.defined_in = defined_in
