# from __future__ import annotations
from typing import Dict
import logging

# if TYPE_CHECKING:
from . import recipes
from . import inputs


class Order:
    """
    Serializable instructions to prepare a product, based on a recipe and its
    input files
    """
    def __init__(
            self,
            mixer: str,
            sources: Dict[str, inputs.InputFile],
            recipe: "recipes.Recipe",
            step: int):
        # Name of the Mixer to use
        self.mixer = mixer
        # Dict mapping source names to pathnames of GRIB files
        self.sources = sources
        # Destination file name (without path or .png extension)
        self.basename = f"{recipe.name}+{step:03d}"
        # Recipe name
        self.recipe = recipe
        # Product step
        self.step = step
        # Output file name, set after the product has been rendered
        self.output = None
        # Logger for this output
        self.log = logging.getLogger(f"arkimaps.order.{self.basename}")

    def __getstate__(self):
        state = self.__dict__.copy()
        # logger objects don't pickle correctly on python 3.6
        del state['log']
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)
        self.log = logging.getLogger(f"arkimaps.order.{self.basename}")

    def __str__(self):
        return self.basename

    def __repr__(self):
        return self.basename

    def prepare(self, workdir: str):
        """
        Run all the steps of the recipe and render the resulting file
        """
        from .mixers import Mixer

        mixer = Mixer(workdir, self)
        for step in self.recipe.steps:
            self.log.info("%s %r", step.name, step.params)
            step.run(mixer)

        mixer.serve()
