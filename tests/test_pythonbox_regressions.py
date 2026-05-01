import ast
import importlib.util
import os
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "PythonBox_v8.py"


def load_pythonbox_module():
    spec = importlib.util.spec_from_file_location("pythonbox_v8", SOURCE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class PythonArchitectRegressionTests(unittest.TestCase):
    def _pythonarchitect_class(self):
        tree = ast.parse(SOURCE.read_text(encoding="utf-8"))
        for node in tree.body:
            if isinstance(node, ast.ClassDef) and node.name == "PythonArchitect":
                return node
        self.fail("PythonArchitect class not found")

    def test_pythonarchitect_has_no_shadowed_methods(self):
        methods = [
            node.name
            for node in self._pythonarchitect_class().body
            if isinstance(node, ast.FunctionDef)
        ]
        duplicates = sorted({name for name in methods if methods.count(name) > 1})

        self.assertEqual([], duplicates)

    def test_f5_run_script_uses_debug_output_panel(self):
        run_script = None
        for node in self._pythonarchitect_class().body:
            if isinstance(node, ast.FunctionDef) and node.name == "run_script":
                run_script = node
                break
        self.assertIsNotNone(run_script)

        call_targets = []
        for node in ast.walk(run_script):
            if (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Attribute)
                and isinstance(node.func.value, ast.Attribute)
                and isinstance(node.func.value.value, ast.Name)
                and node.func.value.value.id == "self"
            ):
                call_targets.append((node.func.value.attr, node.func.attr))

        self.assertIn(("debug_output", "run_normal"), call_targets)
        self.assertNotIn(("output_panel", "run_code"), call_targets)

    def test_qt6_removed_editor_apis_are_not_used(self):
        source = SOURCE.read_text(encoding="utf-8")

        self.assertNotIn(".fontMetrics().width(", source)
        self.assertNotIn(".setTabStopWidth(", source)

    def test_main_window_can_be_constructed_offscreen(self):
        os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
        module = load_pythonbox_module()
        app = module.QApplication.instance() or module.QApplication([])
        window = module.PythonArchitect()

        try:
            self.assertIsNotNone(window.tab_editor.current_editor())
        finally:
            window.close()
            window.deleteLater()
            app.processEvents()


class ExternalPythonCommandTests(unittest.TestCase):
    def test_windows_external_commands_use_current_interpreter(self):
        module = load_pythonbox_module()

        with (
            mock.patch.object(module.sys, "platform", "win32"),
            mock.patch.object(module.sys, "executable", r"C:\Current Python\python.exe"),
        ):
            cmd = module.build_external_python_command(Path("tool.py"))

        self.assertEqual(['cmd', '/c', 'start', '', 'cmd', '/k'], cmd[:6])
        self.assertEqual(r"C:\Current Python\python.exe", cmd[6])
        self.assertEqual("tool.py", cmd[7])

    def test_non_windows_external_commands_use_current_interpreter(self):
        module = load_pythonbox_module()

        with (
            mock.patch.object(module.sys, "platform", "linux"),
            mock.patch.object(module.sys, "executable", "/opt/current-python/bin/python"),
            mock.patch.object(module.shutil, "which", return_value=None),
        ):
            cmd = module.build_external_python_command(Path("tool.py"))

        self.assertEqual(["/opt/current-python/bin/python", "tool.py"], cmd)


if __name__ == "__main__":
    unittest.main()
