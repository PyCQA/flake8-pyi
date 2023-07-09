## List of warnings

The following warnings are currently emitted by default:

| Code | Description
|------|-------------
| Y001 | Names of `TypeVar`s, `ParamSpec`s and `TypeVarTuple`s in stubs should usually start with `_`. This makes sure you don't accidentally expose names internal to the stub.
| Y002 | An `if` test must be a simple comparison against `sys.platform` or `sys.version_info`. Stub files support simple conditionals to indicate differences between Python versions or platforms, but type checkers only understand a limited subset of Python syntax. This warning is emitted on conditionals that type checkers may not understand.
| Y003 | Unrecognized `sys.version_info` check. Similar to Y002, but adds some additional checks specific to `sys.version_info` comparisons.
| Y004 | Version comparison must use only major and minor version. Type checkers like mypy don't know about patch versions of Python (e.g. 3.4.3 versus 3.4.4), only major and minor versions (3.3 versus 3.4). Therefore, version checks in stubs should only use the major and minor versions. If new functionality was introduced in a patch version, pretend that it was there all along.
| Y005 | Version comparison must be against a length-n tuple.
| Y006 | Use only `<` and `>=` for version comparisons. Comparisons involving `>` and `<=` may produce unintuitive results when tools do use the full `sys.version_info` tuple.
| Y007 | Unrecognized `sys.platform` check. Platform checks should be simple string comparisons.
| Y008 | Unrecognized platform in a `sys.platform` check. To prevent you from typos, we warn if you use a platform name outside a small set of known platforms (e.g. `"linux"` and `"win32"`).
| Y009 | Empty class or function body should contain `...`, not `pass`. This is just a stylistic choice, but it's the one typeshed made.
| Y010 | Function body must contain only `...`. Stub files should not contain code, so function bodies should be empty.
| Y011 | Only simple default values (`int`, `float`, `complex`, `bytes`, `str`, `bool`, `None`, `...`, or simple container literals) are allowed for typed function arguments. Type checkers ignore the default value, so the default value is not useful information for type-checking, but it may be useful information for other users of stubs such as IDEs. If you're writing a stub for a function that has a more complex default value, use `...` instead of trying to reproduce the runtime default exactly in the stub. Also use `...` for very long numbers, very long strings, very long bytes, or defaults that vary according to the machine Python is being run on.
| Y012 | Class body must not contain `pass`.
| Y013 | Non-empty class body must not contain `...`.
| Y014 | Only simple default values are allowed for any function arguments. A stronger version of Y011 that includes arguments without type annotations.
| Y015 | Only simple default values are allowed for assignments. Similar to Y011, but for assignments rather than parameter annotations.
| Y016 | Unions shouldn't contain duplicates, e.g. `str \| str` is not allowed.
| Y017 | Stubs should not contain assignments with multiple targets or non-name targets. E.g. `T, S = TypeVar("T"), TypeVar("S")` is disallowed, as is `foo.bar = TypeVar("T")`.
| Y018 | A private `TypeVar` should be used at least once in the file in which it is defined.
| Y019 | Certain kinds of methods should use `typing_extensions.Self` instead of defining custom `TypeVar`s for their return annotation. This check currently applies for instance methods that return `self`, class methods that return an instance of `cls`, and `__new__` methods.
| Y020 | Quoted annotations should never be used in stubs.
| Y021 | Docstrings should not be included in stubs.
| Y022 | The `typing` and `typing_extensions` modules include various aliases to stdlib objects. Use these as little as possible (e.g. prefer `builtins.list` over `typing.List`, `collections.Counter` over `typing.Counter`, etc.).
| Y023 | Where there is no detriment to backwards compatibility, import objects such as `ClassVar` and `NoReturn` from `typing` rather than `typing_extensions`.
| Y024 | Use `typing.NamedTuple` instead of `collections.namedtuple`, as it allows for more precise type inference.
| Y025 | Always alias `collections.abc.Set` when importing it, so as to avoid confusion with `builtins.set`. E.g. use `from collections.abc import Set as AbstractSet` instead of `from collections.abc import Set`.
| Y026 | Type aliases should be explicitly demarcated with `typing.TypeAlias` (or use a [PEP-695](https://peps.python.org/pep-0695/) type statement).
| Y028 | Always use class-based syntax for `typing.NamedTuple`, instead of assignment-based syntax.
| Y029 | It is almost always redundant to define `__str__` or `__repr__` in a stub file, as the signatures are almost always identical to `object.__str__` and `object.__repr__`.
| Y030 | Union expressions should never have more than one `Literal` member, as `Literal[1] \| Literal[2]` is semantically identical to `Literal[1, 2]`.
| Y031 | `TypedDict`s should use class-based syntax instead of assignment-based syntax wherever possible. (In situations where this is not possible, such as if a field is a Python keyword or an invalid identifier, this error will not be emitted.)
| Y032 | The second argument of an `__eq__` or `__ne__` method should usually be annotated with `object` rather than `Any`.
| Y033 | Do not use type comments (e.g. `x = ... # type: int`) in stubs. Always use annotations instead (e.g. `x: int`).
| Y034 | Y034 detects common errors where certain methods are annotated as having a fixed return type, despite returning `self` at runtime. Such methods should be annotated with `typing_extensions.Self`. This check looks for:<br><br>&nbsp;&nbsp;**1.**&nbsp;&nbsp;Any in-place BinOp dunder methods (`__iadd__`, `__ior__`, etc.) that do not return `Self`.<br>&nbsp;&nbsp;**2.**&nbsp;&nbsp;`__new__`, `__enter__` and `__aenter__` methods that return the class's name unparameterised.<br>&nbsp;&nbsp;**3.**&nbsp;&nbsp;`__iter__` methods that return `Iterator`, even if the class inherits directly from `Iterator`.<br>&nbsp;&nbsp;**4.**&nbsp;&nbsp;`__aiter__` methods that return `AsyncIterator`, even if the class inherits directly from `AsyncIterator`.<br><br>This check excludes methods decorated with `@overload` or `@abstractmethod`.
| Y035 | `__all__`, `__match_args__` and `__slots__` in a stub file should always have values, as these special variables in a `.pyi` file have identical semantics in a stub as at runtime. E.g. write `__all__ = ["foo", "bar"]` instead of `__all__: list[str]`.
| Y036 | Y036 detects common errors in `__exit__` and `__aexit__` methods. For example, the first argument in an `__exit__` method should either be annotated with `object`, `_typeshed.Unused` (a special alias for `object`) or `type[BaseException] \| None`.
| Y037 | Use PEP 604 syntax instead of `typing.Union` and `typing.Optional`. E.g. use `str \| int` instead of `Union[str, int]`, and use `str \| None` instead of `Optional[str]`.
| Y038 | Use `from collections.abc import Set as AbstractSet` instead of `from typing import AbstractSet`.
| Y039 | Use `str` instead of `typing.Text`.
| Y040 | Never explicitly inherit from `object`, as all classes implicitly inherit from `object` in Python 3.
| Y041 | Y041 detects redundant numeric unions in the context of parameter annotations. For example, PEP 484 specifies that type checkers should allow `int` objects to be passed to a function, even if the function states that it accepts a `float`. As such, `int` is redundant in the union `int \| float` in the context of a parameter annotation. In the same way, `int` is sometimes redundant in the union `int \| complex`, and `float` is sometimes redundant in the union `float \| complex`.
| Y042 | Type alias names should use CamelCase rather than snake_case.
| Y043 | Do not use names ending in "T" for private type aliases. (The "T" suffix implies that an object is a `TypeVar`.)
| Y044 | `from __future__ import annotations` has no effect in stub files, since type checkers automatically treat stubs as having those semantics.
| Y045 | `__iter__` methods should never return `Iterable[T]`, as they should always return some kind of iterator.
| Y046 | A private `Protocol` should be used at least once in the file in which it is defined.
| Y047 | A private `TypeAlias` should be used at least once in the file in which it is defined.
| Y048 | Function bodies should contain exactly one statement. (Note that if a function body includes a docstring, the docstring counts as a "statement".)
| Y049 | A private `TypedDict` should be used at least once in the file in which it is defined.
| Y050 | Prefer `typing_extensions.Never` over `typing.NoReturn` for argument annotations. This is a purely stylistic choice in the name of readability.
| Y051 | Y051 detects redundant unions between `Literal` types and builtin supertypes. For example, `Literal[5]` is redundant in the union `int \| Literal[5]`, and `Literal[True]` is redundant in the union `Literal[True] \| bool`.
| Y052 | Y052 disallows assignments to constant values where the assignment does not have a type annotation. For example, `x = 0` in the global namespace is ambiguous in a stub, as there are four different types that could be inferred for the variable `x`: `int`, `Final[int]`, `Literal[0]`, or `Final[Literal[0]]`. Enum members are excluded from this check, as are various special assignments such as `__all__` and `__match_args__`.
| Y053 | Only string and bytes literals <=50 characters long are permitted.
| Y054 | Only numeric literals with a string representation <=10 characters long are permitted.
| Y055 | Unions of the form `type[X] \| type[Y]` can be simplified to `type[X \| Y]`. Similarly, `Union[type[X], type[Y]]` can be simplified to `type[Union[X, Y]]`.
| Y056 | Do not call methods such as `.append()`, `.extend()` or `.remove()` on `__all__`. Different type checkers have varying levels of support for calling these methods on `__all__`. Use `+=` instead, which is known to be supported by all major type checkers.
| Y057 | Do not use `typing.ByteString` or `collections.abc.ByteString`. These types have unclear semantics, and are deprecated; use  `typing_extensions.Buffer` or a union such as `bytes \| bytearray \| memoryview` instead. See [PEP 688](https://peps.python.org/pep-0688/) for more details.

## Warnings disabled by default

The following error codes are also provided, but are disabled by default due to
the risk of false-positive errors. To enable these error codes, use
`--extend-select={code1,code2,...}` on the command line or in your flake8
configuration file.

Note that `--extend-select` **will not work** if you have
`--select` specified on the command line or in your configuration file. We
recommend only using `--extend-select`, never `--select`.

| Code | Description
|------|------------
| Y090 | `tuple[int]` means "a tuple of length 1, in which the sole element is of type `int`". Consider using `tuple[int, ...]` instead, which means "a tuple of arbitrary (possibly 0) length, in which all elements are of type `int`".
