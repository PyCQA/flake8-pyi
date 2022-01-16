# flags: --select=Y017,Y093
from typing import TypeAlias, ParamSpec as _ParamSpec, _Alias, TypedDict

X = int  # Y093 Use typing_extensions.TypeAlias for type aliases
X: TypeAlias = int

a = b = int  # Y017 Only simple assignments allowed
a.b = int  # Y017 Only simple assignments allowed

_P = _ParamSpec("_P")
List = _Alias()

TD = TypedDict("TD", {"in": bool})
