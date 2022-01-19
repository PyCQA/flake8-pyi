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
and ``isort`` formatting is also checked automatically (but only for ``pyi.py``).

We advise setting up a virtual environment before formatting your PR or (optionally)
running the tests::

    $ python3 -m venv env
    $ source env/bin/activate
    $ pip install -r requirements-dev.txt

To format your code with ``isort`` and ``black``, run::

    $ isort pyi.py
    $ black pyi.py

If you want, you can also run locally the commands that GitHub Actions runs.
Look in ``.github/workflows/`` to find the commands.
For example, to run tests::

    $ python3 -m pytest
