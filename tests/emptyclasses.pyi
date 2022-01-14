class EmptyClass:
    ...

class PassingEmptyClass:
    pass  # Y009 Empty body should contain "...", not "pass"

class PassingNonEmptyClass:
    x: int
    pass  # Y012 Class body must not contain "pass"

class PassingNonEmptyClass2:
    pass  # Y012 Class body must not contain "pass"
    x: int

class EllipsisNonEmptyClass:
    x: int
    ...  # Y013 Non-empty class body must not contain "..."

class EllipsisNonEmptyClass2:
    ...  # Y013 Non-empty class body must not contain "..."
    x: int
