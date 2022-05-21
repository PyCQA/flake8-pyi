# flags: --extend-ignore=Y037
import builtins
import typing
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
mixed_subscript_union: Union[str, Literal['foo'], typing_extensions.Literal['bar']]  # Y030 Multiple Literal members in a union. Combine them into one, e.g. "Literal['foo', 'bar']".
just_literals_pipe_union: TypeAlias = Literal[True] | Literal['idk']  # Y030 Multiple Literal members in a union. Use a single Literal, e.g. "Literal[True, 'idk']".
mixed_pipe_union: TypeAlias = Union[Literal[966], int, Literal['baz']]  # Y030 Multiple Literal members in a union. Combine them into one, e.g. "Literal[966, 'baz']".
many_literal_members_but_needs_combining: TypeAlias = int | Literal['a', 'b'] | Literal['baz']  # Y030 Multiple Literal members in a union. Combine them into one, e.g. "Literal['a', 'b', 'baz']".

a: int | float  # Y041 Use "float" instead of "int | float" (see "The numeric tower" in PEP 484)
b: Union[builtins.float, str, bytes, builtins.int]  # Y041 Use "float" instead of "int | float" (see "The numeric tower" in PEP 484)
def func(arg: float | list[str] | type[bool] | complex) -> None: ...  # Y041 Use "complex" instead of "float | complex" (see "The numeric tower" in PEP 484)

class Foo:
    def method(self, arg: int | builtins.float | complex) -> None: ...  # Y041 Use "complex" instead of "float | complex" (see "The numeric tower" in PEP 484)  # Y041 Use "complex" instead of "int | complex" (see "The numeric tower" in PEP 484)

c: Union[builtins.complex, memoryview, slice, int]  # Y041 Use "complex" instead of "int | complex" (see "The numeric tower" in PEP 484)

# Don't error with Y041 here, the two error messages combined are quite confusing
d: int | int | float  # Y016 Duplicate union member "int"

e: Union[int, str, bool]  # Y042 Use "int" instead of "bool | int", as "bool" is a subclass of "int"
f: Literal["foo"] | Literal["bar"] | int | float | builtins.bool  # Y041 Use "float" instead of "int | float" (see "The numeric tower" in PEP 484)  # Y042 Use "int" instead of "bool | int", as "bool" is a subclass of "int"  # Y030 Multiple Literal members in a union. Combine them into one, e.g. "Literal['foo', 'bar']".
