# flags: --no-pyi-aware-file-checker
from typing import Union


ManyStr = list[EitherStr]  # F821 undefined name 'EitherStr'
EitherStr = Union[str, bytes]


def function(accepts: EitherStr) -> None:
    ...


del EitherStr  # private name, not exported
