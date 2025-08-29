# flags: --extend-select=Y092

# Tests for pseudo-protocols like `Sequence`, `Mapping`, or `MutableMapping`
# imported from collections.abc.
#
# We're explicitly not testing for imports from typing as that should already
# trigger Y022 (import from collections.abc instead from typing).

import collections.abc
from collections.abc import Iterable, Mapping, MutableMapping, Sequence
from collections.abc import Mapping as MyMapping

def test_sequence(seq: Sequence[int]) -> None: ...  # Y092 Don't use pseudo-protocol "Sequence" as parameter type. Use a protocol instead.
def test_mapping(mapping: Mapping[str, int]) -> None: ...  # Y092 Don't use pseudo-protocol "Mapping" as parameter type. Use a protocol instead.
def test_mutable_mapping(mapping: MutableMapping[str, int]) -> None: ...  # Y092 Don't use pseudo-protocol "MutableMapping" as parameter type. Use a protocol instead.
def test_import_alias(mapping: MyMapping[str, int]) -> None: ...  # TODO: import aliases are currently not supported.
def test_plain(seq: Sequence) -> None: ...  # Y092 Don't use pseudo-protocol "Sequence" as parameter type. Use a protocol instead.
def test_union(arg: Sequence[int] | int) -> None: ...  # Y092 Don't use pseudo-protocol "Sequence" as parameter type. Use a protocol instead.
def test_nested(arg: list[Sequence[int]]) -> None: ...  # Y092 Don't use pseudo-protocol "Sequence" as parameter type. Use a protocol instead.
def test_full_type(seq: collections.abc.Sequence[int]) -> None: ...  # Y092 Don't use pseudo-protocol "Sequence" as parameter type. Use a protocol instead.

x: Sequence[int]  # ok
def test_iterable(it: Iterable[str]) -> None: ...  # ok
def test_as_return_type() -> Sequence[int]: ...  # ok

class Foo:
    x: Sequence[int]  # ok

    def test_method(self, seq: Sequence[int]) -> None: ...  # Y092 Don't use pseudo-protocol "Sequence" as parameter type. Use a protocol instead.
