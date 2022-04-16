import typing
from typing import (  # Y037 Use PEP 604 union types instead of typing.Union (e.g. "int | str" instead of "Union[int, str]").
    ParamSpec as _ParamSpec,
    TypeAlias,
    TypedDict,
    Union,
    _Alias,
)

import typing_extensions
from typing_extensions import Literal

U = typing.Literal["ham", "bacon"]  # Y026 Use typing_extensions.TypeAlias for type aliases
V = Literal["spam", "eggs"]  # Y026 Use typing_extensions.TypeAlias for type aliases
X = typing_extensions.Literal["foo", "bar"]  # Y026 Use typing_extensions.TypeAlias for type aliases
Y = int | str  # Y026 Use typing_extensions.TypeAlias for type aliases
Z = Union[str, bytes]  # Y026 Use typing_extensions.TypeAlias for type aliases

A: typing.TypeAlias = typing.Literal["ham", "bacon"]
B: typing_extensions.TypeAlias = Literal["spam", "eggs"]
C: TypeAlias = typing_extensions.Literal["foo", "bar"]
D: TypeAlias = int | str
E: TypeAlias = Union[str, bytes]
F: TypeAlias = int
G: typing.TypeAlias = int
H: typing_extensions.TypeAlias = int

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
