# flags: --extend-ignore=Y037
import builtins
import collections.abc
import typing
from collections.abc import Mapping
from typing import (
    Annotated,
    Any,
    Optional,
    ParamSpec as _ParamSpec,
    TypeAlias,
    TypedDict,
    Union,
    _Alias,
)

import typing_extensions
from typing_extensions import Literal

StringMapping = Mapping[str, str]  # Y026 Use typing_extensions.TypeAlias for type aliases, e.g. "StringMapping: TypeAlias = Mapping[str, str]"
IntSequence = collections.abc.Sequence[int]  # Y026 Use typing_extensions.TypeAlias for type aliases, e.g. "IntSequence: TypeAlias = collections.abc.Sequence[int]"
P = builtins.tuple[int, int]  # Y026 Use typing_extensions.TypeAlias for type aliases, e.g. "P: TypeAlias = builtins.tuple[int, int]"
Q = tuple[int, int]  # Y026 Use typing_extensions.TypeAlias for type aliases, e.g. "Q: TypeAlias = tuple[int, int]"
R = Any  # Y026 Use typing_extensions.TypeAlias for type aliases, e.g. "R: TypeAlias = Any"
S = Optional[str]  # Y026 Use typing_extensions.TypeAlias for type aliases, e.g. "S: TypeAlias = Optional[str]"
T = Annotated[int, "some very useful metadata"]  # Y026 Use typing_extensions.TypeAlias for type aliases, e.g. "T: TypeAlias = Annotated[int, 'some very useful metadata']"
U = typing.Literal["ham", "bacon"]  # Y026 Use typing_extensions.TypeAlias for type aliases, e.g. "U: TypeAlias = typing.Literal['ham', 'bacon']"
V = Literal["[(", ")]"]  # Y026 Use typing_extensions.TypeAlias for type aliases, e.g. "V: TypeAlias = Literal['[(', ')]']"
X = typing_extensions.Literal["foo", "bar"]  # Y026 Use typing_extensions.TypeAlias for type aliases, e.g. "X: TypeAlias = typing_extensions.Literal['foo', 'bar']"
Y = int | str  # Y026 Use typing_extensions.TypeAlias for type aliases, e.g. "Y: TypeAlias = int | str"
Z = Union[str, bytes]  # Y026 Use typing_extensions.TypeAlias for type aliases, e.g. "Z: TypeAlias = Union[str, bytes]"

StringMapping: TypeAlias = Mapping[str, str]
IntSequence: TypeAlias = collections.abc.Sequence[int]
A: typing.TypeAlias = typing.Literal["ham", "bacon"]
B: typing_extensions.TypeAlias = Literal["spam", "eggs"]
C: TypeAlias = typing_extensions.Literal["foo", "bar"]
D: TypeAlias = int | str
E: TypeAlias = Union[str, bytes]
F: TypeAlias = int
G: typing.TypeAlias = int
H: typing_extensions.TypeAlias = int
I: TypeAlias = Annotated[int, "some very useful metadata"]
J: TypeAlias = Optional[str]
K: TypeAlias = Any
L: TypeAlias = tuple[int, int]
P: TypeAlias = builtins.tuple[int, int]

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
