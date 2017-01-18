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

Currently this plugin doesn't add any warnings of its own.  It does reserve
codes starting with **Y0**.


License
-------

MIT


Tests
-----

Just run::

    python3.6 setup.py test

Note: tests require 3.6+ due to testing variable annotations.


Change Log
----------

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

Glued together by `Łukasz Langa <mailto:lukasz@langa.pl>`_.
