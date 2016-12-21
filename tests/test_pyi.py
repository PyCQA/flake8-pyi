from pathlib import Path
import subprocess
import unittest


class PyiTestCase(unittest.TestCase):
    maxDiff = None

    def test_vanilla_flake8_not_clean(self):
        filename = Path(__file__).absolute().parent / 'forward_refs.pyi'
        proc = subprocess.run(
            ['flake8', '--no-pyi-aware-file-checker', str(filename)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=60,
        )
        stdout_text = proc.stdout.decode('utf8')
        self.assertEqual(proc.returncode, 1, stdout_text)
        actual = '\n'.join(
            line.split('/')[-1] for line in stdout_text.split('\n')
        )
        expected = (
            "forward_refs.pyi:1:25: F821 undefined name 'C'\n" +
            "forward_refs.pyi:9:35: F821 undefined name 'C'\n"
        )
        self.assertMultiLineEqual(expected, actual)

    def test_patched_flake8_clean(self):
        filename = Path(__file__).absolute().parent / 'forward_refs.pyi'
        proc = subprocess.run(
            ['flake8', str(filename)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=60,
        )
        self.assertEqual(proc.returncode, 0, proc.stdout.decode('utf8'))
        self.assertEqual(proc.stdout, b'', proc.stdout.decode('utf8'))
        

if __name__ == '__main__':
    unittest.main()
