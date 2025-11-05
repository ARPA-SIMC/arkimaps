# from __future__ import annotations
from abc import ABC
from typing import TYPE_CHECKING, Any, Dict, Generic, Type, TypeVar

from .models import BaseDataModel

if TYPE_CHECKING:
    from .config import Config


ROOT = TypeVar("ROOT", bound="RootComponent[BaseDataModel, Any]")
SPEC = TypeVar("SPEC", bound=BaseDataModel)


class InvalidComponentError(Exception):
    """Exception raised when a component is badly specified."""


class Component(Generic[SPEC], ABC):
    """
    Base class for components instantiated from a dict structure parsed from
    JSON or YAML
    """

    Spec: Type[SPEC]

    def __init__(self, *, config: "Config", name: str, defined_in: str, args: Dict[str, Any]) -> None:
        """
        Common initialization for all components
        """
        # Configuration for this run
        self.config = config
        # Name of the input in the recipe
        self.name = name
        # File name where this input was defined
        self.defined_in = defined_in
        # Input data as specified in the recipe
        self.spec = self.Spec(**args)


class TypeRegistry(Generic[ROOT]):
    """
    Registry of type objects by name
    """

    def __init__(self) -> None:
        self.registry: Dict[str, Type[ROOT]] = {}

    def register(self, impl_cls: Type[ROOT]) -> Type[ROOT]:
        """
        Add a class to the registry
        """
        name = getattr(impl_cls, "NAME", None)
        if name is None:
            name = impl_cls.__name__.lower()
        self.registry[name] = impl_cls
        return impl_cls

    def by_name(self, name: str) -> Type[ROOT]:
        """
        Lookup a class by name
        """
        return self.registry[name.lower()]


class RootComponent(Generic[SPEC], Component[SPEC], ABC):
    """
    Base class for components class hierarchies.
    """

    NAME: str
    __registry__: TypeRegistry[Any]

    def __init_subclass__(cls, **kwargs: Any) -> None:
        """
        Maintain the subclass registry
        """
        # The first subclass found defines the root registry for that type
        if not hasattr(cls, "__registry__"):
            raise InvalidComponentError(f"Class {cls.__name__} is a root component without __registry__ member")

        if ABC in cls.__bases__:
            # Do not register abstract classes
            return

        cls.__registry__.register(cls)

    @classmethod
    def lookup(cls, name: str) -> Type[ROOT]:
        """
        Lookup a component class by name
        """
        try:
            return cls.__registry__.by_name(name)
        except KeyError as e:
            raise KeyError(f"unknown input {name}. Available: {', '.join(cls.__registry__.registry.keys())}") from e
