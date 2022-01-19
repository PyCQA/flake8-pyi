import typing
from typing import NamedTuple

T = NamedTuple("T", [('foo', int), ('bar', str)])  # Y028 Use class-based syntax for NamedTuples
U = typing.NamedTuple("U", [('baz', bytes)])  # Y028 Use class-based syntax for NamedTuples

class V(NamedTuple):
    foo: int
    bar: str
