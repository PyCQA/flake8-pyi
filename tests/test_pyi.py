import os
from pathlib import Path
import subprocess
import sys
from typing import Sequence, Tuple
import unittest


class PyiTestCase(unittest.TestCase):
    maxDiff = None  # type: int

    def checkFile(self, filename: str, pyi_aware: bool) -> Tuple[int, str, str]:
        file_path = Path(__file__).absolute().parent / filename
        cmdline = ['flake8', '-j0', str(file_path)]
        if not pyi_aware:
            cmdline.insert(-1, '--no-pyi-aware-file-checker')
        env = os.environ.copy()
        env['PYTHONWARNINGS'] = 'ignore'
        proc = subprocess.run(
            cmdline,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=60,
            env=env,
        )
        stdout_text = proc.stdout.decode('utf8')
        stderr_text = proc.stderr.decode('utf8')
        return proc.returncode, stdout_text, stderr_text

    def checkFileOutput(self, filename: str, *, pyi_aware: bool = True,
                        stdout_lines: Sequence[str] = (), stderr_lines: Sequence[str] = ()) -> None:
        returncode, stdout, stderr = self.checkFile(filename, pyi_aware=pyi_aware)
        expected_returncode = 1 if stdout else 0
        self.assertEqual(returncode, expected_returncode, stdout)

        for (actual, expected_lines) in [(stdout, stdout_lines), (stderr, stderr_lines)]:
            actual = '\n'.join(
                line.split('/')[-1] for line in actual.split('\n') if line
            )
            expected = '\n'.join(
                '{filename}:{line}'.format(filename=filename, line=line)
                for line in expected_lines
            )
            self.assertMultiLineEqual(expected, actual)

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
        self.checkFileOutput('forward_refs.pyi', pyi_aware=False, stdout_lines=stdout_lines)

    @unittest.skipIf(sys.version_info < (3, 6), "variable annotations used")
    def test_patched_flake8_clean_forward_refs(self) -> None:
        self.checkFileOutput('forward_refs_annassign.pyi', pyi_aware=True, stdout_lines=())

    def test_vanilla_flake8_not_clean_del(self) -> None:
        stdout_lines = ("4:16: F821 undefined name 'EitherStr'",)
        self.checkFileOutput('del.pyi', pyi_aware=False, stdout_lines=stdout_lines)

    def test_patched_flake8_clean_del(self) -> None:
        self.checkFileOutput('del.pyi', pyi_aware=True, stdout_lines=())

    def test_typevar(self) -> None:
        stdout_lines = (
            '3:1: Y001 Name of private TypeVar must start with _',
        )
        self.checkFileOutput('typevar.pyi', stdout_lines=stdout_lines)

    def test_sys_platform(self) -> None:
        stdout_lines = (
            '3:4: Y007 Unrecognized sys.platform check',
            '3:4: Y007 Unrecognized sys.platform check',
            '6:4: Y007 Unrecognized sys.platform check',
            '9:4: Y008 Unrecognized platform "linus"',
        )
        self.checkFileOutput('sysplatform.pyi', stdout_lines=stdout_lines)

    def test_sys_versioninfo(self) -> None:
        stdout_lines = (
            '6:4: Y003 Unrecognized sys.version_info check',
            '9:4: Y003 Unrecognized sys.version_info check',
            '12:4: Y003 Unrecognized sys.version_info check',
            '15:4: Y003 Unrecognized sys.version_info check',
            '18:4: Y003 Unrecognized sys.version_info check',
            '24:4: Y005 Version comparison must be against a length-1 tuple',
            '30:4: Y005 Version comparison must be against a length-2 tuple',
            '33:4: Y003 Unrecognized sys.version_info check',
            '36:4: Y003 Unrecognized sys.version_info check',
            '39:4: Y003 Unrecognized sys.version_info check',
            '42:4: Y004 Version comparison must use only major and minor version',
            '45:4: Y006 Use only < and >= for version comparisons',
            '48:4: Y006 Use only < and >= for version comparisons',
            '51:4: Y006 Use only < and >= for version comparisons',
            '60:4: Y002 If test must be a simple comparison against sys.platform or sys.version_info',
        )
        self.checkFileOutput('sysversioninfo.pyi', stdout_lines=stdout_lines)

    def test_comparisons(self) -> None:
        stdout_lines = (
            '3:4: Y002 If test must be a simple comparison against sys.platform or sys.version_info',
            '6:4: Y002 If test must be a simple comparison against sys.platform or sys.version_info',
            '9:4: Y002 If test must be a simple comparison against sys.platform or sys.version_info',
            '12:4: Y002 If test must be a simple comparison against sys.platform or sys.version_info',
        )
        self.checkFileOutput('comparisons.pyi', stdout_lines=stdout_lines)


if __name__ == '__main__':
    unittest.main()
