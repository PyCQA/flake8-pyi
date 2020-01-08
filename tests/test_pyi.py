import os
from pathlib import Path
import subprocess
import sys
from typing import Sequence, Tuple
import unittest


class PyiTestCase(unittest.TestCase):
    maxDiff = None  # type: int

    def checkFile(
        self, filename: str, pyi_aware: bool, extra_options: Sequence[str] = ()
    ) -> Tuple[int, str, str]:
        file_path = Path(__file__).absolute().parent / filename
        cmdline = ["flake8", "-j0", *extra_options, str(file_path)]
        if not pyi_aware:
            cmdline.insert(-1, "--no-pyi-aware-file-checker")
        env = os.environ.copy()
        env["PYTHONWARNINGS"] = "ignore"
        proc = subprocess.run(
            cmdline, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=60, env=env
        )
        stdout_text = proc.stdout.decode("utf8")
        stderr_text = proc.stderr.decode("utf8")
        return proc.returncode, stdout_text, stderr_text

    def checkStdin(
        self, filename: str, pyi_aware: bool, extra_options: Sequence[str] = ()
    ) -> Tuple[int, str, str]:
        file_path = Path(__file__).absolute().parent / filename
        cmdline = [
            "flake8",
            "-j0",
            "--stdin-display-name=" + filename,
            *extra_options,
            "-",
        ]
        if not pyi_aware:
            cmdline.insert(-1, "--no-pyi-aware-file-checker")
        env = os.environ.copy()
        env["PYTHONWARNINGS"] = "ignore"
        proc = subprocess.run(
            cmdline,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=60,
            env=env,
            input=file_path.read_bytes(),
        )
        stdout_text = proc.stdout.decode("utf8")
        stderr_text = proc.stderr.decode("utf8")
        return proc.returncode, stdout_text, stderr_text

    def checkFileOutput(
        self,
        filename: str,
        *,
        pyi_aware: bool = True,
        stdout_lines: Sequence[str] = (),
        stderr_lines: Sequence[str] = (),
        extra_options: Sequence[str] = ()
    ) -> None:
        def check_output(returncode: int, stdout: str, stderr: str):
            expected_returncode = 1 if stdout else 0

            for (actual, expected_lines) in [
                (stderr, stderr_lines),
                (stdout, stdout_lines),
            ]:
                actual = "\n".join(
                    line.split("/")[-1] for line in actual.split("\n") if line
                )
                expected = "\n".join(
                    "{filename}:{line}".format(filename=filename, line=line)
                    for line in expected_lines
                )
                self.assertMultiLineEqual(expected, actual)

            self.assertEqual(returncode, expected_returncode, stdout)

        with self.subTest(stdin=False):
            check_output(
                *self.checkFile(
                    filename, pyi_aware=pyi_aware, extra_options=extra_options
                )
            )

        with self.subTest(stdin=True):
            check_output(
                *self.checkStdin(
                    filename, pyi_aware=pyi_aware, extra_options=extra_options
                )
            )

    def test_vanilla_flake8_not_clean_forward_refs(self) -> None:
        stdout_lines = (
            "4:22: F821 undefined name 'CStr'",
            "5:14: F821 undefined name 'C'",
            "10:25: F821 undefined name 'C'",
            "14:9: F821 undefined name 'C'",
            # The following two only raised on the _annassign.pyi variant
            # "15:13: F821 undefined name 'C'",
            # "22:12: F821 undefined name 'C'",
            "27:35: F821 undefined name 'C'",
        )
        self.checkFileOutput(
            "forward_refs.pyi", pyi_aware=False, stdout_lines=stdout_lines
        )

    @unittest.skipIf(sys.version_info < (3, 6), "variable annotations used")
    def test_patched_flake8_clean_forward_refs(self) -> None:
        self.checkFileOutput(
            "forward_refs_annassign.pyi", pyi_aware=True, stdout_lines=()
        )

    def test_vanilla_flake8_not_clean_del(self) -> None:
        stdout_lines = ("4:16: F821 undefined name 'EitherStr'",)
        self.checkFileOutput("del.pyi", pyi_aware=False, stdout_lines=stdout_lines)

    def test_patched_flake8_clean_del(self) -> None:
        self.checkFileOutput("del.pyi", pyi_aware=True, stdout_lines=())

    def test_typevar(self) -> None:
        stdout_lines = ("3:1: Y001 Name of private TypeVar must start with _",)
        self.checkFileOutput("typevar.pyi", stdout_lines=stdout_lines)

    def test_sys_platform(self) -> None:
        stdout_lines = (
            "3:4: Y007 Unrecognized sys.platform check",
            "3:4: Y007 Unrecognized sys.platform check",
            "6:4: Y007 Unrecognized sys.platform check",
            '9:4: Y008 Unrecognized platform "linus"',
        )
        self.checkFileOutput("sysplatform.pyi", stdout_lines=stdout_lines)

    def test_sys_versioninfo(self) -> None:
        stdout_lines = (
            "6:4: Y003 Unrecognized sys.version_info check",
            "9:4: Y003 Unrecognized sys.version_info check",
            "12:4: Y003 Unrecognized sys.version_info check",
            "15:4: Y003 Unrecognized sys.version_info check",
            "18:4: Y003 Unrecognized sys.version_info check",
            "24:4: Y005 Version comparison must be against a length-1 tuple",
            "30:4: Y005 Version comparison must be against a length-2 tuple",
            "33:4: Y003 Unrecognized sys.version_info check",
            "36:4: Y003 Unrecognized sys.version_info check",
            "39:4: Y003 Unrecognized sys.version_info check",
            "42:4: Y004 Version comparison must use only major and minor version",
            "45:4: Y006 Use only < and >= for version comparisons",
            "48:4: Y006 Use only < and >= for version comparisons",
            "51:4: Y006 Use only < and >= for version comparisons",
            "60:4: Y002 If test must be a simple comparison against sys.platform or sys.version_info",
        )
        self.checkFileOutput("sysversioninfo.pyi", stdout_lines=stdout_lines)

    def test_comparisons(self) -> None:
        stdout_lines = (
            "3:4: Y002 If test must be a simple comparison against sys.platform or sys.version_info",
            "6:4: Y002 If test must be a simple comparison against sys.platform or sys.version_info",
            "9:4: Y002 If test must be a simple comparison against sys.platform or sys.version_info",
            "12:4: Y002 If test must be a simple comparison against sys.platform or sys.version_info",
        )
        self.checkFileOutput("comparisons.pyi", stdout_lines=stdout_lines)

    def test_class_def(self) -> None:
        stdout_lines = (
            '5:5: Y009 Empty body should contain "...", not "pass"',
            '9:5: Y012 Class body must not contain "pass"',
            '12:5: Y012 Class body must not contain "pass"',
            '17:5: Y013 Non-empty class body must not contain "..."',
            '20:5: Y013 Non-empty class body must not contain "..."',
        )
        self.checkFileOutput("emptyclasses.pyi", stdout_lines=stdout_lines)

    def test_function_def(self) -> None:
        stdout_lines = (
            '5:5: Y009 Empty body should contain "...", not "pass"',
            '19:5: Y010 Function body must contain only "..."',
            '23:5: Y010 Function body must contain only "..."',
        )
        self.checkFileOutput("emptyfunctions.pyi", stdout_lines=stdout_lines)

    def test_empty_init(self) -> None:
        # should have no output if it's not explicitly selected
        self.checkFileOutput("emptyinit.pyi", stdout_lines=())
        stdout_lines = (
            "3:9: Y090 Use explicit attributes instead of assignments in __init__",
        )
        self.checkFileOutput(
            "emptyinit.pyi", stdout_lines=stdout_lines, extra_options=("--select=Y090",)
        )

    def test_raise_in_function_body(self) -> None:
        self.checkFileOutput("raise.pyi", stdout_lines=())
        stdout_lines = (
            '3:9: Y091 Function body must not contain "raise"',
            '6:9: Y091 Function body must not contain "raise"',
        )
        self.checkFileOutput(
            "raise.pyi", stdout_lines=stdout_lines, extra_options=("--select=Y091",)
        )

    def test_defaults(self) -> None:
        stdout_lines = (
            '3:17: Y011 Default values for typed arguments must be "..."',
            '7:20: Y011 Default values for typed arguments must be "..."',
            '9:10: Y014 Default values for arguments must be "..."',
            '13:20: Y011 Default values for typed arguments must be "..."',
        )
        self.checkFileOutput("defaults.pyi", stdout_lines=stdout_lines)

    def test_attribute_values(self) -> None:
        stdout_lines = (
            '7:15: Y015 Attribute must not have a default value other than "..."',
            '8:10: Y015 Attribute must not have a default value other than "..."',
            '9:10: Y015 Attribute must not have a default value other than "..."',
            '10:10: Y015 Attribute must not have a default value other than "..."',
            '19:19: Y015 Attribute must not have a default value other than "..."',
            '20:14: Y015 Attribute must not have a default value other than "..."',
            '21:14: Y015 Attribute must not have a default value other than "..."',
            '22:14: Y015 Attribute must not have a default value other than "..."',
        )
        self.checkFileOutput("attribute_annotations.pyi", stdout_lines=stdout_lines)

    def test_attribute_values_strict(self) -> None:
        stdout_lines = ("3:15: Y092 Top-level attribute must not have a default value",)
        self.checkFileOutput(
            "attribute_annotations.pyi",
            stdout_lines=stdout_lines,
            extra_options=("--select=Y092",),
        )


if __name__ == "__main__":
    unittest.main()
