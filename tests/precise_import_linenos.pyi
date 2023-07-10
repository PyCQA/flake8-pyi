# flags: --precise-import-code-linenos --extend-ignore=F401
from __future__ import (
    absolute_import,
    division,
    generators,
    nested_scopes,
    unicode_literals,
    with_statement,
    barry_as_FLUFL,
    annotations,  # Y044 "from __future__ import annotations" has no effect in stub files.
)
from collections.abc import (
    Mapping,
    MutableMapping,
    Sequence,
    MutableSequence,
    Set,  # Y025 Use "from collections.abc import Set as AbstractSet" to avoid confusion with "builtins.set"
    ByteString,  # Y057 Do not use collections.abc.ByteString, which has unclear semantics and is deprecated
    Iterator,
    Iterable,
    Generator,
    Awaitable,
)
from typing import (
    AbstractSet,  # Y038 Use "from collections.abc import Set as AbstractSet" instead of "from typing import AbstractSet" (PEP 585 syntax)
    ClassVar,
    Self,
    Annotated,
    NewType,
    overload,
    type_check_only,
    Final,
    final,
)
