# flags: --extend-ignore=Y037,Y047
import array
import builtins
import collections.abc
import enum
import typing
from collections.abc import Mapping
from typing import (
    Annotated,
    Any,
    Literal,
    Optional,
    ParamSpec as _ParamSpec,
    TypeAlias,
    TypedDict,
    Union,
    _Alias,
)
from weakref import WeakValueDictionary

import typing_extensions

class Foo:
    def baz(self) -> None: ...

StringMapping = Mapping[str, str]  # Y026 Use typing_extensions.TypeAlias for type aliases, e.g. "StringMapping: TypeAlias = Mapping[str, str]"
IntSequence = collections.abc.Sequence[int]  # Y026 Use typing_extensions.TypeAlias for type aliases, e.g. "IntSequence: TypeAlias = collections.abc.Sequence[int]"
IntArray = array.array[int]  # Y026 Use typing_extensions.TypeAlias for type aliases, e.g. "IntArray: TypeAlias = array.array[int]"
FooWeakDict = WeakValueDictionary[str, Foo]  # Y026 Use typing_extensions.TypeAlias for type aliases, e.g. "FooWeakDict: TypeAlias = WeakValueDictionary[str, Foo]"
P = builtins.tuple[int, int]  # Y026 Use typing_extensions.TypeAlias for type aliases, e.g. "P: TypeAlias = builtins.tuple[int, int]"
Q = tuple[int, int]  # Y026 Use typing_extensions.TypeAlias for type aliases, e.g. "Q: TypeAlias = tuple[int, int]"
R = Any  # Y026 Use typing_extensions.TypeAlias for type aliases, e.g. "R: TypeAlias = Any"
S = Optional[str]  # Y026 Use typing_extensions.TypeAlias for type aliases, e.g. "S: TypeAlias = Optional[str]"
T = Annotated[int, "some very useful metadata"]  # Y026 Use typing_extensions.TypeAlias for type aliases, e.g. "T: TypeAlias = Annotated[int, 'some very useful metadata']"
U = typing.Literal["ham", "bacon"]  # Y026 Use typing_extensions.TypeAlias for type aliases, e.g. "U: TypeAlias = typing.Literal['ham', 'bacon']"
V = Literal["[(", ")]"]  # Y026 Use typing_extensions.TypeAlias for type aliases, e.g. "V: TypeAlias = Literal['[(', ')]']"
X = typing_extensions.Literal["foo", "bar"]  # Y026 Use typing_extensions.TypeAlias for type aliases, e.g. "X: TypeAlias = typing_extensions.Literal['foo', 'bar']"  # Y023 Use "typing.Literal" instead of "typing_extensions.Literal"
Y = int | str  # Y026 Use typing_extensions.TypeAlias for type aliases, e.g. "Y: TypeAlias = int | str"
Z = Union[str, bytes]  # Y026 Use typing_extensions.TypeAlias for type aliases, e.g. "Z: TypeAlias = Union[str, bytes]"
ZZ = None  # Y026 Use typing_extensions.TypeAlias for type aliases, e.g. "ZZ: TypeAlias = None"

StringMapping: TypeAlias = Mapping[str, str]
IntSequence: TypeAlias = collections.abc.Sequence[int]
IntArray: TypeAlias = array.array[int]
FooWeakDict: TypeAlias = WeakValueDictionary[str, Foo]
A: typing.TypeAlias = typing.Literal["ham", "bacon"]
B: typing_extensions.TypeAlias = Literal["spam", "eggs"]
C: TypeAlias = typing_extensions.Literal["foo", "bar"]  # Y023 Use "typing.Literal" instead of "typing_extensions.Literal"
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

f: Foo = ...
baz = f.baz

_PrivateAliasT: TypeAlias = str | int  # Y043 Bad name for a type alias (the "T" suffix implies a TypeVar)
_PrivateAliasT2: TypeAlias = typing.Any  # Y043 Bad name for a type alias (the "T" suffix implies a TypeVar)
_PrivateAliasT3: TypeAlias = Literal["not", "a", "chance"]  # Y043 Bad name for a type alias (the "T" suffix implies a TypeVar)
PublicAliasT: TypeAlias = str | int
PublicAliasT2: TypeAlias = Union[str, bytes]
_ABCDEFGHIJKLMNOPQRST: TypeAlias = typing.Any
_PrivateAliasS: TypeAlias = Literal["I", "guess", "this", "is", "okay"]
_PrivateAliasS2: TypeAlias = Annotated[str, "also okay"]

snake_case_alias1: TypeAlias = str | int  # Y042 Type aliases should use the CamelCase naming convention
_snake_case_alias2: TypeAlias = Literal["whatever"]  # Y042 Type aliases should use the CamelCase naming convention

# check that this edge case doesn't crash the plugin
_: TypeAlias = str | int

class FooEnum(enum.Enum):
    BAR = None  # shouldn't emit Y026 because it's an assignment in an enum class
