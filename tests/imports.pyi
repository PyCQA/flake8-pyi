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
    ContextManager  # ContextManager must be importable from typing (but not typing_extensions) for Python 2 compabitility
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
    OrderedDict  # OrderedDict must be importable from typing_extensions (but not typing) for Python 2 compatibility
)


# BAD IMPORTS (Y022 code)
from typing import Dict  # Y022 Use "builtins.dict" instead of "typing.Dict"
from typing import Counter  # Y022 Use "collections.Counter" instead of "typing.Counter"
from typing import AsyncContextManager  # Y022 Use "contextlib.AbstractAsyncContextManager" instead of "typing.AsyncContextManager"
from typing import ChainMap  # Y022 Use "collections.ChainMap" instead of "typing.ChainMap"
from typing_extensions import DefaultDict  # Y022 Use "collections.defaultdict" instead of "typing_extensions.DefaultDict"
from typing_extensions import ChainMap  # Y022 Use "collections.ChainMap" instead of "typing_extensions.ChainMap"
from typing_extensions import AsyncContextManager  # Y022 Use "contextlib.AbstractAsyncContextManager" instead of "typing_extensions.AsyncContextManager"

# BAD IMPORTS (Y023 code)
from typing_extensions import ClassVar  # Y023 Use "typing.ClassVar" instead of "typing_extensions.ClassVar"
from typing_extensions import Awaitable  # Y023 Use "collections.abc.Awaitable" or "typing.Awaitable" instead of "typing_extensions.Awaitable"
from typing_extensions import ContextManager  # Y023 Use "contextlib.AbstractContextManager" or "typing.ContextManager" instead of "typing_extensions.ContextManager"

# BAD IMPORTS: OTHER
from collections import namedtuple  # Y024 Use "typing.NamedTuple" instead of "collections.namedtuple"
from collections.abc import Set  # Y025 Use "from collections.abc import Set as AbstractSet" to avoid confusion with "builtins.set"

# GOOD ATTRIBUTE ACCESS
foo: typing.SupportsIndex
bar: typing_extensions.Final[int]
baz: collections.abc.Sized
blah: collections.deque[int]

# BAD ATTRIBUTE ACCESS (Y022 code)
a: typing.Dict[str, int]  # Y022 Use "builtins.dict" instead of "typing.Dict"
b: typing.Counter[float]  # Y022 Use "collections.Counter" instead of "typing.Counter"
c: typing.AsyncContextManager[None]  # Y022 Use "contextlib.AbstractAsyncContextManager" instead of "typing.AsyncContextManager"
d: typing.ChainMap[int, str]  # Y022 Use "collections.ChainMap" instead of "typing.ChainMap"
e: typing_extensions.DefaultDict[bytes, bytes]  # Y022 Use "collections.defaultdict" instead of "typing_extensions.DefaultDict"
f: typing_extensions.ChainMap[str, str]  # Y022 Use "collections.ChainMap" instead of "typing_extensions.ChainMap"
g: typing_extensions.AsyncContextManager[Any]  # Y022 Use "contextlib.AbstractAsyncContextManager" instead of "typing_extensions.AsyncContextManager"

# BAD ATTRIBUTE ACCESS (Y023 code)
class Foo:
    attribute: typing_extensions.ClassVar[int]  # Y023 Use "typing.ClassVar" instead of "typing_extensions.ClassVar"


h: typing_extensions.Awaitable[float]  # Y023 Use "collections.abc.Awaitable" or "typing.Awaitable" instead of "typing_extensions.Awaitable"
i: typing_extensions.ContextManager[None]  # Y023 Use "contextlib.AbstractContextManager" or "typing.ContextManager" instead of "typing_extensions.ContextManager"

# BAD ATTRIBUTE ACCESS: OTHER
j: collections.namedtuple  # Y024 Use "typing.NamedTuple" instead of "collections.namedtuple"
