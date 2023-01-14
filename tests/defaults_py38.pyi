def f(x: "int", /) -> None: ...  # Y020 Quoted annotations should never be used in stubs
def f1(x: int, /) -> None: ...
def f2(x: int, /, y: "int") -> None: ...  # Y020 Quoted annotations should never be used in stubs
def f3(x: str = "y", /) -> None: ...  # Y011 Default values for typed arguments must be "..."
