# flags: --no-pyi-aware-file-checker --extend-ignore=Y037
import sys
from typing import TypeAlias, Union

ManyStr: TypeAlias = list[EitherStr]  # F821 undefined name 'EitherStr'
EitherStr: TypeAlias = Union[str, bytes]
if sys.version_info >= (3, 14):
    def function(accepts: EitherStr) -> None: ...  # F821 undefined name 'EitherStr'
else:
    def function(accepts: EitherStr) -> None: ...

del EitherStr  # private name, not exported
