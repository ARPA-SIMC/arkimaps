# from __future__ import annotations
from typing import Dict, Optional, List, Iterable
import os
import re
import logging
from .inputs import Input, InputFile

log = logging.getLogger("arkimaps.input_registry")


class InputRegistry:
    """
    Collection of all known inputs
    """
    def __init__(self, *args, **kw):
        # List of input definitions, indexed by name
        self.inputs: Dict[str, List["Input"]] = {}

    def add_input(self, inp: "Input"):
        """
        Add an Input definition
        """
        old = self.inputs.get(inp.name)
        if old is None:
            # First time we see this input: add it
            self.inputs[inp.name] = [inp]
            return

        if len(old) == 1 and old[0].model is None:
            # We had an input for model=None (all models)
            # so we refuse to add more
            raise RuntimeError(
                    f"{inp.defined_in}: input {inp.name} for (any model) already defined in {old[0].defined_in}")

        for i in old:
            if i.model == inp.model:
                # We already had an input for this model name
                raise RuntimeError(
                        f"{inp.defined_in}: input {inp.name} (model {inp.model}) already defined in {i.defined_in}")

        # Input for a new model: store it
        old.append(inp)


class InputStorage(InputRegistry):
    """
    Container for storing input files
    """
    # TODO: merge with Pantry?
    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        self.data_root = kw["data_root"]

    def list_existing_steps(self, inp: "Input") -> Iterable["InputFile"]:
        """
        Generate a sequence of InputFile objects for all input files available
        in storage for the given input
        """
        fn_match = re.compile(rf"{re.escape(inp.pantry_basename)}\+(\d+)\.\w+")
        for fn in os.listdir(self.data_root):
            mo = fn_match.match(fn)
            if not mo:
                continue
            step = int(mo.group(1))
            yield InputFile(os.path.join(self.data_root, fn), inp, step)

    def get_steps(self, input_name: str) -> Dict[Optional[int], "InputFile"]:
        """
        Return the steps available in the pantry for the input with the given
        name
        """
        inps = self.inputs.get(input_name)
        if inps is None:
            return {}

        res: Dict[Optional[int], "InputFile"] = {}
        for inp in inps:
            steps = inp.get_steps(self)
            for step, input_file in steps.items():
                # Keep the first available version for each step
                res.setdefault(step, input_file)
        return res
