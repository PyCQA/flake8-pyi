# ok
field1: int
field2 = ...  # type: int

# not ok
field3: int = 0
field4: int = ...
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
