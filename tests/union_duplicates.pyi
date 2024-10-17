# flags: --extend-ignore=Y037
import builtins
import typing
from collections.abc import Mapping
from typing import (  # Y022 Use "type[MyClass]" instead of "typing.Type[MyClass]" (PEP 585 syntax)
    Literal,
    Type,
    Union,
)

import typing_extensions
from typing_extensions import (  # Y022 Use "type[MyClass]" instead of "typing_extensions.Type[MyClass]" (PEP 585 syntax)
    Type as Type_,
    TypeAlias,
)

def f1_pipe(x: int | str) -> None: ...
def f2_pipe(x: int | int) -> None: ...  # Y016 Duplicate union member "int"
def f3_pipe(x: None | int | int) -> None: ...  # Y016 Duplicate union member "int"
def f4_pipe(x: int | None | int) -> None: ...  # Y016 Duplicate union member "int"
def f5_pipe(x: int | int | None) -> None: ...  # Y016 Duplicate union member "int"
def f6_pipe(x: type[int] | type[str] | type[float]) -> None: ...  # Y055 Multiple "type[Foo]" members in a union. Combine them into one, e.g. "type[int | str | float]".
def f7_pipe(x: type[int] | str | type[float]) -> None: ...  # Y055 Multiple "type[Foo]" members in a union. Combine them into one, e.g. "type[int | float]".
def f8_pipe(x: builtins.type[int] | builtins.type[str] | builtins.type[float]) -> None: ...  # Y055 Multiple "type[Foo]" members in a union. Combine them into one, e.g. "type[int | str | float]".
def f9_pipe(x: builtins.type[int] | str | builtins.type[float]) -> None: ...  # Y055 Multiple "type[Foo]" members in a union. Combine them into one, e.g. "type[int | float]".
def f10_pipe(x: type[int] | builtins.type[float]) -> None: ...  # Y055 Multiple "type[Foo]" members in a union. Combine them into one, e.g. "type[int | float]".
# typing.Type and typing_extensions.Type are intentionally excluded from Y055
# The following type annotations should not generate any Y055 errors
def f11_pipe(x: Type[int] | Type[str]) -> None: ...
def f12_pipe(x: typing.Type[int] | typing.Type[str]) -> None: ...  # Y022 Use "type[MyClass]" instead of "typing.Type[MyClass]" (PEP 585 syntax)  # Y022 Use "type[MyClass]" instead of "typing.Type[MyClass]" (PEP 585 syntax)
def f13_pipe(x: Type_[int] | Type_[str]) -> None: ...
def f14_pipe(x: typing_extensions.Type[int] | typing_extensions.Type[str]) -> None: ...  # Y022 Use "type[MyClass]" instead of "typing_extensions.Type[MyClass]" (PEP 585 syntax)  # Y022 Use "type[MyClass]" instead of "typing_extensions.Type[MyClass]" (PEP 585 syntax)

def f1_union(x: Union[int, str]) -> None: ...
def f2_union(x: Union[int, int]) -> None: ...  # Y016 Duplicate union member "int"
def f3_union(x: Union[None, int, int]) -> None: ...  # Y016 Duplicate union member "int"
def f4_union(x: typing.Union[int, None, int]) -> None: ...  # Y016 Duplicate union member "int"
def f5_union(x: typing.Union[int, int, None]) -> None: ...  # Y016 Duplicate union member "int"
def f6_union(x: Union[type[int], type[str], type[float]]) -> None: ...  # Y055 Multiple "type[Foo]" members in a union. Combine them into one, e.g. "type[Union[int, str, float]]".
def f7_union(x: Union[type[int], str, type[float]]) -> None: ...  # Y055 Multiple "type[Foo]" members in a union. Combine them into one, e.g. "type[Union[int, float]]".
def f8_union(x: Union[builtins.type[int], builtins.type[str], builtins.type[float]]) -> None: ...  # Y055 Multiple "type[Foo]" members in a union. Combine them into one, e.g. "type[Union[int, str, float]]".
def f9_union(x: Union[builtins.type[int], str, builtins.type[float]]) -> None: ...  # Y055 Multiple "type[Foo]" members in a union. Combine them into one, e.g. "type[Union[int, float]]".
def f10_union(x: Union[type[int], builtins.type[float]]) -> None: ...  # Y055 Multiple "type[Foo]" members in a union. Combine them into one, e.g. "type[Union[int, float]]".
# typing.Type and typing_extensions.Type are intentionally excluded from Y055
# The following type annotations should not generate any Y055 errors
def f11_union(x: Union[Type[int], Type[str]]) -> None: ...
def f12_union(x: Union[typing.Type[int], typing.Type[str]]) -> None: ...  # Y022 Use "type[MyClass]" instead of "typing.Type[MyClass]" (PEP 585 syntax) # Y022 Use "type[MyClass]" instead of "typing.Type[MyClass]" (PEP 585 syntax)
def f13_union(x: Union[Type_[int], Type_[str]]) -> None: ...
def f14_union(x: Union[typing_extensions.Type[int], typing_extensions.Type[str]]) -> None: ...  # Y022 Use "type[MyClass]" instead of "typing_extensions.Type[MyClass]" (PEP 585 syntax) # Y022 Use "type[MyClass]" instead of "typing_extensions.Type[MyClass]" (PEP 585 syntax)

just_literals_subscript_union: Union[Literal[1], typing.Literal[2]]  # Y030 Multiple Literal members in a union. Use a single Literal, e.g. "Literal[1, 2]".
mixed_subscript_union: Union[bytes, Literal['foo'], typing_extensions.Literal['bar']]  # Y030 Multiple Literal members in a union. Combine them into one, e.g. "Literal['foo', 'bar']". # Y023 Use "typing.Literal" instead of "typing_extensions.Literal"
just_literals_pipe_union: TypeAlias = Literal[True] | Literal['idk']  # Y042 Type aliases should use the CamelCase naming convention  # Y030 Multiple Literal members in a union. Use a single Literal, e.g. "Literal[True, 'idk']".
_mixed_pipe_union: TypeAlias = Union[Literal[966], bytes, Literal['baz']]  # Y042 Type aliases should use the CamelCase naming convention  # Y047 Type alias "_mixed_pipe_union" is not used  # Y030 Multiple Literal members in a union. Combine them into one, e.g. "Literal[966, 'baz']".
ManyLiteralMembersButNeedsCombining: TypeAlias = int | Literal['a', 'b'] | Literal['baz']  # Y030 Multiple Literal members in a union. Combine them into one, e.g. "Literal['a', 'b', 'baz']".

a: int | float  # No error here, Y041 only applies to argument annotations
b: Union[builtins.float, str, bytes, builtins.int]  # No error here, Y041 only applies to argument annotations
def func(arg: float | list[str] | type[bool] | complex) -> None: ...  # Y041 Use "complex" instead of "float | complex" (see "The numeric tower" in PEP 484)

class Foo:
    def method(self, arg: int | builtins.float | complex) -> None: ...  # Y041 Use "complex" instead of "float | complex" (see "The numeric tower" in PEP 484)  # Y041 Use "complex" instead of "int | complex" (see "The numeric tower" in PEP 484)

c: Union[builtins.complex, memoryview, slice, int]  # No error here, Y041 only applies to argument annotations

# Don't error with Y041 here, the two error messages combined are quite confusing
def foo(d: int | int | float) -> None: ...  # Y016 Duplicate union member "int"
# Don't error with Y055 here either
def baz(d: type[int] | type[int]) -> None: ...  # Y016 Duplicate union member "type[int]"

def bar(f: Literal["foo"] | Literal["bar"] | int | float | builtins.bool) -> None: ...  # Y030 Multiple Literal members in a union. Combine them into one, e.g. "Literal['foo', 'bar']".  # Y041 Use "float" instead of "int | float" (see "The numeric tower" in PEP 484)

# Type aliases are special-cased to be excluded from Y041
MyTypeAlias: TypeAlias = int | float | bool
MySecondTypeAlias: TypeAlias = Union[builtins.int, str, complex, bool]
MyThirdTypeAlias: TypeAlias = Mapping[str, int | builtins.float | builtins.bool]

one: str | Literal["foo"]  # Y051 "Literal['foo']" is redundant in a union with "str"
Two: TypeAlias = Union[Literal[b"bar", b"baz"], bytes]  # Y051 "Literal[b'bar']" is redundant in a union with "bytes"
def three(arg: Literal["foo", 5] | builtins.int | Literal[9, "bar"]) -> None: ...  # Y030 Multiple Literal members in a union. Combine them into one, e.g. "Literal['foo', 5, 9, 'bar']".  # Y051 "Literal[5]" is redundant in a union with "int"

class Four:
    var: builtins.bool | Literal[True]  # Y051 "Literal[True]" is redundant in a union with "bool"

DupesHereSoNoY051: TypeAlias = int | int | Literal[42]  # Y016 Duplicate union member "int"
NightmareAlias1 = int | float | Literal[4, b"bar"] | Literal["foo"]  # Y026 Use typing_extensions.TypeAlias for type aliases, e.g. "NightmareAlias1: TypeAlias = int | float | Literal[4, b'bar'] | Literal['foo']"  # Y030 Multiple Literal members in a union. Combine them into one, e.g. "Literal[4, b'bar', 'foo']".  # Y051 "Literal[4]" is redundant in a union with "int"
nightmare_alias2: TypeAlias = int | float | Literal[True, 4] | Literal["foo"]  # Y042 Type aliases should use the CamelCase naming convention  # Y030 Multiple Literal members in a union. Combine them into one, e.g. "Literal[True, 4, 'foo']".  # Y051 "Literal[4]" is redundant in a union with "int"
DoublyNestedAlias: TypeAlias = Union[type[str], type[float] | type[bytes]]  # Y055 Multiple "type[Foo]" members in a union. Combine them into one, e.g. "type[float | bytes]".
# typing.Type and typing_extensions.Type are intentionally excluded from Y055
DoublyNestedAlias2: TypeAlias = Union[Type[str], typing.Type[float], Type_[bytes], typing_extensions.Type[complex]]  # Y022 Use "type[MyClass]" instead of "typing.Type[MyClass]" (PEP 585 syntax) # Y022 Use "type[MyClass]" instead of "typing_extensions.Type[MyClass]" (PEP 585 syntax)
