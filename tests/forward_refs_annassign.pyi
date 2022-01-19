from typing import Optional, Union, TypeAlias


MaybeCStr: TypeAlias = Optional[CStr]
CStr: TypeAlias = Union[C, str]
__version__: str
__author__: str


def make_default_c() -> C:
    ...


class D(C):
    parent: C

    def __init__(self) -> None:
        ...


class C:
    other: C = ...

    def __init__(self) -> None:
        ...

    def from_str(self, s: str) -> C:
        ...
