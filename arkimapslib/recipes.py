from __future__ import annotations
from typing import TYPE_CHECKING, Dict, Any, List, Tuple, Iterator, Optional
from collections import defaultdict
import os
import inspect
import json
import logging

if TYPE_CHECKING:
    import arkimet

    # Used for kwargs-style dicts
    Kwargs = Dict[str, Any]

log = logging.getLogger("arkimaps.recipes")


class Recipes:
    """
    Repository of all known recipes
    """
    def __init__(self):
        self.recipes = []

    def get(self, name: str):
        """
        Return a recipe by name
        """
        for r in self.recipes:
            if r.name == name:
                return r
        raise KeyError(f"Recipe `{name}` does not exist")

    def document(self, path: str):
        """
        Generate markdown documentation for the recipes found in the given path
        """
        for recipe in self.recipes:
            dest = os.path.join(path, recipe.name) + '.yaml.md'
            recipe.document(dest)


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


class Recipe:
    """
    A parsed and validated recipe
    """
    def __init__(self, name: str, data: Kwargs):
        self.name = name

        # Name of the mixer to use
        self.mixer: str = data.get("mixer", "default")

        # Get the recipe description
        self.description: str = data.get("description", "Unnamed recipe")

        # Get the list of input queries
        self.inputs: Dict[str, List[Input]] = defaultdict(list)
        for name, inputs in data.get("inputs", {}).items():
            for info in inputs:
                self.inputs[name].append(Input(**info))

        # Get the recipe steps
        self.steps: List[Tuple[str, Kwargs]] = []
        for s in data.get("recipe", ()):
            if not isinstance(s, dict):
                raise RuntimeError("recipe step is not a dict")
            step = s.pop("step", None)
            if step is None:
                raise RuntimeError("recipe step does not contain a 'step' name")
            self.steps.append((step, s))

    def document(self, dest: str):
        from .mixer import Mixers
        mixer = Mixers.registry[self.mixer]

        with open(dest, "wt") as fd:
            print(f"# {self.name}: {self.description}", file=fd)
            print(file=fd)
            print(f"Mixer: **{self.mixer}**", file=fd)
            print(file=fd)
            print("## Inputs", file=fd)
            print(file=fd)
            for name, inputs in self.inputs.items():
                print(f"* **{name}**:", file=fd)
                if len(inputs) == 1:
                    inputs[0].document(indent=4, file=fd)
                else:
                    for idx, i in enumerate(inputs, start=1):
                        print(f"    * **Option {idx}**:", file=fd)
                        inputs[0].document(indent=8, file=fd)
            print(file=fd)
            print("## Steps", file=fd)
            print(file=fd)
            for name, args in self.steps:
                print(f"### {name}", file=fd)
                print(file=fd)
                print(inspect.getdoc(getattr(mixer, name)), file=fd)
                print(file=fd)
                if args:
                    print("With arguments:", file=fd)
                    print("```", file=fd)
                    # FIXME: dump as yaml?
                    print(json.dumps(args, indent=2), file=fd)
                    print("```", file=fd)
                print(file=fd)

    def _orders_from_scanner(self, workdir: str, scanner: "Scanner") -> Iterator["Order"]:
        """
        Given a scanner, scan inputs and generate orders with the results
        """
        # Enumerate sources for all inputs, and aggregate them by step and input name
        for name, inputs in self.inputs.items():
            # Enumerate all the options and use the first that gives us data
            for idx, i in enumerate(inputs, start=1):
                count = scanner.scan(name, idx, i)
                if not count:
                    continue

                log.info("%s input %s#%d: %d sources found", self.name, name, idx, count)

        # Generate orders based on the data we found
        count_generated = 0
        for output_step, sources in scanner.by_step.items():
            if len(sources) != len(self.inputs):
                log.debug(
                    "%s+%03d: only %d/%d inputs satisfied: skipping",
                    self.name, output_step, len(sources), len(self.inputs))
                continue

            basename = f"{self.name}+{output_step:03d}"
            dest = os.path.join(workdir, basename)

            count_generated += 1

            yield Order(
                mixer=self.mixer,
                sources=sources,
                dest=dest,
                basename=basename,
                recipe=self.name,
                steps=self.steps,
            )

        log.info("%s: %d orders created", self.name, count_generated)


class Scanner:
    """
    Generate and aggregate input data
    """
    def __init__(
            self,
            recipe: Recipe,
            output_steps: Optional[List[int]] = None):
        self.recipe = recipe
        self.output_steps = output_steps

        # Order information by step
        # by_step[step][input_name][key] = val
        self.by_step: Dict[int, Dict[str, Dict[str, Any]]] = defaultdict(dict)


class ArkimetInputScanner(Scanner):
    """
    Query the arkimet reader for an input and generate orders based on the data
    that comes out
    """
    def __init__(
            self,
            recipe: Recipe,
            reader: arkimet.dataset.Reader,
            output_steps: Optional[List[int]] = None):
        super().__init__(recipe, output_steps)
        self.reader = reader

        # Order information by step
        # by_step[step][input_name][key] = val
        self.by_step: Dict[int, Dict[str, Dict[str, Any]]] = defaultdict(dict)

    def scan(self, name: str, idx: int, i: Input):
        if i.arkimet_matcher is None:
            log.debug("%s input %s#%d: skipping input with no arkimet matcher", self.recipe.name, name, idx)
            return 0

        count = 0
        for md in self.reader.query_data(i.arkimet_matcher):
            trange = md.to_python("timerange")
            output_step = trange['p1']
            if self.output_steps is not None and output_step not in self.output_steps:
                continue

            source = md.to_python("source")
            pathname = os.path.join(source["basedir"], source["file"], f"{source['offset']:06d}.grib")

            count += 1

            # Don't replace a source found by a previous input
            if name in self.by_step:
                continue
            self.by_step[output_step][name] = {
                "input": i,
                "source": pathname,
            }

        return count


class ArkimetRecipe(Recipe):
    def __init__(self, name: str, data: Kwargs, session: Optional[arkimet.dataset.Session]):
        super().__init__(name, data)
        for input_list in self.inputs.values():
            for i in input_list:
                i.compile_arkimet_matcher(session)

    def make_orders(
            self,
            reader: arkimet.dataset.Reader,
            workdir: str,
            output_steps: Optional[List[int]] = None) -> Iterator["Order"]:
        scanner = ArkimetInputScanner(self, reader, output_steps)
        yield from self._orders_from_scanner(workdir, scanner)


class EccodesInputScanner(Scanner):
    """
    Query the arkimet reader for an input and generate orders based on the data
    that comes out
    """
    def __init__(
            self,
            recipe: Recipe,
            input_dir: str,
            output_steps: Optional[List[int]] = None):
        super().__init__(recipe, output_steps)
        self.input_dir = input_dir

        # Read all available input files in a dict indexed by input name
        # and step: {input_name: {step: filename}}
        self.files = defaultdict(dict)
        for fname in os.listdir(input_dir):
            if not fname.endswith(".grib"):
                continue
            name, step = fname[:-5].rsplit("+")
            step = int(step)
            if output_steps is not None and step not in output_steps:
                continue
            self.files[name][step] = fname

    def scan(self, name: str, idx: int, i: Input):
        count = 0
        for step, fname in self.files[name].items():
            pathname = os.path.join(self.input_dir, fname)

            count += 1

            # Don't replace a source found by a previous input
            if name in self.by_step:
                continue
            self.by_step[step][name] = {
                "input": i,
                "source": pathname,
            }

        return count


class EccodesRecipe(Recipe):
    def make_orders(
            self,
            workdir: str,
            output_steps: Optional[List[int]] = None) -> Iterator["Order"]:
        input_dir = os.path.join(workdir, self.name)
        scanner = EccodesInputScanner(self, input_dir, output_steps)
        yield from self._orders_from_scanner(workdir, scanner)


class Order:
    """
    Serializable instructions to prepare a product, based on a recipe and its
    input files
    """
    def __init__(
            self,
            mixer: str,
            sources: Dict[str, str],
            dest: str,
            basename: str,
            recipe: str,
            steps: List[Tuple[str, Kwargs]]):
        # Name of the Mixer to use
        self.mixer = mixer
        # Dict mapping source names to pathnames of GRIB files
        self.sources = sources
        # Destination file path (without .png extension)
        self.dest = dest
        # Destination file name (without path or .png extension)
        self.basename = basename
        # Recipe name
        self.recipe = recipe
        # Recipe steps
        self.steps = steps
        # Output file name, set after the product has been rendered
        self.output = None
        # Logger for this output
        self.log = logging.getLogger(f"arkimaps.order.{basename}")

    def prepare(self):
        """
        Run all the steps of the recipe and render the resulting file
        """
        from arkimapslib.mixer import Mixers

        mixer = Mixers.for_order(self)
        for name, args in self.steps:
            self.log.info("%s %r", name, args)
            meth = getattr(mixer, name, None)
            if meth is None:
                raise RuntimeError("Recipe " + self.name + " uses unknown step " + name)
            meth(**args)

        mixer.serve()
