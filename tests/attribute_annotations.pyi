# ok
field1: int
field2 = ...  # type: int

# not ok
field3: int = 0
field4: int = ...
field5 = 0  # type: int
field6 = 0
field7 = ""

# Allow defaults in classes
class Foo:
    field: int = ...
