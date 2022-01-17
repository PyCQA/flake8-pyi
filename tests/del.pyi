from typing import Union


ManyStr = list[EitherStr]
EitherStr = Union[str, bytes]


def function(accepts: EitherStr) -> None:
    ...


del EitherStr  # private name, not exported
