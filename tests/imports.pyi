# flags: --extend-ignore=F401,F811
#
# Note: DO NOT RUN ISORT ON THIS FILE.
# It's excluded in our pyproject.toml.

# GOOD IMPORTS
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
    ByteString
)
# Things that are of no use for stub files are intentionally omitted.
from typing import (
    Any,
    ClassVar,
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
    NamedTuple,
    Match,
    Pattern,
    TextIO,
    AnyStr,
    NewType,
    NoReturn,
    overload,
)
from typing_extensions import (
    Concatenate,
    Final,
    ParamSpec,
    SupportsIndex,
    final,
    Literal,
    TypeAlias,
    TypeGuard,
    Annotated,
    TypedDict,
)

# BAD IMPORTS (Y022 code)
from typing import Dict  # Y022 Use "dict[KeyType, ValueType]" instead of "typing.Dict[KeyType, ValueType]" (PEP 585 syntax)
from typing import Counter  # Y022 Use "collections.Counter[KeyType]" instead of "typing.Counter[KeyType]" (PEP 585 syntax)
from typing import AsyncContextManager  # Y022 Use "contextlib.AbstractAsyncContextManager[T]" instead of "typing.AsyncContextManager[T]" (PEP 585 syntax)
from typing import ChainMap  # Y022 Use "collections.ChainMap[KeyType, ValueType]" instead of "typing.ChainMap[KeyType, ValueType]" (PEP 585 syntax)
from typing_extensions import Type  # Y022 Use "type[MyClass]" instead of "typing_extensions.Type[MyClass]" (PEP 585 syntax)
from typing_extensions import DefaultDict  # Y022 Use "collections.defaultdict[KeyType, ValueType]" instead of "typing_extensions.DefaultDict[KeyType, ValueType]" (PEP 585 syntax)
from typing_extensions import ChainMap  # Y022 Use "collections.ChainMap[KeyType, ValueType]" instead of "typing_extensions.ChainMap[KeyType, ValueType]" (PEP 585 syntax)
from typing_extensions import AsyncContextManager  # Y022 Use "contextlib.AbstractAsyncContextManager[T]" instead of "typing_extensions.AsyncContextManager[T]" (PEP 585 syntax)

# BAD IMPORTS (Y023 code)
from typing_extensions import ClassVar  # Y023 Use "typing.ClassVar[T]" instead of "typing_extensions.ClassVar[T]"
from typing_extensions import Awaitable  # Y023 Use "collections.abc.Awaitable[T]" (or "typing.Awaitable[T]" in Python 2-compatible code) instead of "typing_extensions.Awaitable[T]"
from typing_extensions import ContextManager  # Y023 Use "contextlib.AbstractContextManager[T]" (or "typing.ContextManager[T]" in Python 2-compatible code) instead of "typing_extensions.ContextManager[T]"
from typing_extensions import runtime_checkable  # Y023 Use "typing.runtime_checkable" instead of "typing_extensions.runtime_checkable"
from typing_extensions import AsyncGenerator  # Y023 Use "collections.abc.AsyncGenerator[YieldType, SendType]" (or "typing.AsyncGenerator[YieldType, SendType]" in Python 2-compatible code) instead of "typing_extensions.AsyncGenerator[YieldType, SendType]"
from typing_extensions import Coroutine  # Y023 Use "collections.abc.Coroutine[YieldType, SendType, ReturnType]" (or "typing.Coroutine[YieldType, SendType, ReturnType]" in Python 2-compatible code) instead of "typing_extensions.Coroutine[YieldType, SendType, ReturnType]"

# BAD IMPORTS (Y027 code)
from typing import ContextManager  # Y027 Use "contextlib.AbstractContextManager[T]" instead of "typing.ContextManager[T]" (PEP 585 syntax)
from typing import OrderedDict  # Y027 Use "collections.OrderedDict[KeyType, ValueType]" instead of "typing.OrderedDict[KeyType, ValueType]" (PEP 585 syntax)
from typing_extensions import OrderedDict  # Y027 Use "collections.OrderedDict[KeyType, ValueType]" instead of "typing_extensions.OrderedDict[KeyType, ValueType]" (PEP 585 syntax)
from typing import Callable  # Y027 Use "collections.abc.Callable" instead of "typing.Callable" (PEP 585 syntax)
from typing import ByteString  # Y027 Use "collections.abc.ByteString" instead of "typing.ByteString" (PEP 585 syntax)
from typing import Container  # Y027 Use "collections.abc.Container[T]" instead of "typing.Container[T]" (PEP 585 syntax)
from typing import Hashable  # Y027 Use "collections.abc.Hashable" instead of "typing.Hashable" (PEP 585 syntax)
from typing import ItemsView  # Y027 Use "collections.abc.ItemsView[KeyType, ValueType]" instead of "typing.ItemsView[KeyType, ValueType]" (PEP 585 syntax)
from typing import Iterable  # Y027 Use "collections.abc.Iterable[T]" instead of "typing.Iterable[T]" (PEP 585 syntax)
from typing import Iterator  # Y027 Use "collections.abc.Iterator[T]" instead of "typing.Iterator[T]" (PEP 585 syntax)
from typing import KeysView  # Y027 Use "collections.abc.KeysView[KeyType]" instead of "typing.KeysView[KeyType]" (PEP 585 syntax)
from typing import Mapping  # Y027 Use "collections.abc.Mapping[KeyType, ValueType]" instead of "typing.Mapping[KeyType, ValueType]" (PEP 585 syntax)
from typing import MappingView  # Y027 Use "collections.abc.MappingView" instead of "typing.MappingView" (PEP 585 syntax)
from typing import MutableMapping  # Y027 Use "collections.abc.MutableMapping[KeyType, ValueType]" instead of "typing.MutableMapping[KeyType, ValueType]" (PEP 585 syntax)
from typing import MutableSequence  # Y027 Use "collections.abc.MutableSequence[T]" instead of "typing.MutableSequence[T]" (PEP 585 syntax)
from typing import MutableSet  # Y027 Use "collections.abc.MutableSet[T]" instead of "typing.MutableSet[T]" (PEP 585 syntax)
from typing import Sequence  # Y027 Use "collections.abc.Sequence[T]" instead of "typing.Sequence[T]" (PEP 585 syntax)
from typing import Sized  # Y027 Use "collections.abc.Sized" instead of "typing.Sized" (PEP 585 syntax)
from typing import ValuesView  # Y027 Use "collections.abc.ValuesView[ValueType]" instead of "typing.ValuesView[ValueType]" (PEP 585 syntax)
from typing import Awaitable  # Y027 Use "collections.abc.Awaitable[T]" instead of "typing.Awaitable[T]" (PEP 585 syntax)
from typing import AsyncIterator  # Y027 Use "collections.abc.AsyncIterator[T]" instead of "typing.AsyncIterator[T]" (PEP 585 syntax)
from typing import AsyncIterable  # Y027 Use "collections.abc.AsyncIterable[T]" instead of "typing.AsyncIterable[T]" (PEP 585 syntax)
from typing import Coroutine  # Y027 Use "collections.abc.Coroutine[YieldType, SendType, ReturnType]" instead of "typing.Coroutine[YieldType, SendType, ReturnType]" (PEP 585 syntax)
from typing import Collection  # Y027 Use "collections.abc.Collection[T]" instead of "typing.Collection[T]" (PEP 585 syntax)
from typing import AsyncGenerator  # Y027 Use "collections.abc.AsyncGenerator[YieldType, SendType]" instead of "typing.AsyncGenerator[YieldType, SendType]" (PEP 585 syntax)
from typing import Reversible  # Y027 Use "collections.abc.Reversible[T]" instead of "typing.Reversible[T]" (PEP 585 syntax)
from typing import Generator  # Y027 Use "collections.abc.Generator[YieldType, SendType, ReturnType]" instead of "typing.Generator[YieldType, SendType, ReturnType]" (PEP 585 syntax)

# BAD IMPORTS: OTHER
from collections import namedtuple  # Y024 Use "typing.NamedTuple" instead of "collections.namedtuple"
from collections.abc import Set  # Y025 Use "from collections.abc import Set as AbstractSet" to avoid confusion with "builtins.set"
from typing import AbstractSet  # Y038 Use "from collections.abc import Set as AbstractSet" instead of "from typing import AbstractSet" (PEP 585 syntax)

# GOOD ATTRIBUTE ACCESS
foo: typing.SupportsIndex

@typing_extensions.final
def bar(arg: collections.abc.Sized) -> typing_extensions.Literal[True]: ...

class Fish:
    blah: collections.deque[int]
    def method(self, arg: typing.SupportsInt = ...) -> None: ...

# BAD ATTRIBUTE ACCESS (Y022 code)
a: typing.Dict[str, int]  # Y022 Use "dict[KeyType, ValueType]" instead of "typing.Dict[KeyType, ValueType]" (PEP 585 syntax)

def func1() -> typing.Counter[float]: ...  # Y022 Use "collections.Counter[KeyType]" instead of "typing.Counter[KeyType]" (PEP 585 syntax)
def func2(c: typing.AsyncContextManager[None]) -> None: ...  # Y022 Use "contextlib.AbstractAsyncContextManager[T]" instead of "typing.AsyncContextManager[T]" (PEP 585 syntax)
def func3(d: typing.ChainMap[int, str] = ...) -> None: ...  # Y022 Use "collections.ChainMap[KeyType, ValueType]" instead of "typing.ChainMap[KeyType, ValueType]" (PEP 585 syntax)

class Spam:
    def meth1(self) -> typing_extensions.DefaultDict[bytes, bytes]: ...  # Y022 Use "collections.defaultdict[KeyType, ValueType]" instead of "typing_extensions.DefaultDict[KeyType, ValueType]" (PEP 585 syntax)
    def meth2(self, f: typing_extensions.ChainMap[str, str]) -> None: ...  # Y022 Use "collections.ChainMap[KeyType, ValueType]" instead of "typing_extensions.ChainMap[KeyType, ValueType]" (PEP 585 syntax)
    def meth3(self, g: typing_extensions.AsyncContextManager[Any] = ...) -> None: ...  # Y022 Use "contextlib.AbstractAsyncContextManager[T]" instead of "typing_extensions.AsyncContextManager[T]" (PEP 585 syntax)

# BAD ATTRIBUTE ACCESS (Y023 code)
class Foo:
    attribute: typing_extensions.ClassVar[int]  # Y023 Use "typing.ClassVar[T]" instead of "typing_extensions.ClassVar[T]"

h: typing_extensions.Awaitable[float]  # Y023 Use "collections.abc.Awaitable[T]" (or "typing.Awaitable[T]" in Python 2-compatible code) instead of "typing_extensions.Awaitable[T]"
i: typing_extensions.ContextManager[None]  # Y023 Use "contextlib.AbstractContextManager[T]" (or "typing.ContextManager[T]" in Python 2-compatible code) instead of "typing_extensions.ContextManager[T]"

# BAD ATTRIBUTE ACCESS (Y027 code)
k: typing_extensions.OrderedDict[int, str]  # Y027 Use "collections.OrderedDict[KeyType, ValueType]" instead of "typing_extensions.OrderedDict[KeyType, ValueType]" (PEP 585 syntax)
l: typing.ContextManager  # Y027 Use "contextlib.AbstractContextManager[T]" instead of "typing.ContextManager[T]" (PEP 585 syntax)

# BAD ATTRIBUTE ACCESS: OTHER
j: collections.namedtuple  # Y024 Use "typing.NamedTuple" instead of "collections.namedtuple"
