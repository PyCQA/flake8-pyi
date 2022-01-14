def empty(x: int) -> float:
    ...

def passing(x: int) -> float:
    pass  # Y009 Empty body should contain "...", not "pass"

def raising(x: int) -> float:
    raise TypeError

class GoodClass:
    def __init__(self, x: int) -> None:
        self.x = x

class BadClass:
    def __init__(self, b: GoodClass, x: int) -> None:
        b.x = x

def returning(x: int) -> float:
    return x / 2  # Y010 Function body must contain only "..."

def multiple_ellipses(x: int) -> float:
    ...
    ...  # Y010 Function body must contain only "..."
