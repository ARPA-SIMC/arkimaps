from __future__ import annotations
from typing import TYPE_CHECKING, ContextManager, Optional, Iterable, BinaryIO, List, Iterator, Dict, Any
from collections import defaultdict
import contextlib
import subprocess
import sys
import os
import arkimet
import logging
from .recipes import Order

if TYPE_CHECKING:
    from .recipes import Recipes, Recipe, Input
    from .kitchen import Kitchen

log = logging.getLogger("arkimaps.pantry")


class Pantry:
    """
    Storage of GRIB files to be processed
    """
    def __init__(self, kitchen: Kitchen, root: str):
        # General run state
        self.kitchen = kitchen
        # Root directory where inputs are stored
        self.root = root

    def fill(self, recipes: Recipes, path: Optional[str] = None):
        """
        Read data from standard input and acquire it into the pantry
        """
        raise NotImplementedError(f"{self.__class__.__name__}.fill() not implemented")

    def order(self, name: str, step: int) -> Order:
        """
        Return an order for the given recipe name and output step
        """
        raise NotImplementedError(f"{self.__class__.__name__}.order() not implemented")

    def orders(self, recipes: Recipes) -> Iterable[Order]:
        """
        Return all orders that can be made with this pantry
        """
        raise NotImplementedError(f"{self.__class__.__name__}.orders() not implemented")

    def store_processing_artifacts(self, tarout):
        """
        Store relevant processing artifacts in the output tarball
        """
        pass

    @contextlib.contextmanager
    def input(self, path: Optional[str] = None):
        """
        Open the binary input stream, from a file, or standard input if path is
        None
        """
        if path is None:
            yield sys.stdin.buffer
        else:
            with open(path, "rb") as fd:
                yield fd

    def _orders_from_scanner(self, recipe, workdir: str, scanner: "Scanner") -> Iterator["Order"]:
        """
        Given a scanner, scan inputs and generate orders with the results
        """
        # Enumerate sources for all inputs, and aggregate them by step and input name
        for name, inputs in recipe.inputs.items():
            # Enumerate all the options and use the first that gives us data
            for idx, i in enumerate(inputs, start=1):
                count = scanner.scan(name, idx, i)
                if not count:
                    continue

                log.info("%s input %s#%d: %d sources found", recipe.name, name, idx, count)

        # Generate orders based on the data we found
        count_generated = 0
        for output_step, sources in scanner.by_step.items():
            if len(sources) != len(recipe.inputs):
                log.debug(
                    "%s+%03d: only %d/%d inputs satisfied: skipping",
                    recipe.name, output_step, len(sources), len(recipe.inputs))
                continue

            basename = f"{recipe.name}+{output_step:03d}"
            dest = os.path.join(workdir, basename)

            count_generated += 1

            yield Order(
                mixer=recipe.mixer,
                sources=sources,
                dest=dest,
                basename=basename,
                recipe=recipe.name,
                steps=recipe.steps,
            )

        log.info("%s: %d orders created", recipe.name, count_generated)


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


class ArkimetPantry(Pantry):
    """
    Arkimet-based storage of GRIB files to be processed
    """
    def __init__(self, kitchen: Kitchen, root: str):
        super().__init__(kitchen, root)
        self.ds_root = os.path.join(self.root, 'arkimet_pantry')

        self.config = arkimet.cfg.Section({
            "format": "grib",
            "step": "yearly",
            "name": "pantry",
            "path": self.ds_root,
            "type": "iseg",
            "unique": "reftime, level, timerange, product",
            # Tell datasets to be fast at the cost of leaving an inconsistent
            # state in case of errors. We can do that since we work on a
            # temporary directory.
            "eatmydata": "yes",
        })

    def fill(self, recipes: Recipes, path: Optional[str] = None):
        """
        Read data from standard input and acquire it into the pantry
        """
        with self.writer() as writer:
            dispatcher = ArkimetDispatcher(writer)
            with self.input(path=path) as infd:
                dispatcher.read(infd)

    def order(self, recipes: Recipes, name: str, step: int) -> Order:
        """
        Return an order for the given recipe name and output step
        """
        recipe = recipes.get(name)
        order = None
        with self.reader() as reader:
            for o in recipe.make_orders(reader, self.root, output_steps=[step]):
                if order is not None:
                    raise RuntimeError(f"Multiple options found to generate {name}+{step:03d}")
                order = o
        if order is None:
            raise KeyError(f"No option found to generate {name}+{step:03d}")
        return order

    def orders(self, recipes: Recipes) -> Iterable[Order]:
        """
        Return all orders that can be made with this pantry
        """
        with self.reader() as reader:
            # List of products that should be rendered
            for recipe in recipes.recipes:
                yield from self.make_orders(recipe, reader, self.root)

    def make_orders(
            self,
            recipe: Recipe,
            reader: arkimet.dataset.Reader,
            workdir: str,
            output_steps: Optional[List[int]] = None) -> Iterator["Order"]:
        scanner = ArkimetInputScanner(recipe, reader, output_steps)
        yield from self._orders_from_scanner(recipe, workdir, scanner)

    @contextlib.contextmanager
    def reader(self) -> ContextManager[arkimet.dataset.Reader]:
        """
        Create and return a dataset reader to query the data stored in the
        pantry
        """
        with self.kitchen.session.dataset_reader(cfg=self.config) as reader:
            yield reader

    @contextlib.contextmanager
    def writer(self) -> ContextManager[arkimet.dataset.Writer]:
        """
        Create and return a dataset writer to store new data in the pantry
        """
        os.makedirs(self.ds_root, exist_ok=True)
        with self.kitchen.session.dataset_writer(cfg=self.config) as writer:
            yield writer


class ArkimetDispatcher:
    """
    Read a stream of arkimet metadata and store its data into a dataset
    """
    def __init__(self, writer: arkimet.dataset.Writer):
        self.writer = writer
        self.batch = []

    def flush_batch(self):
        if not self.batch:
            return
        res = self.writer.acquire_batch(self.batch, drop_cached_data_on_commit=True)
        count_nok = sum(1 for x in res if x != "ok")
        if count_nok > 0:
            raise RuntimeError(f"{count_nok} elements not imported correctly")
        log.debug("imported %d items into pantry", len(self.batch))
        self.batch = []

    def dispatch(self, md: arkimet.Metadata) -> bool:
        self.batch.append(md)
        if len(self.batch) >= 200:
            self.flush_batch()
        return True

    def read(self, infd: BinaryIO):
        """
        Read data from an input file, or standard input.

        The input file is the output of arki-query --inline, which is the same
        as is given as input to arkimet processors.
        """
        arkimet.Metadata.read_bundle(infd, dest=self.dispatch)
        self.flush_batch()


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
            name, step = fname[:-5].rsplit("+", 1)
            model, name = name.split("_", 1)
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


class EccodesPantry(Pantry):
    """
    eccodes-based storage of GRIB files to be processed
    """
    def __init__(self, kitchen: Kitchen, root: str):
        super().__init__(kitchen, root)
        self.data_root = os.path.join(self.root, 'eccodes_pantry')
        self.grib_filter_rules = os.path.join(self.data_root, "grib_filter_rules")

    def fill(self, recipes: Recipes, path: Optional[str] = None):
        """
        Read data from standard input and acquire it into the pantry
        """
        os.makedirs(self.data_root, exist_ok=True)
        # Build grib_filter rules
        with open(self.grib_filter_rules, "w") as f:
            for recipe in recipes.recipes:
                # Create one directory per recipe
                recipe_dir = os.path.join(self.data_root, recipe.name)
                os.makedirs(recipe_dir, exist_ok=True)
                for name, inputs in recipe.inputs.items():
                    for idx, i in enumerate(inputs, start=1):
                        if not i.eccodes:
                            log.info("%s:%s:%d: skipping input with no eccodes filter", recipe.name, name, idx)
                            continue
                        print(f"if ( {i.eccodes} ) {{", file=f)
                        print(f'  write "{recipe_dir}/{i.name}_{name}+[endStep].grib";', file=f)
                        print(f"}}", file=f)

        # Run grib_filter on input
        try:
            proc = subprocess.Popen(["grib_filter", self.grib_filter_rules, "-"], stdin=subprocess.PIPE)

            def dispatch(md: arkimet.Metadata) -> bool:
                proc.stdin.write(md.data)
                return True

            with self.input(path=path) as infd:
                arkimet.Metadata.read_bundle(infd, dest=dispatch)
        finally:
            proc.stdin.close()
            proc.wait()
            if proc.returncode != 0:
                raise RuntimeError(f"grib_filter failed with return code {proc.returncode}")

    def order(self, recipes: Recipes, name: str, step: int) -> Order:
        """
        Return an order for the given recipe name and output step
        """
        recipe = recipes.get(name)
        order = None
        for o in recipe.make_orders(self.data_root, output_steps=[step]):
            if order is not None:
                raise RuntimeError(f"Multiple options found to generate {name}+{step:03d}")
            order = o
        if order is None:
            raise KeyError(f"No option found to generate {name}+{step:03d}")
        return order

    def orders(self, recipes: Recipes) -> Iterable[Order]:
        """
        Return all orders that can be made with this pantry
        """
        # List of products that should be rendered
        for recipe in recipes.recipes:
            yield from self.make_orders(recipe, self.data_root)

    def make_orders(
            self,
            recipe: Recipe,
            workdir: str,
            output_steps: Optional[List[int]] = None) -> Iterator["Order"]:
        input_dir = os.path.join(workdir, recipe.name)
        scanner = EccodesInputScanner(recipe, input_dir, output_steps)
        yield from self._orders_from_scanner(recipe, workdir, scanner)

    def store_processing_artifacts(self, tarout):
        """
        Store relevant processing artifacts in the output tarball
        """
        tarout.add(name=self.grib_filter_rules, arcname="grib_filter_rules")
