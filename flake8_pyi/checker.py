from __future__ import annotations

import argparse
import ast
import logging
import re
from dataclasses import dataclass
from typing import Any, ClassVar, Iterator, Literal

from flake8 import checker
from flake8.options.manager import OptionManager
from flake8.plugins.finder import LoadedPlugin
from flake8.plugins.pyflakes import FlakesChecker
from pyflakes.checker import ModuleScope

from . import errors, visitor

LOG = logging.getLogger("flake8.pyi")


class PyflakesPreProcessor(ast.NodeTransformer):
    """Transform AST prior to passing it to pyflakes.

    This reduces false positives on recursive class definitions.
    """

    def visit_ClassDef(self, node: ast.ClassDef) -> ast.ClassDef:
        self.generic_visit(node)
        node.bases = [
            # Remove the subscript to prevent F821 errors from being emitted
            # for (valid) recursive definitions: Foo[Bar] --> Foo
            base.value if isinstance(base, ast.Subscript) else base
            for base in node.bases
        ]
        return node


class PyiAwareFlakesChecker(FlakesChecker):
    def __init__(self, tree: ast.AST, *args: Any, **kwargs: Any) -> None:
        super().__init__(PyflakesPreProcessor().visit(tree), *args, **kwargs)

    @property
    def annotationsFutureEnabled(self) -> Literal[True]:
        """Always allow forward references in `.pyi` files.

        Pyflakes can already handle forward refs for annotations,
        but only via `from __future__ import annotations`.
        In a stub file, `from __future__ import annotations` is unnecessary,
        so we pretend to pyflakes that it's always present when linting a `.pyi` file.
        """
        return True

    @annotationsFutureEnabled.setter
    def annotationsFutureEnabled(self, value: bool) -> None:
        """Does nothing, as we always want this property to be `True`."""

    def ASSIGN(
        self, tree: ast.Assign, omit: str | tuple[str, ...] | None = None
    ) -> None:
        """Defer evaluation of assignments in the module scope.

        This is a custom implementation of ASSIGN, originally derived from
        handleChildren() in pyflakes 1.3.0.

        This reduces false positives for:
          - TypeVars bound or constrained to forward references
          - Assignments to forward references that are not explicitly
            demarcated as type aliases.
        """
        if not isinstance(self.scope, ModuleScope):
            super().ASSIGN(tree)
            return

        for target in tree.targets:
            self.handleNode(target, tree)

        self.deferFunction(lambda: self.handleNode(tree.value, tree))

    def handleNodeDelete(self, node: ast.AST) -> None:
        """Null implementation.

        Lets users use `del` in stubs to denote private names.
        """
        return


class PyiAwareFileChecker(checker.FileChecker):
    def run_check(self, plugin: LoadedPlugin, **kwargs: Any) -> Any:
        if plugin.obj is FlakesChecker:
            if self.filename == "-":
                filename = self.options.stdin_display_name
            else:
                filename = self.filename

            if filename.endswith(".pyi"):
                LOG.info(
                    f"Replacing FlakesChecker with PyiAwareFlakesChecker while "
                    f"checking {filename!r}"
                )
                plugin = plugin._replace(obj=PyiAwareFlakesChecker)
        return super().run_check(plugin, **kwargs)


_TYPE_COMMENT_REGEX = re.compile(r"#\s*type:\s*(?!\s?ignore)([^#]+)(\s*#.*?)?$")


def _check_for_type_comments(lines: list[str]) -> Iterator[errors.Error]:
    for lineno, line in enumerate(lines, start=1):
        cleaned_line = line.strip()

        if cleaned_line.startswith("#"):
            continue

        if match := _TYPE_COMMENT_REGEX.search(cleaned_line):
            type_comment = match.group(1).strip()

            try:
                ast.parse(type_comment)
            except SyntaxError:
                continue

            yield errors.Error(lineno, 0, errors.Y033, PyiTreeChecker)


@dataclass
class PyiTreeChecker:
    name: ClassVar[str] = "flake8-pyi"
    tree: ast.Module
    lines: list[str]
    filename: str = "(none)"

    def run(self) -> Iterator[errors.Error]:
        if self.filename.endswith(".pyi"):
            yield from _check_for_type_comments(self.lines)
            yield from visitor.PyiVisitor(filename=self.filename).run(self.tree)

    @staticmethod
    def add_options(parser: OptionManager) -> None:
        """This is brittle, there's multiple levels of caching of defaults."""
        parser.parser.set_defaults(filename="*.py,*.pyi")
        parser.extend_default_ignore(errors.DISABLED_BY_DEFAULT)
        parser.add_option(
            "--no-pyi-aware-file-checker",
            default=False,
            action="store_true",
            parse_from_config=True,
            help="don't patch flake8 with .pyi-aware file checker",
        )

    @staticmethod
    def parse_options(options: argparse.Namespace) -> None:
        if not options.no_pyi_aware_file_checker:
            checker.FileChecker = PyiAwareFileChecker
