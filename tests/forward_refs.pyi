from typing import Optional, Union


MaybeCStr = Optional[CStr]
CStr = Union[C, str]


def make_default_c() -> C:
    ...


class D(C):
    def __init__(self) -> None:
        ...


class C:
    def __init__(self) -> None:
        ...

    def from_str(self, s: str) -> C:
        ...
