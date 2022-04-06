import sys
import typing
from typing import Annotated, Literal, TypeAlias, TypeVar

import typing_extensions

__all__ = ["f", "g"]
__match_args__ = ('foo',)  # Y026 Use typing_extensions.TypeAlias for type aliases  # Y020 Quoted annotations should never be used in stubs

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

    __all__ = ('foo',)  # Y026 Use typing_extensions.TypeAlias for type aliases  # Y020 Quoted annotations should never be used in stubs
    __match_args__ = ('foo', 'bar')

if sys.platform == "linux":
    f: "int"  # Y020 Quoted annotations should never be used in stubs
elif sys.platform == "win32":
    f: "str"  # Y020 Quoted annotations should never be used in stubs
else:
    f: "bytes"  # Y020 Quoted annotations should never be used in stubs
