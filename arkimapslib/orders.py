# from __future__ import annotations
from typing import Dict, List, Tuple
import logging


class Order:
    """
    Serializable instructions to prepare a product, based on a recipe and its
    input files
    """
    def __init__(
            self,
            mixer: str,
            sources: Dict[str, str],
            recipe_name: str,
            step: int,
            steps: List[Tuple[str, 'Kwargs']]):
        # Name of the Mixer to use
        self.mixer = mixer
        # Dict mapping source names to pathnames of GRIB files
        self.sources = sources
        # Destination file name (without path or .png extension)
        self.basename = f"{recipe_name}+{step:03d}"
        # Recipe name
        self.recipe_name = recipe_name
        # Product step
        self.step = step
        # Recipe steps
        self.steps = steps
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
        from .mixers import Mixers

        mixer = Mixers.for_order(workdir, self)
        for name, args in self.steps:
            self.log.info("%s %r", name, args)
            meth = getattr(mixer, name, None)
            if meth is None:
                raise RuntimeError("Recipe " + self.recipe_name + " uses unknown step " + name)
            meth(**args)

        mixer.serve()
