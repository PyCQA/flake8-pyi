import builtins
import enum
import os
import sys
import typing
from enum import Enum, Flag, ReprEnum, StrEnum
from typing import Final, Final as _Final, TypeAlias

import typing_extensions

# We shouldn't emit Y015 for simple default values
field1: int
field2: int = ...
field3 = ...  # type: int  # Y033 Do not use type comments in stubs (e.g. use "x: int" instead of "x = ... # type: int")
field4: int = 0
field41: int = 0xFFFFFFFF
field42: int = 1234567890
field43: int = -0xFFFFFFFF
field44: int = -1234567890
field5 = 0  # type: int  # Y033 Do not use type comments in stubs (e.g. use "x: int" instead of "x = ... # type: int")  # Y052 Need type annotation for "field5"
field6 = 0  # Y052 Need type annotation for "field6"
field7 = b""  # Y052 Need type annotation for "field7"
field71 = "foo"  # Y052 Need type annotation for "field71"
field72: str = "foo"
field8 = False  # Y052 Need type annotation for "field8"
field81 = -1  # Y052 Need type annotation for "field81"
field82: float = -98.43
field83 = -42j  # Y052 Need type annotation for "field83"
field84 = 5 + 42j  # Y052 Need type annotation for "field84"
field85 = -5 - 42j  # Y052 Need type annotation for "field85"
field9 = None  # Y026 Use typing_extensions.TypeAlias for type aliases, e.g. "field9: TypeAlias = None"
Field95: TypeAlias = None
Field96: TypeAlias = int | None
Field97: TypeAlias = None | typing.SupportsInt | builtins.str | float | bool
field19 = [1, 2, 3]  # Y052 Need type annotation for "field19"
field191: list[int] = [1, 2, 3]
field20 = (1, 2, 3)  # Y052 Need type annotation for "field20"
field201: tuple[int, ...] = (1, 2, 3)
field21 = {1, 2, 3}  # Y052 Need type annotation for "field21"
field211: set[int] = {1, 2, 3}
field212 = {"foo": "bar"}  # Y052 Need type annotation for "field212"
field213: dict[str, str] = {"foo": "bar"}
field22: Final = {"foo": 5}

# Tests for Final
field11: Final = 1
field12: Final = "foo"
field13: Final = b"foo"
field14: Final = True
field15: _Final = True
field16: typing.Final = "foo"
field17: typing_extensions.Final = "foo"  # Y023 Use "typing.Final" instead of "typing_extensions.Final"
field18: Final = -24j
field181: Final = field18
field182: Final = os.pathsep
field183: Final = None

# We *should* emit Y015 for more complex default values
field221: list[int] = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]  # Y015 Only simple default values are allowed for assignments
field222: list[int] = [100000000000000000000000000000]  # Y054 Numeric literals with a string representation >10 characters long are not permitted
field223: list[int] = [*range(10)]  # Y015 Only simple default values are allowed for assignments
field224: list[int] = list(range(10))  # Y015 Only simple default values are allowed for assignments
field225: list[object] = [{}, 1, 2]  # Y015 Only simple default values are allowed for assignments
field226: tuple[str | tuple[str, ...], ...] = ("foo", ("foo", "bar"))  # Y015 Only simple default values are allowed for assignments
field227: dict[str, object] = {"foo": {"foo": "bar"}}  # Y015 Only simple default values are allowed for assignments
field228: dict[str, list[object]] = {"foo": []}  # Y015 Only simple default values are allowed for assignments
# When parsed, this case results in `None` being placed in the `.keys` list for the `ast.Dict` node
field229: dict[int, int] = {1: 2, **{3: 4}}  # Y015 Only simple default values are allowed for assignments
field23 = "foo" + "bar"  # Y015 Only simple default values are allowed for assignments
field24 = b"foo" + b"bar"  # Y015 Only simple default values are allowed for assignments
field25 = 5 * 5  # Y015 Only simple default values are allowed for assignments
field26: int = 0xFFFFFFFFF  # Y054 Numeric literals with a string representation >10 characters long are not permitted
field27: int = 12345678901  # Y054 Numeric literals with a string representation >10 characters long are not permitted
field28: int = -0xFFFFFFFFF  # Y054 Numeric literals with a string representation >10 characters long are not permitted
field29: int = -12345678901  # Y054 Numeric literals with a string representation >10 characters long are not permitted

class Foo:
    field1: int
    field2: int = ...
    field3 = ...  # type: int  # Y033 Do not use type comments in stubs (e.g. use "x: int" instead of "x = ... # type: int")
    field4: int = 0
    field41: int = 0xFFFFFFFF
    field42: int = 1234567890
    field43: int = -0xFFFFFFFF
    field44: int = -1234567890
    field5 = 0  # type: int  # Y033 Do not use type comments in stubs (e.g. use "x: int" instead of "x = ... # type: int")  # Y052 Need type annotation for "field5"
    field6 = 0  # Y052 Need type annotation for "field6"
    field7 = b""  # Y052 Need type annotation for "field7"
    field71 = "foo"  # Y052 Need type annotation for "field71"
    field72: str = "foo"
    field8 = False  # Y052 Need type annotation for "field8"
    # Tests for Final
    field9: Final = 1
    field10: Final = "foo"
    field11: Final = b"foo"
    field12: Final = True
    field13: _Final = True
    field14: typing.Final = "foo"
    field15: typing_extensions.Final = "foo"  # Y023 Use "typing.Final" instead of "typing_extensions.Final"
    # Standalone strings used to cause issues
    field16 = "x"  # Y052 Need type annotation for "field16"
    if sys.platform == "linux":
        field17 = "y"  # Y052 Need type annotation for "field17"
    elif sys.platform == "win32":
        field18 = "z"  # Y052 Need type annotation for "field18"
    else:
        field19 = "w"  # Y052 Need type annotation for "field19"

    field20 = [1, 2, 3]  # Y052 Need type annotation for "field20"
    field201: list[int] = [1, 2, 3]
    field21 = (1, 2, 3)  # Y052 Need type annotation for "field21"
    field211: tuple[int, ...] = (1, 2, 3)
    field22 = {1, 2, 3}  # Y052 Need type annotation for "field22"
    field221: set[int] = {1, 2, 3}
    field23: Final = {"foo": 5}
    field24 = "foo" + "bar"  # Y015 Only simple default values are allowed for assignments
    field25 = b"foo" + b"bar"  # Y015 Only simple default values are allowed for assignments
    field26 = 5 * 5  # Y015 Only simple default values are allowed for assignments
    field27 = 0xFFFFFFFFF  # Y052 Need type annotation for "field27" # Y054 Numeric literals with a string representation >10 characters long are not permitted
    field28 = 12345678901  # Y052 Need type annotation for "field28" # Y054 Numeric literals with a string representation >10 characters long are not permitted
    field29 = -0xFFFFFFFFF  # Y052 Need type annotation for "field29" # Y054 Numeric literals with a string representation >10 characters long are not permitted
    field30 = -12345678901  # Y052 Need type annotation for "field30" # Y054 Numeric literals with a string representation >10 characters long are not permitted

    Field95: TypeAlias = None
    Field96: TypeAlias = int | None
    Field97: TypeAlias = None | typing.SupportsInt | builtins.str

# Enums are excluded from Y052
class Enum1(Enum):
    FOO = "foo"

class Enum2(enum.IntEnum):
    FOO = 1

class Enum3(Flag):
    FOO = 1

class Enum4(enum.IntFlag):
    FOO = 1

class Enum5(StrEnum):
    FOO = "foo"

class Enum6(ReprEnum):
    FOO = "foo"

class Enum7(enum.Enum):
    FOO = "foo"

class SpecialEnum(enum.Enum): ...

class SubclassOfSpecialEnum(SpecialEnum):
    STILL_OKAY = "foo"
