# -*- coding: utf-8 -*-
"""Regressionstests Bugfix-Library-Transfer Batch #24 + CP-Nachfund + v1.3-Delta — REL_Editor_PythonBox.

D1: QMenu() ohne Parent ist GC-Risiko — muss QMenu(self) sein.
D2: Veraltete Qt-Enums in PySide6 6.4+ dürfen nicht mehr als bare Werte vorkommen.
    Erweitert (CP-Nachfund): Qt.GlobalColor, QPalette.ColorRole bare,
    Qt.PenStyle.NoPen, Qt.ContextMenuPolicy.
U2: json.loads/json.load ohne JSONDecodeError-Handler.
U3: open() im Text-Modus muss encoding= angeben.
U4: Nicht-atomares Schreiben — tmp + os.replace() Muster prüfen.
D4: subprocess.run ohne timeout= — PyInstaller-Build-Aufruf.
"""

import py_compile
import unittest
from pathlib import Path

PROJ = Path(__file__).parent.parent
SRC = PROJ / "PythonBox_v8.py"


class TestD1QMenuParent(unittest.TestCase):
    def test_no_bare_qmenu(self):
        src = SRC.read_text(encoding="utf-8")
        self.assertNotIn("QMenu()", src,
                         "QMenu() ohne Parent ist GC-Risiko; muss QMenu(self) sein")


class TestD2DeprecatedQtEnums(unittest.TestCase):
    def _src(self):
        return SRC.read_text(encoding="utf-8")

    def test_no_bare_userrole(self):
        src = self._src()
        self.assertNotIn("Qt.UserRole", src,
                         "Qt.UserRole (bare) — muss Qt.ItemDataRole.UserRole sein")

    def test_no_bare_align(self):
        src = self._src()
        self.assertNotIn("Qt.AlignRight", src)
        self.assertNotIn("Qt.AlignCenter", src)

    def test_no_bare_orientation(self):
        src = self._src()
        self.assertNotIn("Qt.Horizontal", src)

    def test_no_bare_messagebox(self):
        src = self._src()
        self.assertNotIn("QMessageBox.Save ", src)
        self.assertNotIn("QMessageBox.Discard", src)
        self.assertNotIn("QMessageBox.Cancel", src)
        self.assertNotIn("QMessageBox.Yes", src)

    def test_no_bare_cursor(self):
        src = self._src()
        self.assertNotIn("Qt.PointingHandCursor", src)

    def test_no_bare_globalcolor(self):
        src = self._src()
        self.assertNotIn("Qt.white", src,
                         "Qt.white (bare) — muss Qt.GlobalColor.white sein")
        self.assertNotIn("Qt.black", src,
                         "Qt.black (bare) — muss Qt.GlobalColor.black sein")

    def test_no_bare_qpalette_roles(self):
        src = self._src()
        for role in ("AlternateBase", "ToolTipBase", "ToolTipText",
                     "Button,", "ButtonText", "Link,"):
            self.assertNotIn(f"QPalette.{role.rstrip(',')},", src,
                             f"QPalette.{role.rstrip(',')} (bare) — muss QPalette.ColorRole.{role.rstrip(',')} sein")
        self.assertNotIn("QPalette.Button,", src)
        self.assertNotIn("QPalette.Link,", src)

    def test_no_bare_nopen(self):
        src = self._src()
        self.assertNotIn("Qt.NoPen", src,
                         "Qt.NoPen (bare) — muss Qt.PenStyle.NoPen sein")

    def test_no_bare_contextmenupolicy(self):
        src = self._src()
        self.assertNotIn("Qt.CustomContextMenu", src,
                         "Qt.CustomContextMenu (bare) — muss Qt.ContextMenuPolicy.CustomContextMenu sein")


class TestU2JsonDecodeError(unittest.TestCase):
    def _src(self):
        return SRC.read_text(encoding="utf-8")

    def test_import_settings_has_json_handler(self):
        src = self._src()
        self.assertIn("import_settings_from_json", src)
        self.assertIn("json.JSONDecodeError", src,
                      "json.loads in import_settings_from_json braucht JSONDecodeError-Handler")

    def test_snippet_import_has_json_handler(self):
        src = self._src()
        self.assertIn("import_from_json", src)
        # Mindestens 2 JSONDecodeError-Handler (settings + snippet)
        self.assertGreaterEqual(src.count("json.JSONDecodeError"), 2,
                                "json.loads in import_from_json braucht eigenen JSONDecodeError-Handler")


class TestU3OpenEncoding(unittest.TestCase):
    def test_lock_file_reads_have_encoding(self):
        src = SRC.read_text(encoding="utf-8")
        self.assertIn("open(self.lock_file, 'r', encoding='utf-8')", src)

    def test_lock_file_writes_use_tmp(self):
        # BUG-U4 fix: _save_locks schreibt jetzt atomar über tmp + os.replace
        src = SRC.read_text(encoding="utf-8")
        self.assertIn("str(self.lock_file) + \".tmp\"", src,
                      "_save_locks muss temporäre .tmp-Datei verwenden (BUG-U4)")


class TestU4AtomicWrite(unittest.TestCase):
    """BUG-U4: Nicht-atomares Schreiben — kein direktes open(path, 'w') für Persistenzdaten."""

    def _src(self):
        return SRC.read_text(encoding="utf-8")

    def test_write_settings_export_atomic(self):
        src = self._src()
        # write_settings_export muss tmp-Datei anlegen und os.replace nutzen
        self.assertIn('path.suffix + ".tmp"', src,
                      "write_settings_export: atomares Schreiben via .tmp-Suffix fehlt (BUG-U4)")
        self.assertIn("os.replace(tmp, path)", src,
                      "write_settings_export: os.replace(tmp, path) fehlt (BUG-U4)")

    def test_save_locks_atomic(self):
        src = self._src()
        self.assertIn('os.replace(tmp, self.lock_file)', src,
                      "_save_locks: os.replace(tmp, self.lock_file) fehlt (BUG-U4)")


class TestD4SubprocessTimeout(unittest.TestCase):
    """BUG-D4: subprocess.run ohne timeout= kann GUI einfrieren."""

    def test_pyinstaller_run_has_timeout(self):
        src = SRC.read_text(encoding="utf-8")
        # subprocess.run für PyInstaller-Build muss timeout= haben
        import re
        matches = re.findall(r'subprocess\.run\(cmd.*?\)', src, re.DOTALL)
        for m in matches:
            if 'pyinstaller' in src[max(0, src.index(m) - 200):src.index(m)].lower() or \
               'pyinstaller' in m.lower():
                self.assertIn('timeout=', m,
                              f"subprocess.run für PyInstaller-Build fehlt timeout= (BUG-D4): {m[:80]}")


class TestSyntaxValidity(unittest.TestCase):
    def test_syntax_valid(self):
        py_compile.compile(str(SRC), doraise=True)


if __name__ == "__main__":
    unittest.main()
