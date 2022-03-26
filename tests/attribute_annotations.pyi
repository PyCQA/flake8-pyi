import typing
from typing import Final, TypeAlias

import typing_extensions

field1: int
field2: int = ...
field3 = ...  # type: int  # Y033 Do not use type comments in stubs (e.g. use "x: int" instead of "x = ... # type: int")
field4: int = 0  # Y015 Bad default value. Use "field4: int = ..." instead of "field4: int = 0"
field5 = 0  # type: int  # Y033 Do not use type comments in stubs (e.g. use "x: int" instead of "x = ... # type: int")  # Y015 Bad default value. Use "field5 = ..." instead of "field5 = 0"
field6 = 0  # Y015 Bad default value. Use "field6 = ..." instead of "field6 = 0"
field7 = b""  # Y015 Bad default value. Use "field7 = ..." instead of "field7 = b''"
field8 = False  # Y015 Bad default value. Use "field8 = ..." instead of "field8 = False"

# We don't want this one to trigger Y015 -- it's valid as a TypeAlias
field9 = None    # Y026 Use typing_extensions.TypeAlias for type aliases
field10: TypeAlias = None

# Tests for Final
field11: Final = 1
field12: Final = "foo"
field13: Final = b"foo"
field14: Final = True
field15: Final = ('a', 'b', 'c')
field16: typing.Final = "foo"
field17: typing_extensions.Final = "foo"

class Foo:
    field1: int
    field2: int = ...
    field3 = ...  # type: int  # Y033 Do not use type comments in stubs (e.g. use "x: int" instead of "x = ... # type: int")
    field4: int = 0  # Y015 Bad default value. Use "field4: int = ..." instead of "field4: int = 0"
    field5 = 0  # type: int  # Y033 Do not use type comments in stubs (e.g. use "x: int" instead of "x = ... # type: int")  # Y015 Bad default value. Use "field5 = ..." instead of "field5 = 0"
    field6 = 0  # Y015 Bad default value. Use "field6 = ..." instead of "field6 = 0"
    field7 = b""  # Y015 Bad default value. Use "field7 = ..." instead of "field7 = b''"
    field8 = False  # Y015 Bad default value. Use "field8 = ..." instead of "field8 = False"
    # Tests for Final
    field9: Final = 1
    field10: Final = "foo"
    field11: Final = b"foo"
    field12: Final = True
    field13: Final = ('a', 'b', 'c')
    field14: typing.Final = "foo"
    field15: typing_extensions.Final = "foo"
