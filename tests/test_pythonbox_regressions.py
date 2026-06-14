import ast
import importlib.util
import json
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

    def test_parse_startup_file_argument_accepts_open_flag(self):
        module = load_pythonbox_module()

        startup = module.parse_startup_file_argument(["--open", "demo.py"])

        self.assertEqual("demo.py", startup)

    def test_parse_startup_file_argument_accepts_bare_file_path(self):
        module = load_pythonbox_module()

        startup = module.parse_startup_file_argument(["script.py"])

        self.assertEqual("script.py", startup)


@unittest.skipUnless(shutil.which("git") is not None, "git required")
class GitIntegrationRegressionTests(unittest.TestCase):
    def _write_text(self, file_path: Path, text: str, newline: str = "\n"):
        file_path.write_bytes(text.replace("\n", newline).encode("utf-8"))

    def _create_repo_with_tracked_file(self, initial_text: str, *, newline: str = "\n"):
        tmp_dir = Path(tempfile.mkdtemp(prefix="pythonbox-git-"))
        subprocess.run(["git", "init"], cwd=tmp_dir, check=True, capture_output=True)

        file_path = tmp_dir / "demo.py"
        self._write_text(file_path, initial_text, newline=newline)
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

    def test_git_modified_lines_classify_crlf_replacements_as_modified(self):
        module = load_pythonbox_module()

        _, file_path = self._create_repo_with_tracked_file("a\nb\nc\n", newline="\r\n")
        self._write_text(file_path, "a\nX\nc\n", newline="\r\n")

        git = module.GitIntegration()
        added, modified, deleted = git.get_modified_lines(str(file_path))

        self.assertEqual([], sorted(added))
        self.assertEqual([2], sorted(modified))
        self.assertEqual([1], sorted(deleted))


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

    def test_settings_json_roundtrip_preserves_portable_preferences(self):
        module = load_pythonbox_module()

        with tempfile.TemporaryDirectory() as temp_dir:
            source_settings = self._temp_settings(module, temp_dir)
            source_settings.setValue("font_size", 14)
            source_settings.setValue("tab_size", 2)
            source_settings.setValue("word_wrap", True)
            source_settings.setValue("theme", "Dracula")
            source_settings.setValue("show_minimap", True)
            source_settings.sync()

            export_path = Path(temp_dir) / "pythonbox-settings-v1.json"
            module.write_settings_export(source_settings, export_path)

            payload = json.loads(export_path.read_text(encoding="utf-8"))
            self.assertEqual(module.SETTINGS_EXPORT_SCHEMA, payload["schema"])
            self.assertEqual("Dracula", payload["settings"]["theme"])

            imported_settings = module.QSettings(
                str(Path(temp_dir) / "imported.ini"),
                module.QSettings.Format.IniFormat,
            )
            imported = module.import_settings_from_json(imported_settings, export_path)

            self.assertEqual(14, imported["font_size"])
            self.assertEqual(2, imported_settings.value("tab_size", 4, type=int))
            self.assertTrue(imported_settings.value("word_wrap", False, type=bool))
            self.assertEqual("Dracula", imported_settings.value("theme", "", type=str))
            self.assertTrue(imported_settings.value("show_minimap", False, type=bool))

    def test_main_window_opens_startup_file_in_bootstrap_tab(self):
        module = load_pythonbox_module()
        app = module.QApplication.instance() or module.QApplication([])

        with tempfile.TemporaryDirectory() as temp_dir:
            startup_path = Path(temp_dir) / "demo.py"
            startup_path.write_text("print('hello')\n", encoding="utf-8")

            window = module.PythonArchitect(startup_file=str(startup_path))
            try:
                current_tab = window.tab_editor.current_tab()
                self.assertEqual(1, window.tab_editor.tab_widget.count())
                self.assertIsNotNone(current_tab)
                self.assertEqual(str(startup_path), current_tab.file_path)
                self.assertEqual("print('hello')\n", current_tab.editor.toPlainText())
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


class LibraryExportRegressionTests(unittest.TestCase):
    def test_snippet_library_json_roundtrip_preserves_content_and_locks(self):
        module = load_pythonbox_module()

        with tempfile.TemporaryDirectory() as temp_dir:
            source_root = Path(temp_dir) / "source-library"
            manager = module.LibraryManager(root=source_root)
            manager.save_snippet("Tests", "Alpha", "print('eins')\n")
            manager.toggle_lock("Tests", "Alpha")

            export_path = Path(temp_dir) / "pythonbox-snippets-v1.json"
            manager.export_to_json(export_path)

            payload = json.loads(export_path.read_text(encoding="utf-8"))
            self.assertEqual(module.SNIPPET_EXPORT_SCHEMA, payload["schema"])
            exported_topic = next(topic for topic in payload["topics"] if topic["name"] == "Tests")
            self.assertEqual("Alpha", exported_topic["snippets"][0]["name"])
            self.assertTrue(exported_topic["snippets"][0]["locked"])

            imported_root = Path(temp_dir) / "imported-library"
            imported_manager = module.LibraryManager(root=imported_root)
            result = imported_manager.import_from_json(export_path)

            self.assertEqual(2, result["imported"])
            self.assertIn("Tests", result["topics"])
            self.assertEqual("print('eins')\n", imported_manager.get_content("Tests", "Alpha"))
            self.assertTrue(imported_manager.is_locked("Tests", "Alpha"))


class MinimapToggleRegressionTests(unittest.TestCase):
    """Regression tests for toggle_minimap cleanup."""

    def test_toggle_minimap_off_cleans_up_minimap_object(self):
        """toggle_minimap(False) must delete the Minimap widget (Bug #8).

        Before the fix, turning the minimap OFF via the menu action hid the container
        but left the Minimap object alive and still connected to editor signals
        (textChanged, scrollbar.valueChanged), causing unnecessary background updates.
        """
        source = SOURCE.read_text(encoding="utf-8")
        tree = ast.parse(source)

        toggle_node = None
        for cls_node in tree.body:
            if isinstance(cls_node, ast.ClassDef) and cls_node.name == "PythonArchitect":
                for node in cls_node.body:
                    if isinstance(node, ast.FunctionDef) and node.name == "toggle_minimap":
                        toggle_node = node
                        break
                break

        self.assertIsNotNone(toggle_node, "toggle_minimap not found in PythonArchitect")
        segment = ast.get_source_segment(source, toggle_node)
        self.assertIn(
            "deleteLater",
            segment,
            "toggle_minimap must call deleteLater on the Minimap widget when turning off",
        )
        self.assertIn(
            "self.minimap = None",
            segment,
            "toggle_minimap must set self.minimap = None after deleting the widget",
        )


class ImportOptimizerRegressionTests(unittest.TestCase):
    """Regression tests for ImportOptimizer.organize_imports."""

    @staticmethod
    def _get_optimizer():
        import re as _re
        tree = ast.parse(SOURCE.read_text(encoding="utf-8"))
        ns = {"ast": ast, "re": _re}
        for cls_node in tree.body:
            if isinstance(cls_node, ast.ClassDef) and cls_node.name == "ImportOptimizer":
                seg = ast.get_source_segment(SOURCE.read_text(encoding="utf-8"), cls_node)
                exec(compile(seg, "ImportOptimizer", "exec"), ns)
                break
        return ns["ImportOptimizer"]

    def test_organize_imports_preserves_shebang_as_first_line(self):
        """organize_imports must keep the shebang line at the very top (Bug #7).

        Before the fix, sorted imports were placed before the shebang line, producing
        invalid Python scripts (the interpreter directive must be the first line).
        """
        IO = self._get_optimizer()
        code = "#!/usr/bin/env python3\n# -*- coding: utf-8 -*-\nimport sys\nimport os\n\ndef main():\n    pass\n"
        result, msg = IO.organize_imports(code)
        self.assertIsNotNone(result, f"organize_imports returned None: {msg}")
        self.assertTrue(
            result.startswith("#!/usr/bin/env python3"),
            "Shebang must remain the first line after import reorganisation",
        )

    def test_organize_imports_preserves_encoding_declaration(self):
        """organize_imports must keep the encoding declaration in the first two lines."""
        IO = self._get_optimizer()
        code = "#!/usr/bin/env python3\n# -*- coding: utf-8 -*-\nimport os\n\nx = 1\n"
        result, msg = IO.organize_imports(code)
        self.assertIsNotNone(result)
        lines = result.splitlines()
        self.assertTrue(
            any("coding" in l for l in lines[:3]),
            "Encoding declaration must appear in the first 3 lines after reorganisation",
        )

    def test_organize_imports_deduplicates(self):
        """organize_imports removes duplicate imports."""
        IO = self._get_optimizer()
        code = "import os\nimport os\nfrom pathlib import Path\nfrom pathlib import Path\n\nx = 1\n"
        result, msg = IO.organize_imports(code)
        self.assertIsNotNone(result)
        self.assertEqual(1, result.count("import os"))
        self.assertEqual(1, result.count("from pathlib import Path"))


class MinimapInitRegressionTests(unittest.TestCase):
    """Regression tests for duplicate minimap initialisation in setup_ui."""

    def test_minimap_initialized_exactly_once_in_setup_ui(self):
        """setup_ui must initialize self.minimap = None exactly once (Bug #6).

        Before the fix, self.minimap = None appeared twice inside setup_ui, with
        the second redundant assignment appearing AFTER the first and after widget
        construction was complete. The duplicate is confusing and would silently
        drop any minimap widget created in between.
        """
        source = SOURCE.read_text(encoding="utf-8")
        tree = ast.parse(source)

        setup_ui_node = None
        for cls_node in tree.body:
            if isinstance(cls_node, ast.ClassDef) and cls_node.name == "PythonArchitect":
                for node in cls_node.body:
                    if isinstance(node, ast.FunctionDef) and node.name == "setup_ui":
                        setup_ui_node = node
                        break
                break

        self.assertIsNotNone(setup_ui_node, "setup_ui not found in PythonArchitect")
        segment = ast.get_source_segment(source, setup_ui_node)
        count = segment.count("self.minimap = None")
        self.assertEqual(
            1,
            count,
            f"self.minimap = None must appear exactly once in setup_ui, found {count}",
        )


class OutputPanelRegressionTests(unittest.TestCase):
    """Regression tests for OutputPanel.stop_process."""

    def test_stop_process_disables_stop_button_and_waits(self):
        """OutputPanel.stop_process must call waitForFinished and disable btn_stop (Bug #5).

        Before the fix, stop_process killed the process but never waited for it to
        terminate nor disabled btn_stop, leaving the UI in an inconsistent state and
        creating a race window where the next run_script call could see a stale process.
        """
        source = SOURCE.read_text(encoding="utf-8")
        tree = ast.parse(source)

        stop_node = None
        for cls_node in tree.body:
            if isinstance(cls_node, ast.ClassDef) and cls_node.name == "OutputPanel":
                for node in cls_node.body:
                    if isinstance(node, ast.FunctionDef) and node.name == "stop_process":
                        stop_node = node
                        break
                break

        self.assertIsNotNone(stop_node, "stop_process not found in OutputPanel")
        segment = ast.get_source_segment(source, stop_node)
        self.assertIn(
            "waitForFinished",
            segment,
            "OutputPanel.stop_process must call waitForFinished to avoid race conditions",
        )
        self.assertIn(
            "btn_stop",
            segment,
            "OutputPanel.stop_process must disable btn_stop after killing the process",
        )


class TabIndexRegressionTests(unittest.TestCase):
    """Regression tests for MultiTabEditor tab-index stability after close_tab."""

    def test_modification_signal_uses_editor_identity_not_stale_index(self):
        """MultiTabEditor must not use a captured lambda index for modification signals (Bug #4).

        Before the fix, modificationChanged was connected via
          lambda modified, idx=index: self._on_modification_changed(idx, modified)
        After close_tab() reindexes self.tabs, the captured idx no longer matches
        the new position, so the modified-indicator (●) silently stopped updating.

        After the fix the connection uses _on_modification_changed_by_editor which
        looks up the tab by editor identity instead.
        """
        source = SOURCE.read_text(encoding="utf-8")
        tree = ast.parse(source)

        # Locate new_tab method inside MultiTabEditor
        new_tab_node = None
        for cls_node in tree.body:
            if isinstance(cls_node, ast.ClassDef) and cls_node.name == "MultiTabEditor":
                for node in cls_node.body:
                    if isinstance(node, ast.FunctionDef) and node.name == "new_tab":
                        new_tab_node = node
                        break
                break

        self.assertIsNotNone(new_tab_node, "new_tab not found in MultiTabEditor")
        segment = ast.get_source_segment(source, new_tab_node)

        # The fix removes the old idx=index lambda and routes through the editor-identity method.
        self.assertIn(
            "_on_modification_changed_by_editor",
            segment,
            "new_tab must connect modificationChanged to _on_modification_changed_by_editor",
        )

        # Also verify the new helper method exists on MultiTabEditor
        multi_tab_methods = []
        for cls_node in tree.body:
            if isinstance(cls_node, ast.ClassDef) and cls_node.name == "MultiTabEditor":
                multi_tab_methods = [
                    n.name for n in cls_node.body if isinstance(n, ast.FunctionDef)
                ]
                break

        self.assertIn(
            "_on_modification_changed_by_editor",
            multi_tab_methods,
            "_on_modification_changed_by_editor must be defined on MultiTabEditor",
        )


class SearchReplaceRegressionTests(unittest.TestCase):
    def test_replace_current_respects_case_sensitivity_flag(self):
        """replace_current must honour the case_check state (Bug #2).

        Before the fix, replace_current always compared case-insensitively
        (lower() == lower()) even when the user had case-sensitive search active.
        """
        tree = ast.parse(SOURCE.read_text(encoding="utf-8"))

        replace_current_node = None
        for cls_node in tree.body:
            if isinstance(cls_node, ast.ClassDef) and cls_node.name == "SearchReplaceBar":
                for node in cls_node.body:
                    if isinstance(node, ast.FunctionDef) and node.name == "replace_current":
                        replace_current_node = node
                        break

        self.assertIsNotNone(replace_current_node, "replace_current not found in SearchReplaceBar")

        source_segment = ast.get_source_segment(
            SOURCE.read_text(encoding="utf-8"), replace_current_node
        )
        # After the fix the method must consult case_check.isChecked() to branch.
        self.assertIn(
            "case_check",
            source_segment,
            "replace_current must check case_check.isChecked() to honour case sensitivity",
        )


    """Regression tests for SearchReplaceBar.replace_all."""

    def _get_mask_func(self, module_source: str):
        """Extract and compile _build_string_comment_mask as a standalone function."""
        import textwrap
        tree = ast.parse(module_source)
        func_src = None
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == "_build_string_comment_mask":
                func_src = ast.get_source_segment(module_source, node)
                break
        self.assertIsNotNone(func_src)
        # Dedent so that it can be compiled as a standalone function regardless of class indentation.
        func_src = textwrap.dedent(func_src)
        # Replace the signature to drop the type annotations (which reference List etc.)
        lines = func_src.splitlines()
        lines[0] = "def _build_string_comment_mask(text):"
        standalone = "\n".join(lines) + "\n"
        ns = {}
        exec(compile(standalone, "<mask>", "exec"), ns)
        return ns["_build_string_comment_mask"]

    def test_string_mask_does_not_cross_newlines(self):
        """_build_string_comment_mask must not mark code after a newline as inside a string (Bug #3).

        Before the fix, a single-quoted string without a closing quote on the same line
        would cause the scanner to cross the newline and mark subsequent code as masked.
        That suppressed auto-close brackets for code that was not inside any string.
        """
        source = SOURCE.read_text(encoding="utf-8")
        mask_fn = self._get_mask_func(source)

        text = "'unterminated\nreal_code = (1 + 2)"
        mask = mask_fn(text)
        # 'real_code' starts after the newline; find it by searching past the newline position
        newline_pos = text.index("\n")
        real_code_start = text.index("real_code")  # guaranteed to be after the newline
        self.assertGreater(real_code_start, newline_pos)
        self.assertFalse(
            any(mask[real_code_start:]),
            "Code after a newline must not be masked as inside a string",
        )

    def test_string_mask_marks_string_content(self):
        """_build_string_comment_mask correctly marks content inside a normal string."""
        source = SOURCE.read_text(encoding="utf-8")
        mask_fn = self._get_mask_func(source)

        text = "x = 'hello' + y"
        mask = mask_fn(text)
        hello_start = text.index("h")
        hello_end = text.index("'", hello_start + 1)
        self.assertTrue(
            all(mask[hello_start:hello_end]),
            "Content inside a quoted string must be marked as masked",
        )

    def test_replace_all_preserves_undo_history(self):
        """replace_all must use cursor.select+insertText so undo works (Bug #1).

        Before the fix, setPlainText() was called inside beginEditBlock/endEditBlock
        which had no effect — setPlainText() bypasses the undo stack entirely.
        After the fix the undo stack is intact and Ctrl+Z restores the original text.
        """
        tree = ast.parse(SOURCE.read_text(encoding="utf-8"))

        replace_all_node = None
        for cls_node in tree.body:
            if isinstance(cls_node, ast.ClassDef) and cls_node.name == "SearchReplaceBar":
                for node in cls_node.body:
                    if isinstance(node, ast.FunctionDef) and node.name == "replace_all":
                        replace_all_node = node
                        break

        self.assertIsNotNone(replace_all_node, "replace_all method not found in SearchReplaceBar")

        # The fix: must NOT call setPlainText inside the replace_all body.
        # Instead it must call insertText (cursor-based replacement).
        source_segment = ast.get_source_segment(
            SOURCE.read_text(encoding="utf-8"), replace_all_node
        )
        self.assertNotIn(
            "setPlainText",
            source_segment,
            "replace_all must not call setPlainText (destroys undo history); use cursor.insertText instead",
        )
        self.assertIn(
            "insertText",
            source_segment,
            "replace_all must use cursor.insertText to keep undo history intact",
        )


class ImportOptimizerTopLevelOnlyRegressionTests(unittest.TestCase):
    """Bug #20: organize_imports used ast.walk, moving function/class-level and
    conditional imports to module level, breaking lazy imports and TYPE_CHECKING blocks."""

    def _get_optimizer_source(self):
        source = SOURCE.read_text(encoding="utf-8")
        tree = ast.parse(source)
        for node in tree.body:
            if isinstance(node, ast.ClassDef) and node.name == "ImportOptimizer":
                return ast.get_source_segment(source, node)
        self.fail("ImportOptimizer not found")

    def test_organize_imports_uses_tree_body_not_ast_walk(self):
        """organize_imports must iterate tree.body, not ast.walk(tree), to
        avoid hoisting function/class-level imports to module level."""
        src = self._get_optimizer_source()
        self.assertNotIn(
            "ast.walk",
            src,
            "organize_imports must use tree.body (top-level only), not ast.walk(tree) "
            "which would incorrectly hoist conditional/lazy imports",
        )
        self.assertIn(
            "tree.body",
            src,
            "organize_imports must iterate tree.body to process only top-level imports",
        )


class OnEditorChangedSignalRegressionTests(unittest.TestCase):
    """Bug #19: on_editor_changed connected cursorPositionInfo signal without
    first disconnecting, causing duplicate calls when switching back to a tab."""

    def _get_method_source(self):
        source = SOURCE.read_text(encoding="utf-8")
        tree = ast.parse(source)
        for node in tree.body:
            if isinstance(node, ast.ClassDef) and node.name == "PythonArchitect":
                for item in node.body:
                    if isinstance(item, ast.FunctionDef) and item.name == "on_editor_changed":
                        return ast.get_source_segment(source, item)
        self.fail("on_editor_changed not found in PythonArchitect")

    def test_on_editor_changed_disconnects_before_connect(self):
        """on_editor_changed must disconnect cursorPositionInfo before reconnecting
        to prevent duplicate signal handlers."""
        src = self._get_method_source()
        self.assertIn(
            "disconnect",
            src,
            "on_editor_changed must disconnect cursorPositionInfo before connecting "
            "to avoid duplicate handlers on repeated tab switches",
        )


class MinimapUpdateLayoutRegressionTests(unittest.TestCase):
    """Bug #18: _update_minimap added new Minimap widget to layout without
    first removing the old one, causing layout accumulation on tab switches."""

    def _get_update_minimap_source(self):
        source = SOURCE.read_text(encoding="utf-8")
        tree = ast.parse(source)
        for node in tree.body:
            if isinstance(node, ast.ClassDef) and node.name == "PythonArchitect":
                for item in node.body:
                    if isinstance(item, ast.FunctionDef) and item.name == "_update_minimap":
                        return ast.get_source_segment(source, item)
        self.fail("_update_minimap not found in PythonArchitect")

    def test_update_minimap_removes_old_widget_from_layout(self):
        """_update_minimap must call layout.removeWidget on the old minimap
        before destroying and replacing it."""
        src = self._get_update_minimap_source()
        self.assertIn(
            "removeWidget",
            src,
            "_update_minimap must call layout.removeWidget(self.minimap) before deleteLater()",
        )


class LineNumberAreaPaintRegressionTests(unittest.TestCase):
    """Bug #17: lineNumberAreaPaintEvent called blockBoundingRect on invalid block
    after advancing past the last block, same pattern as Bug #16 in FoldingArea."""

    def _get_paint_event_source(self):
        source = SOURCE.read_text(encoding="utf-8")
        tree = ast.parse(source)
        for node in tree.body:
            if isinstance(node, ast.ClassDef) and node.name == "CodeEditor":
                for item in node.body:
                    if isinstance(item, ast.FunctionDef) and item.name == "lineNumberAreaPaintEvent":
                        return ast.get_source_segment(source, item)
        self.fail("CodeEditor.lineNumberAreaPaintEvent not found")

    def test_line_number_paint_guards_bounding_rect(self):
        """lineNumberAreaPaintEvent must check block.isValid() before blockBoundingRect
        after advancing to block.next()."""
        src = self._get_paint_event_source()
        self.assertIn(
            "block.isValid()",
            src,
            "lineNumberAreaPaintEvent must guard blockBoundingRect with block.isValid()",
        )


class FoldingAreaPaintRegressionTests(unittest.TestCase):
    """Bug #16: FoldingArea.paintEvent called blockBoundingRect on invalid block
    after advancing past the last block, potentially causing a crash at end-of-document."""

    def _get_paint_event_source(self):
        source = SOURCE.read_text(encoding="utf-8")
        tree = ast.parse(source)
        for node in tree.body:
            if isinstance(node, ast.ClassDef) and node.name == "FoldingArea":
                for item in node.body:
                    if isinstance(item, ast.FunctionDef) and item.name == "paintEvent":
                        return ast.get_source_segment(source, item)
        self.fail("FoldingArea.paintEvent not found")

    def test_paint_event_checks_block_valid_before_bounding_rect(self):
        """paintEvent must check block.isValid() before calling blockBoundingRect
        after advancing to block.next()."""
        src = self._get_paint_event_source()
        self.assertIn(
            "block.isValid()",
            src,
            "FoldingArea.paintEvent must guard blockBoundingRect call with block.isValid()",
        )


class GitDiffLineTrackingRegressionTests(unittest.TestCase):
    """Bug #15: get_modified_lines incremented current_line for diff header lines
    (diff --git, index ...) causing all subsequent line numbers to be shifted."""

    def _get_git_class_source(self):
        source = SOURCE.read_text(encoding="utf-8")
        tree = ast.parse(source)
        for node in tree.body:
            if isinstance(node, ast.ClassDef) and node.name == "GitIntegration":
                return ast.get_source_segment(source, node)
        self.fail("GitIntegration class not found")

    def test_get_modified_lines_uses_in_hunk_flag(self):
        """get_modified_lines must track in_hunk state to avoid advancing
        current_line for diff file-level headers."""
        src = self._get_git_class_source()
        self.assertIn("in_hunk", src,
                      "get_modified_lines must use an in_hunk flag to guard "
                      "against false line-number increments from diff headers")


class LinterParsingRegressionTests(unittest.TestCase):
    """Bug #14: _run_flake8/_run_pylint outer except swallowed all results on any int() failure."""

    def _get_linter_class_source(self):
        source = SOURCE.read_text(encoding="utf-8")
        tree = ast.parse(source)
        for node in tree.body:
            if isinstance(node, ast.ClassDef) and node.name == "LinterRunner":
                return ast.get_source_segment(source, node)
        self.fail("LinterRunner class not found")

    def test_flake8_has_per_line_try_except(self):
        """_run_flake8 must have a per-line try/except to avoid discarding all results."""
        src = self._get_linter_class_source()
        # The inner try/except for int conversion must be present
        self.assertIn("ValueError", src,
                      "_run_flake8/_run_pylint must catch ValueError per line, not globally")

    def test_pylint_has_per_line_try_except(self):
        """_run_pylint must have a per-line try/except to avoid discarding all results."""
        src = self._get_linter_class_source()
        self.assertIn("IndexError", src,
                      "_run_pylint must catch IndexError per line, not globally")


class CloseEventUnsavedTabsRegressionTests(unittest.TestCase):
    """Bug #13: closeEvent accepted unconditionally, silently discarding unsaved tabs."""

    def _get_close_event_source(self):
        source = SOURCE.read_text(encoding="utf-8")
        tree = ast.parse(source)
        for node in tree.body:
            if isinstance(node, ast.ClassDef) and node.name == "PythonArchitect":
                for item in node.body:
                    if isinstance(item, ast.FunctionDef) and item.name == "closeEvent":
                        return ast.get_source_segment(source, item)
        self.fail("closeEvent not found in PythonArchitect")

    def test_close_event_checks_is_modified(self):
        """closeEvent must check is_modified before accepting close."""
        src = self._get_close_event_source()
        self.assertIn("is_modified", src,
                      "closeEvent must check tab.is_modified before accepting close")

    def test_close_event_can_ignore(self):
        """closeEvent must be able to call event.ignore() to cancel close."""
        src = self._get_close_event_source()
        self.assertIn("event.ignore()", src,
                      "closeEvent must call event.ignore() when user cancels")

    def test_close_event_offers_save(self):
        """closeEvent must offer to save modified tabs via QMessageBox."""
        src = self._get_close_event_source()
        self.assertIn("QMessageBox", src,
                      "closeEvent must use QMessageBox to ask user about unsaved tabs")


class TranslatorIsGermanRegressionTests(unittest.TestCase):
    """Bug #12: _is_german checked individual chars in "aeoeueAeOeUess" causing
    false-positive detection for any text containing 'a', 'e', 'o', 'u', or 's'."""

    @classmethod
    def _load_translator(cls):
        translator_path = ROOT / "translator.py"
        spec = importlib.util.spec_from_file_location("translator", translator_path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod.TranslationSystem

    def setUp(self):
        TranslationSystem = self._load_translator()
        self.tr = TranslationSystem.__new__(TranslationSystem)
        self.tr.current_lang = 'de'
        self.tr.app_dir = Path(tempfile.mkdtemp())
        self.tr.translations_file = self.tr.app_dir / "locales" / "translations.json"
        self.tr.translations = {}
        self.tr.german_hints = [
            "datei", "bearbeiten", "ansicht", "hilfe", "oeffnen", "öffnen", "speichern",
        ]
        self.tr.string_patterns = []

    def test_plain_english_word_not_german(self):
        """Common English words must not be flagged as German."""
        self.assertFalse(self.tr._is_german("open"),
                         "'open' must not be detected as German (contains 'o','e')")

    def test_plain_english_word_save_not_german(self):
        """'save' must not be flagged as German despite containing 'a','e'."""
        self.assertFalse(self.tr._is_german("save"),
                         "'save' must not be detected as German")

    def test_real_umlaut_is_german(self):
        """Text with real German umlauts must be detected."""
        self.assertTrue(self.tr._is_german("Öffnen"),
                        "Text with ö/Ö must be detected as German")

    def test_ss_sequence_detected(self):
        """Text containing 'ss' (German ligature substitute) should be flagged."""
        self.assertTrue(self.tr._is_german("Strasse"),
                        "'Strasse' (contains 'ss') should be flagged as German")

    def test_german_hint_word_detected(self):
        """Text matching a hint keyword must be detected as German."""
        self.assertTrue(self.tr._is_german("Datei öffnen"),
                        "German hint word 'datei' must trigger German detection")


class InsertCompletionRegressionTests(unittest.TestCase):
    """Bug #11: insert_completion used completion[-0:] (full string) when extra==0."""

    def _get_method_source(self):
        source = SOURCE.read_text(encoding="utf-8")
        tree = ast.parse(source)
        for node in tree.body:
            if isinstance(node, ast.ClassDef) and node.name == "CodeEditor":
                for item in node.body:
                    if isinstance(item, ast.FunctionDef) and item.name == "insert_completion":
                        return ast.get_source_segment(source, item)
        self.fail("insert_completion not found in CodeEditor")

    def test_insert_completion_guards_extra_positive(self):
        """insert_completion must only insert tail when extra > 0 to avoid duplicate text."""
        src = self._get_method_source()
        self.assertIn(
            "extra > 0",
            src,
            "insert_completion must guard with 'extra > 0' to avoid inserting full word when prefix == completion",
        )


class OptimizeImportsUndoRegressionTests(unittest.TestCase):
    """Bug #10: optimize_imports_action used setPlainText, destroying undo history."""

    def _get_method_source(self):
        source = SOURCE.read_text(encoding="utf-8")
        tree = ast.parse(source)
        for node in tree.body:
            if isinstance(node, ast.ClassDef) and node.name == "PythonArchitect":
                for item in node.body:
                    if isinstance(item, ast.FunctionDef) and item.name == "optimize_imports_action":
                        return ast.get_source_segment(source, item)
        self.fail("optimize_imports_action not found in PythonArchitect")

    def test_optimize_imports_does_not_use_set_plain_text(self):
        """optimize_imports_action must not use setPlainText (destroys undo history)."""
        src = self._get_method_source()
        self.assertNotIn(
            "setPlainText",
            src,
            "optimize_imports_action must not call setPlainText (breaks undo); use cursor.insertText instead",
        )

    def test_optimize_imports_uses_cursor_insert(self):
        """optimize_imports_action must use cursor.insertText to preserve undo history."""
        src = self._get_method_source()
        self.assertIn(
            "insertText",
            src,
            "optimize_imports_action must use cursor.insertText to preserve undo history",
        )

    def test_optimize_imports_uses_edit_block(self):
        """optimize_imports_action must wrap insertion in beginEditBlock/endEditBlock."""
        src = self._get_method_source()
        self.assertIn("beginEditBlock", src,
                      "optimize_imports_action must use beginEditBlock for atomic undo step")


class TreeDropRegressionTests(unittest.TestCase):
    """Bug #9: tree_drop crashes with UnicodeDecodeError on non-UTF-8 .py files."""

    def _get_tree_drop_source(self):
        source = SOURCE.read_text(encoding="utf-8")
        tree = ast.parse(source)
        for node in tree.body:
            if isinstance(node, ast.ClassDef) and node.name == "PythonArchitect":
                for item in node.body:
                    if isinstance(item, ast.FunctionDef) and item.name == "tree_drop":
                        return ast.get_source_segment(source, item)
        self.fail("tree_drop method not found in PythonArchitect")

    def test_tree_drop_has_unicode_error_handling(self):
        """tree_drop must catch UnicodeDecodeError when reading dropped .py files."""
        src = self._get_tree_drop_source()
        self.assertIn("UnicodeDecodeError", src,
                      "tree_drop must handle UnicodeDecodeError for non-UTF-8 .py files")

    def test_tree_drop_has_oserror_handling(self):
        """tree_drop must also catch OSError for unreadable files."""
        src = self._get_tree_drop_source()
        self.assertIn("OSError", src,
                      "tree_drop must handle OSError for unreadable .py files")

    def test_tree_drop_has_try_block(self):
        """tree_drop must wrap the read_text call in a try block."""
        src = self._get_tree_drop_source()
        self.assertIn("try:", src,
                      "tree_drop must use try/except when reading dropped .py file content")


if __name__ == "__main__":
    unittest.main()
