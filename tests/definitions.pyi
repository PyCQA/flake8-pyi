from typing import TypeAlias

class _SpecialForm: ...

Protocol: _SpecialForm
class MyProtocol(Protocol): ...

class WorkingSet:
    def require(self) -> None: ...

working_set: WorkingSet
require: TypeAlias = working_set.require
