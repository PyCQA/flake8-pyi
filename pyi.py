#!/usr/bin/env python3
from __future__ import annotations

import argparse
import ast
import logging
import optparse
import re
import sys
from collections import Counter
from collections.abc import Container, Iterable, Iterator, Sequence
from contextlib import contextmanager
from copy import deepcopy
from dataclasses import dataclass
from functools import partial
from itertools import chain
from keyword import iskeyword
from pathlib import Path
from typing import TYPE_CHECKING, Any, ClassVar, NamedTuple

from flake8 import checker  # type: ignore[import]
from flake8.options.manager import OptionManager  # type: ignore[import]
from flake8.plugins.manager import Plugin  # type: ignore[import]
from flake8.plugins.pyflakes import FlakesChecker  # type: ignore[import]
from pyflakes.checker import (
    PY2,
    ClassDefinition,
    ClassScope,
    FunctionScope,
    ModuleScope,
)

if sys.version_info >= (3, 9):
    from ast import unparse
else:
    from ast_decompiler import decompile as unparse

if TYPE_CHECKING:
    from typing import TypeGuard

__version__ = "22.3.0"

LOG = logging.getLogger("flake8.pyi")


class Error(NamedTuple):
    lineno: int
    col: int
    message: str
    type: type


class TypeVarInfo(NamedTuple):
    cls_name: str
    name: str


_MAPPING_SLICE = "KeyType, ValueType"
_TYPE_SLICE = "MyClass"
_COUNTER_SLICE = "KeyType"
_CONTEXTLIB_SLICE = "T"
_SET_SLICE = "T"
_SEQUENCE_SLICE = "T"


# ChainMap and AsyncContextManager do not exist in typing or typing_extensions in Python 2,
# so we can disallow importing them from anywhere except collections and contextlib respectively.
_BAD_Y022_IMPORTS = {
    # typing aliases for collections
    "typing.Counter": ("collections.Counter", _COUNTER_SLICE),
    "typing.Deque": ("collections.deque", _SEQUENCE_SLICE),
    "typing.DefaultDict": ("collections.defaultdict", _MAPPING_SLICE),
    "typing.ChainMap": ("collections.ChainMap", _MAPPING_SLICE),
    # typing aliases for builtins
    "typing.Dict": ("dict", _MAPPING_SLICE),
    "typing.FrozenSet": ("frozenset", _SET_SLICE),
    "typing.List": ("list", _SEQUENCE_SLICE),
    "typing.Set": ("set", _SET_SLICE),
    "typing.Tuple": ("tuple", "Foo, Bar"),
    "typing.Type": ("type", _TYPE_SLICE),
    # One typing alias for contextlib
    "typing.AsyncContextManager": (
        "contextlib.AbstractAsyncContextManager",
        _CONTEXTLIB_SLICE,
    ),
    # typing_extensions aliases for collections
    "typing_extensions.Counter": ("collections.Counter", _COUNTER_SLICE),
    "typing_extensions.Deque": ("collections.deque", _SEQUENCE_SLICE),
    "typing_extensions.DefaultDict": ("collections.defaultdict", _MAPPING_SLICE),
    "typing_extensions.ChainMap": ("collections.ChainMap", _MAPPING_SLICE),
    # One typing_extensions alias for a builtin
    "typing_extensions.Type": ("type", _TYPE_SLICE),
    # one typing_extensions alias for contextlib
    "typing_extensions.AsyncContextManager": (
        "contextlib.AbstractAsyncContextManager",
        _CONTEXTLIB_SLICE,
    ),
}

# typing_extensions.ContextManager is omitted from the Y023 and Y027 collections - special-cased
# We use `None` to signify that the object shouldn't  be parameterised.
_BAD_Y023_IMPORTS = {
    # collections.abc aliases
    "Awaitable": "T",
    "Coroutine": "YieldType, SendType, ReturnType",
    "AsyncIterable": "T",
    "AsyncIterator": "T",
    "AsyncGenerator": "YieldType, SendType",
    # typing aliases
    "Protocol": None,
    "runtime_checkable": None,
    "ClassVar": "T",
    "NewType": None,
    "overload": None,
    "Text": None,
    "NoReturn": None,
}

_BAD_Y027_IMPORTS = {
    "typing.ContextManager": ("contextlib.AbstractContextManager", _CONTEXTLIB_SLICE),
    "typing.OrderedDict": ("collections.OrderedDict", _MAPPING_SLICE),
    "typing_extensions.OrderedDict": ("collections.OrderedDict", _MAPPING_SLICE),
}


class PyiAwareFlakesChecker(FlakesChecker):
    def deferHandleNode(self, node: ast.AST | None, parent) -> None:
        self.deferFunction(lambda: self.handleNode(node, parent))

    def ASSIGN(self, node: ast.Assign) -> None:
        """This is a custom implementation of ASSIGN derived from
        handleChildren() in pyflakes 1.3.0.

        The point here is that on module level, there's type aliases that we
        want to bind eagerly, but defer computation of the values of the
        assignments (the type aliases might have forward references).
        """
        if not isinstance(self.scope, ModuleScope):
            super().ASSIGN(node)
            return

        for target in node.targets:
            self.handleNode(target, node)

        self.deferHandleNode(node.value, node)

    def ANNASSIGN(self, node: ast.AnnAssign) -> None:
        """
        Annotated assignments don't have annotations evaluated on function
        scope, hence the custom implementation. Compared to the pyflakes
        version, we defer evaluation of the annotations (and values on
        module level).
        """
        if node.value:
            # Only bind the *target* if the assignment has value.
            # Otherwise it's not really ast.Store and shouldn't silence
            # UndefinedLocal warnings.
            self.handleNode(node.target, node)
        if not isinstance(self.scope, FunctionScope):
            self.deferHandleNode(node.annotation, node)
        if node.value:
            # If the assignment has value, handle the *value*...
            if isinstance(self.scope, ModuleScope):
                # ...later (if module scope).
                self.deferHandleNode(node.value, node)
            else:
                # ...now.
                self.handleNode(node.value, node)

    def LAMBDA(self, node: ast.Lambda) -> None:
        """This is likely very brittle, currently works for pyflakes 1.3.0.

        Deferring annotation handling depends on the fact that during calls
        to LAMBDA visiting the function's body is already deferred and the
        only eager calls to `handleNode` are for annotations.
        """
        self.handleNode, self.deferHandleNode = self.deferHandleNode, self.handleNode  # type: ignore[assignment]
        super().LAMBDA(node)
        self.handleNode, self.deferHandleNode = self.deferHandleNode, self.handleNode  # type: ignore[assignment]

    def CLASSDEF(self, node: ast.ClassDef) -> None:
        if not isinstance(self.scope, ModuleScope):
            # This shouldn't be necessary because .pyi files don't nest
            # scopes much, but better safe than sorry.
            super().CLASSDEF(node)
            return

        # What follows is copied from pyflakes 1.3.0. The only changes are the
        # deferHandleNode calls.
        for decorator in node.decorator_list:
            self.handleNode(decorator, node)
        for baseNode in node.bases:
            self.deferHandleNode(baseNode, node)
        if not PY2:
            for keywordNode in node.keywords:
                self.deferHandleNode(keywordNode, node)
        self.pushScope(ClassScope)
        # doctest does not process doctest within a doctest
        # classes within classes are processed.
        if (
            self.withDoctest
            and not self._in_doctest()
            and not isinstance(self.scope, FunctionScope)
        ):
            self.deferFunction(lambda: self.handleDoctests(node))
        for stmt in node.body:
            self.handleNode(stmt, node)
        self.popScope()
        self.addBinding(node, ClassDefinition(node.name, node))

    def handleNodeDelete(self, node: ast.AST) -> None:
        """Null implementation.

        Lets users use `del` in stubs to denote private names.
        """
        return


class PyiAwareFileChecker(checker.FileChecker):
    def run_check(self, plugin: Plugin, **kwargs: Any) -> Any:
        if self.filename == "-":
            filename = self.options.stdin_display_name
        else:
            filename = self.filename

        if filename.endswith(".pyi") and plugin["plugin"] == FlakesChecker:
            LOG.info(
                "Replacing FlakesChecker with PyiAwareFlakesChecker while "
                "checking %r",
                filename,
            )
            plugin = dict(plugin)
            plugin["plugin"] = PyiAwareFlakesChecker
        return super().run_check(plugin, **kwargs)


class LegacyNormalizer(ast.NodeTransformer):
    """Transform AST to be consistent across Python versions."""

    if sys.version_info < (3, 9):

        def visit_Index(self, node: ast.Index) -> ast.expr:
            """Index nodes no longer exist in Python 3.9.

            For example, consider the AST representing Union[str, int].
            Before 3.9:    Subscript(value=Name(id='Union'), slice=Index(value=Tuple(...)))
            3.9 and newer: Subscript(value=Name(id='Union'), slice=Tuple(...))
            """
            return node.value


def _is_name(node: ast.expr | None, name: str) -> bool:
    """Return True if `node` is an `ast.Name` node with id `name`

    >>> import ast
    >>> node = ast.Name(id="Any")
    >>> _is_name(node, "Any")
    True
    """
    return isinstance(node, ast.Name) and node.id == name


_TYPING_MODULES = frozenset({"typing", "typing_extensions"})


def _is_object(node: ast.expr, name: str, *, from_: Container[str]) -> bool:
    """Determine whether `node` is an ast representation of `name`.

    Return True if `node` is either:
    1). Of shape `ast.Name(id=<name>)`, or;
    2). Of shape `ast.Attribute(value=ast.Name(id=<parent>), attr=<name>)`,
        where <parent> is a string that can be found within the `from_` collection of
        strings.

    >>> import ast
    >>> node1 = ast.Name(id="Literal")
    >>> node2 = ast.Attribute(value=ast.Name(id="typing"), attr="Literal")
    >>> node3 = ast.Attribute(value=ast.Name(id="typing_extensions"), attr="Literal")
    >>> from functools import partial
    >>> _is_Literal = partial(_is_object, name="Literal", from_=_TYPING_MODULES)
    >>> _is_Literal(node1)
    True
    >>> _is_Literal(node2)
    True
    >>> _is_Literal(node3)
    True
    """
    return _is_name(node, name) or (
        isinstance(node, ast.Attribute)
        and node.attr == name
        and isinstance(node.value, ast.Name)
        and node.value.id in from_
    )


_is_TypeAlias = partial(_is_object, name="TypeAlias", from_=_TYPING_MODULES)
_is_NamedTuple = partial(_is_object, name="NamedTuple", from_={"typing"})
_is_TypedDict = partial(_is_object, name="TypedDict", from_=_TYPING_MODULES)
_is_Literal = partial(_is_object, name="Literal", from_=_TYPING_MODULES)
_is_abstractmethod = partial(_is_object, name="abstractmethod", from_={"abc"})
_is_Any = partial(_is_object, name="Any", from_={"typing"})
_is_overload = partial(_is_object, name="overload", from_={"typing"})
_is_final = partial(_is_object, name="final", from_=_TYPING_MODULES)
_is_Final = partial(_is_object, name="Final", from_=_TYPING_MODULES)
_is_Self = partial(_is_object, name="Self", from_=({"_typeshed"} | _TYPING_MODULES))


def _is_decorated_with_final(
    node: ast.ClassDef | ast.FunctionDef | ast.AsyncFunctionDef,
) -> bool:
    return any(_is_final(decorator) for decorator in node.decorator_list)


def _get_collections_abc_obj_id(node: ast.expr | None) -> str | None:
    """
    If the node represents a subscripted object from collections.abc or typing,
    return the name of the object.
    Else, return None.

    >>> import ast
    >>> node1 = ast.parse('AsyncIterator[str]').body[0].value
    >>> node2 = ast.parse('typing.AsyncIterator[str]').body[0].value
    >>> node3 = ast.parse('typing_extensions.AsyncIterator[str]').body[0].value
    >>> node4 = ast.parse('collections.abc.AsyncIterator[str]').body[0].value
    >>> node5 = ast.parse('collections.OrderedDict[str, int]').body[0].value
    >>> _get_collections_abc_obj_id(node1)
    'AsyncIterator'
    >>> _get_collections_abc_obj_id(node2)
    'AsyncIterator'
    >>> _get_collections_abc_obj_id(node3)
    'AsyncIterator'
    >>> _get_collections_abc_obj_id(node4)
    'AsyncIterator'
    >>> _get_collections_abc_obj_id(node5) is None
    True
    """
    if not isinstance(node, ast.Subscript):
        return None
    subscripted_obj = node.value
    if isinstance(subscripted_obj, ast.Name):
        return subscripted_obj.id
    if not isinstance(subscripted_obj, ast.Attribute):
        return None
    obj_value, obj_attr = subscripted_obj.value, subscripted_obj.attr
    if isinstance(obj_value, ast.Name) and obj_value.id in _TYPING_MODULES:
        return obj_attr
    if (
        isinstance(obj_value, ast.Attribute)
        and _is_name(obj_value.value, "collections")
        and obj_value.attr == "abc"
    ):
        return obj_attr
    return None


_ITER_METHODS = frozenset({("Iterator", "__iter__"), ("AsyncIterator", "__aiter__")})

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
    method: ast.FunctionDef | ast.AsyncFunctionDef, *, classdef: ast.ClassDef
) -> bool:
    """Return `True` if `function` should be rewritten using `_typeshed.Self`."""
    # Much too complex for our purposes to worry about overloaded functions or abstractmethods
    if any(
        _is_overload(deco) or _is_abstractmethod(deco) for deco in method.decorator_list
    ):
        return False

    if not _non_kw_only_args_of(method.args):  # weird, but theoretically possible
        return False

    method_name, returns = method.name, method.returns

    if isinstance(method, ast.AsyncFunctionDef):
        return (
            method_name == "__aenter__"
            and _is_name(returns, classdef.name)
            and not _is_decorated_with_final(classdef)
        )

    if method_name in _INPLACE_BINOP_METHODS:
        return returns is not None and not _is_Self(returns)

    if _is_name(returns, classdef.name):
        return method_name in {"__enter__", "__new__"} and not _is_decorated_with_final(
            classdef
        )

    return_obj_name = _get_collections_abc_obj_id(returns)
    return (return_obj_name, method_name) in _ITER_METHODS and any(
        _get_collections_abc_obj_id(base_node) == return_obj_name
        for base_node in classdef.bases
    )


def _unparse_assign_node(node: ast.Assign | ast.AnnAssign) -> str:
    """Unparse an Assign node, and remove any newlines in it"""
    return unparse(node).replace("\n", "")


def _unparse_func_node(node: ast.FunctionDef | ast.AsyncFunctionDef) -> str:
    """Unparse a function node, and reformat it to fit on one line."""
    return re.sub(r"\s+", " ", unparse(node)).strip()


def _is_list_of_str_nodes(seq: list[ast.expr | None]) -> TypeGuard[list[ast.Str]]:
    return all(isinstance(item, ast.Str) for item in seq)


def _is_bad_TypedDict(node: ast.Call) -> bool:
    """Evaluate whether an assignment-based TypedDict should be rewritten using class syntax.

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

    fieldnames = [field.s for field in typed_dict_fields]

    return all(
        fieldname.isidentifier() and not iskeyword(fieldname)
        for fieldname in fieldnames
    )


def _non_kw_only_args_of(args: ast.arguments) -> list[ast.arg]:
    """Return a list containing the pos-only args and pos-or-kwd args of `args`"""
    # pos-only args don't exist on 3.7
    pos_only_args: list[ast.arg] = getattr(args, "posonlyargs", [])
    return pos_only_args + args.args


@dataclass
class NestingCounter:
    """Class to help the PyiVisitor keep track of internal state"""

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
        """Determine whether the level of nesting is currently non-zero"""
        return bool(self.nesting)


class PyiVisitor(ast.NodeVisitor):
    def __init__(self, filename: Path | None = None) -> None:
        self.filename = Path("(none)") if filename is None else filename
        self.errors: list[Error] = []
        # Mapping of all private TypeVars/ParamSpecs/TypeVarTuples to the nodes where they're defined
        self.typevarlike_defs: dict[TypeVarInfo, ast.Assign] = {}
        # Mapping of each name in the file to the no. of occurrences
        self.all_name_occurrences: Counter[str] = Counter()
        self.string_literals_allowed = NestingCounter()
        self.in_function = NestingCounter()
        self.in_class = NestingCounter()
        # This is only relevant for visiting classes
        self.current_class_node: ast.ClassDef | None = None

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(filename={self.filename!r})"

    def _check_import_or_attribute(
        self, node: ast.Attribute | ast.ImportFrom, module_name: str, object_name: str
    ) -> None:
        fullname = f"{module_name}.{object_name}"

        # Y022 errors
        if fullname in _BAD_Y022_IMPORTS:
            good_cls_name, params = _BAD_Y022_IMPORTS[fullname]
            error_message = Y022.format(
                good_syntax=f'"{good_cls_name}[{params}]"',
                bad_syntax=f'"{fullname}[{params}]"',
            )

        # Y027 errors
        elif fullname in _BAD_Y027_IMPORTS:
            good_cls_name, params = _BAD_Y027_IMPORTS[fullname]
            error_message = Y027.format(
                good_syntax=f'"{good_cls_name}[{params}]"',
                bad_syntax=f'"{fullname}[{params}]"',
            )

        # Y023 errors
        elif module_name == "typing_extensions":
            if object_name in _BAD_Y023_IMPORTS:
                slice_contents = _BAD_Y023_IMPORTS[object_name]
                params = "" if slice_contents is None else f"[{slice_contents}]"
                error_message = Y023.format(
                    good_syntax=f'"typing.{object_name}{params}"',
                    bad_syntax=f'"typing_extensions.{object_name}{params}"',
                )
            elif object_name == "ContextManager":
                suggested_syntax = (
                    f'"contextlib.AbstractContextManager[{_CONTEXTLIB_SLICE}]" '
                    f'(or "typing.ContextManager[{_CONTEXTLIB_SLICE}]" '
                    f"in Python 2-compatible code)"
                )
                error_message = Y023.format(
                    good_syntax=suggested_syntax,
                    bad_syntax=f'"typing_extensions.ContextManager[{_CONTEXTLIB_SLICE}]"',
                )
                error_message += " (PEP 585 syntax)"
            else:
                return

        # Y024 errors
        elif fullname == "collections.namedtuple":
            error_message = Y024

        else:
            return

        self.error(node, error_message)

    def visit_Attribute(self, node: ast.Attribute) -> None:
        self.generic_visit(node)
        thing = node.value
        if not isinstance(thing, ast.Name):
            return

        self._check_import_or_attribute(
            node=node, module_name=thing.id, object_name=node.attr
        )

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        module_name, imported_objects = node.module, node.names

        if module_name is None:
            return

        if module_name == "collections.abc" and any(
            obj.name == "Set" and obj.asname != "AbstractSet"
            for obj in imported_objects
        ):
            return self.error(node, Y025)

        for obj in imported_objects:
            self._check_import_or_attribute(
                node=node, module_name=module_name, object_name=obj.name
            )

    def _check_assignment_to_function(
        self, node: ast.Assign, function: ast.expr, object_name: str
    ) -> None:
        """Attempt to find assignments to TypeVar-like objects.

        TypeVars should usually be private.
        If they are private, they should be used at least once in the file in which they are defined.
        """
        if isinstance(function, ast.Name):
            cls_name = function.id
        elif (
            isinstance(function, ast.Attribute)
            and isinstance(function.value, ast.Name)
            and function.value.id in _TYPING_MODULES
        ):
            cls_name = function.attr
        else:
            return

        if cls_name in {"TypeVar", "ParamSpec", "TypeVarTuple"}:
            if object_name.startswith("_"):
                target_info = TypeVarInfo(cls_name=cls_name, name=object_name)
                self.typevarlike_defs[target_info] = node
            else:
                self.error(node, Y001.format(cls_name))

    def visit_Assign(self, node: ast.Assign) -> None:
        if self.in_function.active:
            # We error for unexpected things within functions separately.
            self.generic_visit(node)
            return
        if len(node.targets) == 1:
            target = node.targets[0]
            if isinstance(target, ast.Name):
                target_name = target.id
            else:
                self.error(node, Y017)
                target_name = None
        else:
            self.error(node, Y017)
            target_name = None
        is_special_assignment = (
            target_name == "__match_args__" and self.in_class.active
        ) or (target_name == "__all__" and not self.in_class.active)
        if is_special_assignment:
            with self.string_literals_allowed.enabled():
                self.generic_visit(node)
        else:
            self.generic_visit(node)
        if target_name is None:
            return
        assignment = node.value
        if isinstance(assignment, ast.Call):
            self._check_assignment_to_function(
                node=node, function=assignment.func, object_name=target_name
            )

        elif isinstance(assignment, (ast.Num, ast.Str, ast.Bytes)):
            return self._Y015_error(node)

        if (
            isinstance(assignment, (ast.Constant, ast.NameConstant))
            and not isinstance(assignment, ast.Ellipsis)
            and assignment.value is not None
        ):
            return self._Y015_error(node)

        # We avoid triggering Y026 for calls and = ... because there are various
        # unusual cases where assignment to the result of a call is legitimate
        # in stubs.
        if not is_special_assignment and not isinstance(
            assignment, (ast.Ellipsis, ast.Call)
        ):
            self.error(node, Y026)

    def visit_Name(self, node: ast.Name) -> None:
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

        # String literals can appear in positional arguments for
        # TypeVar definitions.
        with self.string_literals_allowed.enabled():
            for arg in node.args:
                self.visit(arg)
        # But in keyword arguments they're most likely TypeVar bounds,
        # which should not be quoted.
        for kw in node.keywords:
            self.visit(kw)

    # 3.8+
    def visit_Constant(self, node: ast.Constant) -> None:
        if not self.string_literals_allowed.active and isinstance(node.value, str):
            self.error(node, Y020)

    # 3.7 and lower
    def visit_Str(self, node: ast.Str) -> None:
        if not self.string_literals_allowed.active:
            self.error(node, Y020)

    def visit_Expr(self, node: ast.Expr) -> None:
        if isinstance(node.value, ast.Str):
            self.error(node, Y021)
        else:
            self.generic_visit(node)

    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
        if _is_Final(node.annotation):
            with self.string_literals_allowed.enabled():
                self.generic_visit(node)
            return
        if _is_name(node.target, "__all__") and not self.in_class.active:
            with self.string_literals_allowed.enabled():
                self.generic_visit(node)
            if node.value is None:
                self.error(node, Y035)
            return
        self.generic_visit(node)
        if _is_TypeAlias(node.annotation):
            return
        if node.value and not isinstance(node.value, ast.Ellipsis):
            self._Y015_error(node)

    def _check_union_members(self, members: Sequence[ast.expr]) -> None:
        members_by_dump: dict[str, list[ast.expr]] = {}
        for member in members:
            members_by_dump.setdefault(ast.dump(member), []).append(member)

        dupes_in_union = False
        for member_list in members_by_dump.values():
            if len(member_list) >= 2:
                self.error(member_list[1], Y016.format(unparse(member_list[1])))
                dupes_in_union = True

        if not dupes_in_union:
            self._check_for_multiple_literals(members)

    def _check_for_multiple_literals(self, members: Sequence[ast.expr]) -> None:
        literals_in_union, non_literals_in_union = [], []

        for member in members:
            if isinstance(member, ast.Subscript) and _is_Literal(member.value):
                literals_in_union.append(member.slice)
            else:
                non_literals_in_union.append(member)

        if len(literals_in_union) < 2:
            return

        new_literal_members: list[ast.expr] = []

        for literal in literals_in_union:
            if isinstance(literal, ast.Tuple):
                new_literal_members.extend(literal.elts)
            else:
                new_literal_members.append(literal)

        new_literal_slice = unparse(ast.Tuple(new_literal_members)).strip("()")

        if non_literals_in_union:
            suggestion = f'Combine them into one, e.g. "Literal[{new_literal_slice}]".'
        else:
            suggestion = f'Use a single Literal, e.g. "Literal[{new_literal_slice}]".'

        self.error(members[0], Y030.format(suggestion=suggestion))

    def visit_BinOp(self, node: ast.BinOp) -> None:
        if not isinstance(node.op, ast.BitOr):
            self.generic_visit(node)
            return

        # str|int|None parses as BinOp(BinOp(str, |, int), |, None)
        current: ast.expr = node
        members = []
        while isinstance(current, ast.BinOp) and isinstance(current.op, ast.BitOr):
            members.append(current.right)
            current = current.left

        members.append(current)
        members.reverse()

        # Do not call generic_visit(node), that would call this method again unnecessarily
        for member in members:
            self.visit(member)

        self._check_union_members(members)

    def visit_Subscript(self, node: ast.Subscript) -> None:
        subscripted_object = node.value
        if isinstance(subscripted_object, ast.Name):
            subscripted_object_name = subscripted_object.id
        elif (
            isinstance(subscripted_object, ast.Attribute)
            and isinstance(subscripted_object.value, ast.Name)
            and subscripted_object.value.id in _TYPING_MODULES
        ):
            subscripted_object_name = subscripted_object.attr
        else:
            subscripted_object_name = None

        self.visit(subscripted_object)
        if subscripted_object_name == "Literal":
            with self.string_literals_allowed.enabled():
                self.visit(node.slice)
            return

        if isinstance(node.slice, ast.Tuple):
            self._visit_slice_tuple(node.slice, subscripted_object_name)
        else:
            self.visit(node.slice)

    def _visit_slice_tuple(self, node: ast.Tuple, parent: str | None) -> None:
        if parent == "Union":
            self._check_union_members(node.elts)
            self.visit(node)
        elif parent == "Annotated":
            # Allow literals, except in the first argument
            if len(node.elts) > 1:
                self.visit(node.elts[0])
                with self.string_literals_allowed.enabled():
                    for elt in node.elts[1:]:
                        self.visit(elt)
            else:
                self.visit(node)
        else:
            self.visit(node)

    def visit_If(self, node: ast.If) -> None:
        test = node.test
        # No types can appear in if conditions, so avoid confusing additional errors.
        with self.string_literals_allowed.enabled():
            self.visit(test)
        if isinstance(test, ast.BoolOp):
            for expression in test.values:
                self._check_if_expression(expression)
        else:
            self._check_if_expression(test)
        for line in node.body:
            self.visit(line)
        for line in node.orelse:
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

    def _check_subscript_version_check(self, node: ast.Compare) -> None:
        # unless this is on, comparisons against a single integer aren't allowed
        must_be_single = False
        # if strict equality is allowed, it must be against a tuple of this length
        can_have_strict_equals: int | None = None
        version_info = node.left
        if isinstance(version_info, ast.Subscript):
            slc = version_info.slice
            # TODO: ast.Num works, but is deprecated
            if isinstance(slc, ast.Num):
                # anything other than the integer 0 doesn't make much sense
                if isinstance(slc.n, int) and slc.n == 0:
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
                    isinstance(slc.upper, ast.Num)
                    and isinstance(slc.upper.n, int)
                    and slc.upper.n in (1, 2)
                ):
                    can_have_strict_equals = slc.upper.n
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
            if not isinstance(comparator, ast.Num) or not isinstance(comparator.n, int):
                self.error(node, Y003)
        elif not isinstance(comparator, ast.Tuple):
            self.error(node, Y003)
        else:
            if not all(isinstance(elt, ast.Num) for elt in comparator.elts):
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
        if isinstance(comparator, ast.Str):
            # other values are possible but we don't need them right now
            # this protects against typos
            if comparator.s not in ("linux", "win32", "cygwin", "darwin"):
                self.error(node, Y008.format(platform=comparator.s))
        else:
            self.error(node, Y007)

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        old_class_node = self.current_class_node
        self.current_class_node = node
        with self.in_class.enabled():
            self.generic_visit(node)
        self.current_class_node = old_class_node

        # empty class body should contain "..." not "pass"
        if len(node.body) == 1:
            statement = node.body[0]
            if isinstance(statement, ast.Expr) and isinstance(
                statement.value, ast.Ellipsis
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
            elif isinstance(statement, ast.Expr) and isinstance(
                statement.value, ast.Ellipsis
            ):
                self.error(statement, Y013)

    def _Y034_error(
        self, node: ast.FunctionDef | ast.AsyncFunctionDef, cls_name: str
    ) -> None:
        method_name = node.name
        copied_node = deepcopy(node)
        copied_node.decorator_list.clear()
        copied_node.returns = ast.Name(id="Self")
        first_arg = _non_kw_only_args_of(copied_node.args)[0]
        if method_name == "__new__":
            first_arg.annotation = ast.Subscript(
                value=ast.Name(id="type"), slice=ast.Name(id="Self")
            )
            referrer = '"__new__" methods'
        else:
            first_arg.annotation = ast.Name(id="Self")
            referrer = f'"{method_name}" methods in classes like "{cls_name}"'
        error_message = Y034.format(
            methods=referrer,
            method_name=f"{cls_name}.{method_name}",
            suggested_syntax=_unparse_func_node(copied_node),
        )
        self.error(node, error_message)

    def _visit_synchronous_method(self, node: ast.FunctionDef) -> None:
        method_name = node.name
        all_args = node.args
        classdef = self.current_class_node
        assert classdef is not None

        if _has_bad_hardcoded_returns(node, classdef=classdef):
            return self._Y034_error(node=node, cls_name=classdef.name)

        if all_args.kwonlyargs:
            return

        non_kw_only_args = _non_kw_only_args_of(all_args)

        # Raise an error for defining __str__ or __repr__ on a class, but only if:
        # 1). The method is not decorated with @abstractmethod
        # 2). The method has the exact same signature as object.__str__/object.__repr__
        if method_name in {"__repr__", "__str__"}:
            if (
                len(non_kw_only_args) == 1
                and _is_name(node.returns, "str")
                and not any(_is_abstractmethod(deco) for deco in node.decorator_list)
            ):
                self.error(node, Y029)

        elif method_name in {"__eq__", "__ne__"}:
            if len(non_kw_only_args) == 2 and _is_Any(non_kw_only_args[1].annotation):
                self.error(node, Y032.format(method_name=method_name))

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        if self.in_class.active:
            self._visit_synchronous_method(node)
        self._visit_function(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        if self.in_class.active:
            classdef = self.current_class_node
            assert classdef is not None
            if _has_bad_hardcoded_returns(node, classdef=classdef):
                self._Y034_error(node=node, cls_name=classdef.name)
        self._visit_function(node)

    def _Y019_error(
        self, node: ast.FunctionDef | ast.AsyncFunctionDef, typevar_name: str
    ) -> None:
        cleaned_method = deepcopy(node)
        cleaned_method.decorator_list.clear()
        new_syntax = _unparse_func_node(cleaned_method)
        new_syntax = re.sub(rf"\b{typevar_name}\b", "Self", new_syntax)
        self.error(
            # pass the node for the first argument to `self.error`,
            # rather than the function node,
            # as linenos differ in Python 3.7 and 3.8+ for decorated functions
            node.args.args[0],
            Y019.format(typevar_name=typevar_name, new_syntax=new_syntax),
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

        if arg1_annotation_name.startswith("_"):
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

        cls_typevar: str

        if isinstance(first_arg_annotation.slice, ast.Name):
            cls_typevar = first_arg_annotation.slice.id
        else:
            return

        if not _is_name(first_arg_annotation.value, "type"):
            return

        if cls_typevar == return_annotation.id and cls_typevar.startswith("_"):
            self._Y019_error(method, cls_typevar)

    def check_self_typevars(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> None:
        pos_or_keyword_args = node.args.args

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

    def _visit_function(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> None:
        with self.in_function.enabled():
            self.generic_visit(node)

        for i, statement in enumerate(node.body):
            if i == 0:
                # normally, should just be "..."
                if isinstance(statement, ast.Pass):
                    self.error(statement, Y009)
                    continue
                # Ellipsis is fine. Str (docstrings) is not but we produce
                # tailored error message for it elsewhere.
                elif isinstance(statement, ast.Expr) and isinstance(
                    statement.value, (ast.Ellipsis, ast.Str)
                ):
                    continue
            self.error(statement, Y010)

        if self.in_class.active:
            self.check_self_typevars(node)

    def visit_arguments(self, node: ast.arguments) -> None:
        self.generic_visit(node)
        args = node.args[-len(node.defaults) :]
        for arg, default in chain(
            zip(args, node.defaults), zip(node.kwonlyargs, node.kw_defaults)
        ):
            if default is None:
                continue  # keyword-only arg without a default
            if not isinstance(default, ast.Ellipsis):
                self.error(default, (Y014 if arg.annotation is None else Y011))

    def _Y015_error(self, node: ast.Assign | ast.AnnAssign) -> None:
        old_syntax = _unparse_assign_node(node)
        copy_of_node = deepcopy(node)
        copy_of_node.value = ast.Constant(value=...)
        new_syntax = _unparse_assign_node(copy_of_node)
        error_message = Y015.format(old_syntax=old_syntax, new_syntax=new_syntax)
        self.error(node, error_message)

    def error(self, node: ast.AST, message: str) -> None:
        self.errors.append(Error(node.lineno, node.col_offset, message, PyiTreeChecker))

    def run(self, tree: ast.AST) -> Iterable[Error]:
        self.errors.clear()
        self.visit(tree)
        for (cls_name, typevar_name), def_node in self.typevarlike_defs.items():
            if self.all_name_occurrences[typevar_name] == 1:
                self.error(
                    def_node,
                    Y018.format(typevarlike_cls=cls_name, typevar_name=typevar_name),
                )
        yield from self.errors


_TYPE_COMMENT_REGEX = re.compile(r"#\s*type:\s*(?!\s?ignore)([^#]+)(\s*#.*?)?$")


def _check_for_type_comments(path: Path) -> Iterator[Error]:
    stublines = path.read_text().splitlines()
    for lineno, line in enumerate(stublines, start=1):
        cleaned_line = line.strip()

        if cleaned_line.startswith("#"):
            continue

        match = _TYPE_COMMENT_REGEX.search(cleaned_line)
        if not match:
            continue

        type_comment = match.group(1).strip()

        try:
            ast.parse(type_comment)
        except SyntaxError:
            continue

        yield Error(lineno, 0, Y033, PyiTreeChecker)


@dataclass
class PyiTreeChecker:
    name: ClassVar[str] = "flake8-pyi"
    version: ClassVar[str] = __version__

    tree: ast.Module | None = None
    filename: str = "(none)"
    options: argparse.Namespace | None = None

    def run(self) -> Iterable[Error]:
        assert self.tree is not None
        path = Path(self.filename)
        if path.suffix == ".pyi":
            yield from _check_for_type_comments(path)
            visitor = PyiVisitor(filename=path)
            for error in visitor.run(LegacyNormalizer().visit(self.tree)):
                yield error

    @classmethod
    def add_options(cls, parser: OptionManager) -> None:
        """This is brittle, there's multiple levels of caching of defaults."""
        if isinstance(parser.parser, argparse.ArgumentParser):
            parser.parser.set_defaults(filename="*.py,*.pyi")
        else:
            for option in parser.options:
                if option.long_option_name == "--filename":
                    option.default = "*.py,*.pyi"
                    option.option_kwargs["default"] = option.default
                    option.to_optparse().default = option.default
                    parser.parser.defaults[option.dest] = option.default

        try:
            parser.add_option(
                "--no-pyi-aware-file-checker",
                default=False,
                action="store_true",
                parse_from_config=True,
                help="don't patch flake8 with .pyi-aware file checker",
            )
        except optparse.OptionConflictError:
            # In tests, sometimes this option gets called twice for some reason.
            pass

    @classmethod
    def parse_options(
        cls, optmanager: OptionManager, options: argparse.Namespace, extra_args
    ) -> None:
        """This is also brittle, only checked with flake8 3.2.1 and master."""
        if not options.no_pyi_aware_file_checker:
            checker.FileChecker = PyiAwareFileChecker


# Please keep error code lists in README and CHANGELOG up to date
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
Y011 = 'Y011 Default values for typed arguments must be "..."'
Y012 = 'Y012 Class body must not contain "pass"'
Y013 = 'Y013 Non-empty class body must not contain "..."'
Y014 = 'Y014 Default values for arguments must be "..."'
Y015 = 'Y015 Bad default value. Use "{new_syntax}" instead of "{old_syntax}"'
Y016 = 'Y016 Duplicate union member "{}"'
Y017 = "Y017 Only simple assignments allowed"
Y018 = 'Y018 {typevarlike_cls} "{typevar_name}" is not used'
Y019 = 'Y019 Use "_typeshed.Self" instead of "{typevar_name}", e.g. "{new_syntax}"'
Y020 = "Y020 Quoted annotations should never be used in stubs"
Y021 = "Y021 Docstrings should not be included in stubs"
Y022 = "Y022 Use {good_syntax} instead of {bad_syntax} (PEP 585 syntax)"
Y023 = "Y023 Use {good_syntax} instead of {bad_syntax}"
Y024 = 'Y024 Use "typing.NamedTuple" instead of "collections.namedtuple"'
Y025 = (
    'Y025 Use "from collections.abc import Set as AbstractSet" '
    'to avoid confusion with "builtins.set"'
)
Y026 = "Y026 Use typing_extensions.TypeAlias for type aliases"
Y027 = "Y027 Use {good_syntax} instead of {bad_syntax} (PEP 585 syntax)"
Y028 = "Y028 Use class-based syntax for NamedTuples"
Y029 = "Y029 Defining __repr__ or __str__ in a stub is almost always redundant"
Y030 = "Y030 Multiple Literal members in a union. {suggestion}"
Y031 = "Y031 Use class-based syntax for TypedDicts where possible"
Y032 = (
    'Y032 Prefer "object" to "Any" for the second parameter in "{method_name}" methods'
)
Y033 = 'Y033 Do not use type comments in stubs (e.g. use "x: int" instead of "x = ... # type: int")'
Y034 = 'Y034 {methods} usually return "self" at runtime. Consider using "_typeshed.Self" in "{method_name}", e.g. "{suggested_syntax}"'
Y035 = 'Y035 "__all__" in a stub file must have a value, as it has the same semantics as "__all__" at runtime.'
