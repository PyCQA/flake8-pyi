import sys
from typing import TypeAlias

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

class Foo:
    field1: int
    field2: int = ...
    field3 = ...  # type: int  # Y033 Do not use type comments in stubs (e.g. use "x: int" instead of "x = ... # type: int")
    field4: int = 0  # Y015 Bad default value. Use "field4: int = ..." instead of "field4: int = 0"
    field5 = 0  # type: int  # Y033 Do not use type comments in stubs (e.g. use "x: int" instead of "x = ... # type: int")  # Y015 Bad default value. Use "field5 = ..." instead of "field5 = 0"
    field6 = 0  # Y015 Bad default value. Use "field6 = ..." instead of "field6 = 0"
    field7 = b""  # Y015 Bad default value. Use "field7 = ..." instead of "field7 = b''"
    field8 = False  # Y015 Bad default value. Use "field8 = ..." instead of "field8 = False"
    field9 = "x"  # Y015 Bad default value. Use "field9 = ..." instead of "field9 = 'x'"  # Y020 Quoted annotations should never be used in stubs
    if sys.platform == "linux":
        field10 = "y"  # Y015 Bad default value. Use "field10 = ..." instead of "field10 = 'y'"  # Y020 Quoted annotations should never be used in stubs
