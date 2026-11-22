# Version: 1.6.1 | Release ChatID: E72C9B14
"""Regression tests for GUI Python/Tk selection."""
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class GuiLauncherTests(unittest.TestCase):
    def test_launcher_does_not_blindly_exec_python3(self):
        launcher = (ROOT / 'scripts' / 'gui.sh').read_text()
        self.assertIn('import tkinter', launcher)
        self.assertIn('python3.15', launcher)
        self.assertIn('python-tk@3.15', launcher)

    def test_bad_python_reports_help_without_traceback(self):
        with tempfile.TemporaryDirectory() as temp:
            fake = Path(temp) / 'python3'
            fake.write_text('#!/bin/sh\necho "ModuleNotFoundError: _tkinter" >&2\nexit 1\n')
            fake.chmod(0o755)
            env = dict(os.environ)
            env['PYTHON'] = str(fake)
            env['PATH'] = temp + ':/usr/bin:/bin'
            completed = subprocess.run(['/bin/sh', str(ROOT / 'scripts' / 'gui.sh')], env=env, capture_output=True, text=True)
            self.assertNotEqual(completed.returncode, 0)
            self.assertIn('Tkinter', completed.stderr)
            self.assertNotIn('Traceback', completed.stderr)


if __name__ == '__main__':
    unittest.main()
