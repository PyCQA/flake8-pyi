import glob
import os
import re
import subprocess
import sys
from itertools import zip_longest

import pytest


@pytest.mark.parametrize("path", glob.glob("tests/*.pyi"))
def test_pyi_file(path: str) -> None:
    flags = []
    expected_output = ""

    if match := re.search(r"_py3(\d+)\.pyi$", path):
        if sys.version_info < (3, int(match.group(1))):
            pytest.skip(f"Python {sys.version_info} is too old for {path}")

    with open(path, encoding="UTF-8") as file:
        file_contents = file.read()

    for lineno, line in enumerate(file_contents.splitlines(), start=1):
        if line.startswith("# flags: "):
            flags.extend(line.split()[2:])
            continue
        if line.startswith("#"):
            continue

        error_codes = list(re.finditer(r"# ([A-Z]\d\d\d )", line))

        for match, next_match in zip_longest(error_codes, error_codes[1:]):
            end_pos = len(line) if next_match is None else next_match.start()
            message = line[match.end() : end_pos].strip()
            expected_output += f"{path}:{lineno}: {match.group(1)}{message}\n"

    bad_flag_msg = (
        "--{flag} flags in test files override the .flake8 config file. "
        "Use --extend-{flag} instead."
    ).format

    for flag in flags:
        option = flag.split("=")[0]
        assert option not in {"--ignore", "--select"}, bad_flag_msg(option[2:])

    # Silence DeprecationWarnings from our dependencies (pyflakes, flake8-bugbear, etc.)
    #
    # For DeprecationWarnings coming from flake8-pyi itself,
    # print the first occurence of each warning to stderr.
    # This will fail CI the same as `-Werror:::pyi`,
    # but the test failure report that pytest gives is much easier to read
    # if we use `-Wdefault:::pyi`
    flake8_invocation = [
        sys.executable,
        "-Wignore",
        "-Wdefault:::pyi",
        "-m",
        "flake8",
        "-j0",
    ]

    run_results = [
        # Passing a file on command line
        subprocess.run(
            [*flake8_invocation, *flags, path],
            env={**os.environ, "PYTHONPATH": "."},
            capture_output=True,
            text=True,
        ),
        # Passing "-" as the file, and reading from stdin instead
        subprocess.run(
            [*flake8_invocation, "--stdin-display-name", path, *flags, "-"],
            env={**os.environ, "PYTHONPATH": "."},
            input=file_contents,
            capture_output=True,
            text=True,
        ),
    ]

    for run_result in run_results:
        output = re.sub(":[0-9]+: ", ": ", run_result.stdout)  # ignore column numbers
        if run_result.stderr:
            output += "\n" + run_result.stderr
        assert output == expected_output
