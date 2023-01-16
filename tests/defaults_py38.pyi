import os

def f(x: "int", /) -> None: ...  # Y020 Quoted annotations should never be used in stubs
def f1(x: int, /) -> None: ...
def f2(x: int, /, y: "int") -> None: ...  # Y020 Quoted annotations should never be used in stubs
def f3(x: str = "y", /) -> None: ...
def f4(x: str = os.pathsep, /) -> None: ...  # Y011 Only simple default values allowed for typed arguments
