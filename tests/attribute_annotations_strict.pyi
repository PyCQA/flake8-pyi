# flags: --select=Y092

field1: int
field2: int = ...  # Y092 Top-level attribute must not have a default value
field3 = ...  # type: int
field4: int = 0
field5 = 0  # type: int
field6 = 0
field7 = ""

class Foo:
    field1: int
    field2: int = ...
    field3 = ...  # type: int
    field4: int = 0
    field5 = 0  # type: int
    field6 = 0
    field7 = ""
