# flags: --extend-select=Y090
import builtins
import typing

_Ts = typing.TypeVarTuple("_Ts")

a: tuple[int]  # Y090 "tuple[int]" means "a tuple of length 1, in which the sole element is of type 'int'". Perhaps you meant "tuple[int, ...]"?
b: typing.Tuple[builtins.str]  # Y022 Use "tuple[Foo, Bar]" instead of "typing.Tuple[Foo, Bar]" (PEP 585 syntax)  # Y090 "typing.Tuple[builtins.str]" means "a tuple of length 1, in which the sole element is of type 'builtins.str'". Perhaps you meant "typing.Tuple[builtins.str, ...]"?
c: tuple[int, ...]
d: typing.Tuple[builtins.str, builtins.complex]  # Y022 Use "tuple[Foo, Bar]" instead of "typing.Tuple[Foo, Bar]" (PEP 585 syntax)
e: tuple[typing.Unpack[_Ts]]
f: typing.Tuple[typing.Unpack[_Ts]]  # Y022 Use "tuple[Foo, Bar]" instead of "typing.Tuple[Foo, Bar]" (PEP 585 syntax)
