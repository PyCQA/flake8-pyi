from __future__ import annotations

import ast
import re
from collections.abc import Container, Iterable
from functools import partial  # noqa: F401  # Used in doctests only.
from itertools import groupby
from typing import TYPE_CHECKING, NamedTuple, TypeGuard

from . import errors
from .constants import (  # noqa: F401  # Used in doctests only.
    BAD_TYPINGEXTENSIONS_Y023_IMPORTS,
    BAD_Y022_IMPORTS,
    TYPING_MODULES,
    TYPING_OR_COLLECTIONS_ABC,
)

if TYPE_CHECKING:
    # We don't have typing_extensions as a runtime dependency,
    # but all our annotations are stringized due to __future__ annotations,
    # and mypy thinks typing_extensions is part of the stdlib.
    from typing_extensions import TypeIs


def all_equal(iterable: Iterable[object]) -> bool:
    """Returns True if all the elements are equal to each other.

    Adapted from the CPython itertools documentation.
    """
    g = groupby(iterable)
    next(g, True)
    return not next(g, False)


def ast_node_for(string: str) -> ast.AST:
    """Helper function for doctests."""
    expr = ast.parse(string).body[0]
    assert isinstance(expr, ast.Expr)
    return expr.value


def is_name(node: ast.AST | None, name: str) -> bool:
    """Return True if `node` is an `ast.Name` node with id `name`.

    >>> node = ast.Name(id="Any")
    >>> is_name(node, "Any")
    True
    """
    return isinstance(node, ast.Name) and node.id == name


def is_object(node: ast.AST | None, name: str, *, from_: Container[str]) -> bool:
    """Determine whether `node` is an ast representation of `name`.

    Return True if `node` is either:
    1). Of shape `ast.Name(id=<name>)`, or;
    2). Of shape `ast.Attribute(value=ast.Name(id=<parent>), attr=<name>)`,
        where <parent> is a string that can be found within the `from_` collection of
        strings.

    >>> is_AsyncIterator = partial(is_object, name="AsyncIterator", from_=TYPING_OR_COLLECTIONS_ABC)
    >>> is_AsyncIterator(ast_node_for("AsyncIterator"))
    True
    >>> is_AsyncIterator(ast_node_for("typing.AsyncIterator"))
    True
    >>> is_AsyncIterator(ast_node_for("typing_extensions.AsyncIterator"))
    True
    >>> is_AsyncIterator(ast_node_for("collections.abc.AsyncIterator"))
    True
    """
    match node:
        case ast.Name(id):
            return id == name
        case ast.Attribute(value=ast.Name(id), attr=attr):
            return attr == name and id in from_
        case ast.Attribute(
            value=ast.Attribute(value=ast.Name(id), attr=inner_attr), attr=attr
        ):
            return attr == name and f"{id}.{inner_attr}" in from_
        case _:
            return False


def is_union(node: ast.expr | None) -> TypeIs[ast.BinOp]:
    return isinstance(node, ast.BinOp) and isinstance(node.op, ast.BitOr)


def get_name_of_class_if_from_modules(
    classnode: ast.expr, *, modules: Container[str]
) -> str | None:
    """
    If `classnode` is an `ast.Name`, return `classnode.id`.

    If it's an `ast.Attribute`,check that the part before the dot
    is a module in `modules`.
    If it is, return the part after the dot; if it isn't, return `None`.

    If `classnode` is anything else, return `None`.

    >>> get_name_of_class_if_from_modules(ast_node_for('int'), modules={'builtins'})
    'int'
    >>> int_node = ast_node_for('builtins.int')
    >>> get_name_of_class_if_from_modules(int_node, modules={'builtins'})
    'int'
    >>> get_name_of_class_if_from_modules(int_node, modules={'typing'}) is None
    True
    """
    match classnode:
        case ast.Name(id):
            return id
        case ast.Attribute(value=ast.Name(id=module_name), attr=attr):
            if module_name in modules:
                return attr
        case ast.Attribute(
            value=ast.Attribute(value=ast.Name(id=module_name), attr=inner_attr),
            attr=attr,
        ):
            if f"{module_name}.{inner_attr}" in modules:
                return attr

    return None


def is_type_or_Type(node: ast.expr) -> bool:
    """
    >>> is_type_or_Type(ast_node_for('type'))
    True
    >>> is_type_or_Type(ast_node_for('Type'))
    True
    >>> is_type_or_Type(ast_node_for('builtins.type'))
    True
    >>> is_type_or_Type(ast_node_for('typing_extensions.Type'))
    True
    >>> is_type_or_Type(ast_node_for('typing.Type'))
    True
    """
    cls_name = get_name_of_class_if_from_modules(
        node, modules=TYPING_MODULES | {"builtins"}
    )
    return cls_name in {"type", "Type"}


def is_None(node: ast.expr | None) -> bool:
    return isinstance(node, ast.Constant) and node.value is None


class ExitArgAnalysis(NamedTuple):
    is_union_with_None: bool
    non_None_part: ast.expr | None

    def __repr__(self) -> str:
        if self.non_None_part is None:
            non_None_part_repr = "None"
        else:
            non_None_part_repr = ast.dump(self.non_None_part)

        return (
            f"ExitArgAnalysis("
            f"is_union_with_None={self.is_union_with_None}, "
            f"non_None_part={non_None_part_repr}"
            f")"
        )


def analyse_exit_method_arg(node: ast.BinOp) -> ExitArgAnalysis:
    """Return a two-item tuple analysing the annotation of an exit-method arg.

    The `node` represents a union type written as `X | Y`.

    >>> analyse_exit_method_arg(ast_node_for('int | str'))
    ExitArgAnalysis(is_union_with_None=False, non_None_part=None)
    >>> analyse_exit_method_arg(ast_node_for('int | None'))  # doctest: +ELLIPSIS
    ExitArgAnalysis(is_union_with_None=True, non_None_part=Name(id='int'...))
    >>> analyse_exit_method_arg(ast_node_for('None | str'))  # doctest: +ELLIPSIS
    ExitArgAnalysis(is_union_with_None=True, non_None_part=Name(id='str'...))
    """
    assert isinstance(node.op, ast.BitOr)
    if is_None(node.left):
        return ExitArgAnalysis(is_union_with_None=True, non_None_part=node.right)
    if is_None(node.right):
        return ExitArgAnalysis(is_union_with_None=True, non_None_part=node.left)
    return ExitArgAnalysis(is_union_with_None=False, non_None_part=None)


def unparse_func_node(node: ast.FunctionDef | ast.AsyncFunctionDef) -> str:
    """Unparse a function node, and reformat it to fit on one line."""
    return re.sub(r"\s+", " ", ast.unparse(node))


def is_valid_pep_604_union_member(node: ast.expr) -> bool:
    return is_None(node) or isinstance(node, (ast.Name, ast.Attribute, ast.Subscript))


def is_valid_pep_604_union(node: ast.expr) -> TypeGuard[ast.BinOp]:
    """Does `node` represent a valid PEP-604 union (e.g. `int | str`)?"""
    return (
        isinstance(node, ast.BinOp)
        and isinstance(node.op, ast.BitOr)
        and (
            is_valid_pep_604_union_member(node.left)
            or is_valid_pep_604_union(node.left)
        )
        and is_valid_pep_604_union_member(node.right)
    )


def is_valid_default_value_without_annotation(node: ast.expr) -> bool:
    """Is `node` a valid default for an assignment without an annotation?"""
    match node:
        case ast.Call() | ast.Name() | ast.Attribute() | ast.Subscript():
            return True
        case ast.Constant(value):
            return value in {None, ...}
        case _:
            return is_valid_pep_604_union(node)


def check_import_or_attribute(
    node: ast.Attribute | ast.ImportFrom, module_name: str, object_name: str
) -> str | None:
    """If `node` represents a bad import, return the approriate error message.

    Else, return None.
    """
    fullname = f"{module_name}.{object_name}"

    # Y057 errors
    if fullname in {"typing.ByteString", "collections.abc.ByteString"}:
        return errors.Y057.format(module=module_name)

    # Y024 errors
    if fullname == "collections.namedtuple":
        return errors.Y024

    if module_name in TYPING_MODULES:
        # Y022 errors
        if object_name in BAD_Y022_IMPORTS:
            good_cls_name, slice_contents = BAD_Y022_IMPORTS[object_name]
            params = "" if slice_contents is None else f"[{slice_contents}]"
            return errors.Y022.format(
                good_syntax=f'"{good_cls_name}{params}"',
                bad_syntax=f'"{fullname}{params}"',
            )

        # Y037 errors
        if object_name == "Optional":
            return errors.Y037.format(
                old_syntax=fullname, example='"int | None" instead of "Optional[int]"'
            )
        if object_name == "Union":
            return errors.Y037.format(
                old_syntax=fullname, example='"int | str" instead of "Union[int, str]"'
            )

        # Y039 errors
        if object_name == "Text":
            return errors.Y039.format(module=module_name)

        # Y069 errors
        if object_name == "NoReturn":
            return errors.Y069.format(module=module_name)

    # Y023 errors
    if module_name == "typing_extensions":
        if object_name in BAD_TYPINGEXTENSIONS_Y023_IMPORTS:
            return errors.Y023.format(
                good_syntax=f'"typing.{object_name}"',
                bad_syntax=f'"typing_extensions.{object_name}"',
            )
        if object_name == "ClassVar":
            return errors.Y023.format(
                good_syntax='"typing.ClassVar[T]"',
                bad_syntax='"typing_extensions.ClassVar[T]"',
            )

    return None
