from __future__ import annotations

from typing import TYPE_CHECKING, NamedTuple

if TYPE_CHECKING:
    # Import is only needed for type annotations,
    # and causes a circular import if it's imported at runtime.
    from .checker import PyiTreeChecker


class Error(NamedTuple):
    lineno: int
    col: int
    message: str
    type: type[PyiTreeChecker]


# Please keep error code lists in ERRORCODES and CHANGELOG up to date
Y001 = "Y001 Name of private {} must start with _"
Y002 = (
    "Y002 If test must be a simple comparison against sys.platform or sys.version_info"
)
Y003 = "Y003 Unrecognized sys.version_info check"
Y004 = "Y004 Version comparison must use only major and minor version"
Y005 = "Y005 Version comparison must be against a length-{n} tuple"
Y006 = "Y006 Use only < and >= for version comparisons"
Y007 = "Y007 Unrecognized sys.platform check"
Y008 = 'Y008 Unrecognized platform "{platform}"'
Y009 = 'Y009 Empty body should contain "...", not "pass"'
Y010 = 'Y010 Function body must contain only "..."'
Y011 = "Y011 Only simple default values allowed for typed arguments"
Y012 = 'Y012 Class body must not contain "pass"'
Y013 = 'Y013 Non-empty class body must not contain "..."'
Y014 = "Y014 Only simple default values allowed for arguments"
Y015 = "Y015 Only simple default values are allowed for assignments"
Y016 = 'Y016 Duplicate union member "{}"'
Y017 = "Y017 Only simple assignments allowed"
Y018 = 'Y018 {typevarlike_cls} "{typevar_name}" is not used'
Y019 = (
    'Y019 Use "typing_extensions.Self" instead of "{typevar_name}", e.g. "{new_syntax}"'
)
Y020 = "Y020 Quoted annotations should never be used in stubs"
Y021 = "Y021 Docstrings should not be included in stubs"
Y022 = "Y022 Use {good_syntax} instead of {bad_syntax} (PEP 585 syntax)"
Y023 = "Y023 Use {good_syntax} instead of {bad_syntax}"
Y024 = 'Y024 Use "typing.NamedTuple" instead of "collections.namedtuple"'
Y025 = (
    'Y025 Use "from collections.abc import Set as AbstractSet" '
    'to avoid confusion with "builtins.set"'
)
Y026 = 'Y026 Use typing_extensions.TypeAlias for type aliases, e.g. "{suggestion}"'
Y028 = "Y028 Use class-based syntax for NamedTuples"
Y029 = "Y029 Defining __repr__ or __str__ in a stub is almost always redundant"
Y030 = "Y030 Multiple Literal members in a union. {suggestion}"
Y031 = "Y031 Use class-based syntax for TypedDicts where possible"
Y032 = (
    'Y032 Prefer "object" to "Any" for the second parameter in "{method_name}" methods'
)
Y033 = (
    "Y033 Do not use type comments in stubs "
    '(e.g. use "x: int" instead of "x = ... # type: int")'
)
Y034 = (
    'Y034 {methods} usually return "self" at runtime. '
    'Consider using "typing_extensions.Self" in "{method_name}", '
    'e.g. "{suggested_syntax}"'
)
Y035 = (
    'Y035 "{var}" in a stub file must have a value, '
    'as it has the same semantics as "{var}" at runtime.'
)
Y036 = "Y036 Badly defined {method_name} method: {details}"
Y037 = "Y037 Use PEP 604 union types instead of {old_syntax} (e.g. {example})."
Y038 = (
    'Y038 Use "from collections.abc import Set as AbstractSet" '
    'instead of "from {module} import AbstractSet" (PEP 585 syntax)'
)
Y039 = 'Y039 Use "str" instead of "{module}.Text"'
Y040 = 'Y040 Do not inherit from "object" explicitly, as it is redundant in Python 3'
Y041 = (
    'Y041 Use "{implicit_supertype}" '
    'instead of "{implicit_subtype} | {implicit_supertype}" '
    '(see "The numeric tower" in PEP 484)'
)
Y042 = "Y042 Type aliases should use the CamelCase naming convention"
Y043 = 'Y043 Bad name for a type alias (the "T" suffix implies a TypeVar)'
Y044 = 'Y044 "from __future__ import annotations" has no effect in stub files.'
Y045 = 'Y045 "{iter_method}" methods should return an {good_cls}, not an {bad_cls}'
Y046 = 'Y046 Protocol "{protocol_name}" is not used'
Y047 = 'Y047 Type alias "{alias_name}" is not used'
Y048 = "Y048 Function body should contain exactly one statement"
Y049 = 'Y049 TypedDict "{typeddict_name}" is not used'
Y050 = (
    'Y050 Use "typing_extensions.Never" instead of "NoReturn" for argument annotations'
)
Y051 = 'Y051 "{literal_subtype}" is redundant in a union with "{builtin_supertype}"'
Y052 = 'Y052 Need type annotation for "{variable}"'
Y053 = "Y053 String and bytes literals >50 characters long are not permitted"
Y054 = (
    "Y054 Numeric literals with a string representation "
    ">10 characters long are not permitted"
)
Y055 = 'Y055 Multiple "type[Foo]" members in a union. {suggestion}'
Y056 = (
    'Y056 Calling "{method}" on "__all__" may not be supported by all type checkers '
    "(use += instead)"
)
Y057 = (
    "Y057 Do not use {module}.ByteString, which has unclear semantics and is deprecated"
)
Y058 = (
    'Y058 Use "{good_cls}" as the return value for simple "{iter_method}" methods, '
    'e.g. "{example}"'
)
Y059 = 'Y059 "Generic[]" should always be the last base class'
Y060 = (
    'Y060 Redundant inheritance from "{redundant_base}"; '
    "class would be inferred as generic anyway"
)
Y061 = 'Y061 None inside "Literal[]" expression. Replace with "{suggestion}"'
Y062 = 'Y062 Duplicate "Literal[]" member "{}"'
Y063 = "Y063 Use PEP-570 syntax to indicate positional-only arguments"
Y064 = 'Y064 Use "{suggestion}" instead of "{original}"'
Y065 = 'Y065 Leave {what} unannotated rather than using "Incomplete"'
Y066 = (
    "Y066 When using if/else with sys.version_info, "
    'put the code for new Python versions first, e.g. "{new_syntax}"'
)
Y067 = 'Y067 Use "=None" instead of "Incomplete | None = None"'
Y068 = 'Y068 Do not use "@override" in stub files.'

Y090 = (
    'Y090 "{original}" means '
    '"a tuple of length 1, in which the sole element is of type {typ!r}". '
    'Perhaps you meant "{new}"?'
)
Y091 = (
    'Y091 Argument "{arg}" to protocol method "{method}" should probably not be positional-or-keyword. '
    "Make it positional-only, since usually you don't want to mandate a specific argument name"
)
Y093 = (
    'Y093 Don\'t use pseudo-protocol "{arg}" as parameter type. Use a protocol instead.'
)

DISABLED_BY_DEFAULT = ["Y090", "Y091", "Y093"]
