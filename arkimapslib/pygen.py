# from __future__ import annotations
import contextlib
import io
import os
import time
from collections import defaultdict
from typing import IO, TYPE_CHECKING, Generator, Optional

if TYPE_CHECKING:
    from .orders import Order


class PyGen:
    """
    Helper to generate Python renderer code
    """
    def __init__(self):
        self.plain_imports: list[str] = []
        self.from_imports: dict[str, list[str]] = defaultdict(list)
        self.body = io.StringIO()
        self.indent = ""
        self.import_("Dict", "Generator", "List", "NamedTuple", from_="typing")
        self.import_("contextlib", "io", "json", "os", "time")
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
        self.empty_line()

    def import_(self, *names: str, from_: Optional[str] = None):
        """
        Import a name at the script's head
        """
        if from_ is None:
            dest = self.plain_imports
        else:
            dest = self.from_imports[from_]
        for name in names:
            if name not in dest:
                dest.append(name)

    def write(self, file: IO[str]):
        # Write imports
        if self.plain_imports:
            print("import", ", ".join(self.plain_imports), file=file)
        for from_, names in self.from_imports.items():
            if not names:
                continue
            print("from", from_, "import", ", ".join(names), file=file)
        print(file=file)

        file.write(self.body.getvalue())

    def empty_line(self):
        """
        Add an empty line
        """
        print(file=self.body)

    def line(self, line: str):
        """
        Add a line of code
        """
        print(self.indent, line, sep="", file=self.body)

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
        self.line("try:")
        self.line(f"    os.unlink(os.path.join(workdir, {relpath!r}, {basename!r} '.png'))")
        self.line("except FileNotFoundError:")
        self.line("    pass")
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
        with self.nested() as sub:
            sub.line("macro.plot(*parts)")
            full_relpath = os.path.join(relpath, basename) + ".png"
            for postprocessor in order.flavour.postprocessors:
                full_relpath = postprocessor.add_python(order, full_relpath, self)
            self.line(f"outputs.append(Output({function_name!r}, {full_relpath!r}, magics_output=out.getvalue()))")
