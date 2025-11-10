# from __future__ import annotations
import itertools
import sys
import subprocess
import tempfile
import unittest
from pathlib import Path
from typing import Any, TypeVar, cast, Tuple, Iterable, Iterator

from PIL import Image
import numpy as np

from arkimapslib import postprocess, orders
from arkimapslib.config import Config
from arkimapslib.pygen import PyGen

if hasattr(itertools, "batched"):
    batched = itertools.batched
else:
    # Polyfill for python < 3.12
    T = TypeVar("T")

    def batched(iterable: Iterable[T], n: int, *, strict: bool = False) -> Iterator[Tuple[T, ...]]:
        # batched('ABCDEFG', 3) → ABC DEF G
        if n < 1:
            raise ValueError("n must be at least one")
        iterator = iter(iterable)
        while True:
            batch = tuple(itertools.islice(iterator, n))
            if not batch:
                break
            if strict and len(batch) != n:
                raise ValueError("batched(): incomplete batch")
            yield batch


class TestQuantize(unittest.TestCase):
    def make_rgba_source(self) -> Image.Image:
        gradient = np.linspace(0, 1, 256)
        vert = np.tile(gradient.reshape(256, 1), (1, 256))
        hor = np.rot90(vert)

        red = (hor + vert) / 2
        green = np.rot90(red)
        blue = np.rot90(green)
        alpha = np.rot90(blue)

        raw = (np.stack((red, green, blue, alpha), axis=2) * 255).astype(np.uint8)
        return Image.fromarray(raw, mode="RGBA")

    def make_rgb_source(self) -> Image.Image:
        gradient = np.linspace(0, 1, 256)
        vert = np.tile(gradient.reshape(256, 1), (1, 256))
        hor = np.rot90(vert)

        red = (hor + vert) / 2
        green = np.rot90(red)
        blue = np.rot90(green)

        raw = (np.stack((red, green, blue), axis=2) * 255).astype(np.uint8)
        return Image.fromarray(raw, mode="RGB")

    def quantize(self, path: Path, debug: bool = False, **kwargs: Any) -> None:
        order = cast(orders.Order, None)
        quantize = postprocess.Quantize(config=Config(), name="quantize", defined_in="test code", args=kwargs)
        pygen = PyGen()
        pygen.line("workdir = '.'")
        self.assertEqual(quantize.add_python(order, path.as_posix(), pygen), path.as_posix())
        with tempfile.NamedTemporaryFile("w+t") as script:
            pygen.write(script)
            script.flush()
            subprocess.run([sys.executable, script.name], cwd=path.parent, check=True)
            if debug:
                print("\n***", path)
                pygen.write(sys.stdout)

    def count_colors(self, path: Path) -> int:
        with Image.open(path) as im:
            self.assertEqual(im.mode, "P")
            # Commented out as it does not work in rocky8
            # palette = im.getpalette(rawmode="RGBA")
            # triplet_size = 4
            entry_size = 3
            palette = im.getpalette()
            # Use strict=True from Fedora >= 42
            return len(set(batched(palette, entry_size)))
            # return len(set(batched(palette, entry_size, strict=True)))

    def assertSmaller(self, first: Path, second: Path) -> None:
        """Ensure first is a smaller file than second."""
        first_size = first.stat().st_size
        second_size = second.stat().st_size
        if first_size < second_size:
            return
        self.fail(f"{first} ({first_size}b) is not smaller than {second} ({second_size}b)")

    def assertUnchanged(self, first: Path, second: Path) -> None:
        """Ensure the two files have different contents."""
        if first.read_bytes() == second.read_bytes():
            return
        self.fail(f"{first} and {second} are different")

    def test_quantize_rgba(self) -> None:
        with tempfile.TemporaryDirectory() as workdir_str:
            workdir = Path(workdir_str)
            orig = workdir / "orig.png"

            img = self.make_rgba_source()
            img.save(orig)

            q8 = workdir / "quant8.png"
            img.save(q8)
            self.quantize(q8, colors=8, dither=False)
            q8d = workdir / "quant8d.png"
            img.save(q8d)
            self.quantize(q8d, colors=8, dither=True)
            q64 = workdir / "quant64.png"
            img.save(q64)
            self.quantize(q64, colors=64, dither=False)
            q64d = workdir / "quant64d.png"
            img.save(q64d)
            self.quantize(q64d, colors=64, dither=True)
            q256 = workdir / "quant256.png"
            img.save(q256)
            self.quantize(q256, colors=256, dither=False)
            q256d = workdir / "quant256d.png"
            img.save(q256d)
            self.quantize(q256d, colors=256, dither=True)

            # Uncomment to run an image viewer to evaluate images
            # subprocess.run(["geeqie"], cwd=workdir, check=True)

            self.assertLessEqual(self.count_colors(q8), 9)
            self.assertSmaller(q8, orig)

            self.assertLessEqual(self.count_colors(q8d), 8)
            self.assertSmaller(q8d, orig)
            self.assertSmaller(q8, q8d)

            self.assertEqual(self.count_colors(q64), 65)
            self.assertSmaller(q64, orig)
            self.assertSmaller(q8, q64)

            self.assertEqual(self.count_colors(q64d), 62)
            self.assertSmaller(q64d, orig)
            self.assertSmaller(q8d, q64d)
            self.assertSmaller(q64, q64d)

            self.assertEqual(self.count_colors(q256), 177)
            self.assertSmaller(q256, orig)
            self.assertSmaller(q64, q256)

            self.assertEqual(self.count_colors(q256), 177)
            self.assertSmaller(q256d, orig)
            self.assertSmaller(q256, q256d)

    def test_quantize_rgb(self) -> None:
        with tempfile.TemporaryDirectory() as workdir_str:
            workdir = Path(workdir_str)
            orig = workdir / "orig.png"

            img = self.make_rgb_source()
            img.save(orig)

            q8 = workdir / "quant8.png"
            img.save(q8)
            self.quantize(q8, colors=8, dither=False)
            q8d = workdir / "quant8d.png"
            img.save(q8d)
            self.quantize(q8d, colors=8, dither=True)
            q64 = workdir / "quant64.png"
            img.save(q64)
            self.quantize(q64, colors=64, dither=False)
            q64d = workdir / "quant64d.png"
            img.save(q64d)
            self.quantize(q64d, colors=64, dither=True)
            q256 = workdir / "quant256.png"
            img.save(q256)
            self.quantize(q256, colors=256, dither=False)
            q256d = workdir / "quant256d.png"
            img.save(q256d)
            self.quantize(q256d, colors=256, dither=True)

            # Uncomment to run an image viewer to evaluate images
            # subprocess.run(["geeqie"], cwd=workdir, check=True)

            self.assertLessEqual(self.count_colors(q8), 9)
            self.assertSmaller(q8, orig)

            self.assertLessEqual(self.count_colors(q8d), 9)
            self.assertSmaller(q8d, orig)
            self.assertSmaller(q8, q8d)

            self.assertLessEqual(self.count_colors(q64), 65)
            self.assertSmaller(q64, orig)
            self.assertSmaller(q8, q64)

            self.assertUnchanged(q64d, orig)

            self.assertEqual(self.count_colors(q256), 256)
            self.assertSmaller(q256, orig)
            self.assertSmaller(q64, q256)

            self.assertUnchanged(q256d, orig)
