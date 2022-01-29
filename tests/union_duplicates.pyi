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
