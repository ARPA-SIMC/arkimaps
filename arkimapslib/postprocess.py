# from __future__ import annotations

from typing import TYPE_CHECKING, Dict, Type

from .utils import TypeRegistry

if TYPE_CHECKING:
    from .orders import Order
    from .pygen import PyGen


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

    def add_python(self, order: "Order", full_relpath: str, gen: "PyGen") -> str:
        """
        Add a python function to postprocess the image at ``full_relpath``.

        Return the new value for ``full_relpath`` after the postprocessing
        """
        pass
