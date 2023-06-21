# from __future__ import annotations

import logging
import os
from typing import TYPE_CHECKING, Dict, Type

from .utils import TypeRegistry

if TYPE_CHECKING:
    from .orders import Order
    from .pygen import PyGen
    from .lint import Lint
    from .config import Config

log = logging.getLogger("postprocess")


class Postprocessors(TypeRegistry["Postprocessor"]):
    """
    Registry of available Postprocessor implementations
    """
    def lint(self, *, lint: "Lint", name: str, defined_in: str, **kwargs):
        cls = self.registry.get(name)
        if cls is None:
            lint.warn_postprocessor(f"postprocessor {name!r} not found", defined_in=defined_in, name=name)
            return
        cls.lint(lint=lint, name=name, defined_in=defined_in, **kwargs)


postprocessors = Postprocessors()


class Postprocessor:
    def __init__(self, *, config: "Config", **kwargs):
        self.config = config

    @classmethod
    def lint(
            cls, *,
            config: "Config",
            lint: "Lint",
            name: str,
            defined_in: str,
            **kwargs):
        """
        Consistency check the given input arguments
        """
        for k, v in kwargs.items():
            lint.warn_input(f"Unknown parameter: {k!r}", defined_in=defined_in, name=name)

    @classmethod
    def create(cls, name: str, **kwargs):
        try:
            impl_cls = postprocessors.by_name(name)
        except KeyError as e:
            raise KeyError(
                    f"flavour requires unknown postprocessor {name}."
                    f" Available: {', '.join(postprocessors.registry.keys())}") from e
        return impl_cls(**kwargs)

    def static_path(self, path: str) -> str:
        """
        Resolve path into an absolute path
        """
        for static_dir in self.config.static_dir:
            if not os.path.isdir(static_dir):
                continue
            abspath = os.path.abspath(os.path.join(static_dir, path))
            cp = os.path.commonpath((abspath, static_dir))
            if not os.path.samefile(cp, static_dir):
                raise RuntimeError(f"{path} leads outside the static directory")
            if not os.path.exists(abspath):
                continue
            return abspath
        raise RuntimeError(f"{path} does not exist inside {self.config.static_dir}")

    def add_python(self, order: "Order", full_relpath: str, gen: "PyGen") -> str:
        """
        Add a python function to postprocess the image at ``full_relpath``.

        Return the new value for ``full_relpath`` after the postprocessing
        """
        pass


@postprocessors.register
class Watermark(Postprocessor):
    """
    Write a string on the image
    """
    def __init__(self, *, message: str, font: str, x: int, y: int, **kwargs):
        super().__init__(**kwargs)
        self.message = message
        self.font = self.static_path(font)
        self.x = x
        self.y = y
        log.info("%s resolved as %s", font, self.font)
        # TODO: placement

    def add_python(self, order: "Order", full_relpath: str, gen: "PyGen") -> str:
        gen.line("from PIL import Image, ImageDraw, ImageFont")
        gen.line(f"with Image.open(os.path.join(workdir, {full_relpath!r})) as im:")
        with gen.nested() as sub:
            sub.line("draw = ImageDraw.Draw(im)")
            sub.line(f"fnt = ImageFont.truetype({self.font!r})")
            # FIXME: color hardcoded
            # FIXME: convert negative coordinates into coordinates relative to image size
            sub.line(f"draw.text(({self.x}, {self.y}), {self.message!r}, font=fnt, fill=(0, 0, 255, 128))")
            sub.line(f"im.save(os.path.join(workdir, {full_relpath!r}))")
        return full_relpath
