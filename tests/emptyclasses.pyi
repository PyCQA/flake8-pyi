class EmptyClass:
    ...

class PassingEmptyClass:
    pass  # Y009

class PassingNonEmptyClass:
    x: int
    pass  # Y011

class PassingNonEmptyClass2:
    pass  # Y011
    x: int

class EllipsisNonEmptyClass:
    x: int
    ...  # Y012

class EllipsisNonEmptyClass2:
    ...  # Y012
    x: int
