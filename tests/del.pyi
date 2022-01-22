from typing import TypeAlias, Union

ManyStr: TypeAlias = list[EitherStr]
EitherStr: TypeAlias = Union[str, bytes]

def function(accepts: EitherStr) -> None: ...
del EitherStr  # private name, not exported
