import ast
import importlib.util
import os
import shutil
import subprocess
import tempfile
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


@unittest.skipUnless(shutil.which("git") is not None, "git required")
class GitIntegrationRegressionTests(unittest.TestCase):
    def _create_repo_with_tracked_file(self, initial_text: str):
        tmp_dir = Path(tempfile.mkdtemp(prefix="pythonbox-git-"))
        subprocess.run(["git", "init"], cwd=tmp_dir, check=True, capture_output=True)

        file_path = tmp_dir / "demo.py"
        file_path.write_text(initial_text, encoding="utf-8")
        subprocess.run(["git", "-C", str(tmp_dir), "add", "demo.py"], check=True, capture_output=True)

        self.addCleanup(shutil.rmtree, tmp_dir, True)
        return tmp_dir, file_path

    def test_git_status_formats_combined_codes_readably(self):
        module = load_pythonbox_module()

        _, file_path = self._create_repo_with_tracked_file("a\nb\nc\n")
        file_path.write_text("a\nX\nc\n", encoding="utf-8")

        git = module.GitIntegration()
        status = git.get_file_status(str(file_path))

        self.assertEqual("+ Added / ● Modified", status)

    def test_git_modified_lines_classify_replacements_as_modified(self):
        module = load_pythonbox_module()

        _, file_path = self._create_repo_with_tracked_file("a\nb\nc\n")
        file_path.write_text("a\nX\nc\n", encoding="utf-8")

        git = module.GitIntegration()
        added, modified, deleted = git.get_modified_lines(str(file_path))

        self.assertEqual([], sorted(added))
        self.assertEqual([2], sorted(modified))
        self.assertEqual([1], sorted(deleted))

    def test_git_modified_lines_classify_insertions_as_added(self):
        module = load_pythonbox_module()

        _, file_path = self._create_repo_with_tracked_file("a\nc\n")
        file_path.write_text("a\nb\nc\n", encoding="utf-8")

        git = module.GitIntegration()
        added, modified, deleted = git.get_modified_lines(str(file_path))

        self.assertEqual([2], sorted(added))
        self.assertEqual([], sorted(modified))
        self.assertEqual([], sorted(deleted))


class SettingsRegressionTests(unittest.TestCase):
    def _temp_settings(self, module, folder: str):
        settings_path = Path(folder) / "settings.ini"
        return module.QSettings(str(settings_path), module.QSettings.Format.IniFormat)

    def test_settings_dialog_reads_and_writes_runtime_minimap_key(self):
        module = load_pythonbox_module()
        app = module.QApplication.instance() or module.QApplication([])

        with tempfile.TemporaryDirectory() as temp_dir:
            settings = self._temp_settings(module, temp_dir)
            settings.setValue("show_minimap", True)

            dialog = module.SettingsDialog(settings=settings)
            try:
                emissions = []
                dialog.settings_applied.connect(lambda: emissions.append(True))
                self.assertTrue(dialog.minimap_check.isChecked())

                dialog.minimap_check.setChecked(False)
                dialog.apply_settings()

                self.assertFalse(settings.value("show_minimap", True, type=bool))
                self.assertEqual([True], emissions)
            finally:
                dialog.deleteLater()
                app.processEvents()

    def test_main_window_reacts_to_minimap_setting_changes(self):
        module = load_pythonbox_module()
        app = module.QApplication.instance() or module.QApplication([])

        with tempfile.TemporaryDirectory() as temp_dir:
            settings = self._temp_settings(module, temp_dir)
            settings.setValue("show_minimap", False)

            with mock.patch.object(module, "QSettings", lambda *args, **kwargs: settings):
                window = module.PythonArchitect()

            try:
                self.assertFalse(window.minimap_action.isChecked())
                self.assertTrue(window.minimap_container.isHidden())

                settings.setValue("show_minimap", True)
                window._apply_settings_to_editors()

                self.assertTrue(window.minimap_action.isChecked())
                self.assertFalse(window.minimap_container.isHidden())
            finally:
                window.close()
                window.deleteLater()
                app.processEvents()

    def test_save_file_as_cancel_keeps_original_path(self):
        module = load_pythonbox_module()
        app = module.QApplication.instance() or module.QApplication([])

        with tempfile.TemporaryDirectory() as temp_dir:
            original_path = Path(temp_dir) / "demo.py"
            original_path.write_text("print('hi')\n", encoding="utf-8")

            window = module.PythonArchitect()
            try:
                tab = window.tab_editor.current_tab()
                tab.file_path = str(original_path)

                with mock.patch.object(
                    module.QFileDialog, "getSaveFileName", return_value=("", "")
                ):
                    window.save_file_as()

                self.assertEqual(str(original_path), tab.file_path)
            finally:
                window.close()
                window.deleteLater()
                app.processEvents()


if __name__ == "__main__":
    unittest.main()
