import glob
import os
import re
import subprocess

import pytest


@pytest.mark.parametrize("path", glob.glob("tests/*.pyi"))
def test_pyi_file(path):
    expected_output = ""
    command = ["flake8", "-j0"]

    with open(path) as file:
        for lineno, line in enumerate(file, start=1):
            if line.startswith("# flags: "):
                command.extend(line.split()[2:])
                continue

            for error_comment in re.findall("# [A-Z][0-9][0-9][0-9][^#]*", line):
                expected_output += f"{path}:{lineno}: {error_comment[1:].strip()}\n"

    command.append(str(path))

    actual_output = subprocess.run(
        command,
        env={**os.environ, "PYTHONPATH": "."},
        stderr=subprocess.STDOUT,
        stdout=subprocess.PIPE,
    ).stdout.decode()
    actual_output = re.sub(":[0-9]+: ", ": ", actual_output)  # ignore column numbers
    assert actual_output == expected_output

