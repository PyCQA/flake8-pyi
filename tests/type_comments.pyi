from typing import Sequence, TypeAlias

a: TypeAlias = None  # type: int  # Y033 Do not use type comments in stubs
b: TypeAlias = None  # type: str  # And here's an extra comment about why it's that type  # Y033 Do not use type comments in stubs

def func(
    arg1,  # type: dict[str, int]  # Y033 Do not use type comments in stubs
    arg2  # type: Sequence[bytes]  # And here's some more info about this arg  # Y033 Do not use type comments in stubs
): ...

class Foo:
    attr: TypeAlias = None  # type: set[str]  # Y033 Do not use type comments in stubs

c: TypeAlias = None  # type: ignore
d: TypeAlias = None  # type: ignore[attr-defined]
# Whole line commented out  # type: int
e: TypeAlias = None  # type: can't parse me!
