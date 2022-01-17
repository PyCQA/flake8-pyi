from _typeshed import Self
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


_S = TypeVar("_S")


class BadClass:
    def __new__(cls: type[_S], *args: str, **kwargs: int) -> _S:  # Y019 Use "_typeshed.Self" instead of "_S", e.g. "def __new__(cls: type[Self], *args: str, **kwargs: int) -> Self: ..."
        ...

    def bad_instance_method(self: _S, arg: bytes) -> _S:  # Y019 Use "_typeshed.Self" instead of "_S", e.g. "def bad_instance_method(self: Self, arg: bytes) -> Self: ..."
        ...

    @classmethod
    def bad_class_method(cls: type[_S], arg: int) -> _S:  # Y019 Use "_typeshed.Self" instead of "_S", e.g. "def bad_class_method(cls: type[Self], arg: int) -> Self: ..."
        ...


class GoodClass:
    def __new__(cls: type[Self], *args: list[int], **kwargs: set[str]) -> Self:
        ...

    def good_instance_method_1(self: Self, arg: bytes) -> Self:
        ...

    def good_instance_method_2(self, arg1: _S, arg2: _S) -> _S:
        ...

    @classmethod
    def good_cls_method_1(cls: type[Self], arg: int) -> Self:
        ...

    @classmethod
    def good_cls_method_2(cls, arg1: _S, arg2: _S) -> _S:
        ...

    @staticmethod
    def static_method(arg1: _S) -> _S:
        ...
