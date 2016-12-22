from typing import Optional, Union


MaybeCStr = Optional[CStr]
CStr = Union[C, str]
__version__: str
__author__: str = ...


def make_default_c() -> C:
    ...


class D(C):
    parent: C

    def __init__(self) -> None:
        ...


class C:
    other: C = None

    def __init__(self) -> None:
        ...

    def from_str(self, s: str) -> C:
        ...
