# isort: skip_file
# flags: --precise-import-code-linenos --extend-ignore=F401

from __future__ import (
    absolute_import,
    annotations,  # Y044 "from __future__ import annotations" has no effect in stub files.
    barry_as_FLUFL,
    division,
    generators,
    nested_scopes,
    unicode_literals,
    with_statement,
)
from collections.abc import (
    Awaitable,
    ByteString,  # Y057 Do not use collections.abc.ByteString, which has unclear semantics and is deprecated
    Generator,
    Iterable,
    Iterator,
    Mapping,
    MutableMapping,
    MutableSequence,
    Sequence,
    Set,  # Y025 Use "from collections.abc import Set as AbstractSet" to avoid confusion with "builtins.set"
)
from typing import (
    AbstractSet,  # Y038 Use "from collections.abc import Set as AbstractSet" instead of "from typing import AbstractSet" (PEP 585 syntax)
    Annotated,
    ClassVar,
    Final,
    NewType,
    Self,
    final,
    overload,
    type_check_only,
)
