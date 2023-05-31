# from __future__ import annotations

import logging

log = logging.getLogger("arkimaps.lint")


class Lint:
    """
    Collect consistency check remarks
    """
    def warn_input(self, msg: str, *, defined_in: str, name: str, **kwargs) -> None:
        log.warning("%s, input %s: %s", defined_in, name, msg)

    def warn_flavour(self, msg: str, *, defined_in: str, name: str, **kwargs) -> None:
        log.warning("%s, flavour %s: %s", defined_in, name, msg)

    def warn_recipe(self, msg: str, *, defined_in: str, name: str, **kwargs) -> None:
        log.warning("%s, recipe %s: %s", defined_in, name, msg)

    def warn_recipe_step(self, msg: str, *, defined_in: str, name: str, step: str, **kwargs) -> None:
        log.warning("%s, recipe step %s in %s: %s", defined_in, step, name, msg)
