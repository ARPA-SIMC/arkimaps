# from __future__ import annotations
import contextlib
import datetime
import json
import logging
import subprocess
import sys
import time
from abc import ABC, abstractmethod
from collections import defaultdict
from functools import cached_property
from pathlib import Path
from typing import TYPE_CHECKING, Iterator, List, Optional

from arkimapslib import outputbundle
from arkimapslib.config import Config
from arkimapslib.definitions import Definitions
from arkimapslib.flavours import Flavour
from arkimapslib.orders import Order
from arkimapslib.render import Renderer

from .cmdline import Command, Fail
from .kitchen import Kitchen, WorkingKitchen
from .lint import Lint

if TYPE_CHECKING:
    from .kitchen import ArkimetEmptyKitchen

SYSTEM_RECIPE_DIR = Path("/usr/share/arkimaps/recipes")
SYSTEM_STYLES_DIR = Path("/usr/share/magics/styles/ecmwf")

log = logging.getLogger("arkimaps")


class LogCollector(logging.Handler):
    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        self.entries = outputbundle.Log()

    def emit(self, record: logging.LogRecord):
        self.entries.append(
            ts=time.clock_gettime(time.CLOCK_REALTIME), level=record.levelno, msg=self.format(record), name=record.name
        )


class DefinitionsCommand(Command):
    """
    Command that loads YAML Definitions
    """

    definitions: Definitions

    @classmethod
    def make_subparser(cls, subparsers):
        parser = super().make_subparser(subparsers)

        local_recipe_dir = Path("recipes")
        if local_recipe_dir.is_dir():
            recipe_dir = local_recipe_dir.absolute()
        else:
            recipe_dir = SYSTEM_RECIPE_DIR

        parser.add_argument(
            "--recipes",
            type=Path,
            metavar="dir",
            action="store",
            default=recipe_dir,
            help=f"directory with the YAML recipes (default: ./recipes (if existing) or {SYSTEM_RECIPE_DIR})",
        )

        parser.add_argument(
            "--flavours",
            action="store",
            default="default",
            help='comma-separated list of flavours to render. Default: "%(default)s"',
        )

        return parser

    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        self.config = Config()
        self.defs = Definitions(config=self.config)
        self.defs.load([self.args.recipes])

    @abstractmethod
    def create_kitchen(self) -> Kitchen:
        """
        Instantiate the Kitchen object for this class
        """

    @cached_property
    def flavours(self) -> List[Flavour]:
        """
        Parse --flavours argument into a list of flavours
        """
        flavours = []
        for flavour_name in self.args.flavours.split(","):
            flavour = self.defs.flavours.get(flavour_name)
            if flavour is None:
                raise Fail(f'Flavour "{flavour_name}" not found')
            flavours.append(flavour)
        return flavours


class KitchenCommand(ABC, DefinitionsCommand):
    """
    Command that requires a kitchen
    """

    kitchen: Kitchen

    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        self.kitchen = self.create_kitchen()

    @abstractmethod
    def create_kitchen(self) -> Kitchen:
        """
        Instantiate the Kitchen object for this class
        """


class EmptyKitchenCommand(KitchenCommand):
    """
    Command that requires a kitchen only to load recipes
    """

    kitchen: "ArkimetEmptyKitchen"

    def create_kitchen(self) -> "ArkimetEmptyKitchen":
        from arkimapslib.kitchen import ArkimetEmptyKitchen

        return ArkimetEmptyKitchen(definitions=self.defs)


class WorkingKitchenCommand(KitchenCommand):
    """
    Mixin for commands that need a kitchen that can be used to generate
    products
    """

    kitchen: WorkingKitchen

    @classmethod
    def make_subparser(cls, subparsers):
        parser = super().make_subparser(subparsers)
        parser.add_argument(
            "--filter",
            metavar="{arkimet|eccodes}",
            default="arkimet",
            help="backend to use to organise data into recipe inputs. Default: %(default)s",
        )
        parser.add_argument(
            "--grib",
            action="store_true",
            help="read input as GRIB data instead of arkimet output. Implies --filter=eccodes",
        )
        return parser

    def create_kitchen(self) -> WorkingKitchen:
        return self.make_kitchen()

    def make_kitchen(self, workdir: Optional[Path] = None) -> WorkingKitchen:
        if self.args.grib or self.args.filter == "eccodes":
            from arkimapslib.kitchen import EccodesKitchen

            return EccodesKitchen(definitions=self.defs, workdir=workdir, grib_input=self.args.grib)
        elif self.args.filter == "arkimet":
            from arkimapslib.kitchen import ArkimetKitchen

            return ArkimetKitchen(definitions=self.defs, workdir=workdir)
        else:
            raise Fail(f"Unsupported value `{self.args.filter}` for --filter")


class WorkdirKitchenCommand(WorkingKitchenCommand):
    """
    Command that uses a user-defined workdir
    """

    @classmethod
    def make_subparser(cls, subparsers):
        parser = super().make_subparser(subparsers)
        parser.add_argument("workdir", type=Path, metavar="dir", action="store", help="working directory")
        return parser

    def create_kitchen(self) -> WorkingKitchen:
        return self.make_kitchen(self.args.workdir)


class OptionalWorkdirKitchenCommand(WorkingKitchenCommand):
    """
    Command that uses a user-defined workdir
    """

    @classmethod
    def make_subparser(cls, subparsers):
        parser = super().make_subparser(subparsers)
        parser.add_argument(
            "--workdir", type=Path, metavar="dir", action="store", help="working directory. Default: a temporary one"
        )
        return parser

    def create_kitchen(self) -> WorkingKitchen:
        return self.make_kitchen(self.args.workdir)


class RenderCommand(WorkingKitchenCommand):
    """
    Command line options to control rendering of recipes
    """

    @classmethod
    def make_subparser(cls, subparsers):
        parser = super().make_subparser(subparsers)

        local_styles_dir = Path("styles")
        if local_styles_dir.is_dir():
            styles_dir = local_styles_dir.absolute()
        else:
            styles_dir = SYSTEM_STYLES_DIR

        parser.add_argument(
            "--styles",
            type=Path,
            metavar="dir",
            action="store",
            default=str(styles_dir),
            help=f"styles directory. Default: ./styles (if existing) or {SYSTEM_STYLES_DIR}",
        )
        parser.add_argument(
            "--output",
            "-o",
            type=Path,
            metavar="file.tar|zip",
            action="store",
            help="write rendered output to the given file. Default: write to stdout",
        )

        return parser

    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)

        # Collect log entries that we can then add to the output data
        # TODO: save intermediate log in workdir
        self.log_collector = LogCollector()
        self.log_collector.setLevel(logging.DEBUG)
        root_logger = logging.getLogger()
        root_logger.addHandler(self.log_collector)

    def get_styles_directory(self) -> Path:
        """
        Return the directory where Magics styles are stored
        """
        return self.args.styles

    @contextlib.contextmanager
    def open_output(self) -> Iterator[outputbundle.Writer]:
        if self.args.output:
            with self.args.output.open("wb") as out:
                writer_cls: outputbundle.Writer
                if self.args.output.suffix == ".zip":
                    writer_cls = outputbundle.ZipWriter(out=out)
                else:
                    writer_cls = outputbundle.TarWriter(out=out)
                with writer_cls as bundle:
                    yield bundle
        else:
            with outputbundle.TarWriter(out=sys.stdout.buffer) as bundle:
                yield bundle

    def render_tarball(self) -> None:
        """
        Render all recipes for which inputs are available, into a tarball
        """
        orders: List[Order] = []
        for flavour in self.flavours:
            # List of products that should be rendered
            orders += self.kitchen.make_orders(flavour=flavour)

        # Prepare input summary after we're done with input processing
        input_summary = outputbundle.InputSummary()
        self.kitchen.defs.inputs.summarize(self.kitchen.pantry, orders, input_summary)

        renderer = Renderer(
            config=self.kitchen.config, workdir=self.kitchen.workdir, styles_dir=self.get_styles_directory()
        )

        rendered: List[Order] = []
        with self.open_output() as bundle:
            # Add input summary
            bundle.add_input_summary(input_summary)

            # Perform rendering
            rendered = renderer.render(orders, bundle)

            bundle.add_log(self.log_collector.entries)

            # Add products summary
            products_info = outputbundle.Products()
            for order in rendered:
                products_info.add_order(order)
            bundle.add_products(products_info)

            # Let the Pantry store processing artifacts if it has any
            self.kitchen.pantry.store_processing_artifacts(bundle)

    def print_render_plan(self):
        """
        Print a list of operations that would be done during rendering
        """
        for flavour in self.flavours:
            # List of products that should be rendered
            orders = self.kitchen.make_orders(flavour=flavour)
            by_name = defaultdict(list)
            for order in orders:
                by_name[order.recipe.name].append(order)
            for name, orders in by_name.items():
                print(f"{flavour}: {name}:")
                for order in orders:
                    print(f"  {order}")


#
# Command line actions
#


class PrintArkiQuery(EmptyKitchenCommand):
    """
    print an arkimet query to query data that can be used by the recipes found
    """

    NAME = "print-arki-query"

    def run(self):
        merged = self.kitchen.get_merged_arki_query(self.flavours)
        print(merged)


class DocumentRecipes(EmptyKitchenCommand):
    """
    generate recipes documentation
    """

    NAME = "document-recipes"

    @classmethod
    def make_subparser(cls, subparsers):
        parser = super().make_subparser(subparsers)
        parser.add_argument(
            "--destdir",
            type=Path,
            metavar="dir",
            action="store",
            help="directory where documentation is written. It defaults to the recipes directory",
        )
        return parser

    def run(self):
        dest = self.args.destdir
        if dest is None:
            dest = self.args.recipes
        dest.mkdir(parents=True, exist_ok=True)
        if len(self.flavours) != 1:
            raise Fail(f"One flavour needed, {len(self.flavours)} provided")

        self.kitchen.document_recipes(self.flavours[0], dest)


class DumpRecipes(EmptyKitchenCommand):
    """
    dump content parsed from recipes directory
    """

    NAME = "dump-recipes"

    @classmethod
    def make_subparser(cls, subparsers):
        parser = super().make_subparser(subparsers)
        parser.add_argument("--inputs", action="store_true", help="dump inputs instead of recipes")
        return parser

    def dump_recipes(self):
        res_inputs = {}
        for name, inputs in self.kitchen.pantry.inputs.inputs.items():
            res_inputs[name] = []
            for idx, inp in enumerate(inputs, start=1):
                res_inputs[name].append(inp.to_dict())

        res = {}
        res["inputs"] = res_inputs
        json.dump(res, sys.stdout, indent=1)
        print()
        # TODO: self.recipes = Recipes()
        # TODO: self.flavours: Dict[str, Flavour] = {}

    def dump_inputs(self):
        all_inputs = self.kitchen.list_inputs(self.flavours)
        for name in sorted(all_inputs):
            print(name)

    def run(self):
        if self.args.inputs:
            self.dump_inputs()
        else:
            self.dump_recipes()


class LintCmd(EmptyKitchenCommand):
    """
    Validate contents of recipes
    """

    NAME = "lint"

    def run(self):
        for flavour in self.flavours:
            log.info("%s: checking flavour", flavour.name)
            lint = Lint(flavour)
            flavour.lint(lint)

            for inputs in self.kitchen.pantry.inputs.values():
                for inp in inputs:
                    log.info("%s (%s): checking input", inp.name, inp.spec.model)
                    inp.lint(lint)

            for recipe in self.defs.recipes:
                if not flavour.allows_recipe(recipe):
                    continue
                recipe.lint(lint)


class Dispatch(WorkdirKitchenCommand):
    """
    do not render: dispatch into a working directory
    """

    @classmethod
    def make_subparser(cls, subparsers):
        parser = super().make_subparser(subparsers)
        parser.add_argument(
            "input",
            action="store",
            help="input file to dispatch. Default: stdin",
        )
        return parser

    def run(self):
        """
        Acquire input data
        """
        self.kitchen.fill_pantry(path=Path(self.args.input) if self.args.input else None, flavours=self.flavours)


class Render(RenderCommand, WorkdirKitchenCommand):
    """
    render data that was already dispatched
    """

    @classmethod
    def make_subparser(cls, subparsers):
        parser = super().make_subparser(subparsers)
        parser.add_argument(
            "--simulate",
            action="store_true",
            help="print what products would be generated" " (note that this will still generate derived inputs)",
        )
        return parser

    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        self.kitchen.pantry.rescan()

    def run(self):
        """
        Render all recipes for which inputs are available
        """
        if self.args.simulate:
            self.print_render_plan()
        else:
            self.render_tarball()


class Preview(RenderCommand, WorkdirKitchenCommand):
    """
    generate the given product only, and display it with xdg-open
    """

    @classmethod
    def make_subparser(cls, subparsers):
        parser = super().make_subparser(subparsers)
        parser.add_argument(
            "-d", "--date", metavar="datetime", action="store", help="render product at this reference time"
        )
        parser.add_argument("name", metavar="prod[+step]", action="store", help="name of the product to preview")
        return parser

    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        self.kitchen.pantry.rescan()

    def run(self):
        """
        Generate the given product only, and preview it with xdg-open
        """
        if "+" in self.args.name:
            name, step = self.args.name.split("+")
            step = int(step, 10)
        else:
            name = self.args.name
            step = None

        if self.args.date is not None:
            res = subprocess.run(["date", "--date=" + self.args.date, "+%s"], text=True, capture_output=True)
            reftime = datetime.datetime.fromtimestamp(int(res.stdout))
        else:
            reftime = None

        flavours = self.parse_flavours()
        if len(flavours) != 1:
            raise Fail("Only 1 flavour is supported for preview")
        flavour = flavours[0]

        # Make an order
        order = self.kitchen.make_order(self.kitchen.recipes.get(name), flavour=flavour, step=step, reftime=reftime)

        # Prepare it
        renderer = Renderer(
            config=self.kitchen.config, workdir=self.kitchen.workdir, styles_dir=self.get_styles_directory()
        )
        order = renderer.render_one(order)
        log.info("Rendered %s to %s", order.recipe.name, order.output.relpath)

        # Display it
        output_pathname = self.kitchen.workdir / order.output.relpath
        subprocess.run(["xdg-open", str(output_pathname)], check=True)
        input("Press enter when done> ")

        output_pathname.unlink()


class Process(RenderCommand, OptionalWorkdirKitchenCommand):
    """
    draw maps based on GRIB data
    """

    def run(self):
        # Acquire input data
        self.kitchen.fill_pantry(flavours=self.flavours)
        self.render_tarball()
