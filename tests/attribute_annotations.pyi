# ok
field1: int
field2: int = ...  # Y092
field3 = ...  # type: int

# not ok
field4: int = 0
field5 = 0  # type: int
field6 = 0
field7 = ""

class Foo:
    # ok
    field1: int
    field2: int = ...
    field3 = ...  # type: int

    # not ok
    field4: int = 0
    field5 = 0  # type: int
    field6 = 0
    field7 = ""
