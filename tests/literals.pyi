import typing
from typing import Annotated, Final, Literal

Literal[None]  # Y061 None inside "Literal[]" expression. Replace with "None"
Literal[True, None]  # Y061 None inside "Literal[]" expression. Replace with "Literal[True] | None"

Literal[True, True]  # Y062 Duplicate "Literal[]" member "True"
Literal[True, True, True]  # Y062 Duplicate "Literal[]" member "True"
Literal[True, False, True, False]  # Y062 Duplicate "Literal[]" member "True" # Y062 Duplicate "Literal[]" member "False"

###
# The following rules here are slightly subtle,
# but make sense when it comes to giving the best suggestions to users of flake8-pyi.
###

# If Y061 and Y062 both apply, but all the duplicate members are None,
# only emit Y061...
Literal[None, None]  # Y061 None inside "Literal[]" expression. Replace with "None"
Literal[1, None, "foo", None]  # Y061 None inside "Literal[]" expression. Replace with "Literal[1, 'foo'] | None"

# ... but if Y061 and Y062 both apply
# and there are no None members in the Literal[] slice,
# only emit Y062:
Literal[None, True, None, True]  # Y062 Duplicate "Literal[]" member "True"

# Nested Literal values are the same values as a flat slice.
Literal[1, Literal[2, 1]]  # Y062 Duplicate "Literal[]" member "1"
Literal[1, Literal[2, 3]]
Literal[Literal[1], Literal[1]]  # Y062 Duplicate "Literal[]" member "1"
Literal[1, Literal[1, 1]]  # Y062 Duplicate "Literal[]" member "1"
Literal["a", Literal["b", "a"]]  # Y062 Duplicate "Literal[]" member "'a'"
Literal[0, typing.Literal[0]]  # Y062 Duplicate "Literal[]" member "0"
Literal[Annotated[Literal[1, 1], "m"]]  # Y062 Duplicate "Literal[]" member "1"
Literal[True, Literal[False, True], False]  # Y062 Duplicate "Literal[]" member "True" # Y062 Duplicate "Literal[]" member "False"

x: Final[Literal[True]]  # Y064 Use "x: Final = True" instead of "x: Final[Literal[True]]"
# If Y061 and Y064 both apply, only emit Y064
y: Final[Literal[None]]  # Y064 Use "y: Final = None" instead of "y: Final[Literal[None]]"
z: Final[Literal[True, False]]
