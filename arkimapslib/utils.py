from __future__ import annotations
from typing import Generic, TypeVar, Dict, Type

T = TypeVar('T')


class ClassRegistry(Generic[T]):
    """
    Registry of classes
    """
    registry: Dict[str, Type[T]] = {}

    @classmethod
    def register(cls, impl_cls: Type[T]):
        """
        Add an input class to the registry
        """
        name = getattr(impl_cls, "NAME", None)
        if name is None:
            name = impl_cls.__name__.lower()
        cls.registry[name] = impl_cls

    @classmethod
    def by_name(cls, name: str) -> Type[T]:
        return cls.registry[name.lower()]
