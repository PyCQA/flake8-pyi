# Contributing to flake8-pyi

Welcome! flake8-pyi started off as a project to help lint typeshed stubs, but aims to
be a package that can be utilised by any user of Python stubs. Any PRs towards that
end will be warmly received.


## Guide to the codebase

The plugin consists of a single file: `pyi.py`. Tests are run using `pytest`, and can be
found in the `tests` folder.


## Tests and formatting

When you make a pull request, [pre-commit.ci](https://pre-commit.ci/) bots will
automatically reformat your code using `black` and `isort`. GitHub Actions will
also run the full test suite on your proposed changes.

If you wish to (optionally) run the tests or format your code prior to submitting your PR,
however, we advise setting up a virtual environment first:

    $ python3 -m venv env
    $ source env/bin/activate
    $ pip install -r requirements-dev.txt
    $ pip install -e .

To format your code with `isort` and `black`, run:

    $ isort pyi.py
    $ black pyi.py

If you want, you can also run locally the commands that GitHub Actions runs.
Look in `.github/workflows/` to find the commands.
For example, to run tests:

    $ python3 -m pytest -vv

To run the tests in a single test file, use the `-k` option. For example, to
run all tests in `tests/quotes.pyi`:

    $ python3 -m pytest -vv -k quotes.pyi


## Making a release

`flake8-pyi` uses calendar-based versioning. For example, the first
release in January 2022 should be called 22.1.0, followed by 22.1.1.

Releasing a new version is easy:

- Make a PR that updates the version header in `CHANGELOG.md`
  and the `__version__` attribute in `pyi.py`.
- Merge the PR and wait for tests to complete.
- Draft a release using the GitHub UI. The tag name should be
  identical to the version (e.g., `22.1.0`) and the release notes
  should be copied from `CHANGELOG.md`.
- A workflow will run and automatically upload the release to PyPI.
  If it doesn't work, check the Actions tab to see what went wrong.
