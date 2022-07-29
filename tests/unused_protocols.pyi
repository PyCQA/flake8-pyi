import typing
from typing import Protocol

import typing_extensions

class _Foo(Protocol):  # Y046 Protocol "_Foo" is not used
    bar: int

class _Bar(typing.Protocol):  # Y046 Protocol "_Bar" is not used
    bar: int

class _Baz(typing_extensions.Protocol):  # Y046 Protocol "_Baz" is not used  # Y023 Use "typing.Protocol" instead of "typing_extensions.Protocol"
    bar: int

class UnusedButPublicProtocol(Protocol):
    bar: int

class _UsedPrivateProtocol(Protocol):
    bar: int

def uses__UsedPrivateProtocol(arg: _UsedPrivateProtocol) -> None: ...
