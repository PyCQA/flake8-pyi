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

class Foo1:
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

def f1(x: Incomplete | None = None): ...  # Y067 Use "=None" instead of "Incomplete | None = None"
def f2(x: Incomplete | None): ...
def f3(x: Incomplete | int = None): ...
def f4(x: None = None): ...

class Foo2:
    def f1(self, x: Incomplete | None = None): ...  # Y067 Use "=None" instead of "Incomplete | None = None"
    def f2(self, x: Incomplete | None): ...
    def f3(self, x: Incomplete | int = None): ...
    def f4(self, x: None = None): ...

a1: Incomplete | None = None
a2: Incomplete | None
a3: Incomplete | int
a4: None = None
