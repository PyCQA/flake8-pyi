from typing import Literal

Literal[None]  # Y061 None inside Literal[...] expression. Replace with None
Literal[True, None]  # Y061 None inside Literal[...] expression. Replace with Literal[True] | None
Literal[1, None, "foo"]  # Y061 None inside Literal[...] expression. Replace with Literal[1, 'foo'] | None
Literal[None, None]  # Y061 None inside Literal[...] expression. Replace with Literal[None] | None
