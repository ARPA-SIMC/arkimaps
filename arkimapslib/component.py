# from __future__ import annotations
from abc import ABC
from typing import TYPE_CHECKING, Any, Dict, Generic, Optional, Type, TypeVar

from .models import BaseDataModel

if TYPE_CHECKING:
    from .config import Config


SPEC = TypeVar("SPEC", bound=BaseDataModel)
ROOT = TypeVar("ROOT", bound="RootComponent")


class InvalidComponentError(Exception):
    """Exception raised when a component is badly specified."""


class Component(Generic[SPEC], ABC):
    """
    Base class for components instantiated from a dict structure parsed from
    JSON or YAML
    """

    Spec: Type[SPEC]
    spec: SPEC

    def __init_subclass__(cls, spec: Optional[Type[SPEC]] = None, **kwargs: Any) -> None:
        """
        Maintain the subclass registry
        """
        if spec is not None:
            cls.Spec = spec
        elif ABC not in cls.__bases__:
            raise InvalidComponentError(f"Component class {cls.__name__} is not abstract but lacks a spec= argument")

    def __init__(self, *, config: "Config", name: str, defined_in: str, args: Dict[str, Any]) -> None:
        """
        Common initialization for all components
        """
        # Configuration for this run
        self.config = config
        # Name of the component
        self.name = name
        # File name where this component was defined
        self.defined_in = defined_in
        # Input data that defines the component
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

    def lookup(self, name: str) -> Type[ROOT]:
        """
        Lookup a component class by name
        """
        try:
            return self.registry[name.lower()]
        except KeyError as e:
            raise KeyError(f"unknown input {name}. Available: {', '.join(self.registry.keys())}") from e


class RootComponent(Component[SPEC], ABC):
    """
    Base class for components class hierarchies.
    """

    NAME: str
    __registry__: TypeRegistry[Any]

    def __init_subclass__(cls, **kwargs: Any) -> None:
        """
        Maintain the subclass registry
        """
        super().__init_subclass__(**kwargs)

        # The first subclass found defines the root registry for that type
        if not hasattr(cls, "__registry__"):
            raise InvalidComponentError(f"Class {cls.__name__} is a root component without __registry__ member")

        if ABC in cls.__bases__:
            # Do not register abstract classes
            return

        cls.__registry__.register(cls)
