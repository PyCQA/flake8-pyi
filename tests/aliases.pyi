from collections.abc import Mapping
import builtins
import collections
import typing
from typing import ParamSpec as _ParamSpec, TypeAlias, TypedDict, Union, _Alias  # Y037 Use PEP 604 union types instead of typing.Union (e.g. "int | str" instead of "Union[int, str]").

import typing_extensions

T = builtins.str  # Y026 Use typing_extensions.TypeAlias for type aliases
U = typing.AbstractSet  # Y026 Use typing_extensions.TypeAlias for type aliases
V = Mapping  # Y026 Use typing_extensions.TypeAlias for type aliases
X = int  # Y026 Use typing_extensions.TypeAlias for type aliases
Y = int | str  # Y026 Use typing_extensions.TypeAlias for type aliases
Z = Union[str, bytes]  # Y026 Use typing_extensions.TypeAlias for type aliases

X: TypeAlias = int
Y: typing.TypeAlias = int
Z: typing_extensions.TypeAlias = int

a = b = int  # Y017 Only simple assignments allowed
a.b = int  # Y017 Only simple assignments allowed

_P = _ParamSpec("_P")
List = _Alias()

TD = TypedDict("TD", {"in": bool})

def foo() -> None: ...
alias_for_foo_but_not_type_alias = foo

alias_for_function_from_builtins = dir

class Foo:
    def baz(self) -> None: ...

f: Foo = ...
baz = f.baz

typealias_for_deque = collections.deque  # Y026 Use typing_extensions.TypeAlias for type aliases
uses_typealias_for_deque_in_annotation: typealias_for_deque
