import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "PythonBox_v8.py"
sys.path.insert(0, str(ROOT))
from PythonBox_v8 import parse_cli_args, LinterRunner


def run_lint(target: str, timeout: int = 30) -> subprocess.CompletedProcess:
    env = {**os.environ, "PYTHONIOENCODING": "utf-8"}
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--lint", target],
        capture_output=True, text=True, timeout=timeout, env=env,
    )


def run_headless(arguments, timeout: int = 30) -> subprocess.CompletedProcess:
    env = {**os.environ, "PYTHONIOENCODING": "utf-8"}
    return subprocess.run(
        [sys.executable, str(SCRIPT), *arguments],
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


class TestParseCLIArgs(unittest.TestCase):

    def test_open_flag(self):
        args = parse_cli_args(["--open", "test.py"])
        self.assertEqual(args.open, "test.py")
        self.assertIsNone(args.lint)

    def test_lint_flag(self):
        args = parse_cli_args(["--lint", "test.py"])
        self.assertEqual(args.lint, "test.py")
        self.assertIsNone(args.open)

    def test_positional_file(self):
        args = parse_cli_args(["test.py"])
        self.assertEqual(args.open, "test.py")
        self.assertIsNone(args.lint)

    def test_no_args(self):
        args = parse_cli_args([])
        self.assertIsNone(args.open)
        self.assertIsNone(args.lint)
        self.assertIsNone(args.run)
        self.assertIsNone(args.theme)

    def test_unknown_args_preserved(self):
        args = parse_cli_args(["--open", "test.py", "-style", "fusion"])
        self.assertEqual(args.open, "test.py")
        self.assertIn("-style", args._remaining)

    def test_run_flag(self):
        args = parse_cli_args(["--run", "tool.py"])
        self.assertEqual(args.run, "tool.py")
        self.assertIsNone(args.open)
        self.assertIsNone(args.lint)

    def test_theme_flag_is_normalized(self):
        args = parse_cli_args(["--theme", "light"])
        self.assertEqual(args.theme, "Light")

    def test_theme_flag_preserves_qt_args(self):
        args = parse_cli_args(["--theme", "dracula", "-style", "fusion"])
        self.assertEqual(args.theme, "Dracula")
        self.assertIn("-style", args._remaining)

    def test_lint_with_real_flake8(self):
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
                self.assertTrue(len(finding_lines) > 0,
                                "flake8 should find duplicate import")
                for line in finding_lines:
                    self.assertRegex(line, r".+:\d+:\d+: \S+ .+")
        finally:
            os.unlink(path)


class TestLinterDetection(unittest.TestCase):

    @patch("shutil.which", return_value=None)
    @patch("subprocess.run")
    def test_missing_flake8_not_detected(self, mock_run, mock_which):
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_run.return_value = mock_result
        runner = LinterRunner.__new__(LinterRunner)
        runner.has_flake8 = False
        runner.has_pylint = False
        runner._check_available_linters()
        self.assertFalse(runner.has_flake8)
        self.assertFalse(getattr(runner, '_flake8_via_module', False))

    @patch("shutil.which", return_value=None)
    @patch("subprocess.run")
    def test_missing_pylint_not_detected(self, mock_run, mock_which):
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_run.return_value = mock_result
        runner = LinterRunner.__new__(LinterRunner)
        runner.has_flake8 = False
        runner.has_pylint = False
        runner._check_available_linters()
        self.assertFalse(runner.has_pylint)
        self.assertFalse(getattr(runner, '_pylint_via_module', False))

    @patch("shutil.which", return_value=None)
    @patch("subprocess.run")
    def test_module_flake8_detected_on_success(self, mock_run, mock_which):
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_run.return_value = mock_result
        runner = LinterRunner.__new__(LinterRunner)
        runner.has_flake8 = False
        runner.has_pylint = False
        runner._check_available_linters()
        self.assertTrue(runner.has_flake8)
        self.assertTrue(runner._flake8_via_module)


class TestHeadlessRun(unittest.TestCase):

    def test_run_executes_script_and_returns_exit_code(self):
        with tempfile.NamedTemporaryFile(suffix=".py", mode="w",
                                         encoding="utf-8", delete=False) as f:
            f.write("import sys\nprint('run-ok')\nsys.exit(3)\n")
            f.flush()
            path = f.name
        try:
            result = run_headless(["--run", path])
            self.assertEqual(result.returncode, 3)
            self.assertIn("run-ok", result.stdout)
            self.assertNotIn("QApplication", result.stderr)
        finally:
            os.unlink(path)

    def test_run_forwards_extra_arguments(self):
        with tempfile.NamedTemporaryFile(suffix=".py", mode="w",
                                         encoding="utf-8", delete=False) as f:
            f.write("import sys\nprint('|'.join(sys.argv[1:]))\n")
            f.flush()
            path = f.name
        try:
            result = run_headless(["--run", path, "eins", "zwei"])
            self.assertEqual(result.returncode, 0)
            self.assertIn("eins|zwei", result.stdout)
        finally:
            os.unlink(path)


if __name__ == "__main__":
    unittest.main()
