# flags: --no-pyi-aware-file-checker
from typing import TypeAlias, Union

ManyStr: TypeAlias = list[EitherStr]  # F821 undefined name 'EitherStr'
EitherStr: TypeAlias = Union[str, bytes]
def function(accepts: EitherStr) -> None: ...

del EitherStr  # private name, not exported
