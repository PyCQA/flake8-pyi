import glob
import os
import os.path
import re
import subprocess
import sys
from itertools import zip_longest

import pytest


IGNORED_DEPRECATION_WARNINGS = [
    # Ignore all DeprecationWarnings that come from pyflakes or flake8-bugbear
    rf"{re.escape(os.path.join('pyflakes', 'checker.py'))}:\d+: DeprecationWarning: ",
    r"bugbear\.py:\d+: DeprecationWarning: ",
]
IGNORED_DEPRECATION_PATTERNS = [
    re.compile(pattern) for pattern in IGNORED_DEPRECATION_WARNINGS
]


def get_filtered_stderr(stderr: str) -> str:
    lines = stderr.splitlines()

    grouped_lines = []
    skip_this_line = False
    for line, next_line in zip_longest(lines, lines[1:]):
        if skip_this_line:
            skip_this_line = False
        elif next_line is None:
            grouped_lines.append(line)
        elif "DeprecationWarning" in line:
            grouped_lines.append(line + "\n" + next_line)
            skip_this_line = True
        else:
            grouped_lines.append(line)

    return "\n".join(
        line
        for line in grouped_lines
        if not any(pattern.search(line) for pattern in IGNORED_DEPRECATION_PATTERNS)
    )


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
        "--ignore flags in test files override the .flake8 config file. "
        "Use --extend-ignore instead."
    )
    for flag in flags:
        option = flag.split("=")[0]
        assert option != "--ignore", bad_flag_msg

    run_results = [
        # Passing a file on command line
        subprocess.run(
            [sys.executable, "-Wa", "-m", "flake8", "-j0", *flags, path],
            env={**os.environ, "PYTHONPATH": "."},
            capture_output=True,
            text=True,
        ),
        # Passing "-" as the file, and reading from stdin instead
        subprocess.run(
            [
                sys.executable,
                "-Wa",
                "-m",
                "flake8",
                "-j0",
                "--stdin-display-name",
                path,
                *flags,
                "-",
            ],
            env={**os.environ, "PYTHONPATH": "."},
            input=file_contents,
            capture_output=True,
            text=True,
        ),
    ]

    for run_result in run_results:
        output = run_result.stdout
        if stderr := get_filtered_stderr(run_result.stderr):
            output += "\n" + stderr
        output = re.sub(":[0-9]+: ", ": ", output)  # ignore column numbers
        assert output == expected_output
