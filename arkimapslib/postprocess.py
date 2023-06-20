# from __future__ import annotations

from typing import Dict, Type
from .utils import TypeRegistry


class Postprocessors(TypeRegistry["Postprocessor"]):
    """
    Registry of available Postprocessor implementations
    """
    pass


postprocessors = Postprocessors()


class Postprocessor:
    def __init__(self):
        pass

    @classmethod
    def create(cls, name: str, **kwargs):
        try:
            impl_cls = postprocessors.by_name(name)
        except KeyError as e:
            raise KeyError(
                    f"flavour requires unknown postprocessor {name}."
                    f" Available: {', '.join(postprocessors.registry.keys())}") from e
        return impl_cls(**kwargs)
