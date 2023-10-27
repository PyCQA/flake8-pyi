# flags: --extend-ignore=F401,F811
#
# Note: DO NOT RUN ISORT ON THIS FILE.
# It's excluded in our pyproject.toml.

import typing
import typing_extensions
from typing import Optional  # Y037 Use PEP 604 union types instead of typing.Optional (e.g. "int | None" instead of "Optional[int]").
from typing import Union  # Y037 Use PEP 604 union types instead of typing.Union (e.g. "int | str" instead of "Union[int, str]").
from typing_extensions import Optional  # Y037 Use PEP 604 union types instead of typing_extensions.Optional (e.g. "int | None" instead of "Optional[int]").
from typing_extensions import Union  # Y037 Use PEP 604 union types instead of typing_extensions.Union (e.g. "int | str" instead of "Union[int, str]").

x1: Optional[str]
x2: Optional
x3: Union[str, int]
x4: Union


y1: typing.Optional[str]  # Y037 Use PEP 604 union types instead of typing.Optional (e.g. "int | None" instead of "Optional[int]").
y2: typing.Optional  # Y037 Use PEP 604 union types instead of typing.Optional (e.g. "int | None" instead of "Optional[int]").
y3: typing.Union[str, int]  # Y037 Use PEP 604 union types instead of typing.Union (e.g. "int | str" instead of "Union[int, str]").
y4: typing.Union  # Y037 Use PEP 604 union types instead of typing.Union (e.g. "int | str" instead of "Union[int, str]").
y5: typing_extensions.Optional[str]  # Y037 Use PEP 604 union types instead of typing_extensions.Optional (e.g. "int | None" instead of "Optional[int]").
y6: typing_extensions.Optional  # Y037 Use PEP 604 union types instead of typing_extensions.Optional (e.g. "int | None" instead of "Optional[int]").
y7: typing_extensions.Union[str, int]  # Y037 Use PEP 604 union types instead of typing_extensions.Union (e.g. "int | str" instead of "Union[int, str]").
y8: typing_extensions.Union  # Y037 Use PEP 604 union types instead of typing_extensions.Union (e.g. "int | str" instead of "Union[int, str]").


def f1(x: Optional[str] = ...) -> None: ...
def f2() -> Optional[str]: ...
def f3() -> Union[str, int]: ...
def f4(x: Union[str, int] = ...) -> None: ...
def f5(x: Optional) -> None: ...
def f6(x: Union) -> None: ...


def g1(x: typing.Optional[str] = ...) -> None: ...  # Y037 Use PEP 604 union types instead of typing.Optional (e.g. "int | None" instead of "Optional[int]").
def g2() -> typing.Optional[str]: ...  # Y037 Use PEP 604 union types instead of typing.Optional (e.g. "int | None" instead of "Optional[int]").
def g3() -> typing.Union[str, int]: ...  # Y037 Use PEP 604 union types instead of typing.Union (e.g. "int | str" instead of "Union[int, str]").
def g4(x: typing.Union[str, int] = ...) -> None: ...  # Y037 Use PEP 604 union types instead of typing.Union (e.g. "int | str" instead of "Union[int, str]").
def g5(x: typing.Optional) -> None: ...  # Y037 Use PEP 604 union types instead of typing.Optional (e.g. "int | None" instead of "Optional[int]").
def g6(x: typing.Union) -> None: ...  # Y037 Use PEP 604 union types instead of typing.Union (e.g. "int | str" instead of "Union[int, str]").
