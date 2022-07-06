# flags: --no-pyi-aware-file-checker --extend-ignore=Y037
from typing import TypeAlias, Union

ManyStr: TypeAlias = list[EitherStr]  # Y001 Name of private type alias must start with _  # F821 undefined name 'EitherStr'
_EitherStr: TypeAlias = Union[str, bytes]
def function(accepts: _EitherStr) -> None: ...

del _EitherStr  # private name, not exported
