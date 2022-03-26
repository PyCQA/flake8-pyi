# Change Log

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
