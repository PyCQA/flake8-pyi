from __future__ import annotations

import ast
import logging
import re
from collections.abc import Iterator
from dataclasses import dataclass
from typing import ClassVar

from flake8.options.manager import OptionManager

from . import errors, visitor

LOG = logging.getLogger("flake8.pyi")


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
        parser.parser.set_defaults(filename="*.py,*.pyi")
        parser.extend_default_ignore(errors.DISABLED_BY_DEFAULT)
