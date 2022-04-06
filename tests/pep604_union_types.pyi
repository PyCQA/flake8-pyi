import typing
from typing import (  # Y037 Use PEP 604 union types instead of typing.Optional (e.g. "int | None" instead of "Optional[int]"). # Y037 Use PEP 604 union types instead of typing.Union (e.g. "int | str" instead of "Union[int, str]").
    Optional,
    Union,
)

x1: Optional[str]
x2: Optional
x3: Union[str, int]
x4: Union


y1: typing.Optional[str]  # Y037 Use PEP 604 union types instead of typing.Optional (e.g. "int | None" instead of "Optional[int]").
y2: typing.Optional  # Y037 Use PEP 604 union types instead of typing.Optional (e.g. "int | None" instead of "Optional[int]").
y3: typing.Union[str, int]  # Y037 Use PEP 604 union types instead of typing.Union (e.g. "int | str" instead of "Union[int, str]").
y4: typing.Union  # Y037 Use PEP 604 union types instead of typing.Union (e.g. "int | str" instead of "Union[int, str]").


def f1(x: Optional[str] = ...) -> None: ...
def f2() -> Optional[str]: ...
def f3() -> Union[str, int]: ...
def f4(x: Union[str, int] = ...) -> None: ...
def f5(x: Optional) -> None: ...
def f6(x: Union) -> None: ...


def g1(x: typing.Optional[str] = ...) -> None: ...  # Y037 Use PEP 604 union types instead of typing.Optional (e.g. "int | None" instead of "Optional[int]").
def g2() -> typing.Optional[str]: ...  # Y037 Use PEP 604 union types instead of typing.Optional (e.g. "int | None" instead of "Optional[int]").
def g3() -> typing.Union[str, int]: ...  # Y037 Use PEP 604 union types instead of typing.Union (e.g. "int | str" instead of "Union[int, str]").
def g4(x: typing.Union[str, int] = ...) -> None: ...  # Y037 Use PEP 604 union types instead of typing.Union (e.g. "int | str" instead of "Union[int, str]").
def g5(x: typing.Optional) -> None: ...  # Y037 Use PEP 604 union types instead of typing.Optional (e.g. "int | None" instead of "Optional[int]").
def g6(x: typing.Union) -> None: ...  # Y037 Use PEP 604 union types instead of typing.Union (e.g. "int | str" instead of "Union[int, str]").
