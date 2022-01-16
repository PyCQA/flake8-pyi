Change Log
----------

unreleased
~~~~~~~~~~

* detect usage of non-integer indices in sys.version_info checks
* extend Y010 to check async functions in addition to normal functions 
* introduce Y093 (require using TypeAlias for type aliases)
* introduce Y017 (disallows assignments with multiple targets or non-name targets)
* extend Y001 to cover ParamSpec and TypeVarTuple in addition to TypeVar
* introduce Y018 (detect unused TypeVars)
* introduce Y016 (duplicate union member)
* support Python 3.10
* discontinue support for Python 3.6

20.10.0
~~~~~~~

* support Python 3.9

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
