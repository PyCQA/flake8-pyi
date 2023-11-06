# This test file checks that disabled-by-default error codes aren't triggered,
# unless they're explicitly enabled
from typing import (  # Y022 Use "tuple[Foo, Bar]" instead of "typing.Tuple[Foo, Bar]" (PEP 585 syntax)
    Tuple,
)

# These would trigger Y090, but it's disabled by default
x: tuple[int]
y: Tuple[str]
