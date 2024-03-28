# flags: --extend-select=Y090
import typing

_Ts = typing.TypeVarTuple("_Ts")

e: tuple[*_Ts]
f: typing.Tuple[*_Ts]  # Y022 Use "tuple[Foo, Bar]" instead of "typing.Tuple[Foo, Bar]" (PEP 585 syntax)
