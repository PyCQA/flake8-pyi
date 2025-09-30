import typing
import typing as t
from typing import override
from typing import override as over

class Foo:
    def f(self) -> None: ...
    def g(self) -> None: ...
    def h(self) -> None: ...
    def j(self) -> None: ...

class Bar(Foo):
    @override
    def f(self) -> None: ...  # Y068 Do not use "@override" in stub files.
    @typing.override
    def g(self) -> None: ...  # Y068 Do not use "@override" in stub files.
    @t.override
    def h(self) -> None: ...  # Ideally we'd catch this too, but the infrastructure is not in place.
    @over
    def j(self) -> None: ...  # Ideally we'd catch this too, but the infrastructure is not in place.
