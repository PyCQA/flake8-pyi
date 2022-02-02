from typing import Sequence, TypeAlias

a: TypeAlias = None  # type: int  # Y033 Do not use type comments in stubs (e.g. use "x: int" instead of "x = ... # type: int")
b: TypeAlias = None  # type: str  # And here's an extra comment about why it's that type  # Y033 Do not use type comments in stubs (e.g. use "x: int" instead of "x = ... # type: int")
c: TypeAlias = None  #type: int  # Y033 Do not use type comments in stubs (e.g. use "x: int" instead of "x = ... # type: int")
d: TypeAlias = None  #      type: int  # Y033 Do not use type comments in stubs (e.g. use "x: int" instead of "x = ... # type: int")
e: TypeAlias = None#    type: int  # Y033 Do not use type comments in stubs (e.g. use "x: int" instead of "x = ... # type: int")
f: TypeAlias = None#type:int  # Y033 Do not use type comments in stubs (e.g. use "x: int" instead of "x = ... # type: int")

def func(
    arg1,  # type: dict[str, int]  # Y033 Do not use type comments in stubs (e.g. use "x: int" instead of "x = ... # type: int")
    arg2  # type: Sequence[bytes]  # And here's some more info about this arg  # Y033 Do not use type comments in stubs (e.g. use "x: int" instead of "x = ... # type: int")
): ...

class Foo:
    attr: TypeAlias = None  # type: set[str]  # Y033 Do not use type comments in stubs (e.g. use "x: int" instead of "x = ... # type: int")

g: TypeAlias = None  # type: ignore
h: TypeAlias = None  # type: ignore[attr-defined]
i: TypeAlias = None  #type: ignore
j: TypeAlias = None  #      type: ignore
k: TypeAlias = None#    type: ignore
l: TypeAlias = None#type:ignore

# Whole line commented out  # type: int
m: TypeAlias = None  # type: can't parse me!

class Bar:
    n: TypeAlias = None  # type: can't parse me either!
    # This whole line is commented out and indented # type: str
