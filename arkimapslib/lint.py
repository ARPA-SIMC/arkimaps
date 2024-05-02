# from __future__ import annotations

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .flavours import Flavour

log = logging.getLogger("arkimaps.lint")


class Lint:
    """
    Collect consistency check remarks
    """

    def __init__(self, flavour: "Flavour") -> None:
        self.flavour = flavour

    def warn_input(self, msg: str, *, defined_in: str, name: str, **kwargs) -> None:
        log.warning("%s, input %s: %s", defined_in, name, msg)

    def warn_flavour(self, msg: str, *, defined_in: str, name: str, **kwargs) -> None:
        log.warning("%s, flavour %s: %s", defined_in, name, msg)

    def warn_postprocessor(self, msg: str, *, defined_in: str, name: str, **kwargs) -> None:
        log.warning("%s, postprocessor %s: %s", defined_in, name, msg)

    def warn_recipe(self, msg: str, *, defined_in: str, name: str, **kwargs) -> None:
        log.warning("%s, recipe %s: %s", defined_in, name, msg)

    def warn_recipe_step(self, msg: str, *, defined_in: str, name: str, step: str, **kwargs) -> None:
        log.warning("%s, recipe step %s in %s: %s", defined_in, step, name, msg)
