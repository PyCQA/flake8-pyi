from typing import TypeAlias

field0: int
field1: int = ...  # Y032 Default value unnecessary for module-level attribute
field2: int = 0  # Y032 Default value unnecessary for module-level attribute
field3 = ...  # type: int
field4: int = 0  # Y015 Attribute must not have a default value other than "..."
field5 = 0  # type: int  # Y015 Attribute must not have a default value other than "..."

# TODO: Ideally the error code for field6 would be Y032,
# but it isn't because the `Foo` class has a separate attribute that is also named "field6",
# and the PyiVisitor plays it safe by only raising Y032 if a symbol only appears once in a file.
field6 = 0  # Y015 Attribute must not have a default value other than "..."

field7 = b""  # Y015 Attribute must not have a default value other than "..."
field8: str = ...

thing_using_field3: TypeAlias = field3.to_bytes
thing_using_field4: TypeAlias = field4.to_bytes
thing_using_field5: TypeAlias = field5.to_bytes
thing_using_field7: TypeAlias = field7.decode

class Foo:
    field3 = ...  # type: int
    field4: int = 0  # Y015 Attribute must not have a default value other than "..."
    field5 = 0  # type: int  # Y015 Attribute must not have a default value other than "..."
    field6 = 0  # Y015 Attribute must not have a default value other than "..."
    field7 = b""  # Y015 Attribute must not have a default value other than "..."
    thing_using_field8_in_class: TypeAlias = field8.startswith
