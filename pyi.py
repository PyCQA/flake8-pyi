#!/usr/bin/env python3
from __future__ import annotations

import argparse
import ast
import logging
import re
import sys
from collections import Counter, defaultdict
from collections.abc import Container, Iterable, Iterator, Sequence, Set as AbstractSet
from contextlib import contextmanager
from copy import deepcopy
from dataclasses import dataclass
from functools import cached_property, partial
from itertools import chain, groupby, zip_longest
from keyword import iskeyword
from typing import TYPE_CHECKING, Any, ClassVar, Literal, NamedTuple, Protocol

from flake8 import checker
from flake8.options.manager import OptionManager
from flake8.plugins.finder import LoadedPlugin
from flake8.plugins.pyflakes import FlakesChecker
from pyflakes.checker import ModuleScope

if TYPE_CHECKING:
    # We don't have typing_extensions as a runtime dependency,
    # but all our annotations are stringized due to __future__ annotations,
    # and mypy thinks typing_extensions is part of the stdlib.
    from typing_extensions import TypeAlias, TypeGuard

LOG = logging.getLogger("flake8.pyi")

if sys.version_info >= (3, 12):
    _TypeAliasNodeType: TypeAlias = ast.TypeAlias | ast.AnnAssign
else:
    _TypeAliasNodeType: TypeAlias = ast.AnnAssign


class Error(NamedTuple):
    lineno: int
    col: int
    message: str
    type: type[PyiTreeChecker]


class TypeVarInfo(NamedTuple):
    cls_name: str
    name: str


class NodeWithLocation(Protocol):
    lineno: int
    col_offset: int


def all_equal(iterable: Iterable[object]) -> bool:
    """Returns True if all the elements are equal to each other.

    Adapted from the CPython itertools documentation.
    """
    g = groupby(iterable)
    next(g, True)
    return not next(g, False)


_MAPPING_SLICE = "KeyType, ValueType"

# Y022: Use stdlib imports instead of aliases from typing/typing_extensions
_BAD_Y022_IMPORTS: dict[str, tuple[str, str | None]] = {
    # Aliases for collections
    "Counter": ("collections.Counter", "KeyType"),
    "Deque": ("collections.deque", "T"),
    "DefaultDict": ("collections.defaultdict", _MAPPING_SLICE),
    "ChainMap": ("collections.ChainMap", _MAPPING_SLICE),
    "OrderedDict": ("collections.OrderedDict", _MAPPING_SLICE),
    # Aliases for builtins
    "Dict": ("dict", _MAPPING_SLICE),
    "FrozenSet": ("frozenset", "T"),
    "List": ("list", "T"),
    "Set": ("set", "T"),
    "Tuple": ("tuple", "Foo, Bar"),
    "Type": ("type", "MyClass"),
    # Aliases for contextlib
    "ContextManager": ("contextlib.AbstractContextManager", "T"),
    "AsyncContextManager": ("contextlib.AbstractAsyncContextManager", "T"),
    # Aliases for re
    "Match": ("re.Match", "T"),
    "Pattern": ("re.Pattern", "T"),
    # Aliases for collections.abc
    # AbstractSet and ByteString are deliberately omitted
    # (special-cased elsewhere).
    # If the second element of the tuple is `None`,
    # it signals that the object shouldn't be parameterized
    "Collection": ("collections.abc.Collection", "T"),
    "ItemsView": ("collections.abc.ItemsView", _MAPPING_SLICE),
    "KeysView": ("collections.abc.KeysView", "KeyType"),
    "Mapping": ("collections.abc.Mapping", _MAPPING_SLICE),
    "MappingView": ("collections.abc.MappingView", None),
    "MutableMapping": ("collections.abc.MutableMapping", _MAPPING_SLICE),
    "MutableSequence": ("collections.abc.MutableSequence", "T"),
    "MutableSet": ("collections.abc.MutableSet", "T"),
    "Sequence": ("collections.abc.Sequence", "T"),
    "ValuesView": ("collections.abc.ValuesView", "ValueType"),
    "Iterable": ("collections.abc.Iterable", "T"),
    "Iterator": ("collections.abc.Iterator", "T"),
    "Generator": ("collections.abc.Generator", "YieldType, SendType, ReturnType"),
    "Hashable": ("collections.abc.Hashable", None),
    "Reversible": ("collections.abc.Reversible", "T"),
    "Sized": ("collections.abc.Sized", None),
    "Coroutine": ("collections.abc.Coroutine", "YieldType, SendType, ReturnType"),
    "AsyncGenerator": ("collections.abc.AsyncGenerator", "YieldType, SendType"),
    "AsyncIterator": ("collections.abc.AsyncIterator", "T"),
    "AsyncIterable": ("collections.abc.AsyncIterable", "T"),
    "Awaitable": ("collections.abc.Awaitable", "T"),
    "Callable": ("collections.abc.Callable", None),
    "Container": ("collections.abc.Container", "T"),
}

# Y023: Import things from typing instead of typing_extensions
# if they're available from the typing module on 3.8+
_BAD_TYPINGEXTENSIONS_Y023_IMPORTS = frozenset(
    {
        "Any",
        "AnyStr",
        "BinaryIO",
        "Final",
        "ForwardRef",
        "Generic",
        "IO",
        "Literal",
        "Protocol",
        "TextIO",
        "runtime_checkable",
        "NewType",
        "SupportsAbs",
        "SupportsComplex",
        "SupportsFloat",
        "SupportsIndex",
        "SupportsInt",
        "SupportsRound",
        "TypedDict",
        "final",
        "overload",
        "NoReturn",
        # ClassVar deliberately omitted,
        # as it's the only one in this group that should be parameterised.
        # It is special-cased elsewhere.
        #
        # Text/Optional/Union are also deliberately omitted,
        # as well as the various stdlib aliases in typing(_extensions),
        # as you shouldn't be importing them from anywhere! (Y039)
    }
)


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


def _ast_node_for(string: str) -> ast.AST:
    """Helper function for doctests."""
    expr = ast.parse(string).body[0]
    assert isinstance(expr, ast.Expr)
    return expr.value


def _is_name(node: ast.AST | None, name: str) -> bool:
    """Return True if `node` is an `ast.Name` node with id `name`.

    >>> node = ast.Name(id="Any")
    >>> _is_name(node, "Any")
    True
    """
    return isinstance(node, ast.Name) and node.id == name


_TYPING_MODULES = frozenset({"typing", "typing_extensions"})
_TYPING_OR_COLLECTIONS_ABC = _TYPING_MODULES | {"collections.abc"}


def _is_object(node: ast.AST | None, name: str, *, from_: Container[str]) -> bool:
    """Determine whether `node` is an ast representation of `name`.

    Return True if `node` is either:
    1). Of shape `ast.Name(id=<name>)`, or;
    2). Of shape `ast.Attribute(value=ast.Name(id=<parent>), attr=<name>)`,
        where <parent> is a string that can be found within the `from_` collection of
        strings.

    >>> _is_AsyncIterator = partial(_is_object, name="AsyncIterator", from_=_TYPING_OR_COLLECTIONS_ABC)
    >>> _is_AsyncIterator(_ast_node_for("AsyncIterator"))
    True
    >>> _is_AsyncIterator(_ast_node_for("typing.AsyncIterator"))
    True
    >>> _is_AsyncIterator(_ast_node_for("typing_extensions.AsyncIterator"))
    True
    >>> _is_AsyncIterator(_ast_node_for("collections.abc.AsyncIterator"))
    True
    """
    if _is_name(node, name):
        return True
    if not (isinstance(node, ast.Attribute) and node.attr == name):
        return False
    node_value = node.value
    if isinstance(node_value, ast.Name):
        return node_value.id in from_
    return (
        isinstance(node_value, ast.Attribute)
        and isinstance(node_value.value, ast.Name)
        and f"{node_value.value.id}.{node_value.attr}" in from_
    )


_is_BaseException = partial(_is_object, name="BaseException", from_={"builtins"})
_is_TypeAlias = partial(_is_object, name="TypeAlias", from_=_TYPING_MODULES)
_is_NamedTuple = partial(_is_object, name="NamedTuple", from_=_TYPING_MODULES)
_is_deprecated = partial(
    _is_object, name="deprecated", from_={"typing_extensions", "warnings"}
)
_is_TypedDict = partial(
    _is_object, name="TypedDict", from_=_TYPING_MODULES | {"mypy_extensions"}
)
_is_Literal = partial(_is_object, name="Literal", from_=_TYPING_MODULES)
_is_abstractmethod = partial(_is_object, name="abstractmethod", from_={"abc"})
_is_Any = partial(_is_object, name="Any", from_=_TYPING_MODULES)
_is_overload = partial(_is_object, name="overload", from_=_TYPING_MODULES)
_is_final = partial(_is_object, name="final", from_=_TYPING_MODULES)
_is_Self = partial(_is_object, name="Self", from_=({"_typeshed"} | _TYPING_MODULES))
_is_TracebackType = partial(_is_object, name="TracebackType", from_={"types"})
_is_builtins_object = partial(_is_object, name="object", from_={"builtins"})
_is_builtins_type = partial(_is_object, name="type", from_={"builtins"})
_is_Unused = partial(_is_object, name="Unused", from_={"_typeshed"})
_is_Incomplete = partial(_is_object, name="Incomplete", from_={"_typeshed"})
_is_Iterable = partial(_is_object, name="Iterable", from_=_TYPING_OR_COLLECTIONS_ABC)
_is_AsyncIterable = partial(
    _is_object, name="AsyncIterable", from_=_TYPING_OR_COLLECTIONS_ABC
)
_is_Protocol = partial(_is_object, name="Protocol", from_=_TYPING_MODULES)
_is_NoReturn = partial(_is_object, name="NoReturn", from_=_TYPING_MODULES)
_is_Final = partial(_is_object, name="Final", from_=_TYPING_MODULES)
_is_Generator = partial(_is_object, name="Generator", from_=_TYPING_OR_COLLECTIONS_ABC)
_is_AsyncGenerator = partial(
    _is_object, name="AsyncGenerator", from_=_TYPING_OR_COLLECTIONS_ABC
)
_is_Generic = partial(_is_object, name="Generic", from_=_TYPING_MODULES)
_is_Unpack = partial(_is_object, name="Unpack", from_=_TYPING_MODULES)


def _is_object_or_Unused(node: ast.expr | None) -> bool:
    return _is_builtins_object(node) or _is_Unused(node)


def _get_name_of_class_if_from_modules(
    classnode: ast.expr, *, modules: Container[str]
) -> str | None:
    """
    If `classnode` is an `ast.Name`, return `classnode.id`.

    If it's an `ast.Attribute`,check that the part before the dot
    is a module in `modules`.
    If it is, return the part after the dot; if it isn't, return `None`.

    If `classnode` is anything else, return `None`.

    >>> _get_name_of_class_if_from_modules(_ast_node_for('int'), modules={'builtins'})
    'int'
    >>> int_node = _ast_node_for('builtins.int')
    >>> _get_name_of_class_if_from_modules(int_node, modules={'builtins'})
    'int'
    >>> _get_name_of_class_if_from_modules(int_node, modules={'typing'}) is None
    True
    """
    if isinstance(classnode, ast.Name):
        return classnode.id
    if isinstance(classnode, ast.Attribute):
        module_node = classnode.value
        if isinstance(module_node, ast.Name) and module_node.id in modules:
            return classnode.attr
        if (
            isinstance(module_node, ast.Attribute)
            and isinstance(module_node.value, ast.Name)
            and f"{module_node.value.id}.{module_node.attr}" in modules
        ):
            return classnode.attr
    return None


def _is_type_or_Type(node: ast.expr) -> bool:
    """
    >>> _is_type_or_Type(_ast_node_for('type'))
    True
    >>> _is_type_or_Type(_ast_node_for('Type'))
    True
    >>> _is_type_or_Type(_ast_node_for('builtins.type'))
    True
    >>> _is_type_or_Type(_ast_node_for('typing_extensions.Type'))
    True
    >>> _is_type_or_Type(_ast_node_for('typing.Type'))
    True
    """
    cls_name = _get_name_of_class_if_from_modules(
        node, modules=_TYPING_MODULES | {"builtins"}
    )
    return cls_name in {"type", "Type"}


def _is_None(node: ast.expr) -> bool:
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


def _analyse_exit_method_arg(node: ast.BinOp) -> ExitArgAnalysis:
    """Return a two-item tuple analysing the annotation of an exit-method arg.

    The `node` represents a union type written as `X | Y`.

    >>> _analyse_exit_method_arg(_ast_node_for('int | str'))
    ExitArgAnalysis(is_union_with_None=False, non_None_part=None)
    >>> _analyse_exit_method_arg(_ast_node_for('int | None'))
    ExitArgAnalysis(is_union_with_None=True, non_None_part=Name(id='int', ctx=Load()))
    >>> _analyse_exit_method_arg(_ast_node_for('None | str'))
    ExitArgAnalysis(is_union_with_None=True, non_None_part=Name(id='str', ctx=Load()))
    """
    assert isinstance(node.op, ast.BitOr)
    if _is_None(node.left):
        return ExitArgAnalysis(is_union_with_None=True, non_None_part=node.right)
    if _is_None(node.right):
        return ExitArgAnalysis(is_union_with_None=True, non_None_part=node.left)
    return ExitArgAnalysis(is_union_with_None=False, non_None_part=None)


_INPLACE_BINOP_METHODS = frozenset(
    {
        "__iadd__",
        "__isub__",
        "__imul__",
        "__imatmul__",
        "__itruediv__",
        "__ifloordiv__",
        "__imod__",
        "__ipow__",
        "__ilshift__",
        "__irshift__",
        "__iand__",
        "__ixor__",
        "__ior__",
    }
)


def _has_bad_hardcoded_returns(
    method: ast.FunctionDef | ast.AsyncFunctionDef, *, class_ctx: EnclosingClassContext
) -> bool:
    """Return `True` if `function` should be rewritten with `typing_extensions.Self`."""
    # PEP 673 forbids the use of `typing(_extensions).Self` in metaclasses.
    # Do our best to avoid false positives here:
    if class_ctx.is_metaclass:
        return False

    # Much too complex for our purposes to worry
    # about overloaded functions or abstractmethods
    if any(
        _is_overload(deco) or _is_abstractmethod(deco) for deco in method.decorator_list
    ):
        return False

    # weird, but theoretically possible
    if not method.args.posonlyargs and not method.args.args:
        return False

    method_name, returns = method.name, method.returns

    if isinstance(method, ast.AsyncFunctionDef):
        return (
            method_name == "__aenter__"
            and _is_name(returns, class_ctx.cls_name)
            and not class_ctx.is_decorated_with_final
        )

    if method_name in _INPLACE_BINOP_METHODS:
        return returns is not None and not _is_Self(returns)

    if _is_name(returns, class_ctx.cls_name):
        return (
            method_name in {"__enter__", "__new__"}
            and not class_ctx.is_decorated_with_final
        )

    if isinstance(returns, ast.Subscript):
        return_obj_name = _get_name_of_class_if_from_modules(
            returns.value, modules=_TYPING_OR_COLLECTIONS_ABC
        )
        if method_name == "__iter__":
            bad_returns = {"Iterable", "Iterator"}
            return return_obj_name in bad_returns and class_ctx.contains_in_bases(
                "Iterator", from_=_TYPING_OR_COLLECTIONS_ABC
            )
        elif method_name == "__aiter__":
            bad_returns = {"AsyncIterable", "AsyncIterator"}
            return return_obj_name in bad_returns and class_ctx.contains_in_bases(
                "AsyncIterator", from_=_TYPING_OR_COLLECTIONS_ABC
            )

    return False


def _unparse_func_node(node: ast.FunctionDef | ast.AsyncFunctionDef) -> str:
    """Unparse a function node, and reformat it to fit on one line."""
    return re.sub(r"\s+", " ", ast.unparse(node))


def _is_list_of_str_nodes(seq: list[ast.expr | None]) -> TypeGuard[list[ast.Constant]]:
    return all(
        isinstance(item, ast.Constant) and type(item.value) is str for item in seq
    )


def _is_bad_TypedDict(node: ast.Call) -> bool:
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

    typed_dict_fields = typed_dict_annotations.keys

    if not _is_list_of_str_nodes(typed_dict_fields):
        return False

    fieldnames = [field.value for field in typed_dict_fields]

    return all(
        fieldname.isidentifier() and not iskeyword(fieldname)
        for fieldname in fieldnames
    )


def _is_assignment_which_must_have_a_value(
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


def _analyse_union(members: Sequence[ast.expr]) -> UnionAnalysis:
    """Return a tuple providing analysis of a given sequence of union members.

    >>> source = 'Union[int, memoryview, memoryview, Literal["foo"], Literal[1], type[float], type[str]]'
    >>> union = _ast_node_for(source)
    >>> analysis = _analyse_union(union.slice.elts)
    >>> len(analysis.members_by_dump["Name(id='memoryview', ctx=Load())"])
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
        name_if_builtins_cls = _get_name_of_class_if_from_modules(
            member, modules={"builtins"}
        )
        if name_if_builtins_cls is not None:
            builtins_classes_in_union.add(name_if_builtins_cls)
        if isinstance(member, ast.Subscript) and _is_Literal(member.value):
            literals_in_union.append(member.slice)
        else:
            non_literals_in_union = True
        if isinstance(member, ast.Subscript) and _is_builtins_type(member.value):
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


def _analyse_typing_Literal(node: ast.Subscript) -> TypingLiteralAnalysis:
    """Return a tuple providing analysis of a `typing.Literal` slice."""

    members_by_dump: defaultdict[str, list[ast.expr]] = defaultdict(list)
    members_without_none: list[ast.expr] = []
    none_members: list[ast.expr] = []

    members = node.slice.elts if isinstance(node.slice, ast.Tuple) else [node.slice]

    for member in members:
        members_by_dump[ast.dump(member)].append(member)
        if _is_None(member):
            none_members.append(member)
        else:
            members_without_none.append(member)

    return TypingLiteralAnalysis(
        members_by_dump=members_by_dump,
        members_without_none=members_without_none,
        none_members=none_members,
        contains_only_none=bool(none_members and not members_without_none),
    )


_COMMON_METACLASSES = {
    "type": "builtins",
    "ABCMeta": "abc",
    "EnumMeta": "enum",
    "EnumType": "enum",
}


@dataclass(frozen=True)
class EnclosingClassContext:
    node: ast.ClassDef
    cls_name: str
    bases_map: defaultdict[str, set[str | None]]

    def contains_in_bases(self, obj: str, *, from_: AbstractSet[str]) -> bool:
        if obj not in self.bases_map:
            return False
        if None in self.bases_map[obj]:
            return True
        return bool(self.bases_map[obj] & from_)

    @cached_property
    def is_protocol_class(self) -> bool:
        return self.contains_in_bases("Protocol", from_=_TYPING_MODULES)

    @cached_property
    def is_typeddict_class(self) -> bool:
        return self.contains_in_bases(
            "TypedDict", from_=(_TYPING_MODULES | {"mypy_extensions"})
        )

    @cached_property
    def is_enum_class(self) -> bool:
        return any(base_name.endswith(("Enum", "Flag")) for base_name in self.bases_map)

    @cached_property
    def is_metaclass(self) -> bool:
        return any(
            self.contains_in_bases(metacls, from_={module})
            for metacls, module in _COMMON_METACLASSES.items()
        )

    @cached_property
    def is_decorated_with_final(self) -> bool:
        return any(_is_final(decorator) for decorator in self.node.decorator_list)


class ClassBase(NamedTuple):
    module: str | None
    obj: str


def _analyze_classdef(node: ast.ClassDef) -> EnclosingClassContext:
    bases_map: defaultdict[str, set[str | None]] = defaultdict(set)

    def _unravel(node: ast.expr) -> str | None:
        if isinstance(node, ast.Name):
            return node.id
        if isinstance(node, ast.Attribute):
            value = _unravel(node.value)
            if value is None:
                return None
            return f"{value}.{node.attr}"
        return None

    def _analyze_base_node(
        base_node: ast.expr, top_level: bool = True
    ) -> ClassBase | None:
        if isinstance(base_node, ast.Name):
            return ClassBase(None, base_node.id)
        if isinstance(base_node, ast.Attribute):
            value = _unravel(base_node.value)
            if value is None:
                return None
            return ClassBase(value, base_node.attr)
        if isinstance(base_node, ast.Subscript) and top_level:
            return _analyze_base_node(base_node.value, top_level=False)
        return None

    for base_node in node.bases:
        base = _analyze_base_node(base_node)
        if base is None:
            continue
        bases_map[base.obj].add(base.module)

    return EnclosingClassContext(node=node, cls_name=node.name, bases_map=bases_map)


_ALLOWED_MATH_ATTRIBUTES_IN_DEFAULTS = frozenset(
    {"math.inf", "math.nan", "math.e", "math.pi", "math.tau"}
)

_ALLOWED_ATTRIBUTES_IN_DEFAULTS = frozenset(
    {
        "sys.base_prefix",
        "sys.byteorder",
        "sys.exec_prefix",
        "sys.executable",
        "sys.hexversion",
        "sys.maxsize",
        "sys.platform",
        "sys.prefix",
        "sys.stdin",
        "sys.stdout",
        "sys.stderr",
        "sys.version",
        "sys.version_info",
        "sys.winver",
        "_typeshed.sentinel",
    }
)

_ALLOWED_SIMPLE_ATTRIBUTES_IN_DEFAULTS = frozenset({"sentinel"})


def _is_valid_default_value_with_annotation(
    node: ast.expr, *, allow_containers: bool = True
) -> bool:
    """Is `node` valid as a default value for a function or method parameter in a stub?

    Note that this function is *also* used to determine
    the validity of default values for ast.AnnAssign nodes.
    (E.g. `foo: int = 5` is OK, but `foo: TypeVar = TypeVar("foo")` is not.)
    """
    # lists, tuples, sets
    if isinstance(node, (ast.List, ast.Tuple, ast.Set)):
        return (
            allow_containers
            and len(node.elts) <= 10
            and all(
                _is_valid_default_value_with_annotation(elt, allow_containers=False)
                for elt in node.elts
            )
        )

    # dicts
    if isinstance(node, ast.Dict):
        return (
            allow_containers
            and len(node.keys) <= 10
            and all(
                (
                    subnode is not None
                    and _is_valid_default_value_with_annotation(
                        subnode, allow_containers=False
                    )
                )
                for subnode in chain(node.keys, node.values)
            )
        )

    # `...`, bools, None, str, bytes,
    # positive ints, positive floats, positive complex numbers with no real part
    if isinstance(node, ast.Constant):
        return True

    # Negative ints, negative floats, negative complex numbers with no real part,
    # some constants from the math module
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
        numeric_types = {int, float, complex}
        if (
            isinstance(node.operand, ast.Constant)
            and type(node.operand.value) in numeric_types
        ):
            return True
        if isinstance(node.operand, ast.Attribute) and isinstance(
            node.operand.value, ast.Name
        ):
            fullname = f"{node.operand.value.id}.{node.operand.attr}"
            return (
                fullname in _ALLOWED_MATH_ATTRIBUTES_IN_DEFAULTS
                and fullname != "math.nan"
            )
        return False

    # Complex numbers with a real part and an imaginary part...
    if (
        isinstance(node, ast.BinOp)
        and isinstance(node.op, (ast.Add, ast.Sub))
        and isinstance(node.right, ast.Constant)
        and type(node.right.value) is complex
    ):
        left = node.left
        # ...Where the real part is positive:
        if isinstance(left, ast.Constant) and type(left.value) in {int, float}:
            return True
        # ...Where the real part is negative:
        if (
            isinstance(left, ast.UnaryOp)
            and isinstance(left.op, ast.USub)
            and isinstance(left.operand, ast.Constant)
            and type(left.operand.value) in {int, float}
        ):
            return True
        return False

    # Special cases
    if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name):
        fullname = f"{node.value.id}.{node.attr}"
        return (fullname in _ALLOWED_ATTRIBUTES_IN_DEFAULTS) or (
            fullname in _ALLOWED_MATH_ATTRIBUTES_IN_DEFAULTS
        )
    if isinstance(node, ast.Name):
        return node.id in _ALLOWED_SIMPLE_ATTRIBUTES_IN_DEFAULTS

    return False


def _is_valid_pep_604_union_member(node: ast.expr) -> bool:
    return _is_None(node) or isinstance(node, (ast.Name, ast.Attribute, ast.Subscript))


def _is_valid_pep_604_union(node: ast.expr) -> TypeGuard[ast.BinOp]:
    """Does `node` represent a valid PEP-604 union (e.g. `int | str`)?"""
    return (
        isinstance(node, ast.BinOp)
        and isinstance(node.op, ast.BitOr)
        and (
            _is_valid_pep_604_union_member(node.left)
            or _is_valid_pep_604_union(node.left)
        )
        and _is_valid_pep_604_union_member(node.right)
    )


def _is_valid_default_value_without_annotation(node: ast.expr) -> bool:
    """Is `node` a valid default for an assignment without an annotation?"""
    return (
        isinstance(node, (ast.Call, ast.Name, ast.Attribute, ast.Subscript))
        or (isinstance(node, ast.Constant) and node.value in {None, ...})
        or _is_valid_pep_604_union(node)
    )


def _check_import_or_attribute(
    node: ast.Attribute | ast.ImportFrom, module_name: str, object_name: str
) -> str | None:
    """If `node` represents a bad import, return the approriate error message.

    Else, return None.
    """
    fullname = f"{module_name}.{object_name}"

    # Y057 errors
    if fullname in {"typing.ByteString", "collections.abc.ByteString"}:
        return Y057.format(module=module_name)

    # Y024 errors
    if fullname == "collections.namedtuple":
        return Y024

    if module_name in _TYPING_MODULES:
        # Y022 errors
        if object_name in _BAD_Y022_IMPORTS:
            good_cls_name, slice_contents = _BAD_Y022_IMPORTS[object_name]
            params = "" if slice_contents is None else f"[{slice_contents}]"
            return Y022.format(
                good_syntax=f'"{good_cls_name}{params}"',
                bad_syntax=f'"{fullname}{params}"',
            )

        # Y037 errors
        if object_name == "Optional":
            return Y037.format(
                old_syntax=fullname, example='"int | None" instead of "Optional[int]"'
            )
        if object_name == "Union":
            return Y037.format(
                old_syntax=fullname, example='"int | str" instead of "Union[int, str]"'
            )

        # Y039 errors
        if object_name == "Text":
            return Y039.format(module=module_name)

    # Y023 errors
    if module_name == "typing_extensions":
        if object_name in _BAD_TYPINGEXTENSIONS_Y023_IMPORTS:
            return Y023.format(
                good_syntax=f'"typing.{object_name}"',
                bad_syntax=f'"typing_extensions.{object_name}"',
            )
        if object_name == "ClassVar":
            return Y023.format(
                good_syntax='"typing.ClassVar[T]"',
                bad_syntax='"typing_extensions.ClassVar[T]"',
            )

    return None


@dataclass
class NestingCounter:
    """Class to help the PyiVisitor keep track of internal state."""

    nesting: int = 0

    @contextmanager
    def enabled(self) -> Iterator[None]:
        self.nesting += 1
        try:
            yield
        finally:
            self.nesting -= 1

    @property
    def active(self) -> bool:
        """Determine whether the level of nesting is currently non-zero."""
        return bool(self.nesting)


class PyiVisitor(ast.NodeVisitor):
    filename: str
    errors: list[Error]

    # Mapping of all private TypeVars/ParamSpecs/TypeVarTuples
    # to the nodes where they're defined.
    #
    # The value type is a list, because any given TypeVar
    # could have multiple definitions,
    # e.g. in different sys.version_info branches
    typevarlike_defs: defaultdict[TypeVarInfo, list[ast.Assign]]
    # The same for private protocol definitions
    protocol_defs: defaultdict[str, list[ast.ClassDef]]
    # The same for class-based private TypedDicts
    class_based_typeddicts: defaultdict[str, list[ast.ClassDef]]
    # And for assignment-based TypedDicts
    assignment_based_typeddicts: defaultdict[str, list[ast.Assign]]
    # And for private TypeAliases
    typealias_decls: defaultdict[str, list[_TypeAliasNodeType]]

    # Mapping of each name in the file to the no. of occurrences
    all_name_occurrences: Counter[str]

    string_literals_allowed: NestingCounter
    long_strings_allowed: NestingCounter
    in_function: NestingCounter
    visiting_arg: NestingCounter
    Y061_suppressed: NestingCounter

    # This is only relevant for visiting classes
    enclosing_class_ctx: EnclosingClassContext | None = None

    def __init__(self, filename: str) -> None:
        self.filename = filename
        self.errors = []
        self.typevarlike_defs = defaultdict(list)
        self.protocol_defs = defaultdict(list)
        self.class_based_typeddicts = defaultdict(list)
        self.assignment_based_typeddicts = defaultdict(list)
        self.typealias_decls = defaultdict(list)
        self.all_name_occurrences = Counter()
        self.string_literals_allowed = NestingCounter()
        self.long_strings_allowed = NestingCounter()
        self.in_function = NestingCounter()
        self.visiting_arg = NestingCounter()
        self.Y061_suppressed = NestingCounter()

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(filename={self.filename!r})"

    @property
    def visiting_enum_class(self) -> bool:
        return (
            self.enclosing_class_ctx is not None
            and self.enclosing_class_ctx.is_enum_class
        )

    def visit_Attribute(self, node: ast.Attribute) -> None:
        self.generic_visit(node)
        if error_msg := _check_import_or_attribute(
            node=node, module_name=ast.unparse(node.value), object_name=node.attr
        ):
            self.error(node, error_msg)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        self.generic_visit(node)
        module_name = node.module

        if module_name is None:
            return

        imported_names = {obj.name: obj for obj in node.names}

        if module_name == "__future__":
            if "annotations" in imported_names:
                self.error(node, Y044)
            return

        if (
            module_name == "collections.abc"
            and "Set" in imported_names
            and imported_names["Set"].asname != "AbstractSet"
        ):
            self.error(node, Y025)

        for object_name in imported_names:
            if error_msg := _check_import_or_attribute(node, module_name, object_name):
                self.error(node, error_msg)

        if module_name in _TYPING_MODULES and "AbstractSet" in imported_names:
            self.error(node, Y038.format(module=module_name))

    def _check_for_typevarlike_assignments(
        self, node: ast.Assign, function: ast.expr, object_name: str
    ) -> None:
        """Attempt to find assignments to TypeVar-like objects.

        TypeVars should usually be private.
        If they are private, they should be used at least once
        in the file in which they are defined.
        """
        cls_name = _get_name_of_class_if_from_modules(function, modules=_TYPING_MODULES)

        if cls_name in {"TypeVar", "ParamSpec", "TypeVarTuple"}:
            if object_name.startswith("_"):
                target_info = TypeVarInfo(cls_name=cls_name, name=object_name)
                self.typevarlike_defs[target_info].append(node)
            else:
                self.error(node, Y001.format(cls_name))

    def _check_default_value_without_type_annotation(
        self, node: ast.Assign, assignment: ast.expr, target_name: str
    ) -> None:
        if _is_valid_default_value_without_annotation(assignment):
            return
        if _is_valid_default_value_with_annotation(assignment):
            # Annoying special-casing to exclude enums from Y052
            if not self.visiting_enum_class:
                self.error(node, Y052.format(variable=target_name))
        else:
            self.error(node, Y015)

    def visit_Assign(self, node: ast.Assign) -> None:
        if self.in_function.active:
            # We error for unexpected things within functions separately.
            self.generic_visit(node)
            return
        if len(node.targets) == 1:
            target: ast.expr | None = node.targets[0]
            if isinstance(target, ast.Name):
                target_name = target.id
            else:
                self.error(node, Y017)
                target_name = None
        else:
            self.error(node, Y017)
            target = target_name = None
        is_special_assignment = _is_assignment_which_must_have_a_value(
            target_name, in_class=self.enclosing_class_ctx is not None
        )
        assignment = node.value
        if isinstance(assignment, ast.Call):
            # For constructs like `T = TypeVar("T"),
            # we check each parameter individually in visit_Call
            # for whether string-literals are okay
            self.generic_visit(node)
        else:
            with self.string_literals_allowed.enabled():
                self.generic_visit(node)
        if target_name is None:
            return
        assert isinstance(target, ast.Name)
        if isinstance(assignment, ast.Call):
            function = assignment.func
            if _is_TypedDict(function):
                if target_name.startswith("_"):
                    self.assignment_based_typeddicts[target_name].append(node)
            else:
                self._check_for_typevarlike_assignments(
                    node=node, function=function, object_name=target_name
                )
            return

        if not is_special_assignment:
            self._check_for_type_aliases(node, target, assignment)
            self._check_default_value_without_type_annotation(
                node, assignment, target_name
            )

    def visit_AugAssign(self, node: ast.AugAssign) -> None:
        """Allow `__all__ += ['foo', 'bar']` in a stub file."""
        target, value = node.target, node.value
        self.visit(target)
        if _is_name(target, "__all__") and isinstance(node.op, ast.Add):
            with self.string_literals_allowed.enabled():
                self.visit(value)
        else:
            self.visit(value)

    def _check_for_type_aliases(
        self, node: ast.Assign, target: ast.Name, assignment: ast.expr
    ) -> None:
        """
        Check for assignments that look like they could be type aliases,
        but aren't annotated with `typing(_extensions).TypeAlias`.

        We avoid triggering Y026 for calls and = ... because there are various
        unusual cases where assignment to the result of a call is legitimate
        in stubs (`T = TypeVar("T")`, `List = _Alias()`, etc.).

        We also avoid triggering Y026 for aliases like `X = str`.
        It's ultimately nearly impossible to reliably detect
        whether these are type aliases or variable aliases,
        unless you're a type checker (and we're not).

        The only exceptions are the type aliases `X = (typing.)Any`
        (special-cased, because it is so common in a stub),
        and `X = None` (special-cased because it is so special).
        """
        if (
            isinstance(assignment, ast.Subscript)
            or _is_valid_pep_604_union(assignment)
            or _is_Any(assignment)
            or (_is_None(assignment) and not self.visiting_enum_class)
        ):
            new_node = ast.AnnAssign(
                target=target,
                annotation=ast.Name(id="TypeAlias", ctx=ast.Load()),
                value=assignment,
                simple=1,
            )
            self.error(node, Y026.format(suggestion=ast.unparse(new_node)))

    def visit_Name(self, node: ast.Name) -> None:
        self.generic_visit(node)
        self.all_name_occurrences[node.id] += 1

    def visit_Call(self, node: ast.Call) -> None:
        function = node.func
        self.visit(function)

        if _is_NamedTuple(function):
            return self.error(node, Y028)
        elif _is_TypedDict(function):
            if _is_bad_TypedDict(node):
                self.error(node, Y031)
            return
        elif _is_deprecated(function):
            with (
                self.string_literals_allowed.enabled(),
                self.long_strings_allowed.enabled(),
            ):
                for arg in chain(node.args, node.keywords):
                    self.visit(arg)
            return
        elif (
            isinstance(function, ast.Attribute)
            and isinstance(function.value, ast.Name)
            and function.value.id == "__all__"
        ):
            return self.error(node, Y056.format(method=f".{function.attr}()"))

        # String literals can appear as the first positional argument for
        # TypeVar/ParamSpec/TypeVarTuple/NamedTuple/TypedDict/NewType definitions, etc.
        if node.args:
            with self.string_literals_allowed.enabled():
                self.visit(node.args[0])
        # But in other arguments they're most likely TypeVar bounds,
        # which should not be quoted.
        for arg in chain(node.args[1:], node.keywords):
            self.visit(arg)

    def visit_Constant(self, node: ast.Constant) -> None:
        if isinstance(node.value, str) and not self.string_literals_allowed.active:
            self.error(node, Y020)
        elif (
            isinstance(node.value, (str, bytes))
            and not self.long_strings_allowed.active
        ):
            if len(node.value) > 50:
                self.error(node, Y053)
        elif isinstance(node.value, (int, float, complex)):
            if len(str(node.value)) > 10:
                # The maximum character limit is arbitrary, but here's what it's based on:
                # Hex representation of 32-bit integers tend to be 10 chars.
                # So is the decimal representation
                # of the maximum positive signed 32-bit integer.
                # 0xFFFFFFFF --> 4294967295
                self.error(node, Y054)

    def visit_Expr(self, node: ast.Expr) -> None:
        if isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
            self.error(node, Y021)
        else:
            self.generic_visit(node)

    _Y042_REGEX = re.compile(r"^_?[a-z]")

    # Y043: Error for alias names in "T"
    # (plus possibly a single digit afterwards), but only if:
    #
    # - The name starts with "_"
    # - The penultimate character in the name is an ASCII-lowercase letter
    _Y043_REGEX = re.compile(r"^_.*[a-z]T\d?$")

    def _check_typealias(self, node: _TypeAliasNodeType, alias_name: str) -> None:
        if alias_name.startswith("_"):
            self.typealias_decls[alias_name].append(node)
        if self._Y042_REGEX.match(alias_name):
            self.error(node, Y042)
        if self._Y043_REGEX.match(alias_name):
            self.error(node, Y043)

    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
        node_annotation = node.annotation
        node_target = node.target
        node_value = node.value

        is_special_assignment = isinstance(
            node_target, ast.Name
        ) and _is_assignment_which_must_have_a_value(
            node_target.id, in_class=self.enclosing_class_ctx is not None
        )

        is_typealias = _is_TypeAlias(node_annotation) and isinstance(
            node_target, ast.Name
        )

        self.visit(node_target)

        Y064_encountered = self._check_for_Y064_violations(node)
        if Y064_encountered:
            with self.Y061_suppressed.enabled():
                self.visit(node_annotation)
        else:
            self.visit(node_annotation)

        if node_value is not None:
            if is_typealias:
                self.visit(node_value)
            else:
                with self.string_literals_allowed.enabled():
                    self.visit(node_value)

        if is_special_assignment:
            if node_value is None:
                assert isinstance(node_target, ast.Name)
                self.error(node, Y035.format(var=node_target.id))
            return

        if is_typealias:
            assert isinstance(node_target, ast.Name)
            self._check_typealias(node=node, alias_name=node_target.id)
            # Don't bother checking whether
            # nodes marked as TypeAliases have valid assignment values.
            # Type checkers will emit errors for those.
            return

        if _is_Final(node_annotation) and isinstance(
            node_value, (ast.Attribute, ast.Name)
        ):
            return

        if node_value and not _is_valid_default_value_with_annotation(node_value):
            self.error(node, Y015)

    if sys.version_info >= (3, 12):

        def visit_TypeAlias(self, node: ast.TypeAlias) -> None:
            self.generic_visit(node)
            self._check_typealias(node=node, alias_name=node.name.id)

    def _check_for_Y064_violations(self, node: ast.AnnAssign) -> bool:
        annotation = node.annotation

        if node.value or not isinstance(annotation, ast.Subscript):
            return False

        value = annotation.value
        slice_ = annotation.slice

        if (
            _is_Final(value)
            and isinstance(slice_, ast.Subscript)
            and _is_Literal(slice_.value)
            and isinstance(slice_.slice, ast.Constant)
        ):
            final = ast.Name(id="Final", ctx=ast.Load())
            suggestion = ast.AnnAssign(
                target=node.target,
                annotation=final,
                value=slice_.slice,
                simple=node.simple,
            )
            self.error(
                node,
                Y064.format(
                    suggestion=ast.unparse(suggestion), original=ast.unparse(node)
                ),
            )
            return True
        return False

    def _check_union_members(
        self, members: Sequence[ast.expr], is_pep_604_union: bool
    ) -> None:
        first_union_member = members[0]
        analysis = _analyse_union(members)

        for member_list in analysis.members_by_dump.values():
            if len(member_list) >= 2:
                self.error(member_list[1], Y016.format(ast.unparse(member_list[1])))

        if not analysis.dupes_in_union:
            self._check_for_Y051_violations(analysis)
            if analysis.multiple_literals_in_union:
                self._error_for_multiple_literals_in_union(first_union_member, analysis)
            elif analysis.multiple_type_subscripts_in_union:
                self._error_for_multiple_type_subscripts_in_union(
                    first_union_member, analysis, is_pep_604_union
                )
            if self.visiting_arg.active:
                self._check_for_redundant_numeric_unions(first_union_member, analysis)

    def _check_for_Y051_violations(self, analysis: UnionAnalysis) -> None:
        """Search for redundant unions such as `str | Literal["foo"]`, etc."""
        seen_builtins: set[type[object]] = set()
        for literal in analysis.combined_literal_members:
            if not isinstance(literal, ast.Constant):
                continue
            typ = type(literal.value)
            typename = typ.__name__
            if (
                typ in {str, bytes, int, bool}
                and typename in analysis.builtins_classes_in_union
                and typ not in seen_builtins
            ):
                seen_builtins.add(typ)
                self.error(
                    literal,
                    Y051.format(
                        literal_subtype=f"Literal[{ast.unparse(literal)}]",
                        builtin_supertype=typename,
                    ),
                )

    def _check_for_redundant_numeric_unions(
        self, first_union_member: ast.expr, analysis: UnionAnalysis
    ) -> None:
        builtins_in_union = analysis.builtins_classes_in_union
        errors: list[tuple[str, str]] = []
        add_error = errors.append
        if "complex" in builtins_in_union:
            if "float" in builtins_in_union:
                add_error(("float", "complex"))
            if "int" in builtins_in_union:
                add_error(("int", "complex"))
        elif "float" in builtins_in_union and "int" in builtins_in_union:
            add_error(("int", "float"))
        for subtype, supertype in errors:
            self.error(
                first_union_member,
                Y041.format(implicit_subtype=subtype, implicit_supertype=supertype),
            )

    def _error_for_multiple_literals_in_union(
        self, first_union_member: ast.expr, analysis: UnionAnalysis
    ) -> None:
        new_literal_members = analysis.combined_literal_members
        new_literal_slice = ast.unparse(ast.Tuple(new_literal_members)).strip("()")

        if analysis.non_literals_in_union:
            suggestion = f'Combine them into one, e.g. "Literal[{new_literal_slice}]".'
        else:
            suggestion = f'Use a single Literal, e.g. "Literal[{new_literal_slice}]".'

        self.error(first_union_member, Y030.format(suggestion=suggestion))

    def _error_for_multiple_type_subscripts_in_union(
        self,
        first_union_member: ast.expr,
        analysis: UnionAnalysis,
        is_pep_604_union: bool,
    ) -> None:
        # Union using bit or, e.g. type[str] | type[int]
        if is_pep_604_union:
            new_union = " | ".join(
                ast.unparse(expr) for expr in analysis.combined_type_subscripts
            )
        # Union is the explicit Union type, e.g. Union[type[str], type[int]]
        else:
            type_slice = ast.unparse(
                ast.Tuple(analysis.combined_type_subscripts)
            ).strip("()")
            new_union = f"Union[{type_slice}]"

        suggestion = f'Combine them into one, e.g. "type[{new_union}]".'
        self.error(first_union_member, Y055.format(suggestion=suggestion))

    def visit_BinOp(self, node: ast.BinOp) -> None:
        if not isinstance(node.op, ast.BitOr):
            self.generic_visit(node)
            return

        # str|int|None parses as BinOp(BinOp(str, |, int), |, None)
        current: ast.expr = node
        members: list[ast.expr] = []
        while isinstance(current, ast.BinOp) and isinstance(current.op, ast.BitOr):
            members.append(current.right)
            current = current.left

        members.append(current)
        members.reverse()

        # Do not call generic_visit(node),
        # that would call this method again unnecessarily
        for member in members:
            self.visit(member)

        self._check_union_members(members, is_pep_604_union=True)

    def _Y090_error(self, node: ast.Subscript) -> None:
        current_code = ast.unparse(node)
        typ = ast.unparse(node.slice)
        copied_node = deepcopy(node)
        copied_node.slice = ast.Tuple(elts=[copied_node.slice, ast.Constant(...)])
        suggestion = ast.unparse(copied_node)
        self.error(node, Y090.format(original=current_code, typ=typ, new=suggestion))

    def visit_Subscript(self, node: ast.Subscript) -> None:
        subscripted_object = node.value
        subscripted_object_name = _get_name_of_class_if_from_modules(
            subscripted_object, modules=_TYPING_MODULES | {"builtins"}
        )
        self.visit(subscripted_object)
        if subscripted_object_name == "Literal":
            with self.string_literals_allowed.enabled():
                self._visit_typing_Literal(node)
            return

        if isinstance(node.slice, ast.Tuple):
            self._visit_slice_tuple(node.slice, subscripted_object_name)
        else:
            self.visit(node.slice)
            if subscripted_object_name in {"tuple", "Tuple"} and not (
                isinstance(node.slice, ast.Subscript) and _is_Unpack(node.slice.value)
            ):
                self._Y090_error(node)

    def _visit_typing_Literal(self, node: ast.Subscript) -> None:
        analysis = _analyse_typing_Literal(node)

        Y062_encountered = False
        for member_list in analysis.members_by_dump.values():
            if len(member_list) > 1 and not _is_None(member_list[0]):
                Y062_encountered = True
                self.error(member_list[1], Y062.format(ast.unparse(member_list[1])))

        if not Y062_encountered and not self.Y061_suppressed.active:
            if analysis.contains_only_none:
                self.error(node.slice, Y061.format(suggestion="None"))
            elif analysis.none_members:
                if len(analysis.members_without_none) == 1:
                    new_literal_slice = ast.unparse(analysis.members_without_none[0])
                else:
                    new_slice_node = ast.Tuple(elts=analysis.members_without_none)
                    new_literal_slice = ast.unparse(new_slice_node).strip("()")
                suggestion = f"Literal[{new_literal_slice}] | None"
                self.error(analysis.none_members[0], Y061.format(suggestion=suggestion))

        with self.long_strings_allowed.enabled():
            self.visit(node.slice)

    def _visit_slice_tuple(self, node: ast.Tuple, parent: str | None) -> None:
        if parent == "Union":
            self._check_union_members(node.elts, is_pep_604_union=False)
            self.visit(node)
        elif parent == "Annotated":
            # Allow literals, except in the first argument
            if len(node.elts) > 1:
                self.visit(node.elts[0])
                with (
                    self.string_literals_allowed.enabled(),
                    self.long_strings_allowed.enabled(),
                ):
                    for elt in node.elts[1:]:
                        self.visit(elt)
            else:
                self.visit(node)
        else:
            self.visit(node)

    def visit_If(self, node: ast.If) -> None:
        self._check_for_Y066_violations(node)

        test = node.test
        # No types can appear in if conditions, so avoid confusing additional errors.
        with self.string_literals_allowed.enabled():
            self.visit(test)
        if isinstance(test, ast.BoolOp):
            for expression in test.values:
                self._check_if_expression(expression)
        else:
            self._check_if_expression(test)
        for line in chain(node.body, node.orelse):
            self.visit(line)

    def _check_if_expression(self, node: ast.expr) -> None:
        if not isinstance(node, ast.Compare):
            self.error(node, Y002)
            return
        if len(node.comparators) != 1:
            # mypy doesn't support chained comparisons
            self.error(node, Y002)
            return
        if isinstance(node.left, ast.Subscript):
            self._check_subscript_version_check(node)
        elif isinstance(node.left, ast.Attribute):
            if _is_name(node.left.value, "sys"):
                if node.left.attr == "platform":
                    self._check_platform_check(node)
                elif node.left.attr == "version_info":
                    self._check_version_check(node)
                else:
                    self.error(node, Y002)
            else:
                self.error(node, Y002)
        else:
            self.error(node, Y002)

    def _check_for_Y066_violations(self, node: ast.If) -> None:
        def is_version_info(attr: ast.expr) -> bool:
            return (
                isinstance(attr, ast.Attribute)
                and _is_name(attr.value, "sys")
                and attr.attr == "version_info"
            )

        def if_chain_ends_with_else(if_chain: ast.If) -> bool:
            orelse = if_chain.orelse
            if len(orelse) == 1 and isinstance(orelse[0], ast.If):
                return if_chain_ends_with_else(orelse[0])
            return bool(orelse)

        test = node.test
        if not isinstance(test, ast.Compare):
            return

        left = test.left
        op = test.ops[0]
        if (
            is_version_info(left)
            and isinstance(op, ast.Lt)  # sys.version_info < ...
            and if_chain_ends_with_else(node)
        ):
            new_syntax = "if " + ast.unparse(test).replace("<", ">=", 1)
            self.error(node, Y066.format(new_syntax=new_syntax))

    def _check_subscript_version_check(self, node: ast.Compare) -> None:
        # unless this is on, comparisons against a single integer aren't allowed
        must_be_single = False
        # if strict equality is allowed, it must be against a tuple of this length
        can_have_strict_equals: int | None = None
        version_info = node.left
        if isinstance(version_info, ast.Subscript):
            slc = version_info.slice
            if isinstance(slc, ast.Constant):
                # anything other than the integer 0 doesn't make much sense
                if type(slc.value) is int and slc.value == 0:
                    must_be_single = True
                else:
                    self.error(node, Y003)
                    return
            elif isinstance(slc, ast.Slice):
                if slc.lower is not None or slc.step is not None:
                    self.error(node, Y003)
                    return
                elif (
                    # allow only [:1] and [:2]
                    isinstance(slc.upper, ast.Constant)
                    and type(slc.upper.value) is int
                    and slc.upper.value in {1, 2}
                ):
                    can_have_strict_equals = slc.upper.value
                else:
                    self.error(node, Y003)
                    return
            else:
                # extended slicing
                self.error(node, Y003)
                return
        self._check_version_check(
            node,
            must_be_single=must_be_single,
            can_have_strict_equals=can_have_strict_equals,
        )

    def _check_version_check(
        self,
        node: ast.Compare,
        *,
        must_be_single: bool = False,
        can_have_strict_equals: int | None = None,
    ) -> None:
        comparator = node.comparators[0]
        if must_be_single:
            if (
                not isinstance(comparator, ast.Constant)
                or type(comparator.value) is not int
            ):
                self.error(node, Y003)
        elif not isinstance(comparator, ast.Tuple):
            self.error(node, Y003)
        else:
            if not all(
                isinstance(elt, ast.Constant) and type(elt.value) is int
                for elt in comparator.elts
            ):
                self.error(node, Y003)
            elif len(comparator.elts) > 2:
                # mypy only supports major and minor version checks
                self.error(node, Y004)

            cmpop = node.ops[0]
            if isinstance(cmpop, (ast.Lt, ast.GtE)):
                pass
            elif isinstance(cmpop, (ast.Eq, ast.NotEq)):
                if can_have_strict_equals is not None:
                    if len(comparator.elts) != can_have_strict_equals:
                        self.error(node, Y005.format(n=can_have_strict_equals))
                else:
                    self.error(node, Y006)
            else:
                self.error(node, Y006)

    def _check_platform_check(self, node: ast.Compare) -> None:
        cmpop = node.ops[0]
        # "in" might also make sense but we don't currently have one
        if not isinstance(cmpop, (ast.Eq, ast.NotEq)):
            self.error(node, Y007)
            return

        comparator = node.comparators[0]
        if isinstance(comparator, ast.Constant) and type(comparator.value) is str:
            # other values are possible but we don't need them right now
            # this protects against typos
            if comparator.value not in {"linux", "win32", "cygwin", "darwin"}:
                self.error(node, Y008.format(platform=comparator.value))
        else:
            self.error(node, Y007)

    def _check_class_bases(self, bases: list[ast.expr]) -> None:
        Y040_encountered = False
        Y059_encountered = False
        Generic_basenode: ast.Subscript | None = None
        subscript_bases: list[ast.Subscript] = []
        num_bases = len(bases)

        for i, base_node in enumerate(bases, start=1):
            if not Y040_encountered and _is_builtins_object(base_node):
                self.error(base_node, Y040)
                Y040_encountered = True
            if isinstance(base_node, ast.Subscript):
                subscript_bases.append(base_node)
                if _is_Generic(base_node.value):
                    Generic_basenode = base_node
                    if i < num_bases and not Y059_encountered:
                        Y059_encountered = True
                        self.error(base_node, Y059)

        if Generic_basenode is not None:
            assert subscript_bases
            if len(subscript_bases) > 1 and all_equal(
                ast.dump(subscript_base.slice) for subscript_base in subscript_bases
            ):
                msg = Y060.format(redundant_base=ast.unparse(Generic_basenode))
                self.error(Generic_basenode, msg)

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        old_context = self.enclosing_class_ctx
        self.enclosing_class_ctx = _analyze_classdef(node)

        if node.name.startswith("_"):
            if self.enclosing_class_ctx.is_protocol_class:
                self.protocol_defs[node.name].append(node)
            elif self.enclosing_class_ctx.is_typeddict_class:
                self.class_based_typeddicts[node.name].append(node)

        self.generic_visit(node)
        self._check_class_bases(node.bases)
        self.enclosing_class_ctx = old_context

        # empty class body should contain "..." not "pass"
        if len(node.body) == 1:
            statement = node.body[0]
            if (
                isinstance(statement, ast.Expr)
                and isinstance(statement.value, ast.Constant)
                and statement.value.value is ...
            ):
                return
            elif isinstance(statement, ast.Pass):
                self.error(statement, Y009)
                return

        for statement in node.body:
            # "pass" should not used in class body
            if isinstance(statement, ast.Pass):
                self.error(statement, Y012)
            # "..." should not be used in non-empty class body
            elif (
                isinstance(statement, ast.Expr)
                and isinstance(statement.value, ast.Constant)
                and statement.value.value is ...
            ):
                self.error(statement, Y013)

    def _check_exit_method(  # noqa: C901
        self, node: ast.FunctionDef | ast.AsyncFunctionDef, method_name: str
    ) -> None:
        all_args = node.args
        non_kw_only_args = all_args.posonlyargs + all_args.args
        num_args = len(non_kw_only_args)
        varargs = all_args.vararg

        def error_for_bad_exit_method(details: str) -> None:
            self.error(node, Y036.format(method_name=method_name, details=details))

        if num_args < 4:
            if varargs:
                varargs_annotation = varargs.annotation
                if not (
                    varargs_annotation is None
                    or _is_object_or_Unused(varargs_annotation)
                ):
                    error_for_bad_exit_method(
                        f"Star-args in an {method_name} method "
                        f'should be annotated with "object", '
                        f'not "{ast.unparse(varargs_annotation)}"'
                    )
            else:
                error_for_bad_exit_method(
                    f"If there are no star-args, "
                    f"there should be at least 3 non-keyword-only args "
                    f'in an {method_name} method (excluding "self")'
                )

        if len(all_args.defaults) < (num_args - 4):
            error_for_bad_exit_method(
                f"All arguments after the first 4 in an {method_name} method "
                f"must have a default value"
            )

        if None in all_args.kw_defaults:
            error_for_bad_exit_method(
                f"All keyword-only arguments in an {method_name} method "
                f"must have a default value"
            )

        def error_for_bad_annotation(
            annotation_node: ast.expr, *, arg_number: Literal[1, 2, 3]
        ) -> None:
            exit_arg_descriptions = [
                ("first", "type[BaseException] | None"),
                ("second", "BaseException | None"),
                ("third", "types.TracebackType | None"),
            ]

            arg_name, correct_annotation = exit_arg_descriptions[arg_number - 1]

            error_msg_details = (
                f"The {arg_name} arg in an {method_name} method "
                f'should be annotated with "{correct_annotation}" or "object", '
                f'not "{ast.unparse(annotation_node)}"'
            )

            error_for_bad_exit_method(details=error_msg_details)

        if num_args >= 2:
            arg1_annotation = non_kw_only_args[1].annotation
            if arg1_annotation is None or _is_object_or_Unused(arg1_annotation):
                pass
            elif _is_valid_pep_604_union(arg1_annotation):
                is_union_with_None, non_None_part = _analyse_exit_method_arg(
                    arg1_annotation
                )
                if not (
                    is_union_with_None
                    and isinstance(non_None_part, ast.Subscript)
                    and _is_type_or_Type(non_None_part.value)
                    and _is_BaseException(non_None_part.slice)
                ):
                    error_for_bad_annotation(arg1_annotation, arg_number=1)
            else:
                error_for_bad_annotation(arg1_annotation, arg_number=1)

        if num_args >= 3:
            arg2_annotation = non_kw_only_args[2].annotation
            if arg2_annotation is None or _is_object_or_Unused(arg2_annotation):
                pass
            elif _is_valid_pep_604_union(arg2_annotation):
                is_union_with_None, non_None_part = _analyse_exit_method_arg(
                    arg2_annotation
                )
                if not (is_union_with_None and _is_BaseException(non_None_part)):
                    error_for_bad_annotation(arg2_annotation, arg_number=2)
            else:
                error_for_bad_annotation(arg2_annotation, arg_number=2)

        if num_args >= 4:
            arg3_annotation = non_kw_only_args[3].annotation
            if arg3_annotation is None or _is_object_or_Unused(arg3_annotation):
                pass
            elif _is_valid_pep_604_union(arg3_annotation):
                is_union_with_None, non_None_part = _analyse_exit_method_arg(
                    arg3_annotation
                )
                if not (is_union_with_None and _is_TracebackType(non_None_part)):
                    error_for_bad_annotation(arg3_annotation, arg_number=3)
            else:
                error_for_bad_annotation(arg3_annotation, arg_number=3)

    def _Y034_error(
        self, node: ast.FunctionDef | ast.AsyncFunctionDef, cls_name: str
    ) -> None:
        method_name = node.name
        copied_node = deepcopy(node)
        copied_node.decorator_list.clear()
        copied_node.returns = ast.Name(id="Self")
        if method_name == "__new__":
            referrer = '"__new__" methods'
        else:
            referrer = f'"{method_name}" methods in classes like "{cls_name}"'
        error_message = Y034.format(
            methods=referrer,
            method_name=f"{cls_name}.{method_name}",
            suggested_syntax=_unparse_func_node(copied_node),
        )
        self.error(node, error_message)

    def _Y058_error(
        self, node: ast.FunctionDef, args: list[ast.arg], example_returns: str
    ) -> None:
        assert node.name in {"__iter__", "__aiter__"}
        good_cls = "Iterator" if node.name == "__iter__" else "AsyncIterator"
        example = f"def {node.name}({args[0].arg}) -> {example_returns}: ..."
        msg = Y058.format(iter_method=node.name, good_cls=good_cls, example=example)
        self.error(node, msg)

    def _check_iter_returns(
        self, node: ast.FunctionDef, returns: ast.expr | None
    ) -> None:
        if _is_Iterable(returns) or (
            isinstance(returns, ast.Subscript) and _is_Iterable(returns.value)
        ):
            msg = Y045.format(
                iter_method="__iter__", good_cls="Iterator", bad_cls="Iterable"
            )
            self.error(node, msg)
            return
        non_kw_only_args = node.args.posonlyargs + node.args.args
        if len(non_kw_only_args) == 1 and not node.args.kwonlyargs:
            if _is_Generator(returns):
                self._Y058_error(node, non_kw_only_args, "Iterator")
            elif (
                isinstance(returns, ast.Subscript)
                and _is_Generator(returns.value)
                and isinstance(returns.slice, ast.Tuple)
            ):
                elts = returns.slice.elts
                if (
                    len(elts) == 3
                    and (_is_Any(elts[1]) or _is_None(elts[1]))
                    and (_is_Any(elts[2]) or _is_None(elts[2]))
                ):
                    example_returns = f"Iterator[{ast.unparse(returns.slice.elts[0])}]"
                    self._Y058_error(node, non_kw_only_args, example_returns)

    def _check_aiter_returns(
        self, node: ast.FunctionDef, returns: ast.expr | None
    ) -> None:
        if _is_AsyncIterable(returns) or (
            isinstance(returns, ast.Subscript) and _is_AsyncIterable(returns.value)
        ):
            msg = Y045.format(
                iter_method="__aiter__",
                good_cls="AsyncIterator",
                bad_cls="AsyncIterable",
            )
            self.error(node, msg)
            return
        non_kw_only_args = node.args.posonlyargs + node.args.args
        if len(non_kw_only_args) == 1 and not node.args.kwonlyargs:
            if _is_AsyncGenerator(returns):
                self._Y058_error(node, non_kw_only_args, "AsyncIterator")
            elif (
                isinstance(returns, ast.Subscript)
                and _is_AsyncGenerator(returns.value)
                and isinstance(returns.slice, ast.Tuple)
            ):
                elts = returns.slice.elts
                if len(elts) == 2 and (_is_Any(elts[1]) or _is_None(elts[1])):
                    example_returns = (
                        f"AsyncIterator[{ast.unparse(returns.slice.elts[0])}]"
                    )
                    self._Y058_error(node, non_kw_only_args, example_returns)

    def _visit_synchronous_method(
        self, node: ast.FunctionDef, class_ctx: EnclosingClassContext
    ) -> None:
        method_name = node.name
        all_args = node.args

        if _has_bad_hardcoded_returns(node, class_ctx=class_ctx):
            return self._Y034_error(node=node, cls_name=class_ctx.cls_name)

        returns = node.returns

        if method_name == "__iter__":
            return self._check_iter_returns(node, returns)

        if method_name == "__aiter__":
            return self._check_aiter_returns(node, returns)

        if method_name in {"__exit__", "__aexit__"}:
            return self._check_exit_method(node=node, method_name=method_name)

        if all_args.kwonlyargs:
            return

        non_kw_only_args = all_args.posonlyargs + all_args.args

        # Raise an error for defining __str__ or __repr__ on a class, but only if:
        # 1). The method is not decorated with @abstractmethod
        # 2). The method has the exact same signature as object.__str__/object.__repr__
        if method_name in {"__repr__", "__str__"}:
            if (
                len(non_kw_only_args) == 1
                and _is_object(returns, "str", from_={"builtins"})
                and not any(_is_abstractmethod(deco) for deco in node.decorator_list)
            ):
                self.error(node, Y029)

        elif method_name in {"__eq__", "__ne__"}:
            if len(non_kw_only_args) == 2 and _is_Any(non_kw_only_args[1].annotation):
                self.error(node, Y032.format(method_name=method_name))

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        if self.enclosing_class_ctx is not None:
            self._visit_synchronous_method(node, self.enclosing_class_ctx)
        self._visit_function(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        if self.enclosing_class_ctx is not None:
            method_name = node.name
            if _has_bad_hardcoded_returns(node, class_ctx=self.enclosing_class_ctx):
                self._Y034_error(node=node, cls_name=self.enclosing_class_ctx.cls_name)
            elif method_name == "__aexit__":
                self._check_exit_method(node=node, method_name=method_name)
        self._visit_function(node)

    def _Y019_error(
        self, node: ast.FunctionDef | ast.AsyncFunctionDef, typevar_name: str
    ) -> None:
        cleaned_method = deepcopy(node)
        cleaned_method.decorator_list.clear()
        if sys.version_info >= (3, 12):
            cleaned_method.type_params = [
                param
                for param in cleaned_method.type_params
                if not (isinstance(param, ast.TypeVar) and param.name == typevar_name)
            ]
        non_kw_only_args = cleaned_method.args.posonlyargs + cleaned_method.args.args
        non_kw_only_args[0].annotation = None
        new_syntax = _unparse_func_node(cleaned_method)
        new_syntax = re.sub(rf"\b{typevar_name}\b", "Self", new_syntax)
        self.error(node, Y019.format(typevar_name=typevar_name, new_syntax=new_syntax))

    @staticmethod
    def _is_likely_private_typevar(
        method: ast.FunctionDef | ast.AsyncFunctionDef, tvar_name: str
    ) -> bool:
        if tvar_name.startswith("_"):
            return True
        if sys.version_info < (3, 12):
            return False
        return any(  # type: ignore[unreachable,unused-ignore]
            isinstance(param, ast.TypeVar) and param.name == tvar_name
            for param in method.type_params
        )

    def _check_instance_method_for_bad_typevars(
        self,
        *,
        method: ast.FunctionDef | ast.AsyncFunctionDef,
        first_arg_annotation: ast.Name | ast.Subscript,
        return_annotation: ast.Name,
    ) -> None:
        if not isinstance(first_arg_annotation, ast.Name):
            return

        if first_arg_annotation.id != return_annotation.id:
            return

        arg1_annotation_name = first_arg_annotation.id

        if self._is_likely_private_typevar(method, arg1_annotation_name):
            self._Y019_error(method, arg1_annotation_name)

    def _check_class_method_for_bad_typevars(
        self,
        *,
        method: ast.FunctionDef | ast.AsyncFunctionDef,
        first_arg_annotation: ast.Name | ast.Subscript,
        return_annotation: ast.Name,
    ) -> None:
        if not isinstance(first_arg_annotation, ast.Subscript):
            return

        if isinstance(first_arg_annotation.slice, ast.Name):
            cls_typevar = first_arg_annotation.slice.id
        else:
            return

        # Don't error if the first argument is annotated
        # with `builtins.type[T]` or `typing.Type[T]`
        # These are edge cases, and it's hard to give good error messages for them.
        if not _is_name(first_arg_annotation.value, "type"):
            return

        if cls_typevar == return_annotation.id and self._is_likely_private_typevar(
            method, cls_typevar
        ):
            self._Y019_error(method, cls_typevar)

    def check_self_typevars(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> None:
        pos_or_keyword_args = node.args.posonlyargs + node.args.args

        if not pos_or_keyword_args:
            return
        return_annotation = node.returns

        if not isinstance(return_annotation, ast.Name):
            return
        first_arg_annotation = pos_or_keyword_args[0].annotation

        if not isinstance(first_arg_annotation, (ast.Name, ast.Subscript)):
            return

        decorator_names = {
            decorator.id
            for decorator in node.decorator_list
            if isinstance(decorator, ast.Name)
        }

        if "classmethod" in decorator_names or node.name == "__new__":
            self._check_class_method_for_bad_typevars(
                method=node,
                first_arg_annotation=first_arg_annotation,
                return_annotation=return_annotation,
            )
        elif "staticmethod" in decorator_names:
            return
        else:
            self._check_instance_method_for_bad_typevars(
                method=node,
                first_arg_annotation=first_arg_annotation,
                return_annotation=return_annotation,
            )

    @staticmethod
    def _is_positional_pre_570_argname(name: str) -> bool:
        # https://peps.python.org/pep-0484/#positional-only-arguments
        return name.startswith("__") and len(name) >= 3 and not name.endswith("__")

    def _check_pep570_syntax_used_where_applicable(
        self, node: ast.FunctionDef | ast.AsyncFunctionDef
    ) -> None:
        if node.args.posonlyargs:
            return
        pos_or_kw_args = node.args.args
        try:
            first_param = pos_or_kw_args[0]
        except IndexError:
            return
        if self.enclosing_class_ctx is None or any(
            isinstance(decorator, ast.Name) and decorator.id == "staticmethod"
            for decorator in node.decorator_list
        ):
            uses_old_syntax = self._is_positional_pre_570_argname(first_param.arg)
        else:
            uses_old_syntax = self._is_positional_pre_570_argname(first_param.arg) or (
                len(pos_or_kw_args) >= 2
                and self._is_positional_pre_570_argname(pos_or_kw_args[1].arg)
            )
        if uses_old_syntax:
            self.error(node, Y063)

    def _visit_function(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> None:
        with self.in_function.enabled():
            self.generic_visit(node)

        if node.name != "__getattr__" and node.returns and _is_Incomplete(node.returns):
            self.error(node.returns, Y065.format(what="return type"))

        body = node.body
        if len(body) > 1:
            self.error(body[1], Y048)
        elif body:
            statement = body[0]
            # normally, should just be "..."
            if isinstance(statement, ast.Pass):
                self.error(statement, Y009)
            # ... is fine. Docstrings are not but we produce
            # tailored error message for them elsewhere.
            elif not (
                isinstance(statement, ast.Expr)
                and isinstance(statement.value, ast.Constant)
                and isinstance(statement.value.value, (str, type(...)))
            ):
                self.error(statement, Y010)

        self._check_pep570_syntax_used_where_applicable(node)
        if self.enclosing_class_ctx is not None:
            self.check_self_typevars(node)

    def visit_arg(self, node: ast.arg) -> None:
        if _is_NoReturn(node.annotation):
            self.error(node, Y050)
        if _is_Incomplete(node.annotation):
            self.error(node, Y065.format(what=f'parameter "{node.arg}"'))
        with self.visiting_arg.enabled():
            self.generic_visit(node)

    def visit_arguments(self, node: ast.arguments) -> None:
        args = node.posonlyargs + node.args
        defaults = [None] * (len(args) - len(node.defaults)) + node.defaults
        assert len(args) == len(defaults)
        for arg, default in zip(args, defaults):
            self.check_arg_default(arg, default)
        if node.vararg is not None:
            self.visit(node.vararg)
        for arg, default in zip_longest(node.kwonlyargs, node.kw_defaults):
            self.check_arg_default(arg, default)
        if node.kwarg is not None:
            self.visit(node.kwarg)

    def check_arg_default(self, arg: ast.arg, default: ast.expr | None) -> None:
        self.visit(arg)
        if default is not None:
            with self.string_literals_allowed.enabled():
                self.visit(default)
        if default is not None and not _is_valid_default_value_with_annotation(default):
            self.error(default, (Y014 if arg.annotation is None else Y011))

    def error(self, node: NodeWithLocation, message: str) -> None:
        self.errors.append(Error(node.lineno, node.col_offset, message, PyiTreeChecker))

    def _check_for_unused_things(self) -> None:
        """
        After the AST tree has been visited,
        analyse whether there are any unused things in this module.

        We currently check for unused
        - TypeVars
        - ParamSpecs
        - TypeVarTuples
        - Aliases
        - Protocols
        - TypedDicts
        """
        for (cls_name, typevar_name), tv_nodelist in self.typevarlike_defs.items():
            if self.all_name_occurrences[typevar_name] == len(tv_nodelist):
                msg = Y018.format(typevarlike_cls=cls_name, typevar_name=typevar_name)
                self.error(tv_nodelist[0], msg)
        for proto_name, proto_nodelist in self.protocol_defs.items():
            if self.all_name_occurrences[proto_name] == 0:
                self.error(proto_nodelist[0], Y046.format(protocol_name=proto_name))
        for td_name, cls_td_nodelist in self.class_based_typeddicts.items():
            if self.all_name_occurrences[td_name] == 0:
                self.error(cls_td_nodelist[0], Y049.format(typeddict_name=td_name))
        for td_name, ass_td_nodelist in self.assignment_based_typeddicts.items():
            if self.all_name_occurrences[td_name] == len(ass_td_nodelist):
                self.error(ass_td_nodelist[0], Y049.format(typeddict_name=td_name))
        for alias_name, alias_nodelist in self.typealias_decls.items():
            if self.all_name_occurrences[alias_name] == len(alias_nodelist):
                self.error(alias_nodelist[0], Y047.format(alias_name=alias_name))

    def run(self, tree: ast.AST) -> Iterator[Error]:
        self.visit(tree)
        self._check_for_unused_things()
        yield from self.errors


_TYPE_COMMENT_REGEX = re.compile(r"#\s*type:\s*(?!\s?ignore)([^#]+)(\s*#.*?)?$")


def _check_for_type_comments(lines: list[str]) -> Iterator[Error]:
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

            yield Error(lineno, 0, Y033, PyiTreeChecker)


@dataclass
class PyiTreeChecker:
    name: ClassVar[str] = "flake8-pyi"
    tree: ast.Module
    lines: list[str]
    filename: str = "(none)"

    def run(self) -> Iterable[Error]:
        if self.filename.endswith(".pyi"):
            yield from _check_for_type_comments(self.lines)
            yield from PyiVisitor(filename=self.filename).run(self.tree)

    @staticmethod
    def add_options(parser: OptionManager) -> None:
        """This is brittle, there's multiple levels of caching of defaults."""
        parser.parser.set_defaults(filename="*.py,*.pyi")
        parser.extend_default_ignore(DISABLED_BY_DEFAULT)
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


# Please keep error code lists in ERRORCODES and CHANGELOG up to date
Y001 = "Y001 Name of private {} must start with _"
Y002 = (
    "Y002 If test must be a simple comparison against sys.platform or sys.version_info"
)
Y003 = "Y003 Unrecognized sys.version_info check"
Y004 = "Y004 Version comparison must use only major and minor version"
Y005 = "Y005 Version comparison must be against a length-{n} tuple"
Y006 = "Y006 Use only < and >= for version comparisons"
Y007 = "Y007 Unrecognized sys.platform check"
Y008 = 'Y008 Unrecognized platform "{platform}"'
Y009 = 'Y009 Empty body should contain "...", not "pass"'
Y010 = 'Y010 Function body must contain only "..."'
Y011 = "Y011 Only simple default values allowed for typed arguments"
Y012 = 'Y012 Class body must not contain "pass"'
Y013 = 'Y013 Non-empty class body must not contain "..."'
Y014 = "Y014 Only simple default values allowed for arguments"
Y015 = "Y015 Only simple default values are allowed for assignments"
Y016 = 'Y016 Duplicate union member "{}"'
Y017 = "Y017 Only simple assignments allowed"
Y018 = 'Y018 {typevarlike_cls} "{typevar_name}" is not used'
Y019 = (
    'Y019 Use "typing_extensions.Self" instead of "{typevar_name}", e.g. "{new_syntax}"'
)
Y020 = "Y020 Quoted annotations should never be used in stubs"
Y021 = "Y021 Docstrings should not be included in stubs"
Y022 = "Y022 Use {good_syntax} instead of {bad_syntax} (PEP 585 syntax)"
Y023 = "Y023 Use {good_syntax} instead of {bad_syntax}"
Y024 = 'Y024 Use "typing.NamedTuple" instead of "collections.namedtuple"'
Y025 = (
    'Y025 Use "from collections.abc import Set as AbstractSet" '
    'to avoid confusion with "builtins.set"'
)
Y026 = 'Y026 Use typing_extensions.TypeAlias for type aliases, e.g. "{suggestion}"'
Y028 = "Y028 Use class-based syntax for NamedTuples"
Y029 = "Y029 Defining __repr__ or __str__ in a stub is almost always redundant"
Y030 = "Y030 Multiple Literal members in a union. {suggestion}"
Y031 = "Y031 Use class-based syntax for TypedDicts where possible"
Y032 = (
    'Y032 Prefer "object" to "Any" for the second parameter in "{method_name}" methods'
)
Y033 = (
    "Y033 Do not use type comments in stubs "
    '(e.g. use "x: int" instead of "x = ... # type: int")'
)
Y034 = (
    'Y034 {methods} usually return "self" at runtime. '
    'Consider using "typing_extensions.Self" in "{method_name}", '
    'e.g. "{suggested_syntax}"'
)
Y035 = (
    'Y035 "{var}" in a stub file must have a value, '
    'as it has the same semantics as "{var}" at runtime.'
)
Y036 = "Y036 Badly defined {method_name} method: {details}"
Y037 = "Y037 Use PEP 604 union types instead of {old_syntax} (e.g. {example})."
Y038 = (
    'Y038 Use "from collections.abc import Set as AbstractSet" '
    'instead of "from {module} import AbstractSet" (PEP 585 syntax)'
)
Y039 = 'Y039 Use "str" instead of "{module}.Text"'
Y040 = 'Y040 Do not inherit from "object" explicitly, as it is redundant in Python 3'
Y041 = (
    'Y041 Use "{implicit_supertype}" '
    'instead of "{implicit_subtype} | {implicit_supertype}" '
    '(see "The numeric tower" in PEP 484)'
)
Y042 = "Y042 Type aliases should use the CamelCase naming convention"
Y043 = 'Y043 Bad name for a type alias (the "T" suffix implies a TypeVar)'
Y044 = 'Y044 "from __future__ import annotations" has no effect in stub files.'
Y045 = 'Y045 "{iter_method}" methods should return an {good_cls}, not an {bad_cls}'
Y046 = 'Y046 Protocol "{protocol_name}" is not used'
Y047 = 'Y047 Type alias "{alias_name}" is not used'
Y048 = "Y048 Function body should contain exactly one statement"
Y049 = 'Y049 TypedDict "{typeddict_name}" is not used'
Y050 = (
    'Y050 Use "typing_extensions.Never" instead of "NoReturn" for argument annotations'
)
Y051 = 'Y051 "{literal_subtype}" is redundant in a union with "{builtin_supertype}"'
Y052 = 'Y052 Need type annotation for "{variable}"'
Y053 = "Y053 String and bytes literals >50 characters long are not permitted"
Y054 = (
    "Y054 Numeric literals with a string representation "
    ">10 characters long are not permitted"
)
Y055 = 'Y055 Multiple "type[Foo]" members in a union. {suggestion}'
Y056 = (
    'Y056 Calling "{method}" on "__all__" may not be supported by all type checkers '
    "(use += instead)"
)
Y057 = (
    "Y057 Do not use {module}.ByteString, which has unclear semantics and is deprecated"
)
Y058 = (
    'Y058 Use "{good_cls}" as the return value for simple "{iter_method}" methods, '
    'e.g. "{example}"'
)
Y059 = 'Y059 "Generic[]" should always be the last base class'
Y060 = (
    'Y060 Redundant inheritance from "{redundant_base}"; '
    "class would be inferred as generic anyway"
)
Y061 = 'Y061 None inside "Literal[]" expression. Replace with "{suggestion}"'
Y062 = 'Y062 Duplicate "Literal[]" member "{}"'
Y063 = "Y063 Use PEP-570 syntax to indicate positional-only arguments"
Y064 = 'Y064 Use "{suggestion}" instead of "{original}"'
Y065 = 'Y065 Leave {what} unannotated rather than using "Incomplete"'
Y066 = (
    "Y066 When using if/else with sys.version_info, "
    'put the code for new Python versions first, e.g. "{new_syntax}"'
)
Y090 = (
    'Y090 "{original}" means '
    '"a tuple of length 1, in which the sole element is of type {typ!r}". '
    'Perhaps you meant "{new}"?'
)

DISABLED_BY_DEFAULT = ["Y090"]
