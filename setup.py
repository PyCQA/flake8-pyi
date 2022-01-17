# Copyright (C) 2016 Łukasz Langa

import ast
import os
import re
from setuptools import setup
import sys


assert sys.version_info >= (3, 7, 0), "flake8-pyi requires Python 3.7+"


current_dir = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(current_dir, "README.rst"), encoding="utf8") as ld_file:
    long_description = ld_file.read()


_version_re = re.compile(r"__version__\s+=\s+(?P<version>.*)")


with open(os.path.join(current_dir, "pyi.py"), "r") as f:
    version = _version_re.search(f.read()).group("version")
    version = str(ast.literal_eval(version))


setup(
    name="flake8-pyi",
    version=version,
    description="A plugin for flake8 to enable linting .pyi files.",
    long_description=long_description,
    keywords="flake8 pyi bugs pyflakes pylint linter qa",
    author="Łukasz Langa",
    author_email="lukasz@langa.pl",
    url="https://github.com/ambv/flake8-pyi",
    license="MIT",
    py_modules=["pyi"],
    zip_safe=False,
    python_requires=">=3.7",
    install_requires=[
        "flake8 >= 3.2.1",
        "pyflakes >= 2.1.1",
        'ast-decompiler >= 0.4.0, <0.5.0; python_version < "3.9"',
    ],
    test_suite="tests.test_pyi",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Framework :: Flake8",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Quality Assurance",
    ],
    entry_points={"flake8.extension": ["Y0 = pyi:PyiTreeChecker"]},
)
