# flags: --no-pyi-aware-file-checker --extend-ignore=Y037
import sys
from typing import TypeAlias, Union

ManyStr: TypeAlias = list[EitherStr]  # F821 undefined name 'EitherStr'
EitherStr: TypeAlias = Union[str, bytes]
# The following line reports "F821 undefined name 'EitherStr'" on Python 3.14+
# but not on earlier versions.
# def function(accepts: EitherStr) -> None: ...  # F821 undefined name 'EitherStr'

del EitherStr  # private name, not exported
