import typing
from typing import NamedTuple, TypedDict

T = NamedTuple("T", [('foo', int), ('bar', str)])  # Y028 Use class-based syntax for NamedTuples
U = typing.NamedTuple("U", [('baz', bytes)])  # Y028 Use class-based syntax for NamedTuples

class V(NamedTuple):
    foo: int
    bar: str

# BAD TYPEDDICTS
W = TypedDict("W", {'foo': str, 'bar': int})  # Y031 Use class-based syntax for TypedDicts where possible
B = typing.TypedDict("B", {'foo': str, 'bar': int})  # Y031 Use class-based syntax for TypedDicts where possible

# GOOD TYPEDDICTS
C = TypedDict("B", {'field has a space': list[int]})
D = TypedDict("C", {'while': bytes, 'for': int})
E = TypedDict("D", {'[][]': dict[str, int]})
F = TypedDict("E", {'1': list[str], '2': str})

class ClassBased(TypedDict):
    foo: str
    bar: int
