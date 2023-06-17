type lowercase_alias = str | int  # Y042 Type aliases should use the CamelCase naming convention
type _LooksLikeATypeVarT = str | int  # Y043 Bad name for a type alias (the "T" suffix implies a TypeVar)
type _Unused = str | int  # Y047 Type alias "_Unused" is not used

x: _LooksLikeATypeVarT
