import sys
import typing
from typing import Annotated, Literal, TypeAlias, TypeVar

import typing_extensions

__all__ = ["f", "g"]
__all__ += ["h"]
__all__.extend(["i"])
__all__.append("j")
__all__.remove("j")
__match_args__ = ('foo',)  # Y020 Quoted annotations should never be used in stubs

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

    __all__ = ('foo',)  # Y020 Quoted annotations should never be used in stubs
    __match_args__ = ('foo', 'bar')

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

# These two shouldn't trigger Y020 -- empty strings can't be "quoted annotations"
k = ""  # Y015 Bad default value. Use "k = ..." instead of "k = ''"
el = r""  # Y015 Bad default value. Use "el = ..." instead of "el = ''"

# The following should also pass,
# But we can't test for it in CI, because the error message is *very* slightly different on 3.7
#
# On 3.7:
# m = u""  # Y015 Bad default value. Use "m = ..." instead of "m = ''"
# On 3.8+:
# m = u""  # Y015 Bad default value. Use "m = ..." instead of "m = u''"
