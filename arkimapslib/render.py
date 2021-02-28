# from __future__ import annotations
from typing import Iterable, ContextManager
import contextlib
import functools
import os
import multiprocessing
import multiprocessing.pool

# if TYPE_CHECKING:
from arkimapslib.recipes import Order


def prepare_order(workdir: str, order: 'Order') -> 'Order':
    order.prepare(workdir)
    return order


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

    @contextlib.contextmanager
    def magics_worker_pool(self) -> ContextManager[multiprocessing.pool.Pool]:
        styles_dir = self.styles_dir

        def initializer():
            # Tell magics where it should take its default styles from
            os.environ["MAGICS_STYLE_PATH"] = styles_dir
            # Tell magics not to print noisy banners
            os.environ["MAGPLUS_QUIET"] = "1"

        # Using maxtasksperchild to regularly restart the workers, to mitigate
        # possible Magics memory leaks
        with multiprocessing.pool.Pool(initializer=initializer, maxtasksperchild=16) as pool:
            yield pool

    def render_one(self, order: 'Order'):
        with override_env(
                MAGICS_STYLE_PATH=self.styles_dir,
                MAGPLUS_QUIET="1"):
            order.prepare(self.workdir)

    def render(self, orders: Iterable['Order']):
        prepare = functools.partial(prepare_order, self.workdir)
        with self.magics_worker_pool() as pool:
            yield from pool.imap_unordered(prepare, orders)
