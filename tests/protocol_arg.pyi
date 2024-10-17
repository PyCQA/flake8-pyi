# flags: --extend-select=Y091
from typing import Protocol

class P(Protocol):
    def method1(self, arg: int) -> None: ...  # Y091 Argument "arg" to protocol method "method1" should probably not be positional-or-keyword. Make it positional-only, since usually you don't want to mandate a specific argument name
    def method2(self, arg: str, /) -> None: ...
    def method3(self, *, arg: str) -> None: ...
    def method4(self, arg: int, /) -> None: ...
    def method5(self, arg: int, /, *, foo: str) -> None: ...
    # Ensure Y091 recognizes this as pos-only for the benefit of users still
    # using the old syntax.
    def method6(self, __arg: int) -> None: ...  # Y063 Use PEP-570 syntax to indicate positional-only arguments
    @staticmethod
    def smethod1(arg: int) -> None: ...  # Y091 Argument "arg" to protocol method "smethod1" should probably not be positional-or-keyword. Make it positional-only, since usually you don't want to mandate a specific argument name
