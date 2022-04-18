import types
import typing
from collections.abc import Awaitable
from types import TracebackType
from typing import (  # Y022 Use "type[MyClass]" instead of "typing.Type[MyClass]" (PEP 585 syntax)
    Any,
    Type,
)

import typing_extensions

# Good __(a)exit__ methods
class One:
    def __exit__(self, *args: object) -> None: ...
    async def __aexit__(self, *args) -> str: ...

class Two:
    def __exit__(self, typ: type[BaseException] | None, *args: object) -> bool | None: ...
    async def __aexit__(self, typ: Type[BaseException] | None, *args: object) -> bool: ...

class Three:
    def __exit__(self, __typ: typing.Type[BaseException] | None, exc: BaseException | None, *args: object) -> None: ...  # Y022 Use "type[MyClass]" instead of "typing.Type[MyClass]" (PEP 585 syntax)
    async def __aexit__(self, typ: typing_extensions.Type[BaseException] | None, __exc: BaseException | None, *args: object) -> None: ...  # Y022 Use "type[MyClass]" instead of "typing_extensions.Type[MyClass]" (PEP 585 syntax)

class Four:
    def __exit__(self, typ: type[BaseException] | None, exc: BaseException | None, tb: TracebackType | None) -> None: ...
    async def __aexit__(self, typ: type[BaseException] | None, exc: BaseException | None, tb: types.TracebackType | None, *args: list[None]) -> None: ...

class Five:
    def __exit__(self, typ: type[BaseException] | None, exc: BaseException | None, tb: TracebackType | None, weird_extra_arg: int = ..., *args: int, **kwargs: str) -> None: ...
    def __aexit__(self, typ: type[BaseException] | None, exc: BaseException | None, tb: TracebackType | None) -> Awaitable[None]: ...

class FiveAndAHalf:
    def __exit__(self, typ: object, exc: object, tb: object) -> None: ...
    async def __aexit__(self, typ: object, exc: object, tb: object) -> None: ...

def __exit__(foo: str, bar: int) -> list[str]: ...
async def __aexit__(spam: bytes, eggs: dict[str, Any]) -> set[int]: ...

# Bad __(a)exit__ methods
class Six:
    def __exit__(self, *args: Any) -> None: ...  # Y036 Badly defined __exit__ method: Star-args in an __exit__ method should be annotated with "object", not "Any"
    async def __aexit__(self) -> None: ...  # Y036 Badly defined __aexit__ method: If there are no star-args, there should be at least 3 non-keyword-only args in an __aexit__ method (excluding "self")

class Seven:
    def __exit__(self, typ, exc, tb, weird_extra_arg) -> None: ...  # Y036 Badly defined __exit__ method: All arguments after the first 4 in an __exit__ method must have a default value
    async def __aexit__(self, typ, exc, tb, *, weird_extra_arg) -> None: ...  # Y036 Badly defined __aexit__ method: All keyword-only arguments in an __aexit__ method must have a default value

class Eight:
    def __exit__(self, typ: type[BaseException], exc: BaseException | None, tb: TracebackType | None) -> None: ...  # Y036 Badly defined __exit__ method: The first arg in an __exit__ method should be annotated with "type[BaseException] | None" or "object", not "type[BaseException]"
    async def __aexit__(self, __typ: type[BaseException] | None, __exc: BaseException, __tb: TracebackType) -> bool | None: ...  # Y036 Badly defined __aexit__ method: The second arg in an __aexit__ method should be annotated with "BaseException | None" or "object", not "BaseException"  # Y036 Badly defined __aexit__ method: The third arg in an __aexit__ method should be annotated with "types.TracebackType | None" or "object", not "TracebackType"

class Nine:
    def __exit__(self, typ: BaseException | None, *args: list[str]) -> bool: ...  # Y036 Badly defined __exit__ method: Star-args in an __exit__ method should be annotated with "object", not "list[str]"  # Y036 Badly defined __exit__ method: The first arg in an __exit__ method should be annotated with "type[BaseException] | None" or "object", not "BaseException | None"
    def __aexit__(self, *args: Any) -> Awaitable[None]: ...  # Y036 Badly defined __aexit__ method: Star-args in an __aexit__ method should be annotated with "object", not "Any"
