import typing
from typing import Optional  # Y036 Use PEP 604 union types instead of typing.Optional.
from typing import Union  # Y036 Use PEP 604 union types instead of typing.Union.

x1: Optional[str]
x2: Optional
x3: Union[str, int]
x4: Union


y1: typing.Optional[str]  # Y036 Use PEP 604 union types instead of typing.Optional.
y2: typing.Optional  # Y036 Use PEP 604 union types instead of typing.Optional.
y3: typing.Union[str, int]  # Y036 Use PEP 604 union types instead of typing.Union.
y4: typing.Union  # Y036 Use PEP 604 union types instead of typing.Union.


def f1(x: Optional[str] = ...) -> None: ...
def f2() -> Optional[str]: ...
def f3() -> Union[str, int]: ...
def f4(x: Union[str, int] = ...) -> None: ...
def f5(x: Optional) -> None: ...
def f6(x: Union) -> None: ...


def g1(x: typing.Optional[str] = ...) -> None: ...  # Y036 Use PEP 604 union types instead of typing.Optional.
def g2() -> typing.Optional[str]: ...  # Y036 Use PEP 604 union types instead of typing.Optional.
def g3() -> typing.Union[str, int]: ...  # Y036 Use PEP 604 union types instead of typing.Union.
def g4(x: typing.Union[str, int] = ...) -> None: ...  # Y036 Use PEP 604 union types instead of typing.Union.
def g5(x: typing.Optional) -> None: ...  # Y036 Use PEP 604 union types instead of typing.Optional.
def g6(x: typing.Union) -> None: ...  # Y036 Use PEP 604 union types instead of typing.Union.
