from typing import TypeVar, Literal, Annotated, TypeAlias

__all__ = ["f", "g"]


def f(x: "int"):  # Y020 Quoted annotations should never be used in stubs
    ...

def g(x: list["int"]):  # Y020 Quoted annotations should never be used in stubs
    ...


_T = TypeVar("_T", bound="int")  # Y020 Quoted annotations should never be used in stubs

def h(x: Literal["a", "b"], y: Literal["c"], z: _T) -> _T:
    ...

def i(x: Annotated[int, "lots", "of", "strings"]) -> None:
    """Documented and guaranteed useful."""  # Y021 Docstrings should not be included in stubs

def j() -> "int":  # Y020 Quoted annotations should never be used in stubs
    ...


Alias: TypeAlias = list["int"]  # Y020 Quoted annotations should never be used in stubs

class Child(list["int"]):  # Y020 Quoted annotations should never be used in stubs
    """Documented and guaranteed useful."""  # Y021 Docstrings should not be included in stubs
