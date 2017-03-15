from typing import TypeVar

a, b = TypeVar('T')  # Y0001

T = TypeVar('T')  # Y0002

_T = TypeVar('_T')  # no error
