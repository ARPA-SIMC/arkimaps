import inspect
import logging
from typing import Dict, Any, override

from docutils.statemachine import StringList

from sphinx.application import Sphinx
from sphinx.ext.autodoc import ClassDocumenter, Documenter

from arkimapslib.steps import Step, MagicsMacro, BaseMagicsParamsSpec

logger = logging.getLogger(__name__)


class StepDocumenter(ClassDocumenter):
    objtype = "step"
    directivetype = ClassDocumenter.objtype
    priority = 10 + ClassDocumenter.priority
    option_spec = dict(ClassDocumenter.option_spec)

    @override
    @classmethod
    def can_document_member(cls, member: Any, membername: str, isattr: bool, parent: Documenter) -> bool:
        return False

    def _get_doc(self, step: type[Step]) -> tuple[str, str | None]:
        docstring = inspect.getdoc(step)
        if docstring is None:
            return "Missing docstring", None
        if "\n" not in docstring:
            return docstring, None
        subject, body = docstring.split("\n", 1)
        body = body.lstrip()
        return subject, body or None

    @override
    def generate(
        self,
        more_content: StringList | None = None,
        real_modname: str | None = None,
        check_module: bool = False,
        all_members: bool = False,
    ) -> None:
        try:
            step = Step.step_by_name(self.name)
        except KeyError:
            logger.warning("Step %r not found", self.name)
            return

        source_name = self.get_sourcename()
        name = step.STEP_NAME
        subject, body = self._get_doc(step)

        self.add_line(f".. _step_{name}:", source_name)
        self.add_line("", source_name)
        title = f"**{name}**"
        self.add_line(title, source_name)
        self.add_line("=" * len(title), source_name)

        self.add_line("", source_name)
        self.add_line(f"**{subject}**", source_name)

        if issubclass(step, MagicsMacro):
            self.add_line("", source_name)
            macro_desc = step.MACRO_NAME
            if step.MACRO_URL is not None:
                macro_desc = f"`{macro_desc} <{step.MACRO_URL}>`_"
            self.add_line(f"Magics macro: {macro_desc}.", source_name)

        self.add_line("", source_name)
        if body is not None:
            for line in body.splitlines():
                self.add_line(line, source_name)
            self.add_line("", source_name)

        self.add_line("Fields:", source_name)
        self.add_line("", source_name)

        argspec = step.Spec
        for fname, field in argspec.__fields__.items():
            if issubclass(step, MagicsMacro) and issubclass(field.type_, BaseMagicsParamsSpec):
                field_doc = field.type_.__doc__ or f"Dictionary of arguments for ``{step.MACRO_NAME}``"
            else:
                field_doc = field.field_info.description
            self.add_line(f"* **{fname}**: {field_doc}", source_name)


def setup(app: Sphinx) -> Dict[str, Any]:
    """Set up the extension."""
    # See https://www.sphinx-doc.org/en/master/development/tutorials/autodoc_ext.html
    app.setup_extension("sphinx.ext.autodoc")  # Require autodoc extension
    app.add_autodocumenter(StepDocumenter)

    return {
        "version": "1",
        "parallel_read_safe": True,
    }
