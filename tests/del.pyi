# flags: --extend-ignore=Y037
from typing import TypeAlias, Union

ManyStr: TypeAlias = list[EitherStr]  # Y042 Name of private type alias must start with _
EitherStr: TypeAlias = Union[str, bytes]  # Y042 Name of private type alias must start with _

def function(accepts: EitherStr) -> None: ...
del EitherStr  # private name, not exported
