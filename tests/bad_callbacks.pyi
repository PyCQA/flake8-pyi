# flags: --extend-select=Y091

import collections.abc
import typing
from collections.abc import Callable
from typing import Any

from typing_extensions import TypeAlias

def bad(
    a: Callable[[], None],  # Y091 "Callable" in argument annotations should generally have "object" as the return type, not "None"
    b: Callable[..., Any],  # Y091 "Callable" in argument annotations should generally have "object" as the return type, not "Any"
    c: typing.Callable[[str, int], typing.Any],  # Y022 Use "collections.abc.Callable" instead of "typing.Callable" (PEP 585 syntax) # Y091 "Callable" in argument annotations should generally have "object" as the return type, not "Any"
    d: collections.abc.Callable[[None], None],  # Y091 "Callable" in argument annotations should generally have "object" as the return type, not "None"
    e: int | str | tuple[Callable[[], None], int, str],  # Y091 "Callable" in argument annotations should generally have "object" as the return type, not "None"
) -> None: ...

def good(
    a: Callable[[], object],
    b: Callable[..., object],
    c: typing.Callable,  # Y022 Use "collections.abc.Callable" instead of "typing.Callable" (PEP 585 syntax)
    d: collections.abc.Callable[[None], object],
) -> None: ...

def also_good() -> Callable[[], None]: ...

_TypeAlias: TypeAlias = collections.abc.Callable[[int, str], Any]
x: _TypeAlias
y: typing.Callable[[], None]  # Y022 Use "collections.abc.Callable" instead of "typing.Callable" (PEP 585 syntax)
