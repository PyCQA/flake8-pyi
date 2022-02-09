# This file is a test case for test_plugin.py

__all__ = ["foo"]  # F822 undefined name 'foo' in __all__


def a_sample():
    class _SpecialForm:
        ...

    Protocol: _SpecialForm

    class Bar(Protocol):  # F821 undefined name 'Protocol'
        ...

    class WorkingSet:
        def require(self) -> None:
            ...

    working_set: WorkingSet
    require = working_set.require  # F821 undefined name 'working_set'
    return require
