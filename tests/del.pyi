from typing import List, Union


ManyStr = List[EitherStr]
EitherStr = Union[str, bytes]


def function(accepts: EitherStr) -> None:
    ...


del EitherStr  # private name, not exported
