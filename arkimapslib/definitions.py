# from __future__ import annotations
import os
from pathlib import Path
from typing import Dict, List

import yaml

from .config import Config
from .flavours import Flavour
from .inputs import Inputs
from .recipes import Recipes


class Definitions:
    """
    Information loaded from YAML recipe directories
    """

    def __init__(self, *, config: Config) -> None:
        self.config = config
        self.recipes = Recipes(config=self.config)
        self.flavours: Dict[str, Flavour] = {}
        self.inputs: Inputs = Inputs()

    def load(self, paths: List[Path]) -> None:
        """
        Load recipes from the given list of directories
        """
        for path in paths:
            self.load_dir(path)

        self.recipes.resolve_derived()

    def load_dir(self, path: Path) -> None:
        """
        Load recipes from the given directory
        """
        from .inputs import Input

        path = path.absolute()
        static_path = path / "static"
        if static_path not in self.config.static_dir:
            self.config.static_dir.insert(0, static_path)

        for dirpath_str, dirnames, fnames in os.walk(path):
            dirpath = Path(dirpath_str)
            relpath = dirpath.relative_to(path)
            for fn in fnames:
                if not fn.endswith(".yaml"):
                    continue
                with (dirpath / fn).open("rt") as fd:
                    recipe = yaml.load(fd, Loader=yaml.SafeLoader)
                if relpath == Path("."):
                    relfn = fn
                else:
                    relfn = os.path.join(relpath, fn)

                inputs = recipe.pop("inputs", None)
                if inputs is not None:
                    for name, input_contents in inputs.items():
                        if "_" in name:
                            raise RuntimeError(f"{relfn}: '_' not allowed in input name {name!r}")
                        if isinstance(input_contents, list):
                            for ic in input_contents:
                                self.inputs.add(Input.create(config=self.config, name=name, defined_in=relfn, **ic))
                        else:
                            self.inputs.add(
                                Input.create(config=self.config, name=name, defined_in=relfn, **input_contents)
                            )

                flavours = recipe.pop("flavours", None)
                if flavours is not None:
                    for flavour in flavours:
                        name = flavour.pop("name", None)
                        if name is None:
                            raise RuntimeError(f"{relfn}: found flavour without name")
                        old = self.flavours.get(name)
                        if old is not None:
                            raise RuntimeError(f"{relfn}: flavour {name} was already defined in {old.defined_in}")
                        self.flavours[name] = Flavour.create(config=self.config, name=name, defined_in=relfn, **flavour)

                recipe["name"] = relfn[:-5]
                recipe["defined_in"] = relfn

                if "recipe" in recipe:
                    self.recipes.add(**recipe)

                if "extends" in recipe:
                    self.recipes.add_derived(**recipe)
