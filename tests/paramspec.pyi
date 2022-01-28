import collections.abc
import typing
from typing import Any, Callable, ParamSpec, TypeVar

_P = ParamSpec("_P")
_T = TypeVar("_T")
_R = TypeVar("_R")

# GOOD FUNCTIONS
def func() -> None: ...
def func1(arg: int) -> str: ...
def func2(arg: Callable[[int], str]) -> Callable[[str], int]: ...
def func3(arg: Callable[..., str]) -> Callable[[str], str]: ...
def func4(arg: Callable[[str], str]) -> Callable[..., str]: ...
def func5(arg: Callable[[str], _R]) -> Callable[[str], _R]: ...
def func6(arg: Callable[[_T], str]) -> Callable[[_T], int]: ...
def func7(arg: Callable[_P, _R]) -> Callable[_P, _R]: ...
def func8(func: Callable[..., _R], *args: str, **kwargs: int) -> _R: ...
def func9(func: Callable[..., _R], *args: Any, **kwargs: int) -> _R: ...
def func10(func: Callable[..., _R], *args: str, **kwargs: Any) -> _R: ...
def func11(func: Callable[_P, _R], *args: _P.args, **kwargs: _P.kwargs) -> _R: ...
def func12(func: Callable[_P, str], *args: _P.args, **kwargs: _P.kwargs) -> int: ...
def func13(func: typing.Callable[_P, str], *args: _P.args, **kwargs: _P.kwargs) -> int: ...
def func14(func: collections.abc.Callable[_P, str], *args: _P.args, **kwargs: _P.kwargs) -> int: ...

# BAD FUNCTIONS
def func15(arg: Callable[..., int]) -> Callable[..., str]: ...  # Y032 Consider using ParamSpec to annotate function "func15"
def func16(arg: Callable[..., _R]) -> Callable[..., _R]: ...  # Y032 Consider using ParamSpec to annotate function "func16"
def func17(arg: Callable[..., _R], *args: Any, **kwargs: Any) -> _R: ...  # Y032 Consider using ParamSpec to annotate function "func17"
def func18(arg: Callable[..., str], *args: Any, **kwargs: Any) -> int: ...  # Y032 Consider using ParamSpec to annotate function "func18"
def func19(arg: collections.abc.Callable[..., str], *args: Any, **kwargs: Any) -> int: ...  # Y032 Consider using ParamSpec to annotate function "func19"
def func20(arg: typing.Callable[..., str], *args: typing.Any, **kwargs: typing.Any) -> int: ...  # Y032 Consider using ParamSpec to annotate function "func20"
def func21(arg: collections.abc.Callable[..., str], *args: typing.Any, **kwargs: typing.Any) -> int: ...  # Y032 Consider using ParamSpec to annotate function "func21"

class Foo:
    def __call__(self, func: Callable[..., _R], *args: Any, **kwargs: Any) -> _R: ...  # Y032 Consider using ParamSpec to annotate function "Foo.__call__"
