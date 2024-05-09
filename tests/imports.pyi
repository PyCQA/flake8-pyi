# flags: --extend-ignore=F401,F811
#
# Note: DO NOT RUN ISORT ON THIS FILE.
# It's excluded in our pyproject.toml.

# BAD IMPORTS (Y044)
from __future__ import annotations  # Y044 "from __future__ import annotations" has no effect in stub files.

# GOOD IMPORTS
import re
import typing
import typing_extensions
import collections
import collections.abc
from collections import ChainMap, Counter, OrderedDict, UserDict, UserList, UserString, defaultdict, deque
from collections.abc import (
    Awaitable,
    Coroutine,
    AsyncIterable,
    AsyncIterator,
    AsyncGenerator,
    Hashable,
    Iterable,
    Iterator,
    Generator,
    Reversible,
    Set as AbstractSet,
    Sized,
    Container,
    Callable,
    Collection,
    MutableSet,
    MutableMapping,
    MappingView,
    KeysView,
    ItemsView,
    ValuesView,
    Sequence,
    MutableSequence,
)
from re import Match, Pattern
# Things that are of no use for stub files are intentionally omitted.
from typing import (
    Any,
    ClassVar,
    Final,
    Generic,
    Protocol,
    TypeVar,
    SupportsAbs,
    SupportsBytes,
    SupportsComplex,
    SupportsFloat,
    SupportsIndex,
    SupportsInt,
    SupportsRound,
    BinaryIO,
    IO,
    Literal,
    NamedTuple,
    TextIO,
    TypedDict,
    AnyStr,
    NewType,
    NoReturn,
    final,
    overload,
)
from typing_extensions import (
    Concatenate,
    ParamSpec,
    TypeAlias,
    TypeGuard,
    Annotated,
)

# BAD IMPORTS (Y022 code)
from typing import Dict  # Y022 Use "dict[KeyType, ValueType]" instead of "typing.Dict[KeyType, ValueType]" (PEP 585 syntax)
from typing import Counter  # Y022 Use "collections.Counter[KeyType]" instead of "typing.Counter[KeyType]" (PEP 585 syntax)
from typing import AsyncContextManager  # Y022 Use "contextlib.AbstractAsyncContextManager[T]" instead of "typing.AsyncContextManager[T]" (PEP 585 syntax)
from typing import ChainMap  # Y022 Use "collections.ChainMap[KeyType, ValueType]" instead of "typing.ChainMap[KeyType, ValueType]" (PEP 585 syntax)
from typing import ContextManager  # Y022 Use "contextlib.AbstractContextManager[T]" instead of "typing.ContextManager[T]" (PEP 585 syntax)
from typing import OrderedDict  # Y022 Use "collections.OrderedDict[KeyType, ValueType]" instead of "typing.OrderedDict[KeyType, ValueType]" (PEP 585 syntax)
from typing import Callable  # Y022 Use "collections.abc.Callable" instead of "typing.Callable" (PEP 585 syntax)
from typing import Container  # Y022 Use "collections.abc.Container[T]" instead of "typing.Container[T]" (PEP 585 syntax)
from typing import Hashable  # Y022 Use "collections.abc.Hashable" instead of "typing.Hashable" (PEP 585 syntax)
from typing import ItemsView  # Y022 Use "collections.abc.ItemsView[KeyType, ValueType]" instead of "typing.ItemsView[KeyType, ValueType]" (PEP 585 syntax)
from typing import Iterable  # Y022 Use "collections.abc.Iterable[T]" instead of "typing.Iterable[T]" (PEP 585 syntax)
from typing import Iterator  # Y022 Use "collections.abc.Iterator[T]" instead of "typing.Iterator[T]" (PEP 585 syntax)
from typing import KeysView  # Y022 Use "collections.abc.KeysView[KeyType]" instead of "typing.KeysView[KeyType]" (PEP 585 syntax)
from typing import Mapping  # Y022 Use "collections.abc.Mapping[KeyType, ValueType]" instead of "typing.Mapping[KeyType, ValueType]" (PEP 585 syntax)
from typing import MappingView  # Y022 Use "collections.abc.MappingView" instead of "typing.MappingView" (PEP 585 syntax)
from typing import MutableMapping  # Y022 Use "collections.abc.MutableMapping[KeyType, ValueType]" instead of "typing.MutableMapping[KeyType, ValueType]" (PEP 585 syntax)
from typing import MutableSequence  # Y022 Use "collections.abc.MutableSequence[T]" instead of "typing.MutableSequence[T]" (PEP 585 syntax)
from typing import MutableSet  # Y022 Use "collections.abc.MutableSet[T]" instead of "typing.MutableSet[T]" (PEP 585 syntax)
from typing import Sequence  # Y022 Use "collections.abc.Sequence[T]" instead of "typing.Sequence[T]" (PEP 585 syntax)
from typing import Sized  # Y022 Use "collections.abc.Sized" instead of "typing.Sized" (PEP 585 syntax)
from typing import ValuesView  # Y022 Use "collections.abc.ValuesView[ValueType]" instead of "typing.ValuesView[ValueType]" (PEP 585 syntax)
from typing import Awaitable  # Y022 Use "collections.abc.Awaitable[T]" instead of "typing.Awaitable[T]" (PEP 585 syntax)
from typing import AsyncIterator  # Y022 Use "collections.abc.AsyncIterator[T]" instead of "typing.AsyncIterator[T]" (PEP 585 syntax)
from typing import AsyncIterable  # Y022 Use "collections.abc.AsyncIterable[T]" instead of "typing.AsyncIterable[T]" (PEP 585 syntax)
from typing import Coroutine  # Y022 Use "collections.abc.Coroutine[YieldType, SendType, ReturnType]" instead of "typing.Coroutine[YieldType, SendType, ReturnType]" (PEP 585 syntax)
from typing import Collection  # Y022 Use "collections.abc.Collection[T]" instead of "typing.Collection[T]" (PEP 585 syntax)
from typing import AsyncGenerator  # Y022 Use "collections.abc.AsyncGenerator[YieldType, SendType]" instead of "typing.AsyncGenerator[YieldType, SendType]" (PEP 585 syntax)
from typing import Reversible  # Y022 Use "collections.abc.Reversible[T]" instead of "typing.Reversible[T]" (PEP 585 syntax)
from typing import Generator  # Y022 Use "collections.abc.Generator[YieldType, SendType, ReturnType]" instead of "typing.Generator[YieldType, SendType, ReturnType]" (PEP 585 syntax)
from typing import Match  # Y022 Use "re.Match[T]" instead of "typing.Match[T]" (PEP 585 syntax)
from typing import Pattern  # Y022 Use "re.Pattern[T]" instead of "typing.Pattern[T]" (PEP 585 syntax)
from typing_extensions import Dict  # Y022 Use "dict[KeyType, ValueType]" instead of "typing_extensions.Dict[KeyType, ValueType]" (PEP 585 syntax)
from typing_extensions import Counter  # Y022 Use "collections.Counter[KeyType]" instead of "typing_extensions.Counter[KeyType]" (PEP 585 syntax)
from typing_extensions import AsyncContextManager  # Y022 Use "contextlib.AbstractAsyncContextManager[T]" instead of "typing_extensions.AsyncContextManager[T]" (PEP 585 syntax)
from typing_extensions import ChainMap  # Y022 Use "collections.ChainMap[KeyType, ValueType]" instead of "typing_extensions.ChainMap[KeyType, ValueType]" (PEP 585 syntax)
from typing_extensions import ContextManager  # Y022 Use "contextlib.AbstractContextManager[T]" instead of "typing_extensions.ContextManager[T]" (PEP 585 syntax)
from typing_extensions import OrderedDict  # Y022 Use "collections.OrderedDict[KeyType, ValueType]" instead of "typing_extensions.OrderedDict[KeyType, ValueType]" (PEP 585 syntax)
from typing_extensions import Callable  # Y022 Use "collections.abc.Callable" instead of "typing_extensions.Callable" (PEP 585 syntax)
from typing_extensions import Container  # Y022 Use "collections.abc.Container[T]" instead of "typing_extensions.Container[T]" (PEP 585 syntax)
from typing_extensions import Hashable  # Y022 Use "collections.abc.Hashable" instead of "typing_extensions.Hashable" (PEP 585 syntax)
from typing_extensions import ItemsView  # Y022 Use "collections.abc.ItemsView[KeyType, ValueType]" instead of "typing_extensions.ItemsView[KeyType, ValueType]" (PEP 585 syntax)
from typing_extensions import Iterable  # Y022 Use "collections.abc.Iterable[T]" instead of "typing_extensions.Iterable[T]" (PEP 585 syntax)
from typing_extensions import Iterator  # Y022 Use "collections.abc.Iterator[T]" instead of "typing_extensions.Iterator[T]" (PEP 585 syntax)
from typing_extensions import KeysView  # Y022 Use "collections.abc.KeysView[KeyType]" instead of "typing_extensions.KeysView[KeyType]" (PEP 585 syntax)
from typing_extensions import Mapping  # Y022 Use "collections.abc.Mapping[KeyType, ValueType]" instead of "typing_extensions.Mapping[KeyType, ValueType]" (PEP 585 syntax)
from typing_extensions import MappingView  # Y022 Use "collections.abc.MappingView" instead of "typing_extensions.MappingView" (PEP 585 syntax)
from typing_extensions import MutableMapping  # Y022 Use "collections.abc.MutableMapping[KeyType, ValueType]" instead of "typing_extensions.MutableMapping[KeyType, ValueType]" (PEP 585 syntax)
from typing_extensions import MutableSequence  # Y022 Use "collections.abc.MutableSequence[T]" instead of "typing_extensions.MutableSequence[T]" (PEP 585 syntax)
from typing_extensions import MutableSet  # Y022 Use "collections.abc.MutableSet[T]" instead of "typing_extensions.MutableSet[T]" (PEP 585 syntax)
from typing_extensions import Sequence  # Y022 Use "collections.abc.Sequence[T]" instead of "typing_extensions.Sequence[T]" (PEP 585 syntax)
from typing_extensions import Sized  # Y022 Use "collections.abc.Sized" instead of "typing_extensions.Sized" (PEP 585 syntax)
from typing_extensions import ValuesView  # Y022 Use "collections.abc.ValuesView[ValueType]" instead of "typing_extensions.ValuesView[ValueType]" (PEP 585 syntax)
from typing_extensions import Awaitable  # Y022 Use "collections.abc.Awaitable[T]" instead of "typing_extensions.Awaitable[T]" (PEP 585 syntax)
from typing_extensions import AsyncIterator  # Y022 Use "collections.abc.AsyncIterator[T]" instead of "typing_extensions.AsyncIterator[T]" (PEP 585 syntax)
from typing_extensions import AsyncIterable  # Y022 Use "collections.abc.AsyncIterable[T]" instead of "typing_extensions.AsyncIterable[T]" (PEP 585 syntax)
from typing_extensions import Coroutine  # Y022 Use "collections.abc.Coroutine[YieldType, SendType, ReturnType]" instead of "typing_extensions.Coroutine[YieldType, SendType, ReturnType]" (PEP 585 syntax)
from typing_extensions import Collection  # Y022 Use "collections.abc.Collection[T]" instead of "typing_extensions.Collection[T]" (PEP 585 syntax)
from typing_extensions import AsyncGenerator  # Y022 Use "collections.abc.AsyncGenerator[YieldType, SendType]" instead of "typing_extensions.AsyncGenerator[YieldType, SendType]" (PEP 585 syntax)
from typing_extensions import Reversible  # Y022 Use "collections.abc.Reversible[T]" instead of "typing_extensions.Reversible[T]" (PEP 585 syntax)
from typing_extensions import Generator  # Y022 Use "collections.abc.Generator[YieldType, SendType, ReturnType]" instead of "typing_extensions.Generator[YieldType, SendType, ReturnType]" (PEP 585 syntax)
from typing_extensions import Match  # Y022 Use "re.Match[T]" instead of "typing_extensions.Match[T]" (PEP 585 syntax)
from typing_extensions import Pattern  # Y022 Use "re.Pattern[T]" instead of "typing_extensions.Pattern[T]" (PEP 585 syntax)

# BAD IMPORTS (Y023 code)
from typing_extensions import ClassVar  # Y023 Use "typing.ClassVar[T]" instead of "typing_extensions.ClassVar[T]"
from typing_extensions import runtime_checkable  # Y023 Use "typing.runtime_checkable" instead of "typing_extensions.runtime_checkable"
from typing_extensions import Literal  # Y023 Use "typing.Literal" instead of "typing_extensions.Literal"
from typing_extensions import final  # Y023 Use "typing.final" instead of "typing_extensions.final"
from typing_extensions import Final  # Y023 Use "typing.Final" instead of "typing_extensions.Final"
from typing_extensions import TypedDict  # Y023 Use "typing.TypedDict" instead of "typing_extensions.TypedDict"

# BAD IMPORTS: OTHER
from collections import namedtuple  # Y024 Use "typing.NamedTuple" instead of "collections.namedtuple"
from collections.abc import Set  # Y025 Use "from collections.abc import Set as AbstractSet" to avoid confusion with "builtins.set"
from typing import AbstractSet  # Y038 Use "from collections.abc import Set as AbstractSet" instead of "from typing import AbstractSet" (PEP 585 syntax)
from typing_extensions import AbstractSet  # Y038 Use "from collections.abc import Set as AbstractSet" instead of "from typing_extensions import AbstractSet" (PEP 585 syntax)
from typing import Text  # Y039 Use "str" instead of "typing.Text"
from typing_extensions import Text  # Y039 Use "str" instead of "typing_extensions.Text"
from typing import ByteString  # Y057 Do not use typing.ByteString, which has unclear semantics and is deprecated
from collections.abc import ByteString  # Y057 Do not use collections.abc.ByteString, which has unclear semantics and is deprecated

# GOOD ATTRIBUTE ACCESS
foo: typing.SupportsIndex
baz: re.Pattern[str]
_T = typing_extensions.TypeVar("_T", default=bool | None)  # Y018 TypeVar "_T" is not used

@typing.final
def bar(arg: collections.abc.Sized) -> typing.Literal[True]: ...

class Fish:
    blah: collections.deque[int]
    def method(self, arg: typing.SupportsInt = ...) -> None: ...

# BAD ATTRIBUTE ACCESS (Y022 code)
a: typing.Dict[str, int]  # Y022 Use "dict[KeyType, ValueType]" instead of "typing.Dict[KeyType, ValueType]" (PEP 585 syntax)
h: typing_extensions.Awaitable[float]  # Y022 Use "collections.abc.Awaitable[T]" instead of "typing_extensions.Awaitable[T]" (PEP 585 syntax)
i: typing_extensions.ContextManager[None]  # Y022 Use "contextlib.AbstractContextManager[T]" instead of "typing_extensions.ContextManager[T]" (PEP 585 syntax)
k: typing_extensions.OrderedDict[int, str]  # Y022 Use "collections.OrderedDict[KeyType, ValueType]" instead of "typing_extensions.OrderedDict[KeyType, ValueType]" (PEP 585 syntax)
l: typing.ContextManager  # Y022 Use "contextlib.AbstractContextManager[T]" instead of "typing.ContextManager[T]" (PEP 585 syntax)
n: typing.Match[bytes]  # Y022 Use "re.Match[T]" instead of "typing.Match[T]" (PEP 585 syntax)

def func1() -> typing.Counter[float]: ...  # Y022 Use "collections.Counter[KeyType]" instead of "typing.Counter[KeyType]" (PEP 585 syntax)
def func2(c: typing.AsyncContextManager[None]) -> None: ...  # Y022 Use "contextlib.AbstractAsyncContextManager[T]" instead of "typing.AsyncContextManager[T]" (PEP 585 syntax)
def func3(d: typing.ChainMap[int, str] = ...) -> None: ...  # Y022 Use "collections.ChainMap[KeyType, ValueType]" instead of "typing.ChainMap[KeyType, ValueType]" (PEP 585 syntax)

class Spam:
    def meth1(self) -> typing_extensions.DefaultDict[bytes, bytes]: ...  # Y022 Use "collections.defaultdict[KeyType, ValueType]" instead of "typing_extensions.DefaultDict[KeyType, ValueType]" (PEP 585 syntax)
    def meth2(self, f: typing_extensions.ChainMap[str, str]) -> None: ...  # Y022 Use "collections.ChainMap[KeyType, ValueType]" instead of "typing_extensions.ChainMap[KeyType, ValueType]" (PEP 585 syntax)
    def meth3(self, g: typing_extensions.AsyncContextManager[Any] = ...) -> None: ...  # Y022 Use "contextlib.AbstractAsyncContextManager[T]" instead of "typing_extensions.AsyncContextManager[T]" (PEP 585 syntax)

# BAD ATTRIBUTE ACCESS (Y023 code)
@typing_extensions.final  # Y023 Use "typing.final" instead of "typing_extensions.final"
class Foo:
    attribute: typing_extensions.ClassVar[int]  # Y023 Use "typing.ClassVar[T]" instead of "typing_extensions.ClassVar[T]"
    attribute2: typing_extensions.Final[int]  # Y023 Use "typing.Final" instead of "typing_extensions.Final"

# BAD ATTRIBUTE ACCESS: OTHER
j: collections.namedtuple  # Y024 Use "typing.NamedTuple" instead of "collections.namedtuple"
m: typing.Text  # Y039 Use "str" instead of "typing.Text"
o: typing.ByteString  # Y057 Do not use typing.ByteString, which has unclear semantics and is deprecated
p: collections.abc.ByteString  # Y057 Do not use collections.abc.ByteString, which has unclear semantics and is deprecated
