# from __future__ import annotations
import asyncio
import contextlib
import io
import json
import logging
import os
import subprocess
import sys
import time
from typing import (TYPE_CHECKING, Dict, Generator, Iterable, List, Optional,
                    Sequence, TextIO)

# if TYPE_CHECKING:
from .orders import Order
from .utils import perf_counter_ns

if TYPE_CHECKING:
    import tarfile

log = logging.getLogger("render")


@contextlib.contextmanager
def override_env(**kw):
    old = {}
    for k, v in kw.items():
        old[k] = os.environ.get(k)
        os.environ[k] = v
    try:
        yield
    finally:
        for k, v in old.items():
            if v is None:
                del os.environ[k]
            else:
                os.environ[k] = v


def groups(orders: Iterable["Order"], count: int) -> Generator[List["Order"], None, None]:
    """
    Given an iterable of orders, generate groups of maximum count items
    """
    group = []
    for order in orders:
        group.append(order)
        if len(group) == count:
            yield group
            group = []
    if group:
        yield group


class Renderer:
    def __init__(self, workdir: str, styles_dir: str = None):
        self.workdir = workdir
        if styles_dir is None:
            styles_dir = "/usr/share/magics/styles/ecmwf"
        self.styles_dir = styles_dir
        self.env_overrides = {
            # Tell magics where it should take its default styles from
            "MAGICS_STYLE_PATH": styles_dir,
            # Tell magics not to print noisy banners
            "MAGPLUS_QUIET": "1",
        }

    @contextlib.contextmanager
    def override_env(self):
        with override_env(**self.env_overrides):
            yield

    def worker_init(self):
        for k, v in self.env_overrides.items():
            os.environ[k] = v

    # @contextlib.contextmanager
    # def magics_worker_pool(self) -> Generator[multiprocessing.pool.Pool, None, None]:
    #     # Using maxtasksperchild to regularly restart the workers, to mitigate
    #     # possible Magics memory leaks
    #     with multiprocessing.pool.Pool(initializer=self.worker_init, maxtasksperchild=16) as pool:
    #         yield pool

    def print_python_preamble(self, timings=False, file: Optional[TextIO] = None):
        """
        Print the preamble of the Python rendering script
        """
        print("import contextlib", file=file)
        print("import io", file=file)
        print("import os", file=file)

        for k, v in self.env_overrides.items():
            print(f"os.environ[{k!r}] = {v!r}", file=file)

        if timings:
            print("import json", file=file)
            print("import time", file=file)
            if hasattr(time, "perf_counter_ns"):
                print("perf_counter_ns = time.perf_counter_ns", file=file)
            else:
                # Polyfill for Python < 3.7"
                print("def perf_counter_ns() -> int:", file=file)
                print("   return int(time.perf_counter() * 1000000000)", file=file)
            print("start = perf_counter_ns()", file=file)

        print("from Magics import macro", file=file)

        if timings:
            print("magics_imported = perf_counter_ns() - start", file=file)

    def print_python_order(self, name: str, order: 'Order', timings=False, file: Optional[TextIO] = None):
        """
        Print a function that renders this order
        """
        print(f"def {name}():", file=file)
        if timings:
            print("    start = perf_counter_ns()", file=file)

        output_pathname = os.path.join(self.workdir, order.relpath, order.basename)
        order_args = "".join([f", {k}={v!r}" for k, v in order.output_options.items()])
        print(f"    output_name={output_pathname!r}", file=file)
        print(f"    parts = [macro.output(output_formats=['png'], output_name=output_name,"
              f" output_name_first_page_number='off'{order_args})]", file=file)

        for step in order.order_steps:
            name, parms = step.as_magics_macro()
            py_parms = []
            for k, v in parms.items():
                py_parms.append(f"{k}={v!r}")
            print(f"    parts.append(macro.{name}({', '.join(py_parms)}))", file=file)

        print("    res = {'output': output_name}", file=file)

        print("    with contextlib.redirect_stdout(io.StringIO()) as out:", file=file)
        print("        macro.plot(*parts)", file=file)
        print("        res['magics_output'] = out.getvalue()", file=file)

        # Return result
        if timings:
            print("    res['time'] = perf_counter_ns() - start", file=file)
        print("    return res", file=file)

    def make_python_renderer(self, orders: Sequence['Order'], timings=False, formatted=False) -> str:
        """
        Render one order to a Python trace file.

        Return the name of the file written
        """
        with io.StringIO() as code:
            self.print_python_preamble(timings, file=code)
            for idx, order in enumerate(orders):
                name = f"order{idx}"
                self.print_python_order(name, order, timings=timings, file=code)
            print("result = {'magics_imported': magics_imported, 'products': []}", file=code)
            for idx, order in enumerate(orders):
                name = f"order{idx}"
                print(f"result['products'].append({name}())", file=code)
            print("print(json.dumps(result))", file=code)
            unformatted = code.getvalue()

        if formatted:
            try:
                from yapf.yapflib import yapf_api
                formatted, changed = yapf_api.FormatCode(unformatted)
                return formatted
            except ModuleNotFoundError:
                return unformatted
        else:
            return unformatted

    def render(self, orders: Iterable['Order'], tarout: "tarfile.TarFile") -> List["Order"]:
        """
        Render the given order list, adding results to the tar file.

        Return the list of orders that have been rendered
        """
        # TODO: hardcoded, make customizable
        orders_per_script = 16
        log.debug("%d orders to dispatch in groups of %d", len(orders), orders_per_script)

        queue: Dict[str, List["Order"]] = {}
        for group in groups(orders, orders_per_script):
            script_file = self.write_render_script(group, formatted=False)
            queue[script_file] = group

        return asyncio.run(self.render_asyncio(queue, tarout))

    async def render_asyncio(self, queue: Dict[str, List["Order"]], tarout: "tarfile.TarFile") -> List["Order"]:
        # TODO: hardcoded default to os.cpu_count, can be configurable
        max_tasks = os.cpu_count()
        pending = set()
        log.debug("%d render scripts to run on %d parallel tasks", len(queue), max_tasks)

        rendered: List["Order"] = []
        while queue or pending:
            # Refill the queue
            while queue and len(pending) < max_tasks:
                script_file, orders = queue.popitem()
                pending.add(asyncio.create_task(self.run_render_script(script_file, orders), name=script_file))

            # Execute the queue
            log.debug("Waiting for %d tasks", len(pending))
            done, pending = await asyncio.wait(pending, return_when=asyncio.FIRST_COMPLETED)
            log.debug("%d tasks done, %d tasks pending", len(done), len(pending))

            # Notify results
            for task in done:
                log.debug("%s: task done", task.get_name())
                try:
                    orders = task.result()
                except Exception as e:
                    log.warning("Task execution failed: %s", e, exc_info=e)
                    continue

                for order in orders:
                    log.info("Rendered %s to %s %s: %s", order.recipe_name, order.relpath, order.basename, order.output)

                    # Move the generated image to the output tar
                    tarout.add(
                        order.output,
                        os.path.join(os.path.join(order.relpath, order.basename) + ".png"))
                    os.unlink(order.output)
                    rendered.append(order)

        return rendered

    async def run_render_script(self, script_file: str, orders: List["Order"]) -> List["Order"]:
        proc = await asyncio.create_subprocess_exec(
                sys.executable, script_file, stdout=asyncio.subprocess.PIPE)

        stdout, stderr = await proc.communicate()
        render_info = json.loads(stdout)
        for order, product_info in zip(orders, render_info["products"]):
            # Set render information in the order
            order.output = product_info["output"] + ".png"
            order.render_time_ns = product_info["time"]

        return orders

    def render_one(self, order: 'Order') -> Optional['Order']:
        # with multiprocessing.pool.Pool(initializer=self.worker_init, processes=1) as pool:
        #     return pool.apply(self.prepare_order, (order,))
        script_file = self.write_render_script([order], formatted=True)

        # Run the render script
        res = subprocess.run([sys.executable, script_file], check=True, stdout=subprocess.PIPE)
        render_info = json.loads(res.stdout)
        product_info = render_info["products"][0]
        # Set render information in the order
        order.output = product_info["output"] + ".png"
        order.render_time_ns = product_info["time"]
        return order

    def write_render_script(self, orders: Sequence['Order'], formatted: bool = False) -> str:
        python_code = self.make_python_renderer(orders, timings=True, formatted=formatted)

        # Write the python code, so that if we trigger a bug in Magics, we
        # have a Python reproducer available
        script_file: Optional[str] = None
        for order in orders:
            path = os.path.join(self.workdir, order.relpath)
            os.makedirs(path, exist_ok=True)
            output_pathname = os.path.join(path, order.basename) + ".py"
            order.render_script = output_pathname

            # Remove the destination file to break possibly existing links from
            # an old workdir
            try:
                os.unlink(output_pathname)
            except FileNotFoundError:
                pass

            if script_file is None:
                script_file = output_pathname
                with open(script_file, "wt") as fd:
                    fd.write(python_code)
            else:
                os.link(script_file, output_pathname)

        return script_file

    def prepare_order(self, order: 'Order') -> Optional['Order']:
        """
        Run all the steps of the recipe and render the resulting file.

        This method imports Magics, and is best called in a subprocess, to
        prevent Magics global state from interfering between renderings with
        different parameters. This is less of an issue during arkimaps
        rendering, where worker processes render multiple orders with the same
        Magics settings, and more of an issue in unit testing.
        """
        # TODO: this is not used anymore
        start = perf_counter_ns()
        try:
            from .worktops import Worktop

            # TODO: Magics also has macro.silent(), though I cannot easily find
            #       its documentation

            path = os.path.join(self.workdir, order.relpath)
            os.makedirs(path, exist_ok=True)

            output_pathname = os.path.join(path, order.basename)

            # Write the python code, so that if we trigger a bug in Magics, we
            # have a Python reproducer available
            python_code = self.make_python_renderer([order])
            with open(output_pathname + ".py", "wt") as fd:
                fd.write(python_code)
            order.render_script = output_pathname + ".py"

            # Render with Magics (Worktop's constructor is where Magics get imported)
            worktop = Worktop(input_files=order.input_files)
            for step in order.order_steps:
                step.run(worktop)

            # Settings of the PNG output
            output = worktop.macro.output(
                output_formats=['png'],
                output_name=output_pathname,
                output_name_first_page_number="off",
                **order.output_options,
            )

            # Render the file and store the output file name into the order
            worktop.macro.plot(
                output,
                *worktop.parts,
            )

            order.output = output_pathname + ".png"

            order.render_time_ns = perf_counter_ns() - start

            return order
        except Exception as e:
            order.log.error("rendering failed: %s", e, exc_info=e)
            return None
