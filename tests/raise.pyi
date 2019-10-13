class Foo:
    def __init__(self) -> None:
        raise ValueError()  # Y091

    def foo(self) -> None:
        raise ValueError()  # Y091
