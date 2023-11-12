from typing import Literal

Literal[None]  # Y061 None inside "Literal[]" expression. Replace with "None"
Literal[None, None]  # Y061 None inside "Literal[]" expression. Replace with "None"
Literal[True, None]  # Y061 None inside "Literal[]" expression. Replace with "Literal[True] | None"
Literal[1, None, "foo", None]  # Y061 None inside "Literal[]" expression. Replace with "Literal[1, 'foo'] | None"

Literal[True, True]  # Y062 Duplicate "Literal[]" member "True"
Literal[True, True, True]  # Y062 Duplicate "Literal[]" member "True"
Literal[True, False, True, False]  # Y062 Duplicate "Literal[]" member "True" # Y062 Duplicate "Literal[]" member "False"

Literal[None, True, None, True]  # Y061 None inside "Literal[]" expression. Replace with "Literal[True, True] | None" # Y062 Duplicate "Literal[]" member "True"
