def empty(x: int) -> float:
    ...

def passing(x: int) -> float:
    pass  # Y009 Empty body should contain "...", not "pass"

def raising(x: int) -> float:
    raise TypeError  # Y010 Function body must contain only "..."

class BadClass:
    def __init__(self, x: int) -> None:
        self.x = x  # Y010 Function body must contain only "..."

    async def async_assign(self, x: int) -> None:
        self.x = x  # Y010 Function body must contain only "..."

class WorseClass:
    def __init__(self, b: BadClass, x: int) -> None:
        b.x = x  # Y010 Function body must contain only "..."

def returning(x: int) -> float:
    return x / 2  # Y010 Function body must contain only "..."

def multiple_ellipses(x: int) -> float:
    ...
    ...  # Y010 Function body must contain only "..."

async def empty_async(x: int) -> float:
    ...

async def passing_async(x: int) -> float:
    pass  # Y009 Empty body should contain "...", not "pass"

async def raising_async(x: int) -> float:
    raise TypeError  # Y010 Function body must contain only "..."

async def returning_async(x: int) -> float:
    return x / 2  # Y010 Function body must contain only "..."

async def multiple_ellipses_async(x: int) -> float:
    ...
    ...  # Y010 Function body must contain only "..."
