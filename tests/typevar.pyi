from typing import ParamSpec, TypeVar, TypeVarTuple

T = TypeVar("T")  # Y001 Name of private TypeVar must start with _
_T = TypeVar("_T")  # Y018 TypeVar "_T" is not used
P = ParamSpec("P")  # Y001 Name of private ParamSpec must start with _
_P = ParamSpec("_P")  # Y018 ParamSpec "_P" is not used
Ts = TypeVarTuple("Ts")  # Y001 Name of private TypeVarTuple must start with _
_Ts = TypeVarTuple("_Ts")  # Y018 TypeVarTuple "_Ts" is not used

_UsedTypeVar = TypeVar("_UsedTypeVar")

def func(arg: _UsedTypeVar) -> _UsedTypeVar:
    ...


_TypeVarUsedInBinOp = TypeVar("_TypeVarUsedInBinOp", bound=str)

def func2(arg: _TypeVarUsedInBinOp | int) -> _TypeVarUsedInBinOp | int:
    ...
