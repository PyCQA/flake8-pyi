from __future__ import annotations

import ast
import sys  # noqa: F401  # Used in doctests only.
from collections import defaultdict
from collections.abc import Sequence
from functools import partial
from itertools import chain
from keyword import iskeyword
from typing import NamedTuple

from .ast_helpers import (
    ast_node_for,  # noqa: F401  # Used in doctests only.
    get_name_of_class_if_from_modules,
    is_None,
    is_object,
    is_union,
)
from .constants import (
    ALLOWED_SIMPLE_NAMES_IN_DEFAULTS,
    NEGATABLE_MATH_ATTRIBUTES_IN_DEFAULTS,
    TYPING_MODULES,
    TYPING_OR_COLLECTIONS_ABC,
)

is_BaseException = partial(is_object, name="BaseException", from_={"builtins"})
is_TypeAlias = partial(is_object, name="TypeAlias", from_=TYPING_MODULES)
is_NamedTuple = partial(is_object, name="NamedTuple", from_=TYPING_MODULES)
is_deprecated = partial(
    is_object, name="deprecated", from_={"typing_extensions", "warnings"}
)
is_TypedDict = partial(
    is_object, name="TypedDict", from_=TYPING_MODULES | {"mypy_extensions"}
)
is_Literal = partial(is_object, name="Literal", from_=TYPING_MODULES)
is_abstractmethod = partial(is_object, name="abstractmethod", from_={"abc"})
is_Any = partial(is_object, name="Any", from_=TYPING_MODULES)
is_overload = partial(is_object, name="overload", from_=TYPING_MODULES)
is_final = partial(is_object, name="final", from_=TYPING_MODULES)
is_Self = partial(is_object, name="Self", from_=({"_typeshed"} | TYPING_MODULES))
is_TracebackType = partial(is_object, name="TracebackType", from_={"types"})
is_builtins_object = partial(is_object, name="object", from_={"builtins"})
is_builtins_type = partial(is_object, name="type", from_={"builtins"})
is_Unused = partial(is_object, name="Unused", from_={"_typeshed"})
is_Incomplete = partial(is_object, name="Incomplete", from_={"_typeshed"})
is_Iterable = partial(is_object, name="Iterable", from_=TYPING_OR_COLLECTIONS_ABC)
is_AsyncIterable = partial(
    is_object, name="AsyncIterable", from_=TYPING_OR_COLLECTIONS_ABC
)
is_Final = partial(is_object, name="Final", from_=TYPING_MODULES)
is_Generator = partial(is_object, name="Generator", from_=TYPING_OR_COLLECTIONS_ABC)
is_AsyncGenerator = partial(
    is_object, name="AsyncGenerator", from_=TYPING_OR_COLLECTIONS_ABC
)
is_Generic = partial(is_object, name="Generic", from_=TYPING_MODULES)
is_Unpack = partial(is_object, name="Unpack", from_=TYPING_MODULES)
is_override = partial(is_object, name="override", from_=TYPING_MODULES)


def is_object_or_Unused(node: ast.expr | None) -> bool:
    return is_builtins_object(node) or is_Unused(node)


def is_IncompleteOrNone(node: ast.expr | None) -> bool:
    return is_union(node) and is_Incomplete(node.left) and is_None(node.right)


def is_bad_TypedDict(node: ast.Call) -> bool:
    """Should the assignment-based TypedDict `node` be rewritten using class syntax?

    Return `False` if the TypedDict appears as though it may be invalidly defined;
    type-checkers will raise an error in that eventuality.
    """

    args = node.args
    if len(args) != 2:
        return False

    typed_dict_annotations = args[1]

    # The runtime supports many ways of creating a TypedDict,
    # e.g. `T = TypeDict('T', [['foo', int], ['bar', str]])`,
    # but PEP 589 states that type-checkers are only expected
    # to accept a dictionary literal for the second argument.
    if not isinstance(typed_dict_annotations, ast.Dict):
        return False

    for key in typed_dict_annotations.keys:
        if not (
            isinstance(key, ast.Constant)
            and type(key.value) is str
            and key.value.isidentifier()
            and not iskeyword(key.value)
        ):
            return False
    return True


def is_assignment_which_must_have_a_value(
    target_name: str | None, *, in_class: bool
) -> bool:
    return (target_name in {"__match_args__", "__slots__"} and in_class) or (
        target_name == "__all__" and not in_class
    )


class UnionAnalysis(NamedTuple):
    members_by_dump: defaultdict[str, list[ast.expr]]
    dupes_in_union: bool
    builtins_classes_in_union: set[str]
    multiple_literals_in_union: bool
    non_literals_in_union: bool
    combined_literal_members: list[ast.expr]
    # type subscript == type[Foo]
    multiple_type_subscripts_in_union: bool
    combined_type_subscripts: list[ast.expr]


def analyse_union(members: Sequence[ast.expr]) -> UnionAnalysis:
    """Return a tuple providing analysis of a given sequence of union members.

    >>> source = 'Union[int, memoryview, memoryview, Literal["foo"], Literal[1], type[float], type[str]]'
    >>> union = ast_node_for(source)
    >>> analysis = analyse_union(union.slice.elts)
    >>> dump = "Name(id='memoryview')" if sys.version_info >= (3, 15) else "Name(id='memoryview', ctx=Load())"
    >>> len(analysis.members_by_dump[dump])
    2
    >>> analysis.dupes_in_union
    True
    >>> "int" in analysis.builtins_classes_in_union
    True
    >>> "float" in analysis.builtins_classes_in_union
    False
    >>> analysis.multiple_literals_in_union
    True
    >>> analysis.non_literals_in_union
    True
    >>> ast.unparse(ast.Tuple(analysis.combined_literal_members))
    "('foo', 1)"
    >>> analysis.multiple_type_subscripts_in_union
    True
    >>> ast.unparse(ast.Tuple(analysis.combined_type_subscripts))
    '(float, str)'
    """

    non_literals_in_union = False
    members_by_dump: defaultdict[str, list[ast.expr]] = defaultdict(list)
    builtins_classes_in_union: set[str] = set()
    literals_in_union = []
    combined_literal_members: list[ast.expr] = []
    type_subscripts_in_union: list[ast.expr] = []

    for member in members:
        members_by_dump[ast.dump(member)].append(member)
        name_if_builtins_cls = get_name_of_class_if_from_modules(
            member, modules={"builtins"}
        )
        if name_if_builtins_cls is not None:
            builtins_classes_in_union.add(name_if_builtins_cls)
        if isinstance(member, ast.Subscript) and is_Literal(member.value):
            literals_in_union.append(member.slice)
        else:
            non_literals_in_union = True
        if isinstance(member, ast.Subscript) and is_builtins_type(member.value):
            type_subscripts_in_union.append(member.slice)

    for literal in literals_in_union:
        if isinstance(literal, ast.Tuple):
            combined_literal_members.extend(literal.elts)
        else:
            combined_literal_members.append(literal)

    return UnionAnalysis(
        members_by_dump=members_by_dump,
        dupes_in_union=any(len(lst) > 1 for lst in members_by_dump.values()),
        builtins_classes_in_union=builtins_classes_in_union,
        multiple_literals_in_union=len(literals_in_union) >= 2,
        non_literals_in_union=non_literals_in_union,
        combined_literal_members=combined_literal_members,
        multiple_type_subscripts_in_union=len(type_subscripts_in_union) >= 2,
        combined_type_subscripts=type_subscripts_in_union,
    )


class TypingLiteralAnalysis(NamedTuple):
    members_by_dump: defaultdict[str, list[ast.expr]]
    members_without_none: list[ast.expr]
    none_members: list[ast.expr]
    contains_only_none: bool


def analyse_typing_Literal(node: ast.Subscript) -> TypingLiteralAnalysis:
    """Return a tuple providing analysis of a `typing.Literal` slice."""

    members_by_dump: defaultdict[str, list[ast.expr]] = defaultdict(list)
    members_without_none: list[ast.expr] = []
    none_members: list[ast.expr] = []

    members = node.slice.elts if isinstance(node.slice, ast.Tuple) else [node.slice]

    for member in members:
        members_by_dump[ast.dump(member)].append(member)
        if is_None(member):
            none_members.append(member)
        else:
            members_without_none.append(member)

    return TypingLiteralAnalysis(
        members_by_dump=members_by_dump,
        members_without_none=members_without_none,
        none_members=none_members,
        contains_only_none=bool(none_members and not members_without_none),
    )


def is_valid_default_value_with_annotation(
    node: ast.expr, *, allow_containers: bool = True
) -> bool:
    """Is `node` valid as a default value for a function or method parameter in a stub?

    Note that this function is *also* used to determine
    the validity of default values for ast.AnnAssign nodes.
    (E.g. `foo: int = 5` is OK, but `foo: TypeVar = TypeVar("foo")` is not.)
    """
    match node:
        case ast.List(elts) | ast.Tuple(elts) | ast.Set(elts):
            return (
                allow_containers
                and len(elts) <= 10
                and all(
                    is_valid_default_value_with_annotation(elt, allow_containers=False)
                    for elt in elts
                )
            )

        case ast.Dict(keys, values):
            return (
                allow_containers
                and len(keys) <= 10
                and all(
                    (
                        subnode is not None
                        and is_valid_default_value_with_annotation(
                            subnode, allow_containers=False
                        )
                    )
                    for subnode in chain(keys, values)
                )
            )

        # `...`, bools, None, str, bytes,
        # positive ints, positive floats, positive complex numbers with no real part
        case ast.Constant():
            return True

        # Negative ints, negative floats, negative complex numbers with no real part
        case ast.UnaryOp(op=ast.USub(), operand=ast.Constant(value=value)):
            return type(value) in {int, float, complex}

        # some constants from the math module
        case ast.UnaryOp(
            op=ast.USub(), operand=ast.Attribute(value=ast.Name(id), attr=attr)
        ):
            return f"{id}.{attr}" in NEGATABLE_MATH_ATTRIBUTES_IN_DEFAULTS

        # Complex numbers with a real part and an imaginary part...
        case ast.BinOp(
            left=left, op=ast.Add() | ast.Sub(), right=ast.Constant(value=complex())
        ):
            match left:
                case ast.Constant(value):
                    return type(value) in {int, float}
                case ast.UnaryOp(op=ast.USub(), operand=ast.Constant(value)):
                    return type(value) in {int, float}
                case _:
                    return False

        # Attribute access like math.inf or enums
        case ast.Attribute():
            return True

        # Special cases
        case ast.Name(id):
            return id in ALLOWED_SIMPLE_NAMES_IN_DEFAULTS

        case _:
            return False
