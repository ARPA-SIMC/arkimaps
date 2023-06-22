# from __future__ import annotations
import asyncio
import contextlib
import json
import logging
import os
import shutil
import subprocess
import sys
from collections import deque
from typing import (TYPE_CHECKING, Deque, Dict, Generator, Iterable, List,
                    Optional, Sequence, Set, Tuple)

from .config import Config
from .orders import Output
from .pygen import PyGen

if TYPE_CHECKING:
    from .orders import Order

if TYPE_CHECKING:
    import tarfile

log = logging.getLogger("render")


# Polyfill for Python 3.6
if hasattr(asyncio, "create_task"):
    asyncio_create_task = asyncio.create_task
else:
    loop = asyncio.get_event_loop()

    def asyncio_create_task(*args, **kw):
        return loop.create_task(*args)


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
    def __init__(self, config: Config, workdir: str, styles_dir: str = None):
        self.config = config
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
        self.orders_by_name: Dict[Tuple[str, str], Order] = {}
        self.renderer_dir = os.path.join(workdir, "renderers")
        if os.path.exists(self.renderer_dir):
            shutil.rmtree(self.renderer_dir)
        os.makedirs(self.renderer_dir)
        self.renderer_sequence = 0

    @contextlib.contextmanager
    def override_env(self):
        with override_env(**self.env_overrides):
            yield

    def worker_init(self):
        for k, v in self.env_overrides.items():
            os.environ[k] = v

    def render(self, orders: Iterable['Order'], tarout: "tarfile.TarFile") -> List["Order"]:
        """
        Render the given order list, adding results to the tar file.

        Return the list of orders that have been rendered
        """
        orders_per_script = self.config.orders_per_script
        log.debug("%d orders to dispatch in groups of %d", len(orders), orders_per_script)

        queue: Deque[str] = deque()
        for group in groups(orders, orders_per_script):
            queue.append(self.write_render_script(group))

        if hasattr(asyncio, "run"):
            return asyncio.run(self.render_asyncio(queue, tarout))
        else:
            # Python 3.6
            loop = asyncio.get_event_loop()
            res = loop.run_until_complete(self.render_asyncio(queue, tarout))
            return res

    async def render_asyncio(self, queue: Deque[str], tarout: "tarfile.TarFile") -> List["Order"]:
        # TODO: hardcoded default to os.cpu_count, can be configurable
        max_tasks = os.cpu_count()
        pending = set()
        log.debug("%d render scripts to run on %d parallel tasks", len(queue), max_tasks)

        rendered: List["Order"] = []
        while queue or pending:
            # Refill the queue
            while queue and len(pending) < max_tasks:
                script_file = queue.popleft()
                pending.add(asyncio_create_task(self.run_render_script(script_file), name=script_file))

            # Execute the queue
            log.debug("Waiting for %d tasks", len(pending))
            done, pending = await asyncio.wait(pending, return_when=asyncio.FIRST_COMPLETED)
            log.debug("%d tasks done, %d tasks pending", len(done), len(pending))

            # Notify results
            for task in done:
                # Python 3.6 compat
                if hasattr(task, "get_name"):
                    log.debug("%s: task done", task.get_name())
                try:
                    orders = task.result()
                except Exception as e:
                    log.warning("Task execution failed: %s", e, exc_info=e)
                    continue

                for order in orders:
                    order.add_to_tarball(self.workdir, tarout)
                    rendered.append(order)

        return rendered

    async def run_render_script(self, script_file: str) -> List["Order"]:
        proc = await asyncio.create_subprocess_exec(
                sys.executable, script_file, stdout=asyncio.subprocess.PIPE)

        stdout, stderr = await proc.communicate()
        render_info = json.loads(stdout)
        timings = render_info["timings"]
        outputs = [Output(*o) for o in render_info["outputs"]]
        orders: Set["Order"] = set()
        for output in outputs:
            # Set render information in the order
            order = self.orders_by_name[(script_file, output.name)]
            order.add_output(output, timing=timings[output.name])
            orders.add(order)

        return list(orders)

    def render_one(self, order: 'Order') -> Optional['Order']:
        script_file = self.write_render_script([order])

        # Run the render script
        res = subprocess.run([sys.executable, script_file], check=True, stdout=subprocess.PIPE)
        render_info = json.loads(res.stdout)
        timings = render_info["timings"]
        outputs = [Output(*o) for o in render_info["outputs"]]
        # Set render information in the order
        output = outputs[0]
        order = self.orders_by_name[(script_file, output.name)]
        order.add_output(output, timing=timings[output.name])
        return order

    def write_render_script(self, orders: Sequence['Order']) -> str:
        """
        Render one order to a Python renderer script.

        Return the name of the file written
        """
        script_file = os.path.join(self.renderer_dir, f"renderer{self.renderer_sequence:03d}.py")
        self.renderer_sequence += 1

        gen = PyGen()

        # Set env overrides
        for k, v in self.env_overrides.items():
            gen.line(f"os.environ[{k!r}] = {v!r}")
        gen.empty_line()

        # Import Magics, timing how long it takes
        with gen.timed("import_magics") as sub:
            sub.line("from Magics import macro")
        gen.empty_line()

        for idx, order in enumerate(orders):
            name = f"order{idx}"
            self.orders_by_name[(script_file, name)] = order
            with gen.render_function(name) as sub:
                order.print_python_function(name, sub)
            gen.empty_line()

        for idx, order in enumerate(orders):
            gen.line(f"order{idx}({self.workdir!r})")
        gen.empty_line()
        gen.line("print(json.dumps({'timings': timings, 'outputs': outputs}))")

        with open(script_file, "wt") as code:
            gen.write(code)

        return script_file
