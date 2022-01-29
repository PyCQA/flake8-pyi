import typing
from typing import Annotated, Literal, TypeAlias, TypeVar

import typing_extensions

__all__ = ["f", "g"]

def f(x: "int"): ...  # Y020 Quoted annotations should never be used in stubs
def g(x: list["int"]): ...  # Y020 Quoted annotations should never be used in stubs
_T = TypeVar("_T", bound="int")  # Y020 Quoted annotations should never be used in stubs
def h(w: Literal["a", "b"], x: typing.Literal["c"], y: typing_extensions.Literal["d"], z: _T) -> _T: ...

def i(x: Annotated[int, "lots", "of", "strings"], b: typing.Annotated[str, "more", "strings"]) -> None:
    """Documented and guaranteed useful."""  # Y021 Docstrings should not be included in stubs

def j() -> "int": ...  # Y020 Quoted annotations should never be used in stubs
Alias: TypeAlias = list["int"]  # Y020 Quoted annotations should never be used in stubs

class Child(list["int"]):  # Y020 Quoted annotations should never be used in stubs
    """Documented and guaranteed useful."""  # Y021 Docstrings should not be included in stubs
