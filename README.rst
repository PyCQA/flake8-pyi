==========
flake8-pyi
==========

A plugin for Flake8 that provides specializations for
`type hinting stub files <https://www.python.org/dev/peps/pep-0484/#stub-files>`_,
especially interesting for linting
`typeshed <https://github.com/python/typeshed/>`_.


Functionality
-------------

1. Adds the ``.pyi`` extension to the default value of the ``--filename``
   command-line argument to Flake8.  This means stubs are linted by default with
   this plugin enabled, without needing to explicitly list every file.

2. Modifies PyFlakes runs for ``.pyi`` files to defer checking type annotation
   expressions after the entire file has been read.  This enables support for
   first-class forward references that stub files use.

3. Provides a number of ``.pyi``-specific warnings that enforce typeshed's
   style guide.

Note: Be careful when using this plugin in the same environment as other flake8
plugins, as they might generate errors that are inappropriate for
``.pyi`` files (e.g., about missing docstrings). We recommend running
``flake8-pyi`` in a dedicated environment in your CI.


List of warnings
----------------

This plugin reserves codes starting with **Y0**. The following warnings are
currently emitted:

* Y001: Names of ``TypeVar``\ s, ``ParamSpec``\ s and ``TypeVarTuple``\ s in stubs
  should usually start with ``_``. This makes sure you don't accidentally expose
  names internal to the stub.
* Y002: If test must be a simple comparison against ``sys.platform`` or
  ``sys.version_info``. Stub files support simple conditionals to indicate
  differences between Python versions or platforms, but type checkers only
  understand a limited subset of Python syntax, and this warning triggers on
  conditionals that type checkers will probably not understand.
* Y003: Unrecognized ``sys.version_info`` check. Similar, but triggers on some
  comparisons involving version checks.
* Y004: Version comparison must use only major and minor version. Type checkers
  like mypy don't know about patch versions of Python (e.g. 3.4.3 versus 3.4.4),
  only major and minor versions (3.3 versus 3.4). Therefore, version checks in
  stubs should only use the major and minor versions. If new functionality was
  introduced in a patch version, pretend that it was there all along.
* Y005: Version comparison must be against a length-n tuple.
* Y006: Use only ``<`` and ``>=`` for version comparisons. Comparisons involving
  ``>`` and ``<=`` may produce unintuitive results when tools do use the full
  ``sys.version_info`` tuple.
* Y007: Unrecognized ``sys.platform`` check. Platform checks should be simple
  string comparisons.
* Y008: Unrecognized platform. To prevent you from typos, we warn if you use a
  platform name outside a small set of known platforms (e.g. ``"linux"`` and
  ``"win32"``).
* Y009: Empty body should contain ``...``, not ``pass``. This is just a stylistic
  choice, but it's the one typeshed made.
* Y010: Function body must contain only ``...``. Stub files should not contain
  code, so function bodies should be empty.
* Y011: All default values for typed function arguments must be ``...``. Type
  checkers ignore the default value, so the default value is not useful
  information in a stub file.
* Y012: Class body must not contain ``pass``.
* Y013: Non-empty class body must not contain ``...``.
* Y014: All default values for arguments must be ``...``. A stronger version
  of Y011 that includes arguments without type annotations.
* Y015: Attribute must not have a default value other than ``...``.
* Y016: Unions shouldn't contain duplicates, e.g. ``str | str`` is not allowed.
* Y017: Stubs should not contain assignments with multiple targets or non-name
  targets.
* Y018: A private ``TypeVar`` should be used at least once in the file in which
  it is defined.
* Y019: Certain kinds of methods should use ``_typeshed.Self`` instead of
  defining custom ``TypeVar``\ s for their return annotation. This check currently
  applies for instance methods that return ``self``, class methods that return
  an instance of ``cls``, and ``__new__`` methods.
* Y020: Quoted annotations should never be used in stubs.
* Y021: Docstrings should not be included in stubs.
* Y022: Imports linting: use typing-module aliases to stdlib objects as little
  as possible (e.g. ``builtins.list`` over ``typing.List``,
  ``collections.Counter`` over ``typing.Counter``, etc.).
* Y023: Where there is no detriment to backwards compatibility, import objects
  such as ``ClassVar`` and ``NoReturn`` from ``typing`` rather than
  ``typing_extensions``.
* Y024: Use ``typing.NamedTuple`` instead of ``collections.namedtuple``, as it
  allows for more precise type inference.
* Y025: Always alias ``collections.abc.Set`` when importing it, so as to avoid
  confusion with ``builtins.set``.
* Y026: Type aliases should be explicitly demarcated with ``typing.TypeAlias``.
* Y027: Same as Y022. Unlike Y022, however, the imports disallowed with this
  error code are required if you wish to write Python 2-compatible stubs.
  Switch this error code off in your config file if you support Python 2.
* Y028: Always use class-based syntax for ``typing.NamedTuple``, instead of
  assignment-based syntax.
* Y029: It is almost always redundant to define ``__str__`` or ``__repr__`` in
  a stub file, as the signatures are almost always identical to
  ``object.__str__`` and ``object.__repr__``.
* Y030: Union expressions should never have more than one ``Literal`` member,
  as ``Literal[1] | Literal[2]`` is semantically identical to
  ``Literal[1, 2]``.

Many error codes enforce modern conventions, and some cannot yet be used in
all cases:

* Y026 is incompatible with the pytype type checker and should be turned
  off for stubs that need to be compatible with pytype. A fix is tracked
  `here <https://github.com/google/pytype/issues/787>`_.
* Y027 is incompatible with Python 2 and should only be used in stubs
  that are meant only for Python 3.

License
-------

MIT


Authors
-------

Originally created by `Łukasz Langa <mailto:lukasz@langa.pl>`_ and
now maintained by
`Jelle Zijlstra <mailto:jelle.zijlstra@gmail.com>`_,
`Alex Waygood <mailto:alex.waygood@gmail.com>`_,
Sebastian Rittau, Akuli, and Shantanu.

See also
--------

* `Changelog <./CHANGELOG.rst>`_
* `Information for contributors <./CONTRIBUTING.rst>`_
