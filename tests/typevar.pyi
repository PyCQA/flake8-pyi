from typing import ParamSpec, TypeVar, TypeVarTuple

T = TypeVar("T")  # Y001 Name of private TypeVar must start with _
_T = TypeVar("_T")
P = ParamSpec("P")  # Y001 Name of private ParamSpec must start with _
_P = ParamSpec("_P")
Ts = TypeVarTuple("Ts")  # Y001 Name of private TypeVarTuple must start with _
_Ts = TypeVarTuple("_Ts")
