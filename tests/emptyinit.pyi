# flags: --select=Y090
class C:
    def __init__(self, x: int) -> None:
        self.x = x  # Y090 Use explicit attributes instead of assignments in __init__
