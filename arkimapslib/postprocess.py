# from __future__ import annotations

from typing import TYPE_CHECKING, Dict, Type

from .utils import TypeRegistry

if TYPE_CHECKING:
    from .orders import Order
    from .pygen import PyGen
    from .lint import Lint


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
    def __init__(self, **kwargs):
        pass

    @classmethod
    def lint(
            cls, *,
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
        self.font = font
        self.x = x
        self.y = y
        # TODO: font (load from static data)
        # TODO: placement

    def add_python(self, order: "Order", full_relpath: str, gen: "PyGen") -> str:
        gen.line("from PIL import Image, ImageDraw, ImageFont")
        gen.line(f"with Image.open(os.path.join(workdir, {full_relpath!r})) as im:")
        with gen.nested() as sub:
            sub.line("draw = ImageDraw.Draw(im)")
            # FIXME: hardcoded
            sub.line("fnt = ImageFont.truetype(os.path.join(workdir, 'LiberationSans-Regular.ttf'))")
            # FIXME: color hardcoded
            # FIXME: convert negative coordinates into coordinates relative to image size
            sub.line(f"draw.text(({self.x}, {self.y}), {self.message!r}, font=fnt, fill=(0, 0, 255, 128))")
            sub.line(f"im.save(os.path.join(workdir, {full_relpath!r}))")
        return full_relpath
