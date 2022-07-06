# flags: --extend-ignore=F723,E261,E262
#
# F723: syntax error in type comment
# E261: at least two spaces before inline comment
# E262: inline comment should start with '# '

from collections.abc import Sequence
from typing import TypeAlias

a = None  # type: int  # Y033 Do not use type comments in stubs (e.g. use "x: int" instead of "x = ... # type: int")  # Y026 Use typing_extensions.TypeAlias for type aliases, e.g. "a: TypeAlias = None"
b = None  # type: str  # And here's an extra comment about why it's that type  # Y033 Do not use type comments in stubs (e.g. use "x: int" instead of "x = ... # type: int")  # Y026 Use typing_extensions.TypeAlias for type aliases, e.g. "b: TypeAlias = None"
C: TypeAlias = None  #type: int  # Y033 Do not use type comments in stubs (e.g. use "x: int" instead of "x = ... # type: int")  # Y042 Name of private type alias must start with _
D: TypeAlias = None  #      type: int  # Y033 Do not use type comments in stubs (e.g. use "x: int" instead of "x = ... # type: int")  # Y042 Name of private type alias must start with _
_E: TypeAlias = None#    type: int  # Y033 Do not use type comments in stubs (e.g. use "x: int" instead of "x = ... # type: int")
_F: TypeAlias = None#type:int  # Y033 Do not use type comments in stubs (e.g. use "x: int" instead of "x = ... # type: int")

def func(
    arg1,  # type: dict[str, int]  # Y033 Do not use type comments in stubs (e.g. use "x: int" instead of "x = ... # type: int")
    arg2  # type: Sequence[bytes]  # And here's some more info about this arg  # Y033 Do not use type comments in stubs (e.g. use "x: int" instead of "x = ... # type: int")
): ...

class Foo:
    attr = None  # type: set[str]  # Y033 Do not use type comments in stubs (e.g. use "x: int" instead of "x = ... # type: int")  # Y026 Use typing_extensions.TypeAlias for type aliases, e.g. "attr: TypeAlias = None"

g = None  # type: ignore  # Y026 Use typing_extensions.TypeAlias for type aliases, e.g. "g: TypeAlias = None"
h = None  # type: ignore[attr-defined]  # Y026 Use typing_extensions.TypeAlias for type aliases, e.g. "h: TypeAlias = None"
I: TypeAlias = None  #type: ignore  # Y042 Name of private type alias must start with _
J: TypeAlias = None  #      type: ignore  # Y042 Name of private type alias must start with _
_K: TypeAlias = None#    type: ignore
_L: TypeAlias = None#type:ignore

# Whole line commented out  # type: int
_M: TypeAlias = None  # type: can't parse me!

class Bar:
    n = None  # type: can't parse me either!  # Y026 Use typing_extensions.TypeAlias for type aliases, e.g. "n: TypeAlias = None"
    # This whole line is commented out and indented # type: str
