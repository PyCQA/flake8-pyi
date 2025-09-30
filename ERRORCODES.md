## Types of warnings

flake8-pyi's error codes can currently be divided into the following categories:

| Category            | Description | Example
|---------------------|-------------|---------
| Understanding stubs | Stub files differ from `.py` files in many respects when it comes to how they work and how they're used. These error codes flag antipatterns that may demonstrate that a user does not fully understand the semantics or purpose of stub files. | Y010
| Correctness         | These error codes flag places where it looks like the stub might be incorrect in a way that would be visible for users of the stub. | Y001
| Redundant code      | These error codes flag places where it looks like code could simply be deleted. | Y016
| Style               | These error codes enforce a consistent, stub-specific style guide. | Y009

## List of warnings

The following warnings are currently emitted by default:

| Code | Description | Code category
|------|-------------|---------------
| <a id="Y001" href="#Y001">Y001</a> | Names of `TypeVar`s, `ParamSpec`s and `TypeVarTuple`s in stubs should usually start with `_`. This makes sure you don't accidentally expose names internal to the stub. | Correctness
| <a id="Y002" href="#Y002">Y002</a> | An `if` test must be a simple comparison against `sys.platform` or `sys.version_info`. Stub files support simple conditionals to indicate differences between Python versions or platforms, but type checkers only understand a limited subset of Python syntax. This warning is emitted on conditionals that type checkers may not understand. | Correctness
| <a id="Y003" href="#Y003">Y003</a> | Unrecognized `sys.version_info` check. Similar to Y002, but adds some additional checks specific to `sys.version_info` comparisons. | Correctness
| <a id="Y004" href="#Y004">Y004</a> | Version comparison must use only major and minor version. Type checkers like mypy don't know about patch versions of Python (e.g. 3.4.3 versus 3.4.4), only major and minor versions (3.3 versus 3.4). Therefore, version checks in stubs should only use the major and minor versions. If new functionality was introduced in a patch version, pretend that it was there all along. | Correctness
| <a id="Y005" href="#Y005">Y005</a> | Version comparison must be against a length-n tuple. | Correctness
| <a id="Y006" href="#Y006">Y006</a> | Use only `<` and `>=` for version comparisons. Comparisons involving `>` and `<=` may produce unintuitive results when tools do use the full `sys.version_info` tuple. | Correctness
| <a id="Y007" href="#Y007">Y007</a> | Unrecognized `sys.platform` check. Platform checks should be simple string comparisons. | Correctness
| <a id="Y008" href="#Y008">Y008</a> | Unrecognized platform in a `sys.platform` check. To prevent you from typos, we warn if you use a platform name outside a small set of known platforms (e.g. `"linux"` and `"win32"`). | Correctness
| <a id="Y009" href="#Y009">Y009</a> | Empty class or function body should contain `...`, not `pass`. | Style
| <a id="Y010" href="#Y010">Y010</a> | Function body must contain only `...`. Stub files are never executed at runtime, so function bodies should be empty. | Understanding stubs
| <a id="Y011" href="#Y011">Y011</a> | Only simple default values (`int`, `float`, `complex`, `bytes`, `str`, `bool`, `None`, `...`, or simple container literals) are allowed for typed function arguments. Type checkers ignore the default value, so the default value is not useful information for type-checking, but it may be useful information for other users of stubs such as IDEs. If you're writing a stub for a function that has a more complex default value, use `...` instead of trying to reproduce the runtime default exactly in the stub. Also use `...` for very long numbers, very long strings, very long bytes, or defaults that vary according to the machine Python is being run on. | Style
| <a id="Y012" href="#Y012">Y012</a> | Class body must not contain `pass`. | Style
| <a id="Y013" href="#Y013">Y013</a> | Non-empty class body must not contain `...`. | Redundant code
| <a id="Y014" href="#Y014">Y014</a> | Only simple default values are allowed for any function arguments. A stronger version of Y011 that includes arguments without type annotations. | Style
| <a id="Y015" href="#Y015">Y015</a> | Only simple default values are allowed for assignments. Similar to Y011, but for assignments rather than parameter annotations. | Style
| <a id="Y016" href="#Y016">Y016</a> | Unions shouldn't contain duplicates, e.g. `str \| str` is not allowed. | Redundant code
| <a id="Y017" href="#Y017">Y017</a> | Stubs should not contain assignments with multiple targets or non-name targets. E.g. `T, S = TypeVar("T"), TypeVar("S")` is disallowed, as is `foo.bar = TypeVar("T")`. | Style
| <a id="Y018" href="#Y018">Y018</a> | A private `TypeVar` should be used at least once in the file in which it is defined. | Redundant code
| <a id="Y019" href="#Y019">Y019</a> | Certain kinds of methods should use [`typing_extensions.Self`](https://docs.python.org/3/library/typing.html#typing.Self) instead of defining custom `TypeVar`s for their return annotation. This check currently applies for instance methods that return `self`, class methods that return an instance of `cls`, and `__new__` methods. | Style
| <a id="Y020" href="#Y020">Y020</a> | Quoted annotations should never be used in stubs. Since stub files are never executed at runtime, forward references can be used in any location without having to use quotes. (See also: Y044.) | Understanding stubs
| <a id="Y021" href="#Y021">Y021</a> | Docstrings should not be included in stubs. | Style
| <a id="Y022" href="#Y022">Y022</a> | The `typing` and `typing_extensions` modules include various aliases to stdlib objects. Use these as little as possible (e.g. prefer `builtins.list` over `typing.List`, `collections.Counter` over `typing.Counter`, etc.). | Style
| <a id="Y023" href="#Y023">Y023</a> | Where there is no detriment to backwards compatibility, import objects such as `ClassVar` and `NoReturn` from `typing` rather than `typing_extensions`. | Style
| <a id="Y024" href="#Y024">Y024</a> | Use `typing.NamedTuple` instead of `collections.namedtuple`, as it allows for more precise type inference. | Correctness
| <a id="Y025" href="#Y025">Y025</a> | Always alias `collections.abc.Set` when importing it, so as to avoid confusion with `builtins.set`. E.g. use `from collections.abc import Set as AbstractSet` instead of `from collections.abc import Set`. | Style
| <a id="Y026" href="#Y026">Y026</a> | Type aliases should be explicitly demarcated with `typing.TypeAlias` (or use a [PEP-695 type statement](https://docs.python.org/3/reference/simple_stmts.html#the-type-statement)). | Correctness
| <a id="Y028" href="#Y028">Y028</a> | Always use class-based syntax for `typing.NamedTuple`, instead of assignment-based syntax. | Correctness
| <a id="Y029" href="#Y029">Y029</a> | It is almost always redundant to define `__str__` or `__repr__` in a stub file, as the signatures are almost always identical to `object.__str__` and `object.__repr__`. | Understanding stubs
| <a id="Y030" href="#Y030">Y030</a> | Union expressions should never have more than one `Literal` member, as `Literal[1] \| Literal[2]` is semantically identical to `Literal[1, 2]`. | Style
| <a id="Y031" href="#Y031">Y031</a> | `TypedDict`s should use class-based syntax instead of assignment-based syntax wherever possible. (In situations where this is not possible, such as if a field is a Python keyword or an invalid identifier, this error will not be emitted.) | Style
| <a id="Y032" href="#Y032">Y032</a> | The second argument of an `__eq__` or `__ne__` method should usually be annotated with `object` rather than `Any`. | Correctness
| <a id="Y033" href="#Y033">Y033</a> | Do not use type comments (e.g. `x = ... # type: int`) in stubs. Always use annotations instead (e.g. `x: int`). | Style
| <a id="Y034" href="#Y034">Y034</a> | Y034 detects common errors where certain methods are annotated as having a fixed return type, despite returning `self` at runtime. Such methods should be annotated with `typing_extensions.Self`. This check looks for:<br><br>&nbsp;&nbsp;**1.**&nbsp;&nbsp;Any in-place BinOp dunder methods (`__iadd__`, `__ior__`, etc.) that do not return `Self`.<br>&nbsp;&nbsp;**2.**&nbsp;&nbsp;`__new__`, `__enter__` and `__aenter__` methods that return the class's name unparameterised.<br>&nbsp;&nbsp;**3.**&nbsp;&nbsp;`__iter__` methods that return `Iterator`, even if the class inherits directly from `Iterator`.<br>&nbsp;&nbsp;**4.**&nbsp;&nbsp;`__aiter__` methods that return `AsyncIterator`, even if the class inherits directly from `AsyncIterator`.<br><br>This check excludes methods decorated with `@overload` or `@abstractmethod`. | Correctness
| <a id="Y035" href="#Y035">Y035</a> | `__all__`, `__match_args__` and `__slots__` in a stub file should always have values, as these special variables in a `.pyi` file have identical semantics in a stub as at runtime. E.g. write `__all__ = ["foo", "bar"]` instead of `__all__: list[str]`. | Correctness
| <a id="Y036" href="#Y036">Y036</a> | Y036 detects common errors in `__exit__` and `__aexit__` methods. For example, the first argument in an `__exit__` method should either be annotated with `object`, `_typeshed.Unused` (a special alias for `object`) or `type[BaseException] \| None`. | Correctness
| <a id="Y037" href="#Y037">Y037</a> | Use PEP 604 syntax instead of `typing(_extensions).Union` and `typing(_extensions).Optional`. E.g. use `str \| int` instead of `Union[str, int]`, and use `str \| None` instead of `Optional[str]`. | Style
| <a id="Y038" href="#Y038">Y038</a> | Use `from collections.abc import Set as AbstractSet` instead of `from typing import AbstractSet` or `from typing_extensions import AbstractSet`. | Style
| <a id="Y039" href="#Y039">Y039</a> | Use `str` instead of `typing.Text` or `typing_extensions.Text`. | Style
| <a id="Y040" href="#Y040">Y040</a> | Never explicitly inherit from `object`, as all classes implicitly inherit from `object` in Python 3. | Style
| <a id="Y041" href="#Y041">Y041</a> | Y041 detects redundant numeric unions in the context of parameter annotations. For example, PEP 484 specifies that type checkers should allow `int` objects to be passed to a function, even if the function states that it accepts a `float`. As such, `int` is redundant in the union `int \| float` in the context of a parameter annotation. In the same way, `int` is sometimes redundant in the union `int \| complex`, and `float` is sometimes redundant in the union `float \| complex`. | Style
| <a id="Y042" href="#Y042">Y042</a> | Type alias names should use CamelCase rather than snake_case. | Style
| <a id="Y043" href="#Y043">Y043</a> | Do not use names ending in "T" for private type aliases. (The "T" suffix implies that an object is a `TypeVar`.) | Style
| <a id="Y044" href="#Y044">Y044</a> | `from __future__ import annotations` has no effect in stub files, since type checkers automatically treat stubs as having those semantics. (See also: Y020.) | Understanding stubs
| <a id="Y045" href="#Y045">Y045</a> | `__iter__` methods should never return `Iterable[T]`, as they should always return some kind of iterator. | Correctness
| <a id="Y046" href="#Y046">Y046</a> | A private `Protocol` should be used at least once in the file in which it is defined. | Redundant code
| <a id="Y047" href="#Y047">Y047</a> | A private `TypeAlias` should be used at least once in the file in which it is defined. | Redundant code
| <a id="Y048" href="#Y048">Y048</a> | Function bodies should contain exactly one statement. This is because stub files are never executed at runtime, so any more than one statement would be redundant. (Note that if a function body includes a docstring, the docstring counts as a "statement".) | Understanding stubs
| <a id="Y049" href="#Y049">Y049</a> | A private `TypedDict` should be used at least once in the file in which it is defined. | Redundant code
| <a id="Y050" href="#Y050">Y050</a> | Prefer `typing_extensions.Never` over `typing.NoReturn` for argument annotations. | Style
| <a id="Y051" href="#Y051">Y051</a> | Y051 detects redundant unions between `Literal` types and builtin supertypes. For example, `Literal[5]` is redundant in the union `int \| Literal[5]`, and `Literal[True]` is redundant in the union `Literal[True] \| bool`. | Redundant code
| <a id="Y052" href="#Y052">Y052</a> | Y052 disallows assignments to constant values where the assignment does not have a type annotation. For example, `x = 0` in the global namespace is ambiguous in a stub, as there are four different types that could be inferred for the variable `x`: `int`, `Final[int]`, `Literal[0]`, or `Final[Literal[0]]`. Enum members are excluded from this check, as are various special assignments such as `__all__` and `__match_args__`. | Correctness
| <a id="Y053" href="#Y053">Y053</a> | Only string and bytes literals <=50 characters long are permitted. (There are some exceptions, such as `Literal` subscripts, metadata strings inside `Annotated` subscripts, and strings passed to `@deprecated`.) | Style
| <a id="Y054" href="#Y054">Y054</a> | Only numeric literals with a string representation <=10 characters long are permitted. | Style
| <a id="Y055" href="#Y055">Y055</a> | Unions of the form `type[X] \| type[Y]` can be simplified to `type[X \| Y]`. Similarly, `Union[type[X], type[Y]]` can be simplified to `type[Union[X, Y]]`. | Style
| <a id="Y056" href="#Y056">Y056</a> | Do not call methods such as `.append()`, `.extend()` or `.remove()` on `__all__`. Different type checkers have varying levels of support for calling these methods on `__all__`. Use `+=` instead, which is known to be supported by all major type checkers. | Correctness
| <a id="Y057" href="#Y057">Y057</a> | Do not use `typing.ByteString` or `collections.abc.ByteString`. These types have unclear semantics, and are deprecated; use  `typing_extensions.Buffer` or a union such as `bytes \| bytearray \| memoryview` instead. See [PEP 688](https://peps.python.org/pep-0688/) for more details. | Correctness
| <a id="Y058" href="#Y058">Y058</a> | Use `Iterator` rather than `Generator` as the return value for simple `__iter__` methods, and `AsyncIterator` rather than `AsyncGenerator` as the return value for simple `__aiter__` methods. Using `(Async)Iterator` for these methods is simpler and more elegant, and reflects the fact that the precise kind of iterator returned from an `__iter__` method is usually an implementation detail that could change at any time, and should not be relied upon. | Style
| <a id="Y059" href="#Y059">Y059</a> | `Generic[]` should always be the last base class, if it is present in a class's bases tuple. At runtime, if `Generic[]` is not the final class in a the bases tuple, this [can cause the class creation to fail](https://github.com/python/cpython/issues/106102). In a stub file, however, this rule is enforced purely for stylistic consistency. | Style
| <a id="Y060" href="#Y060">Y060</a> | Redundant inheritance from `Generic[]`. For example, `class Foo(Iterable[_T], Generic[_T]): ...` can be written more simply as `class Foo(Iterable[_T]): ...`.<br><br>To avoid false-positive errors, and to avoid complexity in the implementation, this check is deliberately conservative: it only flags classes where all subscripted bases have identical code inside their subscript slices. | Style
| <a id="Y061" href="#Y061">Y061</a> | Do not use `None` inside a `Literal[]` slice. For example, use `Literal["foo"] \| None` instead of `Literal["foo", None]`. While both are legal according to [PEP 586](https://peps.python.org/pep-0586/), the former is preferred for stylistic consistency. Note that this warning is not emitted if Y062 is emitted for the same `Literal[]` slice. For example, `Literal[None, None, True, True]` only causes Y062 to be emitted. | Style
| <a id="Y062" href="#Y062">Y062</a> | `Literal[]` slices shouldn't contain duplicates, e.g. `Literal[True, True]` is not allowed. | Redundant code
| <a id="Y063" href="#Y063">Y063</a> | Use [PEP 570 syntax](https://peps.python.org/pep-0570/) (e.g. `def foo(x: int, /) -> None: ...`) to denote positional-only arguments, rather than [the older Python 3.7-compatible syntax described in PEP 484](https://peps.python.org/pep-0484/#positional-only-arguments) (`def foo(__x: int) -> None: ...`, etc.). | Style
| <a id="Y064" href="#Y064">Y064</a> | Use simpler syntax to define final literal types. For example, use `x: Final = 42` instead of `x: Final[Literal[42]]`. | Style
| <a id="Y065" href="#Y065">Y065</a> | Don't use bare `Incomplete` in argument and return annotations. Instead, leave them unannotated. Omitting an annotation entirely from a function will cause some type checkers to view the parameter or return type as "untyped"; this may result in stricter type-checking on code that makes use of the stubbed function. | Style
| <a id="Y066" href="#Y066">Y066</a> | When using if/else with `sys.version_info`, put the code for new Python versions first. | Style
| <a id="Y067" href="#Y067">Y067</a> | Don't use `Incomplete \| None = None` in argument annotations. Instead, just use `=None`. | Style
| <a id="Y068" href="#Y068">Y068</a> | Don't use `@override` in stub files. Problems with a function signature deviating from its superclass are inherited from the implementation, and other tools such as stubtest are better placed to recognize deviations between stubs and the implementation. | Understanding stubs

## Warnings disabled by default

The following error codes are also provided, but are disabled by default due to
the risk of false-positive errors. To enable these error codes, use
`--extend-select={code1,code2,...}` on the command line or in your flake8
configuration file.

Note that `--extend-select` **will not work** if you have
`--select` specified on the command line or in your configuration file. We
recommend only using `--extend-select`, never `--select`.

| Code | Description | Code category
|------|-------------|---------------
| <a id="Y090" href="#Y090">Y090</a> | `tuple[int]` means "a tuple of length 1, in which the sole element is of type `int`". Consider using `tuple[int, ...]` instead, which means "a tuple of arbitrary (possibly 0) length, in which all elements are of type `int`". | Correctness
| <a id="Y091" href="#Y091">Y091</a> | Protocol methods should not have positional-or-keyword parameters. Usually, a positional-only parameter is better.
