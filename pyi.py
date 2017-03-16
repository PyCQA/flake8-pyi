#!/usr/bin/env python3
import logging

import ast
import attr
from flake8 import checker
from flake8.plugins.pyflakes import FlakesChecker
from pathlib import Path
from pyflakes.checker import PY2, ClassDefinition
from pyflakes.checker import ModuleScope, ClassScope, FunctionScope
from typing import Any, Iterable, NamedTuple, Optional, Type

__version__ = '17.1.0'

LOG = logging.getLogger('flake8.pyi')


Error = NamedTuple('Error', [
    ('lineno', int),
    ('col', int),
    ('message', str),
    ('type', Type[Any]),
])


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
        for deco in node.decorator_list:
            self.handleNode(deco, node)
        for baseNode in node.bases:
            self.deferHandleNode(baseNode, node)
        if not PY2:
            for keywordNode in node.keywords:
                self.deferHandleNode(keywordNode, node)
        self.pushScope(ClassScope)
        # doctest does not process doctest within a doctest
        # classes within classes are processed.
        if (self.withDoctest and
                not self._in_doctest() and
                not isinstance(self.scope, FunctionScope)):
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
        if self.filename.endswith('.pyi') and plugin['plugin'] == FlakesChecker:
            LOG.info(
                'Replacing FlakesChecker with PyiAwareFlakesChecker while '
                'checking %r',
                self.filename,
            )
            plugin = dict(plugin)
            plugin['plugin'] = PyiAwareFlakesChecker
        return super().run_check(plugin, **kwargs)


@attr.s
class PyiVisitor(ast.NodeVisitor):
    filename = attr.ib(default=Path('(none)'))
    errors = attr.ib(default=attr.Factory(list))

    def visit_Assign(self, node: ast.Assign) -> None:
        """Attempt to find assignments to type helpers (typevars and aliases), which should be
        private.
        """
        self.generic_visit(node)
        if isinstance(node.value, ast.Call) and isinstance(node.value.func, ast.Name) and \
                node.value.func.id == 'TypeVar':
            for target in node.targets:
                if isinstance(target, ast.Name) and not target.id.startswith('_'):
                    # avoid catching AnyStr in typing (the only library TypeVar so far)
                    if not self.filename.name == 'typing.pyi':
                        self.error(target, Y001)

    def visit_If(self, node: ast.If) -> None:
        self.generic_visit(node)
        test = node.test
        if isinstance(test, ast.BoolOp):
            for expr in test.values:
                self._check_if_expr(expr)
        else:
            self._check_if_expr(test)

    def _check_if_expr(self, node: ast.expr) -> None:
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
            if isinstance(node.left.value, ast.Name) and node.left.value.id == 'sys':
                if node.left.attr == 'platform':
                    self._check_platform_check(node)
                elif node.left.attr == 'version_info':
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
        can_have_strict_equals: Optional[int] = None
        version_info = node.left
        if isinstance(version_info, ast.Subscript):
            slc = version_info.slice
            if isinstance(slc, ast.Index):
                # anything other than the integer 0 doesn't make much sense
                # (things that are in 2.7 and 3.7 but not 3.6?)
                if isinstance(slc.value, ast.Num) and slc.value.n == 0:
                    must_be_single = True
                else:
                    self.error(node, Y003)
            elif isinstance(slc, ast.Slice):
                # allow only [:1] and [:2]
                if slc.lower is not None or slc.step is not None:
                    self.error(node, Y003)
                elif isinstance(slc.upper, ast.Num) and slc.upper.n in (1, 2):
                    can_have_strict_equals = slc.upper.n
                else:
                    self.error(node, Y003)
            else:
                # extended slicing
                self.error(node, Y003)
        self._check_version_check(node, must_be_single=must_be_single,
                                  can_have_strict_equals=can_have_strict_equals)

    def _check_version_check(self, node: ast.Compare, *,
                             must_be_single: bool = False,
                             can_have_strict_equals: Optional[int] = None) -> None:
        comparator = node.comparators[0]
        if must_be_single:
            if not isinstance(comparator, ast.Num) or not isinstance(comparator.n, int):
                self.error(node, Y003)
        else:
            if not isinstance(comparator, ast.Tuple):
                self.error(node, Y003)
            elif not all(isinstance(elt, ast.Num) for elt in comparator.elts):
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
        comparator = node.comparators[0]
        if isinstance(comparator, ast.Str):
            # other values are possible but we don't need them right now
            # this protects against typos
            if comparator.s not in ('linux', 'win32', 'cygwin', 'darwin'):
                self.error(node, Y008.format(platform=comparator.s))
        else:
            self.error(node, Y007)

    def error(self, node: ast.AST, message: str) -> None:
        self.errors.append(Error(
            node.lineno,
            node.col_offset,
            message,
            PyiTreeChecker
        ))

    def run(self, tree: ast.AST) -> Iterable[Error]:
        self.errors.clear()
        self.visit(tree)
        yield from self.errors


@attr.s
class PyiTreeChecker:
    name = 'flake8-pyi'
    version = __version__

    tree = attr.ib(default=None)
    filename = attr.ib(default='(none)')

    def run(self):
        path = Path(self.filename)
        if path.suffix == '.pyi':
            visitor = PyiVisitor(filename=path)
            yield from visitor.run(self.tree)

    @classmethod
    def add_options(cls, parser):
        """This is brittle, there's multiple levels of caching of defaults."""
        for option in parser.options:
            if option.long_option_name == '--filename':
                option.default = '*.py,*.pyi'
                option.option_kwargs['default'] = option.default
                option.to_optparse().default = option.default
                parser.parser.defaults[option.dest] = option.default

        parser.add_option(
            '--no-pyi-aware-file-checker', default=False, action='store_true',
            parse_from_config=True,
            help="don't patch flake8 with .pyi-aware file checker",
        )

    @classmethod
    def parse_options(cls, optmanager, options, extra_args):
        """This is also brittle, only checked with flake8 3.2.1 and master."""
        if not options.no_pyi_aware_file_checker:
            checker.FileChecker = PyiAwareFileChecker


Y001 = 'Y001 Name of private TypeVar must start with _'
Y002 = 'Y002 If test must be a simple comparison against sys.platform or sys.version_info'
Y003 = 'Y003 Unrecognized sys.version_info check'
Y004 = 'Y004 Version comparison must use only major and minor version'
Y005 = 'Y005 Version comparison must be against a length-{n} tuple'
Y006 = 'Y006 Use only < and >= for version comparisons'
Y007 = 'Y007 Unrecognized sys.platform check'
Y008 = 'Y008 Unrecognized platform "{platform}"'
