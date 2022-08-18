import typing
from typing import NoReturn

import typing_extensions
from typing_extensions import Never

def badfunc0(arg: NoReturn) -> None: ...  # Y050 Use "typing_extensions.Never" instead of "NoReturn" for argument annotations
def badfunc1(*args: typing.NoReturn) -> None: ...  # Y050 Use "typing_extensions.Never" instead of "NoReturn" for argument annotations
def badfunc2(**kwargs: typing_extensions.NoReturn) -> None: ...  # Y050 Use "typing_extensions.Never" instead of "NoReturn" for argument annotations  # Y023 Use "typing.NoReturn" instead of "typing_extensions.NoReturn"
def badfunc3(*, arg: NoReturn) -> None: ...  # Y050 Use "typing_extensions.Never" instead of "NoReturn" for argument annotations

def goodfunc0(arg: Never) -> None: ...
def goodfunc1(*args: typing.Never) -> None: ...
def goodfunc2(**kwargs: typing_extensions.Never) -> None: ...
def goodfunc3(*, arg: Never) -> None: ...
