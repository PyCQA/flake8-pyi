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

# Tests for Final
field11: Final = 1
field12: Final = "foo"
field13: Final = b"foo"
field14: Final = True
field15: _Final = True
field16: typing.Final = "foo"
field17: typing_extensions.Final = "foo"
field18: Final = -24j
field181: Final = field18
field182: Final = os.pathsep
field183: Final = None

# We *should* emit Y015 for more complex default values
field19 = [1, 2, 3]  # Y015 Only simple default values are allowed for assignments
field20 = (1, 2, 3)  # Y015 Only simple default values are allowed for assignments
field21 = {1, 2, 3}  # Y015 Only simple default values are allowed for assignments
field22: Final = {"foo": 5}  # Y015 Only simple default values are allowed for assignments
field23 = "foo" + "bar"  # Y015 Only simple default values are allowed for assignments
field24 = b"foo" + b"bar"  # Y015 Only simple default values are allowed for assignments
field25 = 5 * 5  # Y015 Only simple default values are allowed for assignments
field26: int = 0xFFFFFFFFF  # Y054 Only numeric literals with a string representation <=10 characters long are permitted
field27: int = 12345678901  # Y054 Only numeric literals with a string representation <=10 characters long are permitted
field28: int = -0xFFFFFFFFF  # Y054 Only numeric literals with a string representation <=10 characters long are permitted
field29: int = -12345678901  # Y054 Only numeric literals with a string representation <=10 characters long are permitted

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
    field15: typing_extensions.Final = "foo"
    # Standalone strings used to cause issues
    field16 = "x"  # Y052 Need type annotation for "field16"
    if sys.platform == "linux":
        field17 = "y"  # Y052 Need type annotation for "field17"
    elif sys.platform == "win32":
        field18 = "z"  # Y052 Need type annotation for "field18"
    else:
        field19 = "w"  # Y052 Need type annotation for "field19"

    field20 = [1, 2, 3]  # Y015 Only simple default values are allowed for assignments
    field21 = (1, 2, 3)  # Y015 Only simple default values are allowed for assignments
    field22 = {1, 2, 3}  # Y015 Only simple default values are allowed for assignments
    field23: Final = {"foo": 5}  # Y015 Only simple default values are allowed for assignments
    field24 = "foo" + "bar"  # Y015 Only simple default values are allowed for assignments
    field25 = b"foo" + b"bar"  # Y015 Only simple default values are allowed for assignments
    field26 = 5 * 5  # Y015 Only simple default values are allowed for assignments
    field27 = 0xFFFFFFFFF  # Y052 Need type annotation for "field27" # Y054 Only numeric literals with a string representation <=10 characters long are permitted
    field28 = 12345678901  # Y052 Need type annotation for "field28" # Y054 Only numeric literals with a string representation <=10 characters long are permitted
    field29 = -0xFFFFFFFFF  # Y052 Need type annotation for "field29" # Y054 Only numeric literals with a string representation <=10 characters long are permitted
    field30 = -12345678901  # Y052 Need type annotation for "field30" # Y054 Only numeric literals with a string representation <=10 characters long are permitted

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
