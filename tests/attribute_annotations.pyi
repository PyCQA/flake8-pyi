import builtins
import sys
import typing
from typing import Final, Final as _Final, TypeAlias

import typing_extensions

# We shouldn't emit Y015 for simple default values
field1: int
field2: int = ...
field3 = ...  # type: int  # Y033 Do not use type comments in stubs (e.g. use "x: int" instead of "x = ... # type: int")
field4: int = 0
field5 = 0  # type: int  # Y033 Do not use type comments in stubs (e.g. use "x: int" instead of "x = ... # type: int")
field6 = 0
field7 = b""
field71 = "foo"
field72: str = "foo"
field8 = False
field81 = -1
field82: float = -98.43
field83 = -42j
field84 = 5 + 42j
field85 = -5 - 42j
field9 = None  # Y026 Use typing_extensions.TypeAlias for type aliases, e.g. "field9: TypeAlias = None"
Field95: TypeAlias = None
Field96: TypeAlias = int | None
Field97: TypeAlias = None | typing.SupportsInt | builtins.str

# Tests for Final
field11: Final = 1
field12: Final = "foo"
field13: Final = b"foo"
field14: Final = True
field15: _Final = True
field16: typing.Final = "foo"
field17: typing_extensions.Final = "foo"
field18: Final = -24j

# We *should* emit Y015 for more complex default values
field19 = [1, 2, 3]  # Y015 Only simple default values are allowed for assignments
field20 = (1, 2, 3)  # Y015 Only simple default values are allowed for assignments
field21 = {1, 2, 3}  # Y015 Only simple default values are allowed for assignments
field22: Final = {"foo": 5}  # Y015 Only simple default values are allowed for assignments  # Y020 Quoted annotations should never be used in stubs
field23 = "foo" + "bar"  # Y015 Only simple default values are allowed for assignments  # Y020 Quoted annotations should never be used in stubs  # Y020 Quoted annotations should never be used in stubs
field24 = b"foo" + b"bar"  # Y015 Only simple default values are allowed for assignments
field25 = 5 * 5  # Y015 Only simple default values are allowed for assignments

class Foo:
    field1: int
    field2: int = ...
    field3 = ...  # type: int  # Y033 Do not use type comments in stubs (e.g. use "x: int" instead of "x = ... # type: int")
    field4: int = 0
    field5 = 0  # type: int  # Y033 Do not use type comments in stubs (e.g. use "x: int" instead of "x = ... # type: int")
    field6 = 0
    field7 = b""
    field71 = "foo"
    field72: str = "foo"
    field8 = False
    # Tests for Final
    field9: Final = 1
    field10: Final = "foo"
    field11: Final = b"foo"
    field12: Final = True
    field13: _Final = True
    field14: typing.Final = "foo"
    field15: typing_extensions.Final = "foo"
    # Standalone strings used to cause issues
    field16 = "x"
    if sys.platform == "linux":
        field17 = "y"
    elif sys.platform == "win32":
        field18 = "z"
    else:
        field19 = "w"

    field20 = [1, 2, 3]  # Y015 Only simple default values are allowed for assignments
    field21 = (1, 2, 3)  # Y015 Only simple default values are allowed for assignments
    field22 = {1, 2, 3}  # Y015 Only simple default values are allowed for assignments
    field23: Final = {"foo": 5}  # Y015 Only simple default values are allowed for assignments  # Y020 Quoted annotations should never be used in stubs
    field24 = "foo" + "bar"  # Y015 Only simple default values are allowed for assignments  # Y020 Quoted annotations should never be used in stubs  # Y020 Quoted annotations should never be used in stubs
    field25 = b"foo" + b"bar"  # Y015 Only simple default values are allowed for assignments
    field26 = 5 * 5  # Y015 Only simple default values are allowed for assignments

    Field95: TypeAlias = None
    Field96: TypeAlias = int | None
    Field97: TypeAlias = None | typing.SupportsInt | builtins.str
