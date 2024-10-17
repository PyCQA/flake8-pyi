import sys
import typing
from typing import Annotated, Literal, NewType, TypeAlias, TypeVar

import typing_extensions

__all__ = ["f", "g"]
__all__ += ["h"]
__all__.extend(["i"])  # Y056 Calling ".extend()" on "__all__" may not be supported by all type checkers (use += instead)
__all__.append("j")  # Y056 Calling ".append()" on "__all__" may not be supported by all type checkers (use += instead)
__all__.remove("j")  # Y056 Calling ".remove()" on "__all__" may not be supported by all type checkers (use += instead)
__match_args__ = ('foo',)  # Y052 Need type annotation for "__match_args__"
__slots__ = ('foo',)  # Y052 Need type annotation for "__slots__"

def f(x: "int"): ...  # Y020 Quoted annotations should never be used in stubs
def g(x: list["int"]): ...  # Y020 Quoted annotations should never be used in stubs
_T = TypeVar("_T", bound="int")  # Y020 Quoted annotations should never be used in stubs
_T2 = TypeVar("_T", bound=int)
_S = TypeVar("_S")
_U = TypeVar("_U", "int", "str")  # Y020 Quoted annotations should never be used in stubs  # Y020 Quoted annotations should never be used in stubs
_U2 = TypeVar("_U", int, str)

# This is invalid, but type checkers will flag it, so we don't need to
_V = TypeVar()

def make_sure_those_typevars_arent_flagged_as_unused(a: _T, b: _T2, c: _S, d: _U, e: _U2, f: _V) -> tuple[_T, _T2, _S, _U, _U2, _V]: ...

def h(w: Literal["a", "b"], x: typing.Literal["c"], y: typing_extensions.Literal["d"], z: _T) -> _T: ...  # Y023 Use "typing.Literal" instead of "typing_extensions.Literal"

def i(x: Annotated[int, "lots", "of", "strings"], b: typing.Annotated[str, "more", "strings"]) -> None:
    """Documented and guaranteed useful."""  # Y021 Docstrings should not be included in stubs

def j() -> "int": ...  # Y020 Quoted annotations should never be used in stubs
Alias: TypeAlias = list["int"]  # Y020 Quoted annotations should never be used in stubs

class Child(list["int"]):  # Y020 Quoted annotations should never be used in stubs
    """Documented and guaranteed useful."""  # Y021 Docstrings should not be included in stubs

    __all__ = ('foo',)  # Y052 Need type annotation for "__all__"
    __match_args__ = ('foo', 'bar')
    __slots__ = ('foo', 'bar')

if sys.platform == "linux":
    f: "int"  # Y020 Quoted annotations should never be used in stubs
elif sys.platform == "win32":
    f: "str"  # Y020 Quoted annotations should never be used in stubs
else:
    f: "bytes"  # Y020 Quoted annotations should never be used in stubs

class Empty:
    """Empty"""  # Y021 Docstrings should not be included in stubs

def docstring_and_ellipsis() -> None:
    """Docstring"""  # Y021 Docstrings should not be included in stubs
    ...  # Y048 Function body should contain exactly one statement

def docstring_and_pass() -> None:
    """Docstring"""  # Y021 Docstrings should not be included in stubs
    pass  # Y048 Function body should contain exactly one statement

class DocstringAndEllipsis:
    """Docstring"""  # Y021 Docstrings should not be included in stubs
    ...  # Y013 Non-empty class body must not contain "..."

class DocstringAndPass:
    """Docstring"""  # Y021 Docstrings should not be included in stubs
    pass  # Y012 Class body must not contain "pass"

# These three shouldn't trigger Y020 -- empty strings can't be "quoted annotations"
k = ""  # Y052 Need type annotation for "k"
el = r""  # Y052 Need type annotation for "el"
m = u""  # Y052 Need type annotation for "m"

_N = NewType("_N", int)
_NBad = NewType("_N", "int")  # Y020 Quoted annotations should never be used in stubs
