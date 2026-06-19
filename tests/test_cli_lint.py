import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "PythonBox_v8.py"


def run_lint(target: str, timeout: int = 30) -> subprocess.CompletedProcess:
    env = {**os.environ, "PYTHONIOENCODING": "utf-8"}
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--lint", target],
        capture_output=True, text=True, timeout=timeout, env=env,
    )


class TestCLILint(unittest.TestCase):

    def test_lint_clean_file(self):
        with tempfile.NamedTemporaryFile(suffix=".py", mode="w",
                                         encoding="utf-8", delete=False) as f:
            f.write("x = 1\n")
            f.flush()
            path = f.name
        try:
            result = run_lint(path)
            self.assertIn("Keine Findings", result.stdout)
            self.assertEqual(result.returncode, 0)
        finally:
            os.unlink(path)

    def test_lint_syntax_error(self):
        with tempfile.NamedTemporaryFile(suffix=".py", mode="w",
                                         encoding="utf-8", delete=False) as f:
            f.write("def foo(\n")
            f.flush()
            path = f.name
        try:
            result = run_lint(path)
            self.assertEqual(result.returncode, 1)
            self.assertTrue(len(result.stdout.strip()) > 0)
        finally:
            os.unlink(path)

    def test_lint_nonexistent_file(self):
        result = run_lint("nonexistent_file_xyz_12345.py")
        self.assertEqual(result.returncode, 2)
        self.assertIn("nicht gefunden", result.stderr)

    def test_lint_output_format(self):
        with tempfile.NamedTemporaryFile(suffix=".py", mode="w",
                                         encoding="utf-8", delete=False) as f:
            f.write("import os\nimport os\n")
            f.flush()
            path = f.name
        try:
            result = run_lint(path)
            if result.returncode == 1:
                lines = result.stdout.strip().split("\n")
                finding_lines = [l for l in lines if path in l]
                for line in finding_lines:
                    self.assertRegex(line, r".+:\d+:\d+: \S+ .+")
        finally:
            os.unlink(path)

    def test_no_gui_started(self):
        with tempfile.NamedTemporaryFile(suffix=".py", mode="w",
                                         encoding="utf-8", delete=False) as f:
            f.write("x = 1\n")
            f.flush()
            path = f.name
        try:
            result = run_lint(path)
            self.assertNotIn("QApplication", result.stderr)
            self.assertNotIn("Traceback", result.stderr)
        finally:
            os.unlink(path)


if __name__ == "__main__":
    unittest.main()
