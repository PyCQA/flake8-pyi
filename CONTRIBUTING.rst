==========================
Contributing to flake8-pyi
==========================

Welcome! flake8-pyi started off as a project to help lint typeshed stubs, but aims to
be a package that can be utilised by any user of Python stubs. Any PRs towards that
end will be warmly received.


Guide to the codebase
---------------------

The plugin consists of a single file: ``pyi.py``. Tests are run using ``pytest``, and can be
found in the ``tests`` folder.


Tests and formatting
--------------------

When you make a pull request, GitHub Actions runs the full test suite. ``black``
formatting is also checked automatically (but only for ``pyi.py``).

We advise setting up a virtual environment before formatting your PR or (optionally)
running the tests::

    $ python3 -m venv env
    $ source env/bin/activate
    $ pip install -r requirements-dev.txt

To format your code with ``black``, run::

    $ black pyi.py

If you want, you can also run locally the commands that GitHub Actions runs.
Look in ``.github/workflows/`` to find the commands.
For example, to run tests::

    $ python3 -m pytest

Possible future changes
-----------------------

``flake8-pyi`` aims to provide support for modern conventions in writing
typed Python code, such as using ``|`` instead of ``Union`` and using the
``list`` builtin instead of ``typing.List``.

The functionality that supports unquoted forward references in ``.pyi`` files
should ideally be merged into ``flake8`` as the integration is
currently pretty brittle (might break with future versions of ``pyflakes``,
``flake8``, or due to interactions with other overly clever plugins).
