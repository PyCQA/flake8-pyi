# Change Log

## 23.10.0

* Introduce Y090, which warns if you have an annotation such as `tuple[int]` or
  `Tuple[int]`. These mean "a tuple of length 1, in which the sole element is
  of type `int`". This is sometimes what you want, but more usually you'll want
  `tuple[int, ...]`, which means "a tuple of arbitrary (possibly 0) length, in
  which all elements are of type `int`".

  This error code is disabled by default due to the risk of false-positive
  errors. To enable it, use the `--extend-select=Y090` option.
* Y011 now ignores `sentinel` and `_typeshed.sentinel` in default values.

## 23.6.0

Features:
* Support Python 3.12
* Support [PEP 695](https://peps.python.org/pep-0695/) syntax for declaring
  type aliases
* Correctly emit Y019 errors for PEP-695 methods that are generic around a `TypeVar`
  instead of returning `typing_extensions.Self`
* Introduce Y057: Do not use `typing.ByteString` or `collections.abc.ByteString`. These
  types have unclear semantics, and are deprecated; use  `typing_extensions.Buffer` or
  a union such as `bytes | bytearray | memoryview` instead. See
  [PEP 688](https://peps.python.org/pep-0688/) for more details.
* The way in which flake8-pyi modifies pyflakes runs has been improved:
  * When flake8-pyi is installed, pyflakes will now complain about forward references
    in default values for function and method parameters (the same as pyflakes
    does when it checks `.py` files). Unlike in `.py` files, forward references
    in default values are legal in stub files. However, they are never necessary,
    and are considered bad style. (Forward references for parameter *annotations*
    are still allowed.)

    Contributed by [tomasr8](https://github.com/tomasr8).
  * When flake8-pyi is installed, pyflakes's F822 check now produces many fewer false
    positives when flake8 is run on `.pyi` files. It now understands that `x: int` in a
    stub file is sufficient for `x` to be considered "bound", and that `"x"` can
    therefore be included in `__all__`.

Bugfixes:
* Y018, Y046, Y047 and Y049 previously failed to detect unused
  TypeVars/ParamSpecs/TypeAliases/TypedDicts/Protocols if the object in question had
  multiple definitions in the same file (e.g. across two branches of an `if
  sys.version_info >= (3, 10)` check). This bug has now been fixed.
* Y020 was previously not emitted if quoted annotations were used in TypeVar
  constraints. This bug has now been fixed.

Other changes:
* flake8-pyi no longer supports being run on Python 3.7, which has reached its end of life.
* flake8-pyi no longer supports being run with flake8 <v6.

## 23.5.0

* flake8-pyi no longer supports being run with flake8 <5.0.4.
* The way in which flake8-pyi modifies pyflakes runs has been improved:
  * When flake8-pyi is installed, pyflakes now correctly recognises an annotation as
    being equivalent to a binding assignment in a stub file, reducing false
    positives from flake8's F821 error code.
  * When flake8-pyi is installed, there are now fewer pyflakes positives from class
    definitions that have forward references in the bases tuple for the purpose of
    creating recursive or circular type definitions. These are invalid in `.py` files,
    but are supported in stub files.
  * When flake8-pyi is installed, pyflakes will also *complain* about code which (in
    combination with flake8-pyi) it previously had no issue with. For example, it will
    now complain about this code:

    ```py
    class Foo(Bar): ...
    class Bar: ...
    ```

    Although the above code is legal in a stub file, it is considered poor style, and
    the forward reference serves no purpose (there is no recursive or circular
    definition). As such, it is now disallowed by pyflakes when flake8-pyi is
    installed.

  Contributed by [tomasr8](https://github.com/tomasr8).
* Introduce Y056: Various type checkers have different levels of support for method
  calls on `__all__`. Use `__all__ += ["foo", "bar"]` instead, as this is known to be
  supported by all major type checkers.

## 23.4.1

New error codes:
* Y055: Unions of the form `type[X] | type[Y]` can be simplified to `type[X | Y]`.
  Similarly, `Union[type[X], type[Y]]` can be simplified to `type[Union[X, Y]]`.
  Contributed by [tomasr8](https://github.com/tomasr8).

## 23.4.0

* Update error messages for Y019 and Y034 to recommend using
  `typing_extensions.Self` rather than `_typeshed.Self`.

## 23.3.1

New error codes:
* Y053: Disallow string or bytes literals with length >50 characters.
  Previously this rule only applied to parameter default values;
  it now applies everywhere.
* Y054: Disallow numeric literals with a string representation >10 characters long.
  Previously this rule only applied to parameter default values;
  it now applies everywhere.

Other changes:
* Y011/Y014/Y015: Simple container literals (`list`, `dict`, `tuple` and `set`
  literals) are now allowed as default values.
* Y052 is now emitted more consistently.
* Some things that used to result in Y011, Y014 or Y015 being emitted
  now result in Y053 or Y054 being emitted.

## 23.3.0

* Y011/Y014/Y015: Allow `math` constants `math.inf`, `math.nan`, `math.e`,
  `math.pi`, `math.tau`, and their negatives in default values. Some other
  semantically equivalent values, such as `x = inf` (`from math import inf`),
  or `x = np.inf` (`import numpy as np`), should be rewritten to `x = math.inf`.
  Contributed by [XuehaiPan](https://github.com/XuehaiPan).

## 23.1.2

* Y011/Y014/Y015: Increase the maximum character length of literal numbers
  in default values from 7 to 10, allowing hexadecimal representation of
  32-bit integers. Contributed by [Avasam](https://github.com/Avasam).

## 23.1.1

New error codes:
* Y052: Disallow default values in global or class namespaces where the
  assignment does not have a type annotation. Stubs should be explicit about
  the type of all variables in the stub; without type annotations, the type
  checker is forced to make inferences, which may have unpredictable
  consequences. Enum members are excluded from this check, as are various
  special assignments such as `__all__` and `__match_args__`.

Other changes:
* Disallow numeric default values where `len(str(default)) > 7`. If a function
  has a default value where the string representation is greater than 7
  characters, it is likely to be an implementation detail or a constant that
  varies depending on the system you're running on, such as `sys.maxsize`.
* Disallow `str` or `bytes` defaults where the default is >50 characters long,
  for similar reasons.
* Allow `ast.Attribute` nodes as default values for a small number of special
  cases, such as `sys.maxsize` and `sys.executable`.
* Fewer Y020 false positives are now emitted when encountering default values
  in stub files.

## 23.1.0

Bugfixes:
* Do not emit Y020 (quoted annotations) for strings in parameter defaults.
* Fix checking of defaults for functions with positional-only parameters.

Other changes:
* Modify Y036 so that `_typeshed.Unused` is allowed as an annotation for
  parameters in `__(a)exit__` methods. Contributed by
  [Avasam](https://github.com/Avasam)
* Several changes have been made to error codes relating to imports:
    * The Y027 error code has been removed.
    * All errors that used to result in Y027 being emitted now result in Y022
      being emitted instead.
    * Some errors that used to result in Y023 being emitted now result
      in Y022 being emitted instead.
    * `typing.Match` and `typing.Pattern` have been added to the list of imports
      banned by Y022. Use `re.Match` and `re.Pattern` instead.
* flake8-pyi no longer supports stub files that aim to support Python 2. If your
  stubs need to support Python 2, pin flake8-pyi to 22.11.0 or lower.
* Y011, Y014 and Y015 have all been significantly relaxed. `None`, `bool`s,
  `int`s, `float`s, `complex` numbers, strings and `bytes` are all now allowed
  as default values for parameter annotations or assignments.
* Hatchling is now used as the build backend. This should have minimal, if any,
  user-facing impact.

## 22.11.0

Bugfixes:
* Specify encoding when opening files. Prevents `UnicodeDecodeError` on Windows
  when the file contains non-CP1252 characters.
  Contributed by [Avasam](https://github.com/Avasam).
* Significant changes have been made to the Y041 check. Previously, Y041 flagged
  "redundant numeric unions" (e.g. `float | int`, `complex | float` or `complex | int`)
  in all contexts outside of type aliases. This was incorrect. PEP 484 only
  specifies that type checkers should treat `int` as an implicit subtype of
  `float` in the specific context of parameter annotations for functions and
  methods. Y041 has therefore been revised to only emit errors on "redundant
  numeric unions" in the context of parameter annotations.

Other changes:
* Support running with flake8 v6.

## 22.10.0

Bugfixes:
* Do not emit Y020 for empty strings. Y020 concerns "quoted annotations",
  but an empty string can never be a quoted annotation.
* Add special-casing so that Y020 is not emitted for `__slots__` definitions
  inside `class` blocks.
* Expand Y035 to cover `__slots__` definitions as well as `__match_args__` and
  `__all__` definitions.
* Expand Y015 so that errors are emitted for assignments to negative numbers.

Other changes:
* Since v22.8.1, flake8-pyi has emitted a `FutureWarning` if run with flake8<5,
  warning that the plugin would soon become incompatible with flake8<5. Due to
  some issues that mean that some users are unable to upgrade to flake8>=5,
  however, flake8-pyi no longer intends to remove support for running the
  plugin with flake8<5 before Python 3.7 has reached end-of-life. As such, the
  `FutureWarning` is no longer emitted.

## 22.8.2

New error codes:
* Y047: Detect unused `TypeAlias` declarations.
* Y049: Detect unused `TypedDict` definitions.
* Y050: Prefer `typing_extensions.Never` for argument annotations over
  `typing.NoReturn`.
* Y051: Detect redundant unions between `Literal` types and builtin supertypes
  (e.g. `Literal["foo"] | str`, or `Literal[5] | int`).

Other enhancements:
* Support `mypy_extensions.TypedDict`.

## 22.8.1

* Add support for flake8 >= 5.0.0.

## 22.8.0

New error codes:
* Y046: Detect unused `Protocol`s.
* Y048: Function bodies should contain exactly one statement.

Bugfixes:
* Improve error message for the case where a function body contains a docstring
  and a `...` or `pass` statement.

Other changes:
* Pin required flake8 version to <5.0.0 (flake8-pyi is not currently compatible with flake8 5.0.0).

## 22.7.0

New error codes:
* Introduce Y041: Ban redundant numeric unions (`int | float`, `int | complex`,
  `float | complex`).
* Introduce Y042: Type alias names should use CamelCase rather than snake_case
* Introduce Y043: Ban type aliases from having names ending with an uppercase "T".
* Introduce Y044: Discourage unnecessary `from __future__ import annotations` import.
  Contributed by Torsten Wörtwein.
* Introduce Y045: Ban returning `(Async)Iterable` from `__(a)iter__` methods.

Other enhancements and behaviour changes:
* Improve error message for Y026 check.
* Expand Y026 check. Since version 22.4.0, this has only emitted an error for
  assignments to `typing.Literal`, `typing.Union`, and PEP 604 unions. It now also
  emits an error for any subscription on the right-hand side of a simple assignment, as
  well as for assignments to `typing.Any` and `None`.
* Support `typing_extensions.overload` and `typing_extensions.NamedTuple`.
* Slightly expand Y034 to cover the case where a class inheriting from `(Async)Iterator`
  returns `(Async)Iterable` from `__(a)iter__`. These classes should nearly always return
  `Self` from these methods.
* Support Python 3.11.

## 22.5.1

Behaviour changes:
* Relax Y020 check slightly, enabling the idiom `__all__ += ["foo", "bar"]` to be used
  in a stub file.

## 22.5.0

Features:
* Introduce Y039: Use `str` instead of `typing.Text` for Python 3 stubs.
* Teach the Y036 check that `builtins.object` (as well as the unqualified `object`) is
  acceptable as an annotation for an `__(a)exit__` method argument.
* Teach the Y029 check to emit errors for `__repr__` and `__str__` methods that return
  `builtins.str` (as opposed to the unqualified `str`).
* Introduce Y040: Never explicitly inherit from `object` in Python 3 stubs.

## 22.4.1

Features:
* Expand Y027 check to prohibit importing any objects from the `typing` module that are
  aliases for objects living `collections.abc` (except for `typing.AbstractSet`, which
  is special-cased).
* Introduce Y038: Use `from collections.abc import Set as AbstractSet` instead of
  `from typing import AbstractSet`.

Bugfixes:
* Improve inaccurate error messages for Y036.

## 22.4.0

Features:
* Introduce Y036 (check for badly defined `__exit__` and `__aexit__` methods).
* Introduce Y037 (Use PEP 604 syntax instead of `typing.Union` and `typing.Optional`).
  Contributed by Oleg Höfling.

Behaviour changes:
* Expand Y035 to cover `__match_args__` inside class definitions, as well as `__all__`
  in the global scope.

Bugfixes:
* Improve Y026 check (regarding `typing.TypeAlias`) to reduce false-positive errors
  emitted when the plugin encountered variable aliases in a stub file.

## 22.3.0

Bugfixes:
* fix bug where incorrect quoted annotations were not detected within `if` blocks

Behaviour changes:
* Add special-casing so that string literals are allowed in the context of
  `__match_args__` assignments inside a class definition.
* Add special-casing so that arbitrary values can be assigned to a variable in
  a stub file if the variable is annotated with `Final`.

## 22.2.0

Bugfixes:
* fix bugs in several error codes so that e.g. `_T = typing.TypeVar("_T")` is
  recognised as a `TypeVar` definition (previously only `_T = TypeVar("_T")` was
  recognised).
* fix bug where `foo = False` at the module level did not trigger a Y015 error.
* fix bug where `TypeVar`s were erroneously flagged as unused if they were only used in
  a `typing.Union` subscript.
* improve unclear error messages for Y022, Y023 and Y027 error codes.

Features:
* introduce Y032 (prefer `object` to `Any` for the second argument in `__eq__` and
  `__ne__` methods).
* introduce Y033 (always use annotations in stubs, rather than type comments).
* introduce Y034 (detect common errors where return types are hardcoded, but they
  should use `TypeVar`s instead).
* introduce Y035 (`__all__` in a stub has the same semantics as at runtime).

## 22.1.0

* extend Y001 to cover `ParamSpec` and `TypeVarTuple` in addition to `TypeVar`
* detect usage of non-integer indices in `sys.version_info` checks
* extend Y010 to check async functions in addition to normal functions
* extend Y010 to cover what was previously included in Y090 (disallow
  assignments in `__init__` methods) and Y091 (disallow `raise`
  statements). The previous checks were disabled by default.
* introduce Y016 (duplicate union member)
* introduce Y017 (disallows assignments with multiple targets or non-name targets)
* introduce Y018 (detect unused `TypeVar`s)
* introduce Y019 (detect `TypeVar`s that should be `_typeshed.Self`, but aren't)
* introduce Y020 (never use quoted annotations in stubs)
* introduce Y021 (docstrings should not be included in stubs)
* introduce Y022 (prefer stdlib classes over `typing` aliases)
* introduce Y023 (prefer `typing` over `typing_extensions`)
* introduce Y024 (prefer `typing.NamedTuple` to `collections.namedtuple`)
* introduce Y026 (require using `TypeAlias` for type aliases)
* introduce Y025 (always alias `collections.abc.Set`)
* introduce Y027 (Python 2-incompatible extension of Y022)
* introduce Y028 (Use class-based syntax for `NamedTuple`s)
* introduce Y029 (never define `__repr__` or `__str__`)
* introduce Y030 (use `Literal['foo', 'bar']` instead of `Literal['foo'] | Literal['bar']`)
* introduce Y031 (use class-based syntax for `TypedDict`s where possible)
* all errors are now enabled by default
* remove Y092 (top-level attribute must not have a default value)
* `attrs` is no longer a dependency
* `ast_decompiler` has been added as a dependency on Python 3.8 and 3.7
* support Python 3.10
* discontinue support for Python 3.6

## 20.10.0

* support Python 3.9

## 20.5.0

* support flake8 3.8.0
* introduce Y091 (function body must not contain `raise`)
* introduce Y015 (attribute must not have a default value other than `...`)
* introduce Y092 (top-level attribute must not have a default value)

## 19.3.0

* update pyflakes dependency

## 19.2.0

* support Python 3.7
* add a check for non-ellipsis, non-typed arguments
* add checks for checking empty classes
* use --stdin-display-name as the filename when reading from stdin

## 18.3.1

* introduce Y011

## 18.3.0

* (release herp derp, don't use)

## 17.3.0

* introduce Y001 - Y010
* introduce optional Y090

## 17.1.0

* handle `del` statements in stub files

## 16.12.2

* handle annotated assignments in 3.6+ with forward reference support

## 16.12.1

* handle forward references during subclassing on module level

* handle forward references during type aliasing assignments on module level

## 16.12.0

* first published version

* date-versioned
