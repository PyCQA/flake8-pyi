from typing import TypeAlias

_MaybeCStr: TypeAlias = _CStr | None
_CStr: TypeAlias = C | str

__version__: str
__author__: str

def make_default_c() -> C: ...

class D(C):
    parent: C
    def __init__(self) -> None: ...

class C:
    other: C = ...
    def __init__(self) -> None: ...
    def from_str(self, s: str) -> C: ...
