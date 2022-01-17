field1: int
field2: int = ...
field3 = ...  # type: int
field4: int = 0  # Y015 Attribute must not have a default value other than "..."
field5 = 0  # type: int  # Y015 Attribute must not have a default value other than "..."
field6 = 0  # Y015 Attribute must not have a default value other than "..."
field7 = b""  # Y015 Attribute must not have a default value other than "..."

class Foo:
    field1: int
    field2: int = ...
    field3 = ...  # type: int
    field4: int = 0  # Y015 Attribute must not have a default value other than "..."
    field5 = 0  # type: int  # Y015 Attribute must not have a default value other than "..."
    field6 = 0  # Y015 Attribute must not have a default value other than "..."
    field7 = b""  # Y015 Attribute must not have a default value other than "..."
