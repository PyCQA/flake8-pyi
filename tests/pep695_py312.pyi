# Temporary workaround until pyflakes supports PEP 695:
# flags: --extend-ignore=F821

import typing
from collections.abc import Iterator
from typing import (
    Annotated,
    Any,
    Literal,
    NamedTuple,
    NoReturn,
    Protocol,
    Self,
    TypedDict,
)

type lowercase_alias = str | int  # Y042 Type aliases should use the CamelCase naming convention
type _LooksLikeATypeVarT = str | int  # Y043 Bad name for a type alias (the "T" suffix implies a TypeVar)
type _Unused = str | int  # Y047 Type alias "_Unused" is not used
type _List[T] = list[T]

y: _List[int]
x: _LooksLikeATypeVarT

class GenericPEP695Class[T]:
    def __init__(self, x: int) -> None:
        self.x = x  # Y010 Function body must contain only "..."
    def __new__(cls, *args: Any, **kwargs: Any) -> GenericPEP695Class: ...  # Y034 "__new__" methods usually return "self" at runtime. Consider using "typing_extensions.Self" in "GenericPEP695Class.__new__", e.g. "def __new__(cls, *args: Any, **kwargs: Any) -> Self: ..."
    def __repr__(self) -> str: ...  # Y029 Defining __repr__ or __str__ in a stub is almost always redundant
    def __eq__(self, other: Any) -> bool: ...  # Y032 Prefer "object" to "Any" for the second parameter in "__eq__" methods
    def method(self) -> T: ...
    ...  # Y013 Non-empty class body must not contain "..."
    pass  # Y012 Class body must not contain "pass"
    def __exit__(self, *args: Any) -> None: ...  # Y036 Badly defined __exit__ method: Star-args in an __exit__ method should be annotated with "object", not "Any"
    async def __aexit__(self) -> None: ...  # Y036 Badly defined __aexit__ method: If there are no star-args, there should be at least 3 non-keyword-only args in an __aexit__ method (excluding "self")
    def never_call_me(self, arg: NoReturn) -> None: ...  # Y050 Use "typing_extensions.Never" instead of "NoReturn" for argument annotations

class GenericPEP695InheritingFromObject[T](object):  # Y040 Do not inherit from "object" explicitly, as it is redundant in Python 3
    x: T

class GenericPEP695InheritingFromIterator[T](Iterator[T]):
    def __iter__(self) -> Iterator[T]: ...  # Y034 "__iter__" methods in classes like "GenericPEP695InheritingFromIterator" usually return "self" at runtime. Consider using "typing_extensions.Self" in "GenericPEP695InheritingFromIterator.__iter__", e.g. "def __iter__(self) -> Self: ..."

class PEP695BadBody[T]:
    pass  # Y009 Empty body should contain "...", not "pass"

class PEP695Docstring[T]:
    """Docstring"""  # Y021 Docstrings should not be included in stubs
    ...  # Y013 Non-empty class body must not contain "..."

class PEP695BadDunderNew[T]:
    def __new__[S](cls: type[S], *args: Any, **kwargs: Any) -> S: ...  # Y019 Use "typing_extensions.Self" instead of "S", e.g. "def __new__(cls, *args: Any, **kwargs: Any) -> Self: ..."
    def generic_instance_method[S](self: S) -> S: ...  # Y019 Use "typing_extensions.Self" instead of "S", e.g. "def generic_instance_method(self) -> Self: ..."

class PEP695GoodDunderNew[T]:
    def __new__(cls, *args: Any, **kwargs: Any) -> Self: ...

class GenericNamedTuple[T](NamedTuple):
    foo: T

class GenericTypedDict[T](TypedDict):
    foo: T

class GenericTypingDotNamedTuple(typing.NamedTuple):
    foo: T

class GenericTypingDotTypedDict(typing.TypedDict):
    foo: T

type NoDuplicatesInThisUnion = GenericPEP695Class[str] | GenericPEP695Class[int]
type ThisHasDuplicates = GenericPEP695Class[str] | GenericPEP695Class[str]  # Y016 Duplicate union member "GenericPEP695Class[str]"

class _UnusedPEP695Protocol[T](Protocol):  # Y046 Protocol "_UnusedPEP695Protocol" is not used
    x: T

class _UnusedPEP695TypedDict[T](TypedDict):  # Y049 TypedDict "_UnusedPEP695TypedDict" is not used
    x: T

type X = Literal["Y053 will not be emitted here despite it being a very long string literal, because it is inside a `Literal` slice"]
type Y = Annotated[int, "look at me, very long string literal, but it's okay because it's an `Annotated` metadata string"]
