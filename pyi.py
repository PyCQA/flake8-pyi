#!/usr/bin/env python3
from __future__ import annotations

import argparse
import ast
import logging
import optparse
import re
import sys
from collections import Counter
from collections.abc import Iterable, Iterator, Sequence
from contextlib import contextmanager
from copy import deepcopy
from dataclasses import dataclass, field
from itertools import chain
from pathlib import Path
from typing import ClassVar, NamedTuple

from flake8 import checker  # type: ignore
from flake8.plugins.pyflakes import FlakesChecker  # type: ignore
from pyflakes.checker import (  # type: ignore[import]
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

__version__ = "20.10.0"

LOG = logging.getLogger("flake8.pyi")


class Error(NamedTuple):
    lineno: int
    col: int
    message: str
    type: type


class TypeVarInfo(NamedTuple):
    cls_name: str
    name: str


# ChainMap and AsyncContextManager do not exist in typing or typing_extensions in Python 2,
# so we can disallow importing them from anywhere except collections and contextlib respectively.
_BAD_Y022_IMPORTS = {
    # typing aliases for collections
    "typing.Counter": "collections.Counter",
    "typing.Deque": "collections.deque",
    "typing.DefaultDict": "collections.defaultdict",
    "typing.ChainMap": "collections.ChainMap",
    # typing aliases for builtins
    "typing.Dict": "builtins.dict",
    "typing.FrozenSet": "builtins.frozenset",
    "typing.List": "builtins.list",
    "typing.Set": "builtins.set",
    "typing.Tuple": "builtins.tuple",
    "typing.Type": "builtins.type",
    # One typing alias for contextlib
    "typing.AsyncContextManager": "contextlib.AbstractAsyncContextManager",
    # typing_extensions aliases for collections
    "typing_extensions.Counter": "collections.Counter",
    "typing_extensions.Deque": "collections.deque",
    "typing_extensions.DefaultDict": "collections.defaultdict",
    "typing_extensions.ChainMap": "collections.ChainMap",
    # One typing_extensions alias for a builtin
    "typing_extensions.Type": "builtins.type",
    # one typing_extensions alias for contextlib
    "typing_extensions.AsyncContextManager": "contextlib.AbstractAsyncContextManager",
}

# typing_extensions.ContextManager is omitted from the Y023 and Y027 collections - special-cased
_BAD_Y023_IMPORTS = frozenset(
    {
        # collections.abc aliases
        "Awaitable",
        "Coroutine",
        "AsyncIterable",
        "AsyncIterator",
        "AsyncGenerator",
        # typing aliases
        "Protocol",
        "runtime_checkable",
        "ClassVar",
        "NewType",
        "overload",
        "Text",
        "NoReturn",
    }
)

_BAD_Y027_IMPORTS = {
    "typing.ContextManager": "contextlib.AbstractContextManager",
    "typing.OrderedDict": "collections.OrderedDict",
    "typing_extensions.OrderedDict": "collections.OrderedDict",
}


class PyiAwareFlakesChecker(FlakesChecker):
    def deferHandleNode(self, node, parent):
        self.deferFunction(lambda: self.handleNode(node, parent))

    def ASSIGN(self, node):
        """This is a custom implementation of ASSIGN derived from
        handleChildren() in pyflakes 1.3.0.

        The point here is that on module level, there's type aliases that we
        want to bind eagerly, but defer computation of the values of the
        assignments (the type aliases might have forward references).
        """
        if not isinstance(self.scope, ModuleScope):
            return super().ASSIGN(node)

        for target in node.targets:
            self.handleNode(target, node)

        self.deferHandleNode(node.value, node)

    def ANNASSIGN(self, node):
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

    def LAMBDA(self, node):
        """This is likely very brittle, currently works for pyflakes 1.3.0.

        Deferring annotation handling depends on the fact that during calls
        to LAMBDA visiting the function's body is already deferred and the
        only eager calls to `handleNode` are for annotations.
        """
        self.handleNode, self.deferHandleNode = self.deferHandleNode, self.handleNode
        super().LAMBDA(node)
        self.handleNode, self.deferHandleNode = self.deferHandleNode, self.handleNode

    def CLASSDEF(self, node):
        if not isinstance(self.scope, ModuleScope):
            # This shouldn't be necessary because .pyi files don't nest
            # scopes much, but better safe than sorry.
            return super().CLASSDEF(node)

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

    def handleNodeDelete(self, node):
        """Null implementation.

        Lets users use `del` in stubs to denote private names.
        """
        return


class PyiAwareFileChecker(checker.FileChecker):
    def run_check(self, plugin, **kwargs):
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


@dataclass
class PyiVisitor(ast.NodeVisitor):
    filename: Path = Path("(none)")
    errors: list[Error] = field(default_factory=list)
    # Mapping of all private TypeVars/ParamSpecs/TypeVarTuples to the nodes where they're defined
    typevarlike_defs: dict[TypeVarInfo, ast.Assign] = field(default_factory=dict)
    # Mapping of each name in the file to the no. of occurrences
    all_name_occurrences: Counter[str] = field(default_factory=Counter)
    _class_nesting: int = 0
    _function_nesting: int = 0
    _allow_string_literals: int = 0

    @contextmanager
    def allow_string_literals(self) -> Iterator[None]:
        """Context manager that indicates that string literals should be allowed."""
        self._allow_string_literals += 1
        try:
            yield
        finally:
            self._allow_string_literals -= 1

    @property
    def string_literals_allowed(self) -> bool:
        """Determine whether string literals should currently be allowed."""
        return bool(self._allow_string_literals)

    @property
    def in_function(self) -> bool:
        """Determine whether we are inside a `def` statement"""
        return bool(self._function_nesting)

    @property
    def in_class(self) -> bool:
        """Determine whether we are inside a `class` statement"""
        return bool(self._class_nesting)

    def _check_import_or_attribute(
        self, node: ast.Attribute | ast.ImportFrom, module_name: str, object_name: str
    ) -> None:
        fullname = f"{module_name}.{object_name}"

        # Y022 errors
        if fullname in _BAD_Y022_IMPORTS:
            error_message = Y022.format(
                good_cls_name=f'"{_BAD_Y022_IMPORTS[fullname]}"',
                bad_cls_alias=fullname,
            )

        # Y027 errors
        elif fullname in _BAD_Y027_IMPORTS:
            error_message = Y027.format(
                good_cls_name=f'"{_BAD_Y027_IMPORTS[fullname]}"',
                bad_cls_alias=fullname,
            )

        # Y023 errors
        elif module_name == "typing_extensions":
            if object_name in _BAD_Y023_IMPORTS:
                error_message = Y023.format(
                    good_cls_name=f'"typing.{object_name}"',
                    bad_cls_alias=f"typing_extensions.{object_name}",
                )
            elif object_name == "ContextManager":
                suggested_syntax = (
                    '"contextlib.AbstractContextManager" '
                    '(or "typing.ContextManager" in Python 2-compatible code)'
                )
                error_message = Y023.format(
                    good_cls_name=suggested_syntax,
                    bad_cls_alias="typing_extensions.ContextManager",
                )
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

    def visit_Assign(self, node: ast.Assign) -> None:
        if self.in_function:
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
        if target_name == "__all__":
            with self.allow_string_literals():
                self.generic_visit(node)
        else:
            self.generic_visit(node)
        if target_name is None:
            return
        assignment = node.value
        # Attempt to find assignments to type helpers (typevars and aliases),
        # which should usually be private. If they are private,
        # they should be used at least once in the file in which they are defined.
        if isinstance(assignment, ast.Call) and isinstance(assignment.func, ast.Name):
            cls_name = assignment.func.id
            if cls_name in ("TypeVar", "ParamSpec", "TypeVarTuple"):
                if target_name.startswith("_"):
                    target_info = TypeVarInfo(cls_name=cls_name, name=target_name)
                    self.typevarlike_defs[target_info] = node
                else:
                    self.error(target, Y001.format(cls_name))
        if isinstance(node.value, (ast.Num, ast.Str, ast.Bytes)):
            self.error(node.value, Y015)
        # We avoid triggering Y026 for calls and = ... because there are various
        # unusual cases where assignment to the result of a call is legitimate
        # in stubs.
        elif target_name != "__all__" and not isinstance(
            node.value, (ast.Ellipsis, ast.Call)
        ):
            self.error(node, Y026)

    def visit_Name(self, node: ast.Name) -> None:
        self.all_name_occurrences[node.id] += 1

    def visit_Call(self, node: ast.Call) -> None:
        function = node.func
        self.visit(function)
        if isinstance(function, ast.Name):
            if function.id == "NamedTuple":
                return self.error(node, Y028)
        elif isinstance(function, ast.Attribute):
            if (
                isinstance(function.value, ast.Name)
                and function.value.id == "typing"
                and function.attr == "NamedTuple"
            ):
                return self.error(node, Y028)

        # String literals can appear in positional arguments for
        # TypeVar definitions.
        with self.allow_string_literals():
            for arg in node.args:
                self.visit(arg)
        # But in keyword arguments they're most likely TypeVar bounds,
        # which should not be quoted.
        for kw in node.keywords:
            self.visit(kw)

    # 3.8+
    def visit_Constant(self, node: ast.Constant) -> None:
        if not self.string_literals_allowed and isinstance(node.value, str):
            self.error(node, Y020)

    # 3.7 and lower
    def visit_Str(self, node: ast.Str) -> None:
        if not self.string_literals_allowed:
            self.error(node, Y020)

    def visit_Expr(self, node: ast.Expr) -> None:
        if isinstance(node.value, ast.Str):
            self.error(node, Y021)
        else:
            self.generic_visit(node)

    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
        self.generic_visit(node)
        if isinstance(node.annotation, ast.Name) and node.annotation.id == "TypeAlias":
            return
        if node.value and not isinstance(node.value, ast.Ellipsis):
            self.error(node.value, Y015)

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
            if (
                isinstance(member, ast.Subscript)
                and isinstance(member.value, ast.Name)
                and member.value.id == "Literal"
            ):
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
        if isinstance(node.value, ast.Name):
            value_id = node.value.id
        else:
            value_id = None

        self.visit(node.value)
        if value_id == "Literal":
            with self.allow_string_literals():
                self.visit(node.slice)
            return

        if isinstance(node.slice, ast.Tuple):
            self._visit_slice_tuple(node.slice, value_id)
        else:
            self.visit(node.slice)

    def _visit_slice_tuple(self, node: ast.Tuple, parent: str | None) -> None:
        if parent == "Union":
            self._check_union_members(node.elts)
        elif parent == "Annotated":
            # Allow literals, except in the first argument
            if len(node.elts) > 1:
                self.visit(node.elts[0])
                with self.allow_string_literals():
                    for elt in node.elts[1:]:
                        self.visit(elt)
            else:
                self.visit(node)
        else:
            self.visit(node)

    def visit_If(self, node: ast.If) -> None:
        # No types can appear in if conditions, so avoid confusing additional errors.
        with self.allow_string_literals():
            self.generic_visit(node)
        test = node.test
        if isinstance(test, ast.BoolOp):
            for expression in test.values:
                self._check_if_expression(expression)
        else:
            self._check_if_expression(test)

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
            if isinstance(node.left.value, ast.Name) and node.left.value.id == "sys":
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
        self._class_nesting += 1
        self.generic_visit(node)
        self._class_nesting -= 1

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

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        # Raise an error for defining __str__ or __repr__ on a class, but only if:
        # 1). The method is not decorated with @abstractmethod
        # 2). The method has the exact same signature as object.__str__/object.__repr__
        if (
            self.in_class
            and node.name in {"__repr__", "__str__"}
            and isinstance(node.returns, ast.Name)
            and node.returns.id == "str"
            and not any(
                isinstance(deco, ast.Name) and deco.id == "abstractmethod"
                for deco in node.decorator_list
            )
        ):
            all_args = node.args
            # pos-only args don't exist on 3.7
            pos_only_args: list[ast.arg] = getattr(all_args, "posonlyargs", [])
            pos_or_kwd_args = all_args.args
            kwd_only_args = all_args.kwonlyargs

            if ((len(pos_only_args) + len(pos_or_kwd_args)) == 1) and not kwd_only_args:
                self.error(node, Y029)

        self._visit_function(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self._visit_function(node)

    def _Y019_error(
        self, node: ast.FunctionDef | ast.AsyncFunctionDef, typevar_name: str
    ) -> None:
        cleaned_method = deepcopy(node)
        cleaned_method.decorator_list.clear()
        new_syntax = unparse(cleaned_method)
        new_syntax = re.sub(fr"\b{typevar_name}\b", "Self", new_syntax)
        new_syntax = re.sub(r"\s+", " ", new_syntax).strip()

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

        if not isinstance(first_arg_annotation.value, ast.Name):
            return
        if first_arg_annotation.value.id != "type":
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
        self._function_nesting += 1
        self.generic_visit(node)
        self._function_nesting -= 1

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

        if self.in_class:
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


@dataclass
class PyiTreeChecker:
    name: ClassVar[str] = "flake8-pyi"
    version: ClassVar[str] = __version__

    tree: ast.Module | None = None
    filename: str = "(none)"
    options: argparse.Namespace | None = None

    def run(self):
        path = Path(self.filename)
        if path.suffix == ".pyi":
            visitor = PyiVisitor(filename=path)
            for error in visitor.run(LegacyNormalizer().visit(self.tree)):
                yield error

    @classmethod
    def add_options(cls, parser):
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
    def parse_options(cls, optmanager, options, extra_args):
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
Y015 = 'Y015 Attribute must not have a default value other than "..."'
Y016 = 'Y016 Duplicate union member "{}"'
Y017 = "Y017 Only simple assignments allowed"
Y018 = 'Y018 {typevarlike_cls} "{typevar_name}" is not used'
Y019 = 'Y019 Use "_typeshed.Self" instead of "{typevar_name}", e.g. "{new_syntax}"'
Y020 = "Y020 Quoted annotations should never be used in stubs"
Y021 = "Y021 Docstrings should not be included in stubs"
Y022 = 'Y022 Use {good_cls_name} instead of "{bad_cls_alias}"'
Y023 = 'Y023 Use {good_cls_name} instead of "{bad_cls_alias}"'
Y024 = 'Y024 Use "typing.NamedTuple" instead of "collections.namedtuple"'
Y025 = (
    'Y025 Use "from collections.abc import Set as AbstractSet" '
    'to avoid confusion with "builtins.set"'
)
Y026 = "Y026 Use typing_extensions.TypeAlias for type aliases"
Y027 = 'Y027 Use {good_cls_name} instead of "{bad_cls_alias}"'
Y028 = "Y028 Use class-based syntax for NamedTuples"
Y029 = "Y029 Defining __repr__ or __str__ in a stub is almost always redundant"
Y030 = "Y030 Multiple Literal members in a union. {suggestion}"
