import glob
import os
import re
import subprocess

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

        for match in re.finditer("# ([A-Z][0-9][0-9][0-9][^#]*)", line):
            expected_output += f"{path}:{lineno}: {match.group(1).strip()}\n"

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
