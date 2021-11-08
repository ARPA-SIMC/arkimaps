# from __future__ import annotations
from typing import Iterable, Generator, Optional
import contextlib
import functools
import multiprocessing
import multiprocessing.pool
import os
try:
    import distro
except ModuleNotFoundError:
    distro = None

# if TYPE_CHECKING:
from .orders import Order


def prepare_order(workdir: str, order: 'Order') -> Optional['Order']:
    try:
        order.prepare(workdir)
        return order
    except Exception as e:
        order.log.error("rendering failed: %s", e, exc_info=e)
        return None


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
            "MAGICS_STYLE_PATH": self.styles_dir,
            # Tell magics not to print noisy banners
            "MAGPLUS_QUIET": "1",
        }
        if distro is not None and distro.linux_distribution()[:2] == ("Fedora", "34") and "PROJ_LIB" not in os.environ:
            self.env_overrides["PROJ_LIB"] = "/usr/share/proj/"

    @contextlib.contextmanager
    def magics_worker_pool(self) -> Generator[multiprocessing.pool.Pool, None, None]:
        def initializer():
            for k, v in self.env_overrides.items():
                os.environ[k] = v

        # Using maxtasksperchild to regularly restart the workers, to mitigate
        # possible Magics memory leaks
        with multiprocessing.pool.Pool(initializer=initializer, maxtasksperchild=16) as pool:
            yield pool

    def render_one(self, order: 'Order'):
        with override_env(**self.env_overrides):
            order.prepare(self.workdir)

    def render_one_to_python(self, order: 'Order') -> str:
        """
        Render one order to a Python trace file.

        Return the name of the file written
        """
        with override_env(
                MAGICS_STYLE_PATH=self.styles_dir,
                MAGPLUS_QUIET="1"):
            return order.write_python_trace(self.workdir)

    def render(self, orders: Iterable['Order']):
        prepare = functools.partial(prepare_order, self.workdir)
        with self.magics_worker_pool() as pool:
            for order in pool.imap_unordered(prepare, orders):
                if order is not None:
                    yield order
