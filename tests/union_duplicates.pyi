# flags: --extend-ignore=Y037
import builtins
import typing
from collections.abc import Mapping
from typing import Union

import typing_extensions
from typing_extensions import Literal, TypeAlias

def f1_pipe(x: int | str) -> None: ...
def f2_pipe(x: int | int) -> None: ...  # Y016 Duplicate union member "int"
def f3_pipe(x: None | int | int) -> None: ...  # Y016 Duplicate union member "int"
def f4_pipe(x: int | None | int) -> None: ...  # Y016 Duplicate union member "int"
def f5_pipe(x: int | int | None) -> None: ...  # Y016 Duplicate union member "int"

def f1_union(x: Union[int, str]) -> None: ...
def f2_union(x: Union[int, int]) -> None: ...  # Y016 Duplicate union member "int"
def f3_union(x: Union[None, int, int]) -> None: ...  # Y016 Duplicate union member "int"
def f4_union(x: typing.Union[int, None, int]) -> None: ...  # Y016 Duplicate union member "int"
def f5_union(x: typing.Union[int, int, None]) -> None: ...  # Y016 Duplicate union member "int"

just_literals_subscript_union: Union[Literal[1], typing.Literal[2]]  # Y030 Multiple Literal members in a union. Use a single Literal, e.g. "Literal[1, 2]".
mixed_subscript_union: Union[bytes, Literal['foo'], typing_extensions.Literal['bar']]  # Y030 Multiple Literal members in a union. Combine them into one, e.g. "Literal['foo', 'bar']".
just_literals_pipe_union: TypeAlias = Literal[True] | Literal['idk']  # Y042 Type aliases should use the CamelCase naming convention  # Y030 Multiple Literal members in a union. Use a single Literal, e.g. "Literal[True, 'idk']".
_mixed_pipe_union: TypeAlias = Union[Literal[966], bytes, Literal['baz']]  # Y042 Type aliases should use the CamelCase naming convention  # Y047 Type alias "_mixed_pipe_union" is not used  # Y030 Multiple Literal members in a union. Combine them into one, e.g. "Literal[966, 'baz']".
ManyLiteralMembersButNeedsCombining: TypeAlias = int | Literal['a', 'b'] | Literal['baz']  # Y030 Multiple Literal members in a union. Combine them into one, e.g. "Literal['a', 'b', 'baz']".

a: int | float  # Y041 Use "float" instead of "int | float" (see "The numeric tower" in PEP 484)
b: Union[builtins.float, str, bytes, builtins.int]  # Y041 Use "float" instead of "int | float" (see "The numeric tower" in PEP 484)
def func(arg: float | list[str] | type[bool] | complex) -> None: ...  # Y041 Use "complex" instead of "float | complex" (see "The numeric tower" in PEP 484)

class Foo:
    def method(self, arg: int | builtins.float | complex) -> None: ...  # Y041 Use "complex" instead of "float | complex" (see "The numeric tower" in PEP 484)  # Y041 Use "complex" instead of "int | complex" (see "The numeric tower" in PEP 484)

c: Union[builtins.complex, memoryview, slice, int]  # Y041 Use "complex" instead of "int | complex" (see "The numeric tower" in PEP 484)

# Don't error with Y041 here, the two error messages combined are quite confusing
d: int | int | float  # Y016 Duplicate union member "int"

f: Literal["foo"] | Literal["bar"] | int | float | builtins.bool  # Y030 Multiple Literal members in a union. Combine them into one, e.g. "Literal['foo', 'bar']".  # Y041 Use "float" instead of "int | float" (see "The numeric tower" in PEP 484)

# Type aliases are special-cased to be excluded from Y041
MyTypeAlias: TypeAlias = int | float | bool
MySecondTypeAlias: TypeAlias = Union[builtins.int, str, complex, bool]
MyThirdTypeAlias: TypeAlias = Mapping[str, int | builtins.float | builtins.bool]

one: str | Literal["foo"]  # Y051 "Literal['foo']" is redundant in a union with "str"
Two: TypeAlias = Union[Literal[b"bar", b"baz"], bytes]  # Y051 "Literal[b'bar']" is redundant in a union with "bytes"
def three(arg: Literal[5] | builtins.int | Literal[9]) -> None: ...  # Y030 Multiple Literal members in a union. Combine them into one, e.g. "Literal[5, 9]".  # Y051 "Literal[5]" is redundant in a union with "int"

class Four:
    var: builtins.bool | Literal[True]  # Y051 "Literal[True]" is redundant in a union with "bool"

DupesHereSoNoY051: TypeAlias = int | int | Literal[42]  # Y016 Duplicate union member "int"
NightmareAlias1 = int | float | Literal[4] | Literal["foo"]  # Y026 Use typing_extensions.TypeAlias for type aliases, e.g. "NightmareAlias1: TypeAlias = int | float | Literal[4] | Literal['foo']"  # Y030 Multiple Literal members in a union. Combine them into one, e.g. "Literal[4, 'foo']".  # Y041 Use "float" instead of "int | float" (see "The numeric tower" in PEP 484)  # Y051 "Literal[4]" is redundant in a union with "int"
nightmare_alias2: TypeAlias = int | float | Literal[4] | Literal["foo"]  # Y042 Type aliases should use the CamelCase naming convention  # Y030 Multiple Literal members in a union. Combine them into one, e.g. "Literal[4, 'foo']".  # Y051 "Literal[4]" is redundant in a union with "int"
