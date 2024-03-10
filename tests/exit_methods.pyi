# flags: --extend-ignore=Y022

import builtins
import types
import typing
from collections.abc import Awaitable
from types import TracebackType
from typing import Any, Type

import _typeshed
import typing_extensions
from _typeshed import Unused

# Good __(a)exit__ methods
class GoodOne:
    def __exit__(self, *args: object) -> None: ...
    async def __aexit__(self, *args) -> str: ...

class GoodTwo:
    def __exit__(self, typ: type[builtins.BaseException] | None, *args: builtins.object) -> bool | None: ...
    async def __aexit__(self, typ: Type[BaseException] | None, *args: object) -> bool: ...

class GoodThree:
    def __exit__(self, typ: typing.Type[BaseException] | None, /, exc: BaseException | None, *args: object) -> None: ...
    async def __aexit__(self, typ: typing_extensions.Type[BaseException] | None, __exc: BaseException | None, *args: object) -> None: ...

class GoodFour:
    def __exit__(self, typ: type[BaseException] | None, exc: BaseException | None, tb: TracebackType | None) -> None: ...
    async def __aexit__(self, typ: type[BaseException] | None, exc: BaseException | None, tb: types.TracebackType | None, *args: list[None]) -> None: ...

class GoodFive:
    def __exit__(self, typ: type[BaseException] | None, exc: BaseException | None, tb: TracebackType | None, weird_extra_arg: int = ..., *args: int, **kwargs: str) -> None: ...
    def __aexit__(self, typ: type[BaseException] | None, exc: BaseException | None, tb: TracebackType | None) -> Awaitable[None]: ...

class GoodFiveAndAHalf:
    def __exit__(self, typ: object, exc: builtins.object, tb: object) -> None: ...
    async def __aexit__(self, typ: object, exc: object, tb: builtins.object) -> None: ...

class GoodSix:
    def __exit__(self, *args: Unused) -> bool: ...
    def __aexit__(self, typ: Type[BaseException] | None, *args: _typeshed.Unused) -> Awaitable[None]: ...

class GoodSeven:
    def __exit__(self, typ: typing.Type[BaseException] | None, /, exc: BaseException | None, *args: _typeshed.Unused) -> bool: ...
    def __aexit__(self, typ: type[BaseException] | None, exc: BaseException | None, tb: TracebackType | None, weird_extra_arg: int = ..., *args: Unused, **kwargs: Unused) -> Awaitable[None]: ...


# Bad __(a)exit__ methods
class BadOne:
    def __exit__(self, *args: Any) -> None: ...  # Y036 Badly defined __exit__ method: Star-args in an __exit__ method should be annotated with "object", not "Any"
    async def __aexit__(self) -> None: ...  # Y036 Badly defined __aexit__ method: If there are no star-args, there should be at least 3 non-keyword-only args in an __aexit__ method (excluding "self")

class BadTwo:
    def __exit__(self, typ, exc, tb, weird_extra_arg) -> None: ...  # Y036 Badly defined __exit__ method: All arguments after the first 4 in an __exit__ method must have a default value
    async def __aexit__(self, typ, exc, tb, *, weird_extra_arg) -> None: ...  # Y036 Badly defined __aexit__ method: All keyword-only arguments in an __aexit__ method must have a default value

class BadThree:
    def __exit__(self, typ: type[BaseException], exc: BaseException | None, tb: TracebackType | None) -> None: ...  # Y036 Badly defined __exit__ method: The first arg in an __exit__ method should be annotated with "type[BaseException] | None" or "object", not "type[BaseException]"
    async def __aexit__(self, typ: type[BaseException] | None, exc: BaseException, tb: TracebackType, /) -> bool | None: ...  # Y036 Badly defined __aexit__ method: The second arg in an __aexit__ method should be annotated with "BaseException | None" or "object", not "BaseException"  # Y036 Badly defined __aexit__ method: The third arg in an __aexit__ method should be annotated with "types.TracebackType | None" or "object", not "TracebackType"

class BadFour:
    def __exit__(self, typ: BaseException | None, *args: list[str]) -> bool: ...  # Y036 Badly defined __exit__ method: Star-args in an __exit__ method should be annotated with "object", not "list[str]"  # Y036 Badly defined __exit__ method: The first arg in an __exit__ method should be annotated with "type[BaseException] | None" or "object", not "BaseException | None"
    def __aexit__(self, *args: Any) -> Awaitable[None]: ...  # Y036 Badly defined __aexit__ method: Star-args in an __aexit__ method should be annotated with "object", not "Any"

class ThisExistsToTestInteractionBetweenY036AndY063:
    def __exit__(self, __typ, exc, tb, weird_extra_arg) -> None: ...  # Y036 Badly defined __exit__ method: All arguments after the first 4 in an __exit__ method must have a default value  # Y063 Use PEP-570 syntax to indicate positional-only arguments
    async def __aexit__(self, __typ: type[BaseException] | None, __exc: BaseException, __tb: TracebackType) -> bool | None: ...  # Y036 Badly defined __aexit__ method: The second arg in an __aexit__ method should be annotated with "BaseException | None" or "object", not "BaseException"  # Y036 Badly defined __aexit__ method: The third arg in an __aexit__ method should be annotated with "types.TracebackType | None" or "object", not "TracebackType"  # Y063 Use PEP-570 syntax to indicate positional-only arguments
