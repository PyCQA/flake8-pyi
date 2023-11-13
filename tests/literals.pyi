from typing import Literal

Literal[None]  # Y061 None inside "Literal[]" expression. Replace with "None"
Literal[None, None]  # Y061 None inside "Literal[]" expression. Replace with "None"
Literal[True, None]  # Y061 None inside "Literal[]" expression. Replace with "Literal[True] | None"
Literal[1, None, "foo", None]  # Y061 None inside "Literal[]" expression. Replace with "Literal[1, 'foo'] | None"

Literal[True, True]  # Y062 Duplicate "Literal[]" member "True"
Literal[True, True, True]  # Y062 Duplicate "Literal[]" member "True"
Literal[True, False, True, False]  # Y062 Duplicate "Literal[]" member "True" # Y062 Duplicate "Literal[]" member "False"

# If both Y061 and Y062 would be emitted, only emit Y062
Literal[None, True, None, True]  # Y062 Duplicate "Literal[]" member "True"
