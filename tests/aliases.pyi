import typing
from typing import ParamSpec as _ParamSpec, TypeAlias, TypedDict, _Alias

import typing_extensions

X = int  # Y026 Use typing_extensions.TypeAlias for type aliases
X: TypeAlias = int
Y: typing.TypeAlias = int
Z: typing_extensions.TypeAlias = int

a = b = int  # Y017 Only simple assignments allowed
a.b = int  # Y017 Only simple assignments allowed

_P = _ParamSpec("_P")
List = _Alias()

TD = TypedDict("TD", {"in": bool})
