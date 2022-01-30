# NOTE: F401 & F811 are ignored in this file in the .flake8 config file

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
    Callable,
    ClassVar,
    Generic,
    Optional,
    Protocol,
    TypeVar,
    Union,
    AbstractSet,
    ByteString,
    Container,
    Hashable,
    ItemsView,
    Iterable,
    Iterator,
    KeysView,
    Mapping,
    MappingView,
    MutableMapping,
    MutableSequence,
    MutableSet,
    Sequence,
    Sized,
    ValuesView,
    Awaitable,
    AsyncIterator,
    AsyncIterable,
    Coroutine,
    Collection,
    AsyncGenerator,
    Reversible,
    SupportsAbs,
    SupportsBytes,
    SupportsComplex,
    SupportsFloat,
    SupportsIndex,
    SupportsInt,
    SupportsRound,
    Generator,
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
from typing_extensions import Awaitable  # Y023 Use "typing.Awaitable[T]" instead of "typing_extensions.Awaitable[T]"
from typing_extensions import ContextManager  # Y023 Use "contextlib.AbstractContextManager[T]" (or "typing.ContextManager[T]" in Python 2-compatible code) instead of "typing_extensions.ContextManager[T]" (PEP 585 syntax)
from typing_extensions import runtime_checkable  # Y023 Use "typing.runtime_checkable" instead of "typing_extensions.runtime_checkable"
from typing_extensions import AsyncGenerator  # Y023 Use "typing.AsyncGenerator[YieldType, SendType]" instead of "typing_extensions.AsyncGenerator[YieldType, SendType]"
from typing_extensions import Coroutine  # Y023 Use "typing.Coroutine[YieldType, SendType, ReturnType]" instead of "typing_extensions.Coroutine[YieldType, SendType, ReturnType]"

# BAD IMPORTS (Y027 code)
from typing import ContextManager  # Y027 Use "contextlib.AbstractContextManager[T]" instead of "typing.ContextManager[T]" (PEP 585 syntax)
from typing import OrderedDict  # Y027 Use "collections.OrderedDict[KeyType, ValueType]" instead of "typing.OrderedDict[KeyType, ValueType]" (PEP 585 syntax)
from typing_extensions import OrderedDict  # Y027 Use "collections.OrderedDict[KeyType, ValueType]" instead of "typing_extensions.OrderedDict[KeyType, ValueType]" (PEP 585 syntax)

# BAD IMPORTS: OTHER
from collections import namedtuple  # Y024 Use "typing.NamedTuple" instead of "collections.namedtuple"
from collections.abc import Set  # Y025 Use "from collections.abc import Set as AbstractSet" to avoid confusion with "builtins.set"

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

h: typing_extensions.Awaitable[float]  # Y023 Use "typing.Awaitable[T]" instead of "typing_extensions.Awaitable[T]"
i: typing_extensions.ContextManager[None]  # Y023 Use "contextlib.AbstractContextManager[T]" (or "typing.ContextManager[T]" in Python 2-compatible code) instead of "typing_extensions.ContextManager[T]" (PEP 585 syntax)

# BAD ATTRIBUTE ACCESS (Y027 code)
k: typing_extensions.OrderedDict[int, str]  # Y027 Use "collections.OrderedDict[KeyType, ValueType]" instead of "typing_extensions.OrderedDict[KeyType, ValueType]" (PEP 585 syntax)
l: typing.ContextManager  # Y027 Use "contextlib.AbstractContextManager[T]" instead of "typing.ContextManager[T]" (PEP 585 syntax)

# BAD ATTRIBUTE ACCESS: OTHER
j: collections.namedtuple  # Y024 Use "typing.NamedTuple" instead of "collections.namedtuple"
