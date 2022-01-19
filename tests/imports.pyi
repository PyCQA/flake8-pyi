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
from typing import Dict  # Y022 Use "builtins.dict" instead of "typing.Dict"
from typing import Counter  # Y022 Use "collections.Counter" instead of "typing.Counter"
from typing import AsyncContextManager  # Y022 Use "contextlib.AbstractAsyncContextManager" instead of "typing.AsyncContextManager"
from typing import ChainMap  # Y022 Use "collections.ChainMap" instead of "typing.ChainMap"
from typing_extensions import Type  # Y022 Use "builtins.type" instead of "typing_extensions.Type"
from typing_extensions import DefaultDict  # Y022 Use "collections.defaultdict" instead of "typing_extensions.DefaultDict"
from typing_extensions import ChainMap  # Y022 Use "collections.ChainMap" instead of "typing_extensions.ChainMap"
from typing_extensions import AsyncContextManager  # Y022 Use "contextlib.AbstractAsyncContextManager" instead of "typing_extensions.AsyncContextManager"

# BAD IMPORTS (Y023 code)
from typing_extensions import ClassVar  # Y023 Use "typing.ClassVar" instead of "typing_extensions.ClassVar"
from typing_extensions import Awaitable  # Y023 Use "typing.Awaitable" instead of "typing_extensions.Awaitable"
from typing_extensions import ContextManager  # Y023 Use "contextlib.AbstractContextManager" (or "typing.ContextManager" in Python 2-compatible code) instead of "typing_extensions.ContextManager"

# BAD IMPORTS (Y027 code)
from typing import ContextManager  # Y027 Use "contextlib.AbstractContextManager" instead of "typing.ContextManager"
from typing import OrderedDict  # Y027 Use "collections.OrderedDict" instead of "typing.OrderedDict"
from typing_extensions import OrderedDict  # Y027 Use "collections.OrderedDict" instead of "typing_extensions.OrderedDict"

# BAD IMPORTS: OTHER
from collections import namedtuple  # Y024 Use "typing.NamedTuple" instead of "collections.namedtuple"
from collections.abc import Set  # Y025 Use "from collections.abc import Set as AbstractSet" to avoid confusion with "builtins.set"

# GOOD ATTRIBUTE ACCESS
foo: typing.SupportsIndex

@typing_extensions.final
def bar(arg: collections.abc.Sized) -> typing_extensions.Literal[True]:
    ...


class Fish:
    blah: collections.deque[int]

    def method(self, arg: typing.SupportsInt = ...) -> None:
        ...


# BAD ATTRIBUTE ACCESS (Y022 code)
a: typing.Dict[str, int]  # Y022 Use "builtins.dict" instead of "typing.Dict"

def func1() -> typing.Counter[float]:  # Y022 Use "collections.Counter" instead of "typing.Counter"
    ...


def func2(c: typing.AsyncContextManager[None]) -> None:  # Y022 Use "contextlib.AbstractAsyncContextManager" instead of "typing.AsyncContextManager"
    ...


def func3(d: typing.ChainMap[int, str] = ...) -> None:  # Y022 Use "collections.ChainMap" instead of "typing.ChainMap"
    ...


class Spam:
    def meth1() -> typing_extensions.DefaultDict[bytes, bytes]:  # Y022 Use "collections.defaultdict" instead of "typing_extensions.DefaultDict"
        ...

    def meth2(self, f: typing_extensions.ChainMap[str, str]) -> None:  # Y022 Use "collections.ChainMap" instead of "typing_extensions.ChainMap"
        ...

    def meth3(self, g: typing_extensions.AsyncContextManager[Any] = ...) -> None:  # Y022 Use "contextlib.AbstractAsyncContextManager" instead of "typing_extensions.AsyncContextManager"
        ...


# BAD ATTRIBUTE ACCESS (Y023 code)
class Foo:
    attribute: typing_extensions.ClassVar[int]  # Y023 Use "typing.ClassVar" instead of "typing_extensions.ClassVar"


h: typing_extensions.Awaitable[float]  # Y023 Use "typing.Awaitable" instead of "typing_extensions.Awaitable"
i: typing_extensions.ContextManager[None]  # Y023 Use "contextlib.AbstractContextManager" (or "typing.ContextManager" in Python 2-compatible code) instead of "typing_extensions.ContextManager"

# BAD ATTRIBUTE ACCESS (Y027 code)
k: typing_extensions.OrderedDict[int, str]  # Y027 Use "collections.OrderedDict" instead of "typing_extensions.OrderedDict"
l: typing.ContextManager  # Y027 Use "contextlib.AbstractContextManager" instead of "typing.ContextManager"

# BAD ATTRIBUTE ACCESS: OTHER
j: collections.namedtuple  # Y024 Use "typing.NamedTuple" instead of "collections.namedtuple"
