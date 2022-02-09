# flags: --no-pyi-aware-file-checker
from typing import TypeAlias, Union

__all__ = ["foo"]  # F822 undefined name 'foo' in __all__

ManyStr: TypeAlias = list[EitherStr]  # F821 undefined name 'EitherStr'
EitherStr: TypeAlias = Union[str, bytes]
def function(accepts: EitherStr) -> None: ...

del EitherStr  # private name, not exported

class _SpecialForm: ...
Protocol: _SpecialForm

class Bar(Protocol): ...  # F821 undefined name 'Protocol'

class WorkingSet:
    def require(self) -> None: ...

working_set: WorkingSet
require: TypeAlias = working_set.require  # F821 undefined name 'working_set'
