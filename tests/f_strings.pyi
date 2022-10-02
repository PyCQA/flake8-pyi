import sys

bar = sys.platform

x = f""  # Y052 f-strings should never be used in stubs # F541 f-string is missing placeholders
y: f"{bar}"  # Y052 f-strings should never be used in stubs

if sys.platform == f"{bar}":  # Y007 Unrecognized sys.platform check # Y052 f-strings should never be used in stubs
    ...

class Foo:
    attr: f"{x!r}"  # Y052 f-strings should never be used in stubs
