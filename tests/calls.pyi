import typing
from typing import NamedTuple, TypedDict

import mypy_extensions
import typing_extensions

T = NamedTuple("T", [('foo', int), ('bar', str)])  # Y028 Use class-based syntax for NamedTuples
U = typing.NamedTuple("U", [('baz', bytes)])  # Y028 Use class-based syntax for NamedTuples
S = typing_extensions.NamedTuple("S", [('baz', bytes)])  # Y028 Use class-based syntax for NamedTuples

class V(NamedTuple):
    foo: int
    bar: str

# BAD TYPEDDICTS
W = TypedDict("W", {'foo': str, 'bar': int})  # Y031 Use class-based syntax for TypedDicts where possible
B = typing.TypedDict("B", {'foo': str, 'bar': int})  # Y031 Use class-based syntax for TypedDicts where possible
WithTotal = typing_extensions.TypedDict("WithTotal", {'foo': str, 'bar': int}, total=False)  # Y023 Use "typing.TypedDict" instead of "typing_extensions.TypedDict"  # Y031 Use class-based syntax for TypedDicts where possible
BB = mypy_extensions.TypedDict("BB", {'foo': str, 'bar': int})  # Y031 Use class-based syntax for TypedDicts where possible

# we don't want these two to raise errors (type-checkers already do that for us),
# we just want to make sure the plugin doesn't crash if it comes across an invalid TypedDict
InvalidTypedDict = TypedDict("InvalidTypedDict", {7: 9, b"wot": [8, 3]})
WeirdThirdArg = TypedDict("WeirdThirdArg", {'foo': int, "wot": str}, "who knows?")

# GOOD TYPEDDICTS
C = typing.TypedDict("B", {'field has a space': list[int]})
D = typing_extensions.TypedDict("C", {'while': bytes, 'for': int})  # Y023 Use "typing.TypedDict" instead of "typing_extensions.TypedDict"
E = TypedDict("D", {'[][]': dict[str, int]})
F = TypedDict("E", {'1': list[str], '2': str})

class ClassBased(TypedDict):
    foo: str
    bar: int

__all__ = ["T", "U", "S"]
__all__.append("W")  # Y056 Calling ".append()" on "__all__" may not be supported by all type checkers (use += instead)
__all__.extend(["B", "WithTotal"])  # Y056 Calling ".extend()" on "__all__" may not be supported by all type checkers (use += instead)
__all__.remove("U")  # Y056 Calling ".remove()" on "__all__" may not be supported by all type checkers (use += instead)
