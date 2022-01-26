field1: int
field2: int = ...
field3 = ...  # type: int
field4: int = 0  # Y015 Bad default value. Use "field4: int = ..." instead of "field4: int = 0"
field5 = 0  # type: int  # Y015 Bad default value. Use "field5 = ..." instead of "field5 = 0"
field6 = 0  # Y015 Bad default value. Use "field6 = ..." instead of "field6 = 0"
field7 = b""  # Y015 Bad default value. Use "field7 = ..." instead of "field7 = b''"

class Foo:
    field1: int
    field2: int = ...
    field3 = ...  # type: int
    field4: int = 0  # Y015 Bad default value. Use "field4: int = ..." instead of "field4: int = 0"
    field5 = 0  # type: int  # Y015 Bad default value. Use "field5 = ..." instead of "field5 = 0"
    field6 = 0  # Y015 Bad default value. Use "field6 = ..." instead of "field6 = 0"
    field7 = b""  # Y015 Bad default value. Use "field7 = ..." instead of "field7 = b''"
