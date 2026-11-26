from __future__ import annotations

# Only used to build ``BAD_Y022_IMPORTS`` below.
_MAPPING_SLICE = "KeyType, ValueType"

# Y022: Use stdlib imports instead of aliases from typing/typing_extensions
BAD_Y022_IMPORTS: dict[str, tuple[str, str | None]] = {
    # Aliases for collections
    "Counter": ("collections.Counter", "KeyType"),
    "Deque": ("collections.deque", "T"),
    "DefaultDict": ("collections.defaultdict", _MAPPING_SLICE),
    "ChainMap": ("collections.ChainMap", _MAPPING_SLICE),
    "OrderedDict": ("collections.OrderedDict", _MAPPING_SLICE),
    # Aliases for builtins
    "Dict": ("dict", _MAPPING_SLICE),
    "FrozenSet": ("frozenset", "T"),
    "List": ("list", "T"),
    "Set": ("set", "T"),
    "Tuple": ("tuple", "Foo, Bar"),
    "Type": ("type", "MyClass"),
    # Aliases for contextlib
    "ContextManager": ("contextlib.AbstractContextManager", "T"),
    "AsyncContextManager": ("contextlib.AbstractAsyncContextManager", "T"),
    # Aliases for re
    "Match": ("re.Match", "T"),
    "Pattern": ("re.Pattern", "T"),
    # Aliases for collections.abc
    # AbstractSet and ByteString are deliberately omitted
    # (special-cased elsewhere).
    # If the second element of the tuple is `None`,
    # it signals that the object shouldn't be parameterized
    "Collection": ("collections.abc.Collection", "T"),
    "ItemsView": ("collections.abc.ItemsView", _MAPPING_SLICE),
    "KeysView": ("collections.abc.KeysView", "KeyType"),
    "Mapping": ("collections.abc.Mapping", _MAPPING_SLICE),
    "MappingView": ("collections.abc.MappingView", None),
    "MutableMapping": ("collections.abc.MutableMapping", _MAPPING_SLICE),
    "MutableSequence": ("collections.abc.MutableSequence", "T"),
    "MutableSet": ("collections.abc.MutableSet", "T"),
    "Sequence": ("collections.abc.Sequence", "T"),
    "ValuesView": ("collections.abc.ValuesView", "ValueType"),
    "Iterable": ("collections.abc.Iterable", "T"),
    "Iterator": ("collections.abc.Iterator", "T"),
    "Generator": ("collections.abc.Generator", "YieldType, SendType, ReturnType"),
    "Hashable": ("collections.abc.Hashable", None),
    "Reversible": ("collections.abc.Reversible", "T"),
    "Sized": ("collections.abc.Sized", None),
    "Coroutine": ("collections.abc.Coroutine", "YieldType, SendType, ReturnType"),
    "AsyncGenerator": ("collections.abc.AsyncGenerator", "YieldType, SendType"),
    "AsyncIterator": ("collections.abc.AsyncIterator", "T"),
    "AsyncIterable": ("collections.abc.AsyncIterable", "T"),
    "Awaitable": ("collections.abc.Awaitable", "T"),
    "Callable": ("collections.abc.Callable", None),
    "Container": ("collections.abc.Container", "T"),
}

# Y023: Import things from typing instead of typing_extensions
# if they're available from the typing module on 3.8+
BAD_TYPINGEXTENSIONS_Y023_IMPORTS = frozenset(
    {
        "Any",
        "AnyStr",
        "BinaryIO",
        "Final",
        "ForwardRef",
        "Generic",
        "IO",
        "Literal",
        "Protocol",
        "TextIO",
        "runtime_checkable",
        "NewType",
        "SupportsAbs",
        "SupportsComplex",
        "SupportsFloat",
        "SupportsIndex",
        "SupportsInt",
        "SupportsRound",
        "TypedDict",
        "final",
        "overload",
        "NoReturn",
        # ClassVar deliberately omitted,
        # as it's the only one in this group that should be parameterised.
        # It is special-cased elsewhere.
        #
        # Text/Optional/Union are also deliberately omitted,
        # as well as the various stdlib aliases in typing(_extensions),
        # as you shouldn't be importing them from anywhere! (Y039)
    }
)

TYPING_MODULES = frozenset({"typing", "typing_extensions"})
TYPING_OR_COLLECTIONS_ABC = TYPING_MODULES | {"collections.abc"}

INPLACE_BINOP_METHODS = frozenset(
    {
        "__iadd__",
        "__isub__",
        "__imul__",
        "__imatmul__",
        "__itruediv__",
        "__ifloordiv__",
        "__imod__",
        "__ipow__",
        "__ilshift__",
        "__irshift__",
        "__iand__",
        "__ixor__",
        "__ior__",
    }
)

COMMON_METACLASSES = {
    "type": "builtins",
    "ABCMeta": "abc",
    "EnumMeta": "enum",
    "EnumType": "enum",
}

NEGATABLE_MATH_ATTRIBUTES_IN_DEFAULTS = frozenset(
    {"math.inf", "math.e", "math.pi", "math.tau"}
)

ALLOWED_SIMPLE_NAMES_IN_DEFAULTS = frozenset({"sentinel"})
