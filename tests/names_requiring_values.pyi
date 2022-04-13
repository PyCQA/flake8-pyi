__all__: list[str]  # Y035 "__all__" in a stub file must have a value, as it has the same semantics as "__all__" at runtime.
__all__: list[str] = ["foo", "bar", "baz"]
__all__ = ["foo", "bar", "baz"]
__match_args__: list[int]

foo: int = ...
bar: str = ...
baz: list[set[bytes]] = ...

class Foo:
    __all__: list[str]
    __match_args__: tuple[str, ...]  # Y035 "__match_args__" in a stub file must have a value, as it has the same semantics as "__match_args__" at runtime.

class Bar:
    __match_args__ = ('x', 'y')
    x: int
    y: str
