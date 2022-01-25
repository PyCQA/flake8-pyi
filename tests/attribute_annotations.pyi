field0: int
field1: int = ...  # Y032 Default value unnecessary for module-level attribute
field2: int = 0  # Y032 Default value unnecessary for module-level attribute
field3 = ...  # type: int
field4: int = 0  # Y015 Attribute must not have a default value other than "..."
field5 = 0  # type: int  # Y015 Attribute must not have a default value other than "..."
field6 = 0  # Y015 Attribute must not have a default value other than "..."
field7 = b""  # Y015 Attribute must not have a default value other than "..."
field8: str = ...

thing_using_field3: field3
thing_using_field4: field4
thing_using_field5: field5
thing_using_field6: field6
thing_using_field7: field7

class Foo:
    field1: int
    field2: int = ...
    field3 = ...  # type: int
    field4: int = 0  # Y015 Attribute must not have a default value other than "..."
    field5 = 0  # type: int  # Y015 Attribute must not have a default value other than "..."
    field6 = 0  # Y015 Attribute must not have a default value other than "..."
    field7 = b""  # Y015 Attribute must not have a default value other than "..."
    thing_using_field8_in_class: field8
