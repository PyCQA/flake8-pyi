import glob
import os
import re
import subprocess
import sys

import pytest


@pytest.mark.parametrize("path", glob.glob("tests/*.pyi"))
def test_pyi_file(path):
    flags = []
    expected_output = ""

    with open(path) as file:
        file_contents = file.read()

    for lineno, line in enumerate(file_contents.splitlines(), start=1):
        if line.startswith("# flags: "):
            flags.extend(line.split()[2:])
            continue

        match = re.search("# ([A-Z][0-9][0-9][0-9].*)", line)
        if match:
            expected_output += f"{path}:{lineno}: {match.group(1)}\n"

    # TODO: are python-version-dependent error messages really a good idea?
    if sys.version_info < (3, 9):
        expected_output = re.sub(
            r'Y016 Duplicate union member ".*"',
            "Y016 Duplicate union member",
            expected_output,
        )
        expected_output = re.sub(
            r'Y019 Use "_typeshed\.Self" instead of ("_\w+"), e\.g\. "def .*?: \.\.\."',
            r'Y019 Use "_typeshed.Self" instead of \1',
            expected_output,
        )

    run_results = [
        # Passing a file on command line
        subprocess.run(
            ["flake8", "-j0", *flags, path],
            env={**os.environ, "PYTHONPATH": "."},
            stdout=subprocess.PIPE,
        ),
        # Passing "-" as the file, and reading from stdin instead
        subprocess.run(
            ["flake8", "-j0", "--stdin-display-name", path, *flags, "-"],
            env={**os.environ, "PYTHONPATH": "."},
            input=file_contents.encode("utf-8"),
            stdout=subprocess.PIPE,
        ),
    ]

    for run_result in run_results:
        output = run_result.stdout.decode("utf-8")
        output = re.sub(":[0-9]+: ", ": ", output)  # ignore column numbers
        assert output == expected_output
