# flake8-pyi

A plugin for Flake8 that provides specializations for
[type hinting stub files](https://www.python.org/dev/peps/pep-0484/#stub-files),
especially interesting for linting
[typeshed](https://github.com/python/typeshed/).

Refer to [this documentation](https://typing.readthedocs.io/en/latest/source/stubs.html) for more
details on stub files.

## Functionality

1. Adds the `.pyi` extension to the default value of the `--filename`
   command-line argument to Flake8.  This means stubs are linted by default with
   this plugin enabled, without needing to explicitly list every file.

2. Modifies PyFlakes runs for `.pyi` files to defer checking type annotation
   expressions after the entire file has been read.  This enables support for
   first-class forward references that stub files use.

3. Provides a number of `.pyi`-specific warnings that enforce typeshed's
   style guide.

Note: Be careful when using this plugin in the same environment as other flake8
plugins, as they might generate errors that are inappropriate for
`.pyi` files (e.g., about missing docstrings). We recommend running
`flake8-pyi` in a dedicated environment in your CI.

## Lints provided

This plugin reserves codes starting with **Y0**. For a full list of lints
currently provided by flake8-pyi, see the
[list of error codes](https://github.com/PyCQA/flake8-pyi/blob/main/ERRORCODES.md).

Note that several error codes recommend using types from `typing_extensions` or
`_typeshed`. Strictly speaking, these packages are not part of the standard
library. However, these packages are included in typeshed's `stdlib/`
directory, meaning that type checkers believe them to be part of the standard
library even if this does not reflect the reality at runtime. As such, since
stubs are never executed at runtime, types from `typing_extensions` and
`_typeshed` can be used freely in a stubs package, even if the package does not
have an explicit dependency on either `typing_extensions` or typeshed.

Flake8-pyi's checks may produce false positives on stubs that aim to support Python 2.

## License

MIT

## Authors

Originally created by [Łukasz Langa](mailto:lukasz@langa.pl) and
now maintained by
[Jelle Zijlstra](mailto:jelle.zijlstra@gmail.com),
[Alex Waygood](mailto:alex.waygood@gmail.com),
Sebastian Rittau, Akuli, and Shantanu.

## See also

* [List of error codes](https://github.com/PyCQA/flake8-pyi/blob/main/ERRORCODES.md)
* [Changelog](https://github.com/PyCQA/flake8-pyi/blob/main/CHANGELOG.md)
* [Information for contributors](https://github.com/PyCQA/flake8-pyi/blob/main/CONTRIBUTING.md)
