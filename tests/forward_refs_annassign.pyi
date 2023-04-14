# flags: --ignore=Y037
from typing import Optional, TypeAlias, Union

MaybeCStr: TypeAlias = Optional[CStr]
CStr: TypeAlias = Union[C, str]
__version__: str
__author__: str

def make_default_c() -> C: ...

# Disallow forward refs for base classes
class D(C):  # F821 undefined name 'C'
    parent: C
    def __init__(self) -> None: ...

class C:
    other: C = ...
    def __init__(self) -> None: ...
    def from_str(self, s: str) -> C: ...

class Baz(metaclass=Meta):  # F821 undefined name 'Meta'
    ...

class Foo(Bar, Baz, metaclass=Meta):  # F821 undefined name 'Bar'  # F821 undefined name 'Meta'
    ...

class Meta(type):
    ...

class Bar(metaclass=Meta):
    ...

# Allow circular references in annotations
class A:
    foo: B
    bar: dict[str, B]

class B:
    foo: A
    bar: dict[str, A]
