# flags: --select=Y091
class Foo:
    def __init__(self) -> None:
        raise ValueError()  # Y091 Function body must not contain "raise"

    def foo(self) -> None:
        raise ValueError()  # Y091 Function body must not contain "raise"
