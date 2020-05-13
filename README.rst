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

The latter should ideally be merged into ``flake8`` as the integration is
currently pretty brittle (might break with future versions of ``pyflakes``,
``flake8``, or due to interactions with other overly clever plugins).


List of warnings
----------------

This plugin reserves codes starting with **Y0**. The following warnings are
currently emitted:

* Y001: Names of TypeVars in stubs should start with `_`. This makes sure you
  don't accidentally expose names internal to the stub.
* Y002: If test must be a simple comparison against `sys.platform` or
  `sys.version_info`. Stub files support simple conditionals to indicate
  differences between Python versions or platforms, but type checkers only
  understand a limited subset of Python syntax, and this warning triggers on
  conditionals that type checkers will probably not understand.
* Y003: Unrecognized `sys.version_info` check. Similar, but triggers on some
  comparisons involving version checks.
* Y004: Version comparison must use only major and minor version. Type checkers
  like mypy don't know about patch versions of Python (e.g. 3.4.3 versus 3.4.4),
  only major and minor versions (3.3 versus 3.4). Therefore, version checks in
  stubs should only use the major and minor versions. If new functionality was
  introduced in a patch version, pretend that it was there all along.
* Y005: Version comparison must be against a length-n tuple.
* Y006: Use only < and >= for version comparisons. Comparisons involving > and
  <= may produce unintuitive results when tools do use the full sys.version_info
  tuple.
* Y007: Unrecognized `sys.platform` check. Platform checks should be simple
  string comparisons.
* Y008: Unrecognized platform. To prevent you from typos, we warn if you use a
  platform name outside a small set of known platforms (e.g. "linux" and
  "win32").
* Y009: Empty body should contain "...", not "pass". This is just a stylistic
  choice, but it's the one typeshed made.
* Y010: Function body must contain only "...". Stub files should not contain
  code, so function bodies should be empty. Currently, we make exceptions for
  raise statements and for assignments in `__init__` methods.
* Y011: All default values for typed function arguments must be "...". Type
  checkers ignore the default value, so the default value is not useful
  information in a stub file.
* Y012: Class body must not contain "pass".
* Y013: Non-empty class body must not contain "...".
* Y014: All default values for arguments must be "...". A stronger version
  of Y011 that includes arguments without type annotations.
* Y015: Attribute must not have a default value other than "...".

The following warnings are disabled by default:

* Y090: Use explicit attributes instead of assignments in `__init__`. This
  is a stricter version of Y010. Instead of::

    class Thing:
        def __init__(self, x: str) -> None:
            self.x = x

  you should write::

     class Thing:
         x: str
         def __init__(self, x: str) -> None: ...

* Y091: Function body must not contain "raise".
* Y092: Top-level attribute must not have a default value.

License
-------

MIT


Tests
-----

Just run::

    python3.6 setup.py test

Or if you prefer::

    tox

Note: tests require 3.6+ due to testing variable annotations.


Change Log
----------

20.5.0
~~~~~~

* support flake8 3.8.0
* introduce Y091 (function body must not contain "raise")
* introduce Y015 (attribute must not have a default value other than "...")
* introduce Y092 (top-level attribute must not have a default value)

19.3.0
~~~~~~

* update pyflakes dependency

19.2.0
~~~~~~~

* support Python 3.7
* add a check for non-ellipsis, non-typed arguments
* add checks for checking empty classes
* use --stdin-display-name as the filename when reading from stdin

18.3.1
~~~~~~

* introduce Y011

18.3.0
~~~~~~

* (release herp derp, don't use)

17.3.0
~~~~~~

* introduce Y001 - Y010
* introduce optional Y090

17.1.0
~~~~~~

* handle ``del`` statements in stub files

16.12.2
~~~~~~~

* handle annotated assignments in 3.6+ with forward reference support

16.12.1
~~~~~~~

* handle forward references during subclassing on module level

* handle forward references during type aliasing assignments on module level

16.12.0
~~~~~~~

* first published version

* date-versioned


Authors
-------

Glued together by `Łukasz Langa <mailto:lukasz@langa.pl>`_ and
`Jelle Zijlstra <mailto:jelle.zijlstra@gmail.com>`_.
