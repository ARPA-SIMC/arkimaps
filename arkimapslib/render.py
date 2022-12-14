# from __future__ import annotations
import contextlib
import io
import os
import subprocess
import sys
import time
from typing import Iterable, Optional, TextIO

# if TYPE_CHECKING:
from .orders import Order
from .utils import perf_counter_ns


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

    def print_python_preamble(self, testing=False, timings=False, file: Optional[TextIO] = None):
        """
        Print the preamble of the Python rendering script
        """
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

        if testing:
            print("from arkimapslib.unittest import mock_macro as macro", file=file)
        else:
            print("import os", file=file)
            for k, v in self.env_overrides.items():
                print(f"os.environ[{k!r}] = {v!r}", file=file)
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

        print("    macro.plot(*parts)", file=file)

        # Return result
        print("    res = {'output': output_name}", file=file)
        if timings:
            print("    res['time'] = perf_counter_ns() - start", file=file)
        print("    return res", file=file)

    def render_one_to_python(self, order: 'Order', testing=False, timings=False) -> str:
        """
        Render one order to a Python trace file.

        Return the name of the file written
        """
        with io.StringIO() as code:
            self.print_python_preamble(testing, timings, file=code)
            self.print_python_order("order", order, timings=timings, file=code)
            print("result = {'magics_imported': magics_imported, 'products': []}", file=code)
            print("result['products'].append(order())", file=code)
            print("print(json.dumps(result))", file=code)
            unformatted = code.getvalue()

        try:
            from yapf.yapflib import yapf_api
            formatted, changed = yapf_api.FormatCode(unformatted)
        except ModuleNotFoundError:
            pass

        return formatted

        # if fname is None:
        #     fname = self.output_pathname + ".py"

        # with open(fname, "wt") as fd:
        #     print(code, file=fd)

        # return fname

    def render(self, orders: Iterable['Order']):
        # with self.magics_worker_pool() as pool:
        #     for order in pool.imap_unordered(self.prepare_order, orders):
        #         if order is not None:
        #             yield order
        for order in orders:
            rendered = self.run_render_script(order)
            if rendered is not None:
                yield rendered

    def render_one(self, order: 'Order') -> Optional['Order']:
        # with multiprocessing.pool.Pool(initializer=self.worker_init, processes=1) as pool:
        #     return pool.apply(self.prepare_order, (order,))
        return self.run_render_script(order)

    def run_render_script(self, order: 'Order'):
        start = perf_counter_ns()

        path = os.path.join(self.workdir, order.relpath)
        os.makedirs(path, exist_ok=True)
        output_pathname = os.path.join(path, order.basename)

        # Write the python code, so that if we trigger a bug in Magics, we
        # have a Python reproducer available
        python_code = self.render_one_to_python(order, timings=True)
        with open(output_pathname + ".py", "wt") as fd:
            fd.write(python_code)
        order.render_script = output_pathname + ".py"

        # Run the render script
        subprocess.run([sys.executable, order.render_script], check=True)

        # Set render information in the order
        order.output = output_pathname + ".png"
        order.render_time_ns = perf_counter_ns() - start

        return order

    def prepare_order(self, order: 'Order') -> Optional['Order']:
        """
        Run all the steps of the recipe and render the resulting file.

        This method imports Magics, and is best called in a subprocess, to
        prevent Magics global state from interfering between renderings with
        different parameters. This is less of an issue during arkimaps
        rendering, where worker processes render multiple orders with the same
        Magics settings, and more of an issue in unit testing.
        """
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
            python_code = self.render_one_to_python(order)
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
