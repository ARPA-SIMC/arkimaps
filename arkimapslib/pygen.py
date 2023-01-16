# from __future__ import annotations
import contextlib
import time
from typing import TYPE_CHECKING, IO, Generator

if TYPE_CHECKING:
    from .orders import Order


class PyGen:
    """
    Helper to generate Python renderer code
    """
    def __init__(self, file: IO[str], indent: int = 0):
        self.file = file
        self.indent = " " * indent
        self.line("from typing import Dict, Generator, List, NamedTuple, Tuple")
        self.line("import contextlib")
        self.line("import io")
        self.line("import json")
        self.line("import os")
        self.line("import time")
        self.empty_line()
        self.line("class Output(NamedTuple):")
        self.line("    name: str")
        self.line("    relpath: str")
        self.line("    magics_output: str")
        self.empty_line()
        if hasattr(time, "perf_counter_ns"):
            self.line("perf_counter_ns = time.perf_counter_ns")
        else:
            # Polyfill for Python < 3.7"
            self.line("def perf_counter_ns() -> int:")
            self.line("   return int(time.perf_counter() * 1000000000)")
        self.empty_line()
        self.line("timings: Dict[str, int] = {}")
        self.line("outputs: List[Output] = []")
        self.empty_line()
        self.line("@contextlib.contextmanager")
        self.line("def take_time(name: str) -> Generator[None, None, None]:")
        with self.nested() as sub:
            sub.line("start = perf_counter_ns()")
            sub.line("try:")
            sub.line("    yield")
            sub.line("finally:")
            sub.line("    timings[name] = perf_counter_ns() - start")

    def empty_line(self):
        """
        Add an empty line
        """
        print(file=self.file)

    def line(self, line: str):
        """
        Add a line of code
        """
        print(self.indent, line, sep="", file=self.file)

    @contextlib.contextmanager
    def nested(self) -> Generator["PyGen", None, None]:
        """
        Return a PyGen with a higher indentation level
        """
        old_indent = self.indent
        self.indent += "    "
        try:
            yield self
        finally:
            self.indent = old_indent

    @contextlib.contextmanager
    def timed(self, name: str) -> Generator["PyGen", None, None]:
        """
        Wrap code in take_time
        """
        self.line(f"with take_time({name!r}):")
        with self.nested() as sub:
            yield sub

    @contextlib.contextmanager
    def render_function(self, name: str) -> Generator["PyGen", None, None]:
        """
        Return a PyGen that can be used to write the body of the given render
        function
        """
        self.line(f"def {name}(workdir: str) -> None:")
        with self.nested() as sub1:
            with sub1.timed(name) as sub2:
                yield sub2

    def magics_renderer(self, function_name: str, order: "Order", relpath: str, basename: str):
        """
        Write Python code for the Magics rendering portion for the given order
        """
        self.line(f"os.makedirs(os.path.join(workdir, {relpath!r}), exist_ok=True)")
        order_args = "".join([f", {k}={v!r}" for k, v in order.output_options.items()])
        self.line(f"parts = [macro.output(output_formats=['png'],"
                  f" output_name=os.path.join(workdir, {relpath!r}, {basename!r}),"
                  f" output_name_first_page_number='off'{order_args})]")

        for step in order.order_steps:
            name, parms = step.as_magics_macro()
            py_parms = []
            for k, v in parms.items():
                py_parms.append(f"{k}={v!r}")
            self.line(f"parts.append(macro.{name}({', '.join(py_parms)}))")

        self.line("with contextlib.redirect_stdout(io.StringIO()) as out:")
        self.line("    macro.plot(*parts)")
