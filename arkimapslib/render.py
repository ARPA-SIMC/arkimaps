# from __future__ import annotations
from typing import Iterable, Generator, Optional
import contextlib
import os
import multiprocessing
import multiprocessing.pool

# if TYPE_CHECKING:
from .orders import Order


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

    @contextlib.contextmanager
    def magics_worker_pool(self) -> Generator[multiprocessing.pool.Pool, None, None]:
        # Using maxtasksperchild to regularly restart the workers, to mitigate
        # possible Magics memory leaks
        with multiprocessing.pool.Pool(initializer=self.worker_init, maxtasksperchild=16) as pool:
            yield pool

    def render_one_to_python(self, order: 'Order') -> str:
        """
        Render one order to a Python trace file.

        Return the name of the file written
        """
        py_lines = ["import os"]
        for k, v in self.env_overrides.items():
            py_lines.append(f"os.environ[{k!r}] = {v!r}")
        py_lines += [
            "from Magics import macro",
            f"output = macro.output(output_formats=['png'], output_name={order.basename!r},"
            f" output_name_first_page_number='off')",
            "parts = []",
        ]

        for step in order.order_steps:
            name, parms = step.as_magics_macro()
            py_parms = []
            for k, v in parms.items():
                py_parms.append(f"{k}={v!r}")
            py_lines.append(f"parts.append(macro.{name}({', '.join(py_parms)}))")

        py_lines.append("macro.plot(output, *parts)")

        code = "\n".join(py_lines)
        try:
            from yapf.yapflib import yapf_api
            code, changed = yapf_api.FormatCode(code)
        except ModuleNotFoundError:
            pass

        return code

        # if fname is None:
        #     fname = self.output_pathname + ".py"

        # with open(fname, "wt") as fd:
        #     print(code, file=fd)

        # return fname

    def render(self, orders: Iterable['Order']):
        with self.magics_worker_pool() as pool:
            for order in pool.imap_unordered(self.prepare_order, orders):
                if order is not None:
                    yield order

    def render_one(self, order: 'Order') -> Optional['Order']:
        with multiprocessing.pool.Pool(initializer=self.worker_init, processes=1) as pool:
            return pool.apply(self.prepare_order, (order,))

    def prepare_order(self, order: 'Order') -> Optional['Order']:
        """
        Run all the steps of the recipe and render the resulting file.

        This method imports Magics, and is best called in a subprocess, to
        prevent Magics global state from interfering between renderings with
        different parameters. This is less of an issue during arkimaps
        rendering, where worker processes render multiple orders with the same
        Magics settings, and more of an issue in unit testing.
        """
        try:
            from .worktops import Worktop

            output_pathname = os.path.join(self.workdir, order.basename)

            # Write the python code, so that if we trigger a bug in Magics, we
            # have a Python reproducer available
            python_code = self.render_one_to_python(order)
            with open(output_pathname + ".py", "wt") as fd:
                fd.write(python_code)

            # Render with Magics (Worktop's constructor is where Magics get imported)
            worktop = Worktop(output_pathname=output_pathname, input_files=order.input_files)
            for step in order.order_steps:
                step.run(worktop)
            worktop.write_product()
            order.output = output_pathname + ".png"

            return order
        except Exception as e:
            order.log.error("rendering failed: %s", e, exc_info=e)
            return None
