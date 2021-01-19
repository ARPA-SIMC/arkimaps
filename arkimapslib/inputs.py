from __future__ import annotations
from typing import TYPE_CHECKING, Dict, Any, Optional, NamedTuple, Sequence

if TYPE_CHECKING:
    import arkimet

    # Used for kwargs-style dicts
    Kwargs = Dict[str, Any]


class Input:
    """
    An input element to a recipe
    """
    def __init__(
            self,
            name: str,
            arkimet: str,
            eccodes: str,
            mgrib: Optional[Kwargs] = None):
        # name, identifying this instance among other alternatives for this input
        self.name = name
        # arkimet matcher filter
        self.arkimet = arkimet
        # Compiled arkimet matcher, when available/used
        self.arkimet_matcher: Optional[arkimet.Matcher] = None
        # grib_filter if expression
        self.eccodes = eccodes
        # Extra arguments passed to mgrib on loading
        self.mgrib = mgrib

    def __getstate__(self):
        # Don't pickle arkimet_matcher, which is unpicklable and undeeded
        return {
            "name": self.name,
            "arkimet": self.arkimet,
            "arkimet_matcher": None,
            "eccodes": self.eccodes,
            "mgrib": self.mgrib,
        }

    def select_file(self, name: str, step: int, input_files: Sequence["InputFile"]) -> "InputFile":
        """
        Given a recipe input name, a step, and available input files for that
        step, select the input file (or generate a new one) that can be used as
        input for the recipe
        """
        # Look for files that satisfy this input
        for f in input_files:
            if f.name == name and f.info == self:
                return f
        return None

    def compile_arkimet_matcher(self, session: arkimet.Session):
        self.arkimet_matcher = session.matcher(self.arkimet)

    def document(self, file, indent=4):
        """
        Document the details about this input in Markdown
        """
        ind = " " * indent
        print(f"{ind}* **Arkimet matcher**: `{self.arkimet}`", file=file)
        print(f"{ind}* **grib_filter matcher**: `{self.eccodes}`", file=file)
        if self.mgrib:
            for k, v in self.mgrib.items():
                print(f"{ind}* **mgrib {{k}}**: `{v}`", file=file)


class InputFile(NamedTuple):
    """
    An input file stored in the pantry
    """
    # Pathname to the file
    pathname: str
    # Input name in the recipe
    name: str
    # Forecast step
    step: int
    # Input with information about the file
    info: Input
