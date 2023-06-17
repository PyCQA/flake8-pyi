type lowercase_alias = str | int  # Y042 Type aliases should use the CamelCase naming convention
type _LooksLikeATypeVarT = str | int  # Y043 Bad name for a type alias (the "T" suffix implies a TypeVar)
type _Unused = str | int  # Y047 Type alias "_Unused" is not used
# the F821 here is a pyflakes false positive;
# we can get rid of it when there's a pyflakes release that supports PEP 695
type _List[T] = list[T]  # F821 undefined name 'T'

y: _List[int]

x: _LooksLikeATypeVarT
