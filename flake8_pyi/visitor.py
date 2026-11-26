#!/usr/bin/env python3
from __future__ import annotations

import ast
import re
import sys
import types
from collections import Counter, defaultdict
from collections.abc import Container, Iterator, Sequence, Set as AbstractSet
from contextlib import contextmanager
from copy import deepcopy
from dataclasses import dataclass
from functools import cached_property
from itertools import chain, zip_longest
from typing import Literal, NamedTuple, Protocol, TypeAlias

from . import checker, errors
from .ast_helpers import (
    all_equal,
    analyse_exit_method_arg,
    check_import_or_attribute,
    get_name_of_class_if_from_modules,
    is_name,
    is_None,
    is_object,
    is_type_or_Type,
    is_valid_default_value_without_annotation,
    is_valid_pep_604_union,
    unparse_func_node,
)
from .constants import (
    COMMON_METACLASSES,
    INPLACE_BINOP_METHODS,
    TYPING_MODULES,
    TYPING_OR_COLLECTIONS_ABC,
)
from .errors import Error
from .predicates import (
    UnionAnalysis,
    analyse_typing_Literal,
    analyse_union,
    is_abstractmethod,
    is_Any,
    is_assignment_which_must_have_a_value,
    is_AsyncGenerator,
    is_AsyncIterable,
    is_bad_TypedDict,
    is_BaseException,
    is_builtins_object,
    is_deprecated,
    is_final,
    is_Final,
    is_Generator,
    is_Generic,
    is_Incomplete,
    is_IncompleteOrNone,
    is_Iterable,
    is_Literal,
    is_NamedTuple,
    is_object_or_Unused,
    is_overload,
    is_override,
    is_Self,
    is_TracebackType,
    is_TypeAlias,
    is_TypedDict,
    is_Unpack,
    is_valid_default_value_with_annotation,
)

if sys.version_info >= (3, 12):
    _TypeAliasNodeType: TypeAlias = ast.TypeAlias | ast.AnnAssign
else:
    _TypeAliasNodeType: TypeAlias = ast.AnnAssign


class TypeVarInfo(NamedTuple):
    cls_name: str
    name: str


class NodeWithLocation(Protocol):
    lineno: int
    col_offset: int


def _has_bad_hardcoded_returns(
    method: ast.FunctionDef | ast.AsyncFunctionDef, *, class_ctx: EnclosingClassContext
) -> bool:
    """Return `True` if `function` should be rewritten with `typing_extensions.Self`."""
    # PEP 673 forbids the use of `typing(_extensions).Self` in metaclasses.
    # Do our best to avoid false positives here:
    if class_ctx.is_metaclass:
        return False

    # Return false if in a protocol (class inheriting from typing.Protocol); see #539
    if class_ctx.is_protocol_class:
        return False

    # Much too complex for our purposes to worry
    # about overloaded functions or abstractmethods
    if any(
        is_overload(deco) or is_abstractmethod(deco) for deco in method.decorator_list
    ):
        return False

    # weird, but theoretically possible
    if not method.args.posonlyargs and not method.args.args:
        return False

    method_name, returns = method.name, method.returns

    if isinstance(method, ast.AsyncFunctionDef):
        return (
            method_name == "__aenter__"
            and is_name(returns, class_ctx.cls_name)
            and not class_ctx.is_decorated_with_final
        )

    if method_name in INPLACE_BINOP_METHODS:
        return returns is not None and not is_Self(returns)

    if is_name(returns, class_ctx.cls_name):
        return (
            method_name in {"__enter__", "__new__"}
            and not class_ctx.is_decorated_with_final
        )

    if isinstance(returns, ast.Subscript):
        return_obj_name = get_name_of_class_if_from_modules(
            returns.value, modules=TYPING_OR_COLLECTIONS_ABC
        )
        if method_name == "__iter__":
            bad_returns = {"Iterable", "Iterator"}
            return return_obj_name in bad_returns and class_ctx.contains_in_bases(
                "Iterator", from_=TYPING_OR_COLLECTIONS_ABC
            )
        elif method_name == "__aiter__":
            bad_returns = {"AsyncIterable", "AsyncIterator"}
            return return_obj_name in bad_returns and class_ctx.contains_in_bases(
                "AsyncIterator", from_=TYPING_OR_COLLECTIONS_ABC
            )

    return False


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
        return self.contains_in_bases("Protocol", from_=TYPING_MODULES)

    @cached_property
    def is_typeddict_class(self) -> bool:
        return self.contains_in_bases(
            "TypedDict", from_=(TYPING_MODULES | {"mypy_extensions"})
        )

    @cached_property
    def is_enum_class(self) -> bool:
        return any(base_name.endswith(("Enum", "Flag")) for base_name in self.bases_map)

    @cached_property
    def is_metaclass(self) -> bool:
        return any(
            self.contains_in_bases(metacls, from_={module})
            for metacls, module in COMMON_METACLASSES.items()
        )

    @cached_property
    def is_decorated_with_final(self) -> bool:
        return any(is_final(decorator) for decorator in self.node.decorator_list)


class ClassBase(NamedTuple):
    module: str | None
    obj: str


def _analyze_classdef(node: ast.ClassDef) -> EnclosingClassContext:
    bases_map: defaultdict[str, set[str | None]] = defaultdict(set)

    def _unravel(node: ast.expr) -> str | None:
        match node:
            case ast.Name(id):
                return id
            case ast.Attribute(value=value, attr=attr):
                value_str = _unravel(value)
                if value_str is None:
                    return None
                return f"{value_str}.{attr}"
            case _:
                return None

    def _analyze_base_node(
        base_node: ast.expr, top_level: bool = True
    ) -> ClassBase | None:
        match base_node:
            case ast.Name(id):
                return ClassBase(None, id)
            case ast.Attribute(value=value, attr=attr):
                unravelled = _unravel(value)
                if unravelled is None:
                    return None
                return ClassBase(unravelled, attr)
            case ast.Subscript() if top_level:
                return _analyze_base_node(base_node.value, top_level=False)
            case _:
                return None

    for base_node in node.bases:
        base = _analyze_base_node(base_node)
        if base is None:
            continue
        bases_map[base.obj].add(base.module)

    return EnclosingClassContext(node=node, cls_name=node.name, bases_map=bases_map)


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
        if error_msg := check_import_or_attribute(
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
                self.error(node, errors.Y044)
            return

        if (
            module_name == "collections.abc"
            and "Set" in imported_names
            and imported_names["Set"].asname != "AbstractSet"
        ):
            self.error(node, errors.Y025)

        for object_name in imported_names:
            if error_msg := check_import_or_attribute(node, module_name, object_name):
                self.error(node, error_msg)

        if module_name in TYPING_MODULES and "AbstractSet" in imported_names:
            self.error(node, errors.Y038.format(module=module_name))

    def _check_for_typevarlike_assignments(
        self, node: ast.Assign, function: ast.expr, object_name: str
    ) -> None:
        """Attempt to find assignments to TypeVar-like objects.

        TypeVars should usually be private.
        If they are private, they should be used at least once
        in the file in which they are defined.
        """
        cls_name = get_name_of_class_if_from_modules(function, modules=TYPING_MODULES)

        if cls_name in {"TypeVar", "ParamSpec", "TypeVarTuple"}:
            if object_name.startswith("_"):
                target_info = TypeVarInfo(cls_name=cls_name, name=object_name)
                self.typevarlike_defs[target_info].append(node)
            else:
                self.error(node, errors.Y001.format(cls_name))

    def _check_default_value_without_type_annotation(
        self, node: ast.Assign, assignment: ast.expr, target_name: str
    ) -> None:
        if is_valid_default_value_without_annotation(assignment):
            return
        if is_valid_default_value_with_annotation(assignment):
            # Annoying special-casing to exclude enums from Y052
            if not self.visiting_enum_class:
                self.error(node, errors.Y052.format(variable=target_name))
        else:
            self.error(node, errors.Y015)

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
                self.error(node, errors.Y017)
                target_name = None
        else:
            self.error(node, errors.Y017)
            target = target_name = None
        is_special_assignment = is_assignment_which_must_have_a_value(
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
            if is_TypedDict(function):
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
        if is_name(target, "__all__") and isinstance(node.op, ast.Add):
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
            or is_valid_pep_604_union(assignment)
            or is_Any(assignment)
            or (is_None(assignment) and not self.visiting_enum_class)
        ):
            new_node = ast.AnnAssign(
                target=target,
                annotation=ast.Name(id="TypeAlias", ctx=ast.Load()),
                value=assignment,
                simple=1,
            )
            self.error(node, errors.Y026.format(suggestion=ast.unparse(new_node)))

    def visit_Name(self, node: ast.Name) -> None:
        self.generic_visit(node)
        self.all_name_occurrences[node.id] += 1

    def visit_Call(self, node: ast.Call) -> None:
        function = node.func
        self.visit(function)

        if is_NamedTuple(function):
            return self.error(node, errors.Y028)
        elif is_TypedDict(function):
            if is_bad_TypedDict(node):
                self.error(node, errors.Y031)
            return
        elif is_deprecated(function):
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
            return self.error(node, errors.Y056.format(method=f".{function.attr}()"))

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
        match node.value:
            case str() if not self.string_literals_allowed.active:
                self.error(node, errors.Y020)
            case str() | bytes() if not self.long_strings_allowed.active:
                if len(node.value) > 50:
                    self.error(node, errors.Y053)
            case int() | float() | complex():
                if len(str(node.value)) > 10:
                    # The maximum character limit is arbitrary, but here's what it's based on:
                    # Hex representation of 32-bit integers tend to be 10 chars.
                    # So is the decimal representation
                    # of the maximum positive signed 32-bit integer.
                    # 0xFFFFFFFF --> 4294967295
                    self.error(node, errors.Y054)

    def visit_Expr(self, node: ast.Expr) -> None:
        if isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
            self.error(node, errors.Y021)
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
            self.error(node, errors.Y042)
        if self._Y043_REGEX.match(alias_name):
            self.error(node, errors.Y043)

    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
        node_annotation = node.annotation
        node_target = node.target
        node_value = node.value

        is_special_assignment = isinstance(
            node_target, ast.Name
        ) and is_assignment_which_must_have_a_value(
            node_target.id, in_class=self.enclosing_class_ctx is not None
        )

        is_typealias = is_TypeAlias(node_annotation) and isinstance(
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
                self.error(node, errors.Y035.format(var=node_target.id))
            return

        if is_typealias:
            assert isinstance(node_target, ast.Name)
            self._check_typealias(node=node, alias_name=node_target.id)
            # Don't bother checking whether
            # nodes marked as TypeAliases have valid assignment values.
            # Type checkers will emit errors for those.
            return

        if is_Final(node_annotation) and isinstance(
            node_value, (ast.Attribute, ast.Name)
        ):
            return

        if node_value and not is_valid_default_value_with_annotation(node_value):
            self.error(node, errors.Y015)

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
            is_Final(value)
            and isinstance(slice_, ast.Subscript)
            and is_Literal(slice_.value)
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
                errors.Y064.format(
                    suggestion=ast.unparse(suggestion), original=ast.unparse(node)
                ),
            )
            return True
        return False

    def _check_union_members(
        self, members: Sequence[ast.expr], is_pep_604_union: bool
    ) -> None:
        first_union_member = members[0]
        analysis = analyse_union(members)

        for member_list in analysis.members_by_dump.values():
            if len(member_list) >= 2:
                self.error(
                    member_list[1], errors.Y016.format(ast.unparse(member_list[1]))
                )

        if not analysis.dupes_in_union:
            self._check_for_Y051_violations(analysis)
            if analysis.multiple_literals_in_union:
                self._error_for_multiple_literals_in_union(first_union_member, analysis)
            elif analysis.multiple_type_subscripts_in_union:
                self._error_for_multiple_type_subscripts_in_union(
                    first_union_member, analysis, is_pep_604_union
                )

    def _check_for_Y051_violations(self, analysis: UnionAnalysis) -> None:
        """Search for redundant unions such as `str | Literal["foo"]`, etc."""
        seen_builtins: set[type[object]] = set()
        for literal in analysis.combined_literal_members:
            match literal:
                case ast.Constant(value):
                    typ = type(value)
                # Negative integers such as `-1` are parsed as unary operations
                case ast.UnaryOp(op=ast.USub(), operand=ast.Constant(value=int())):
                    typ = int
                case _:
                    continue
            typename = typ.__name__
            if (
                typ in {str, bytes, int, bool}
                and typename in analysis.builtins_classes_in_union
                and typ not in seen_builtins
            ):
                seen_builtins.add(typ)
                self.error(
                    literal,
                    errors.Y051.format(
                        literal_subtype=f"Literal[{ast.unparse(literal)}]",
                        builtin_supertype=typename,
                    ),
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

        self.error(first_union_member, errors.Y030.format(suggestion=suggestion))

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
        self.error(first_union_member, errors.Y055.format(suggestion=suggestion))

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
        self.error(
            node, errors.Y090.format(original=current_code, typ=typ, new=suggestion)
        )

    def visit_Subscript(self, node: ast.Subscript) -> None:
        subscripted_object = node.value
        subscripted_object_name = get_name_of_class_if_from_modules(
            subscripted_object, modules=TYPING_MODULES | {"builtins"}
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
                isinstance(node.slice, ast.Subscript) and is_Unpack(node.slice.value)
            ):
                self._Y090_error(node)

    def _visit_typing_Literal(self, node: ast.Subscript) -> None:
        analysis = analyse_typing_Literal(node)

        Y062_encountered = False
        for member_list in analysis.members_by_dump.values():
            if len(member_list) > 1 and not is_None(member_list[0]):
                Y062_encountered = True
                self.error(
                    member_list[1], errors.Y062.format(ast.unparse(member_list[1]))
                )

        if not Y062_encountered and not self.Y061_suppressed.active:
            if analysis.contains_only_none:
                self.error(node.slice, errors.Y061.format(suggestion="None"))
            elif analysis.none_members:
                if len(analysis.members_without_none) == 1:
                    new_literal_slice = ast.unparse(analysis.members_without_none[0])
                else:
                    new_slice_node = ast.Tuple(elts=analysis.members_without_none)
                    new_literal_slice = ast.unparse(new_slice_node).strip("()")
                suggestion = f"Literal[{new_literal_slice}] | None"
                self.error(
                    analysis.none_members[0], errors.Y061.format(suggestion=suggestion)
                )

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
        self._check_if_expression(test)
        for line in chain(node.body, node.orelse):
            self.visit(line)

    def _check_if_expression(self, node: ast.expr) -> None:
        if isinstance(node, ast.BoolOp):
            # Type checkers understand (nested) `and`/`or` combinations of
            # supported comparisons, e.g. `if A and (B or C)`.
            for expression in node.values:
                self._check_if_expression(expression)
            return
        if not isinstance(node, ast.Compare):
            self.error(node, errors.Y002)
            return
        if len(node.comparators) != 1:
            # mypy doesn't support chained comparisons
            self.error(node, errors.Y002)
            return

        match node.left:
            case ast.Subscript():
                self._check_subscript_version_check(node)
            case ast.Attribute(value=ast.Name("sys"), attr="platform"):
                self._check_platform_check(node)
            case ast.Attribute(value=ast.Name("sys"), attr="version_info"):
                self._check_version_check(node)
            case _:
                self.error(node, errors.Y002)

    def _check_for_Y066_violations(self, node: ast.If) -> None:
        def is_version_info(attr: ast.expr) -> bool:
            return (
                isinstance(attr, ast.Attribute)
                and is_name(attr.value, "sys")
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
            self.error(node, errors.Y066.format(new_syntax=new_syntax))

    def _check_subscript_version_check(self, node: ast.Compare) -> None:
        # unless this is on, comparisons against a single integer aren't allowed
        must_be_single = False
        # if strict equality is allowed, it must be against a tuple of this length
        can_have_strict_equals: int | None = None
        version_info = node.left
        if isinstance(version_info, ast.Subscript):
            match version_info.slice:
                case ast.Constant(value):
                    # anything other than the integer 0 doesn't make much sense
                    if type(value) is int and value == 0:
                        must_be_single = True
                    else:
                        self.error(node, errors.Y003)
                        return
                case ast.Slice(
                    lower=None, upper=ast.Constant(value), step=None
                ) if type(value) is int and value in {1, 2}:
                    can_have_strict_equals = value
                case _:
                    self.error(node, errors.Y003)
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
                self.error(node, errors.Y003)
        elif not isinstance(comparator, ast.Tuple):
            self.error(node, errors.Y003)
        else:
            if not all(
                isinstance(elt, ast.Constant) and type(elt.value) is int
                for elt in comparator.elts
            ):
                self.error(node, errors.Y003)
            elif len(comparator.elts) > 2:
                # mypy only supports major and minor version checks
                self.error(node, errors.Y004)

            match node.ops[0]:
                case ast.Lt() | ast.GtE():
                    pass
                case ast.Eq() | ast.NotEq() if can_have_strict_equals is not None:
                    if len(comparator.elts) != can_have_strict_equals:
                        self.error(node, errors.Y005.format(n=can_have_strict_equals))
                case _:
                    self.error(node, errors.Y006)

    def _check_platform_check(self, node: ast.Compare) -> None:
        match node:
            case ast.Compare(
                comparators=[ast.Constant(value), *_], ops=[ast.Eq() | ast.NotEq(), *_]
            ) if (type(value) is str):
                if value not in {"linux", "win32", "cygwin", "darwin"}:
                    self.error(node, errors.Y008.format(platform=value))
            case _:
                self.error(node, errors.Y007)

    def _check_class_bases(self, bases: list[ast.expr]) -> None:
        Y040_encountered = False
        Y059_encountered = False
        Generic_basenode: ast.Subscript | None = None
        subscript_bases: list[ast.Subscript] = []
        num_bases = len(bases)

        for i, base_node in enumerate(bases, start=1):
            if not Y040_encountered and is_builtins_object(base_node):
                self.error(base_node, errors.Y040)
                Y040_encountered = True
            if isinstance(base_node, ast.Subscript):
                subscript_bases.append(base_node)
                if is_Generic(base_node.value):
                    Generic_basenode = base_node
                    if i < num_bases and not Y059_encountered:
                        Y059_encountered = True
                        self.error(base_node, errors.Y059)

        if Generic_basenode is not None:
            assert subscript_bases
            if len(subscript_bases) > 1 and all_equal(
                ast.dump(subscript_base.slice) for subscript_base in subscript_bases
            ):
                msg = errors.Y060.format(redundant_base=ast.unparse(Generic_basenode))
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
        self.check_class_pass_and_ellipsis(node)

    def check_class_pass_and_ellipsis(self, node: ast.ClassDef) -> None:
        # empty class body should contain "..." not "pass"
        match node.body:
            case [ast.Expr(value=ast.Constant(value=types.EllipsisType()))]:
                return
            case [ast.Pass()]:
                self.error(node.body[0], errors.Y009)
                return
            case _:
                pass

        for statement in node.body:
            match statement:
                case ast.Pass():
                    # "pass" should not used in class body
                    self.error(statement, errors.Y012)
                case ast.Expr(value=ast.Constant(value)) if value is ...:
                    # "..." should not be used in non-empty class body
                    self.error(statement, errors.Y013)

    def _check_exit_method(  # noqa: C901
        self, node: ast.FunctionDef | ast.AsyncFunctionDef, method_name: str
    ) -> None:
        all_args = node.args
        non_kw_only_args = all_args.posonlyargs + all_args.args
        num_args = len(non_kw_only_args)
        varargs = all_args.vararg

        def error_for_bad_exit_method(details: str) -> None:
            self.error(
                node, errors.Y036.format(method_name=method_name, details=details)
            )

        if num_args < 4:
            if varargs:
                varargs_annotation = varargs.annotation
                if not (
                    varargs_annotation is None
                    or is_object_or_Unused(varargs_annotation)
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
            if arg1_annotation is None or is_object_or_Unused(arg1_annotation):
                pass
            elif is_valid_pep_604_union(arg1_annotation):
                is_union_with_None, non_None_part = analyse_exit_method_arg(
                    arg1_annotation
                )
                if not (
                    is_union_with_None
                    and isinstance(non_None_part, ast.Subscript)
                    and is_type_or_Type(non_None_part.value)
                    and is_BaseException(non_None_part.slice)
                ):
                    error_for_bad_annotation(arg1_annotation, arg_number=1)
            else:
                error_for_bad_annotation(arg1_annotation, arg_number=1)

        if num_args >= 3:
            arg2_annotation = non_kw_only_args[2].annotation
            if arg2_annotation is None or is_object_or_Unused(arg2_annotation):
                pass
            elif is_valid_pep_604_union(arg2_annotation):
                is_union_with_None, non_None_part = analyse_exit_method_arg(
                    arg2_annotation
                )
                if not (is_union_with_None and is_BaseException(non_None_part)):
                    error_for_bad_annotation(arg2_annotation, arg_number=2)
            else:
                error_for_bad_annotation(arg2_annotation, arg_number=2)

        if num_args >= 4:
            arg3_annotation = non_kw_only_args[3].annotation
            if arg3_annotation is None or is_object_or_Unused(arg3_annotation):
                pass
            elif is_valid_pep_604_union(arg3_annotation):
                is_union_with_None, non_None_part = analyse_exit_method_arg(
                    arg3_annotation
                )
                if not (is_union_with_None and is_TracebackType(non_None_part)):
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
        error_message = errors.Y034.format(
            methods=referrer,
            method_name=f"{cls_name}.{method_name}",
            suggested_syntax=unparse_func_node(copied_node),
        )
        self.error(node, error_message)

    def _Y058_error(
        self, node: ast.FunctionDef, args: list[ast.arg], example_returns: str
    ) -> None:
        assert node.name in {"__iter__", "__aiter__"}
        good_cls = "Iterator" if node.name == "__iter__" else "AsyncIterator"
        example = f"def {node.name}({args[0].arg}) -> {example_returns}: ..."
        msg = errors.Y058.format(
            iter_method=node.name, good_cls=good_cls, example=example
        )
        self.error(node, msg)

    def _check_iter_returns(
        self, node: ast.FunctionDef, returns: ast.expr | None
    ) -> None:
        if is_Iterable(returns) or (
            isinstance(returns, ast.Subscript) and is_Iterable(returns.value)
        ):
            msg = errors.Y045.format(
                iter_method="__iter__", good_cls="Iterator", bad_cls="Iterable"
            )
            self.error(node, msg)
            return
        non_kw_only_args = node.args.posonlyargs + node.args.args
        if len(non_kw_only_args) == 1 and not node.args.kwonlyargs:
            if is_Generator(returns):
                self._Y058_error(node, non_kw_only_args, "Iterator")
            elif (
                isinstance(returns, ast.Subscript)
                and is_Generator(returns.value)
                and isinstance(returns.slice, ast.Tuple)
            ):
                elts = returns.slice.elts
                if (
                    len(elts) == 3
                    and (is_Any(elts[1]) or is_None(elts[1]))
                    and (is_Any(elts[2]) or is_None(elts[2]))
                ):
                    example_returns = f"Iterator[{ast.unparse(returns.slice.elts[0])}]"
                    self._Y058_error(node, non_kw_only_args, example_returns)

    def _check_aiter_returns(
        self, node: ast.FunctionDef, returns: ast.expr | None
    ) -> None:
        if is_AsyncIterable(returns) or (
            isinstance(returns, ast.Subscript) and is_AsyncIterable(returns.value)
        ):
            msg = errors.Y045.format(
                iter_method="__aiter__",
                good_cls="AsyncIterator",
                bad_cls="AsyncIterable",
            )
            self.error(node, msg)
            return
        non_kw_only_args = node.args.posonlyargs + node.args.args
        if len(non_kw_only_args) == 1 and not node.args.kwonlyargs:
            if is_AsyncGenerator(returns):
                self._Y058_error(node, non_kw_only_args, "AsyncIterator")
            elif (
                isinstance(returns, ast.Subscript)
                and is_AsyncGenerator(returns.value)
                and isinstance(returns.slice, ast.Tuple)
            ):
                elts = returns.slice.elts
                if len(elts) == 2 and (is_Any(elts[1]) or is_None(elts[1])):
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
                and is_object(returns, "str", from_={"builtins"})
                and not any(is_abstractmethod(deco) for deco in node.decorator_list)
            ):
                self.error(node, errors.Y029)

        elif method_name in {"__eq__", "__ne__"}:
            if len(non_kw_only_args) == 2 and is_Any(non_kw_only_args[1].annotation):
                self.error(node, errors.Y032.format(method_name=method_name))

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
        new_syntax = unparse_func_node(cleaned_method)
        new_syntax = re.sub(rf"\b{typevar_name}\b", "Self", new_syntax)
        self.error(
            node, errors.Y019.format(typevar_name=typevar_name, new_syntax=new_syntax)
        )

    @staticmethod
    def is_likely_private_typevar(
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

        if self.is_likely_private_typevar(method, arg1_annotation_name):
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
        if not is_name(first_arg_annotation.value, "type"):
            return

        if cls_typevar == return_annotation.id and self.is_likely_private_typevar(
            method, cls_typevar
        ):
            self._Y019_error(method, cls_typevar)

    def check_self_typevars(
        self,
        node: ast.FunctionDef | ast.AsyncFunctionDef,
        decorator_names: Container[str],
    ) -> None:
        pos_or_keyword_args = node.args.posonlyargs + node.args.args

        if not pos_or_keyword_args:
            return
        return_annotation = node.returns

        if not isinstance(return_annotation, ast.Name):
            return
        first_arg_annotation = pos_or_keyword_args[0].annotation

        if not isinstance(first_arg_annotation, (ast.Name, ast.Subscript)):
            return

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

    def check_protocol_param_kinds(
        self,
        node: ast.FunctionDef | ast.AsyncFunctionDef,
        decorator_names: Container[str],
    ) -> None:
        if "staticmethod" in decorator_names:
            relevant_params = node.args.args
        else:
            relevant_params = node.args.args[1:]  # exclude "self"
        for pos_or_kw in relevant_params:
            if pos_or_kw.arg.startswith("__"):
                continue
            self.error(
                pos_or_kw, errors.Y091.format(arg=pos_or_kw.arg, method=node.name)
            )

    def check_for_override(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> None:
        for deco in node.decorator_list:
            if is_override(deco):
                self.error(deco, errors.Y068)
                return

    @staticmethod
    def is_positional_pre_570_argname(name: str) -> bool:
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
            uses_old_syntax = self.is_positional_pre_570_argname(first_param.arg)
        else:
            uses_old_syntax = self.is_positional_pre_570_argname(first_param.arg) or (
                len(pos_or_kw_args) >= 2
                and self.is_positional_pre_570_argname(pos_or_kw_args[1].arg)
            )
        if uses_old_syntax:
            self.error(node, errors.Y063)

    def _visit_function(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> None:
        with self.in_function.enabled():
            self.generic_visit(node)

        if node.name != "__getattr__" and node.returns and is_Incomplete(node.returns):
            self.error(node.returns, errors.Y065.format(what="return type"))

        match node.body:
            case [_, stm2t2, *_]:
                self.error(stm2t2, errors.Y048)
            # normally, should just be "..."
            case [ast.Pass()]:
                self.error(node.body[0], errors.Y009)
            # ... is fine. Docstrings are not but we produce
            # tailored error message for them elsewhere.
            case [ast.Expr(value=ast.Constant(value=str() | types.EllipsisType()))]:
                pass
            case [statement]:
                self.error(statement, errors.Y010)

        self._check_pep570_syntax_used_where_applicable(node)
        if self.enclosing_class_ctx is not None:
            decorator_names = {
                decorator.id
                for decorator in node.decorator_list
                if isinstance(decorator, ast.Name)
            }
            self.check_self_typevars(node, decorator_names)
            if self.enclosing_class_ctx.is_protocol_class:
                self.check_protocol_param_kinds(node, decorator_names)
            self.check_for_override(node)

    def visit_arg(self, node: ast.arg) -> None:
        if is_Incomplete(node.annotation):
            self.error(node, errors.Y065.format(what=f'parameter "{node.arg}"'))
        with self.visiting_arg.enabled():
            self.generic_visit(node)

    def visit_arguments(self, node: ast.arguments) -> None:
        args = node.posonlyargs + node.args
        defaults = [None] * (len(args) - len(node.defaults)) + node.defaults
        for arg, default in zip(args, defaults, strict=True):
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
        if default is not None and not is_valid_default_value_with_annotation(default):
            self.error(
                default, (errors.Y014 if arg.annotation is None else errors.Y011)
            )
        if is_IncompleteOrNone(arg.annotation) and is_None(default):
            self.error(arg, errors.Y067)

    def error(self, node: NodeWithLocation, message: str) -> None:
        self.errors.append(
            Error(node.lineno, node.col_offset, message, checker.PyiTreeChecker)
        )

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
                msg = errors.Y018.format(
                    typevarlike_cls=cls_name, typevar_name=typevar_name
                )
                self.error(tv_nodelist[0], msg)
        for proto_name, proto_nodelist in self.protocol_defs.items():
            if self.all_name_occurrences[proto_name] == 0:
                self.error(
                    proto_nodelist[0], errors.Y046.format(protocol_name=proto_name)
                )
        for td_name, cls_td_nodelist in self.class_based_typeddicts.items():
            if self.all_name_occurrences[td_name] == 0:
                self.error(
                    cls_td_nodelist[0], errors.Y049.format(typeddict_name=td_name)
                )
        for td_name, ass_td_nodelist in self.assignment_based_typeddicts.items():
            if self.all_name_occurrences[td_name] == len(ass_td_nodelist):
                self.error(
                    ass_td_nodelist[0], errors.Y049.format(typeddict_name=td_name)
                )
        for alias_name, alias_nodelist in self.typealias_decls.items():
            if self.all_name_occurrences[alias_name] == len(alias_nodelist):
                self.error(alias_nodelist[0], errors.Y047.format(alias_name=alias_name))

    def run(self, tree: ast.AST) -> Iterator[Error]:
        self.visit(tree)
        self._check_for_unused_things()
        yield from self.errors
