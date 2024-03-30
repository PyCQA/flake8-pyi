from _typeshed import Incomplete
from typing_extensions import TypeAlias

IncompleteAlias: TypeAlias = Incomplete  # ok

att: Incomplete  # ok

def ok(x: Incomplete | None) -> list[Incomplete]: ...
def aliased(x: IncompleteAlias) -> IncompleteAlias: ...  # ok
def err1(
    x: Incomplete,  # Y065 Leave parameter "x" unannotated rather than using "Incomplete"
) -> None: ...
def err2() -> (
    Incomplete  # Y065 Leave return type unannotated rather than using "Incomplete"
): ...

class Foo:
    att: Incomplete
    def ok(self, x: Incomplete | None) -> list[Incomplete]: ...
    def err1(
        self,
        x: Incomplete,  # Y065 Leave parameter "x" unannotated rather than using "Incomplete"
    ) -> None: ...
    def err2(
        self,
    ) -> (
        Incomplete  # Y065 Leave return type unannotated rather than using "Incomplete"
    ): ...
    def __getattr__(
        self, name: str
    ) -> Incomplete: ...  # allowed in __getattr__ return type

class Bar:
    def __getattr__(
        self,
        name: Incomplete,  # Y065 Leave parameter "name" unannotated rather than using "Incomplete"
    ) -> Incomplete: ...

def __getattr__(name: str) -> Incomplete: ...  # allowed in __getattr__ return type
