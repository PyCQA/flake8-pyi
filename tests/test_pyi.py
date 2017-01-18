import os
from pathlib import Path
import subprocess
import sys
from typing import Tuple
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

    def test_vanilla_flake8_not_clean_forward_refs(self) -> None:
        returncode, stdout, stderr = self.checkFile('forward_refs.pyi', pyi_aware=False)
        self.assertEqual(returncode, 1, stdout)
        actual = '\n'.join(
            line.split('/')[-1] for line in stdout.split('\n') if line
        )
        expected = "\n".join((
            "forward_refs.pyi:4:22: F821 undefined name 'CStr'",
            "forward_refs.pyi:5:14: F821 undefined name 'C'",
            "forward_refs.pyi:10:25: F821 undefined name 'C'",
            "forward_refs.pyi:14:9: F821 undefined name 'C'",
            # The following two only raised on the _annassign.pyi variant
            # "forward_refs.pyi:15:13: F821 undefined name 'C'",
            # "forward_refs.pyi:22:12: F821 undefined name 'C'",
            "forward_refs.pyi:27:35: F821 undefined name 'C'",
        ))
        self.assertMultiLineEqual(expected, actual)
        self.assertEqual(stderr, '')

    @unittest.skipIf(sys.version_info < (3, 6), "variable annotations used")
    def test_patched_flake8_clean_forward_refs(self) -> None:
        returncode, stdout, stderr = self.checkFile('forward_refs_annassign.pyi', pyi_aware=True)
        self.assertEqual(returncode, 0, stdout)
        self.assertEqual(stdout, '')
        self.assertEqual(stderr, '')

    def test_vanilla_flake8_not_clean_del(self) -> None:
        returncode, stdout, stderr = self.checkFile('del.pyi', pyi_aware=False)
        self.assertEqual(returncode, 1, stdout)
        actual = '\n'.join(
            line.split('/')[-1] for line in stdout.split('\n') if line
        )
        expected = "\n".join((
            "del.pyi:4:16: F821 undefined name 'EitherStr'",
        ))
        self.assertMultiLineEqual(expected, actual)
        self.assertEqual(stderr, '')

    def test_patched_flake8_clean_del(self) -> None:
        returncode, stdout, stderr = self.checkFile('del.pyi', pyi_aware=True)
        self.assertEqual(returncode, 0, stdout)
        self.assertEqual(stdout, '')
        self.assertEqual(stderr, '')


if __name__ == '__main__':
    unittest.main()
