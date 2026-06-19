# Changelog / Änderungsprotokoll

Alle wesentlichen Änderungen an diesem Projekt werden hier dokumentiert.
Format basiert auf [Keep a Changelog](https://keepachangelog.com/de/1.1.0/).

## [Unreleased]

### Build / Release
- EXE neu gebaut 2026-06-04 (PyInstaller, OneDrive-externer Build); `START_PythonBox_v8.bat` startet jetzt bevorzugt `dist\PythonBox.exe` und fällt danach auf Root-EXE bzw. Python-Fallback zurück. SHA256: `1F5C024682B5B77BD04963E972F3EDAB9D9E606DE1339D390D2181A8606672BC`.
- EXE neu gebaut 2026-06-01 (PyInstaller `--onefile`, `PythonBox.exe`); 14/14 Tests grün, Smoke-Test bestanden. Vorherige EXE: 2026-04-29.

### Hinzugefügt / Added
- CLI-Lint-Modus: `python PythonBox_v8.py --lint <datei>` führt headless Linting durch (flake8 → pylint → AST-Fallback) und gibt Ergebnisse auf stdout aus. Exit-Codes: 0 = sauber, 1 = Findings, 2 = Fehler. Kein GUI-Start. Nützlich für CI, Automationen und LLM-Agenten.
- `tests/test_cli_lint.py` mit 5 Tests für den CLI-Lint-Modus.
- CLI-Parsing mit `argparse` (`parse_cli_args()` + `parse_known_args`), rückwärtskompatibel zu `--open` und nackten Dateipfaden. Unbekannte Qt-Flags (z. B. `-style fusion`) werden durchgereicht statt abzubrechen.
- Linter-Erkennung: `python -m flake8` / `python -m pylint` als Fallback wenn `shutil.which()` fehlschlägt (typisch auf Windows/Git Bash). Erkennung gated auf `returncode == 0`.
- 3 Unit-Tests für Linter-Detection-Logik (Mock-basiert: fehlender Linter, erfolgreicher Modul-Fallback).
- `llms.txt` mit kanonischem Repo-Kontext, Zielgruppe, Suchphrasen und Abgrenzung zu Devbox/Python-Box/Pybricks.
- README-Starttabelle und GitHub-Actions-Badge für schnellere Nutzerführung.
- App- und Fenstericon über `PythonBox.ico`.
- `build_exe.bat` für lokale PyInstaller-Builds.
- `PORTIERUNGSPLAN.md` mit Desktop-only-Strategie für Windows, macOS und Linux.
- Optionaler JSON-Austausch für Snippet-Bibliothek und portable Editor-Einstellungen (`pythonbox-snippets-v1.json`, `pythonbox-settings-v1.json`).
- Regressionstests für Qt6-Editor-APIs, F5-Ausführung, externe Python-Kommandos und Offscreen-Fensteraufbau.
- Zusätzlicher Git-Regressionstest für CRLF-Ersatzzeilen, damit Windows-Diffs mit ersetzten Zeilen weiterhin als `modified` statt als reine `added`-Treffer klassifiziert bleiben.
- GitHub Actions Workflow für Windows-Regressionstests auf Python 3.10 bis 3.12.
- README-SEO-Einstieg, präzisere Screenshot-Beschreibung und Discovery-Keywords für die GitHub-Suche.

### Geändert / Changed
- Community-Workflows auf `actions/stale@v10` und `actions/first-interaction@v3` aktualisiert.
- README, Security Policy, Contributing Guide und Code of Conduct auf das aktuelle Repository `dev-bricks/pythonbox` und die MIT-Lizenz ausgerichtet.
- `.gitignore` um interne Steuerungsdateien, Secrets, Datenbanken, Logs, Test-Locks und Windows-/Build-Artefakte erweitert.
- Dokumentierte Mindestversion auf Python 3.10+ vereinheitlicht, passend zur Startdatei und Testmatrix.
- Datei-Menü um Export-/Import-Aktionen für Snippets und Einstellungen erweitert; JSON-Importe aktualisieren Bibliothek und Editor-Ansicht direkt.
- Aufgaben- und README-Dokumentation auf den realen Automationsstand korrigiert: aktuell unterstützt PythonBox nur GUI-Start plus Dateiöffnung über `--open` oder nackten Dateipfad, aber keine REST-API und kein allgemeines Headless-CLI.

### Behoben / Fixed
- Veraltete Clone-Pfade und `main.py`-Startbefehle in der Repository-Dokumentation entfernt.
- Öffentliche E-Mail-Adresse aus dem Code of Conduct entfernt.
- Doppelte `run_script`-Definition in `PythonArchitect` beseitigt, damit F5 wieder konsistent über das Debug-Output-Panel läuft.
- Entfernte Qt6-APIs `fontMetrics().width()` und `setTabStopWidth()` durch aktuelle Alternativen ersetzt.
- Externe Python-Skripte starten jetzt mit `sys.executable` statt einem hardcodierten `python`/`python3`.
- Startargumente `--open <datei>`, `--open=<datei>` und nackte Dateipfade werden jetzt beim App-Start ausgewertet und öffnen die Datei direkt im ersten Tab statt sie still zu ignorieren.
- Die Minimap-Option im Einstellungsdialog nutzt jetzt denselben `show_minimap`-Key wie das Ansicht-Menü und wird auch über den Apply-Button direkt auf die Hauptansicht angewendet.
- Kombinierte Git-Porcelain-Statuscodes wie `AM` werden in der Statusleiste lesbar zusammengefasst.
- Git-Diff-Markierungen behandeln ersetzte Zeilen als geändert statt als reine Hinzufügung.
- Der zuvor offene Windows-Gesamtlauf-Befund rund um `test_git_modified_lines_classify_replacements_as_modified` ist lokal nicht mehr reproduzierbar; der vollständige `unittest`-Lauf ist wieder grün und der Git-Diff-Fall wird jetzt zusätzlich mit expliziten CRLF-Dateien abgesichert.
- `Speichern unter` stellt den bisherigen Dateipfad wieder her, wenn der Dialog abgebrochen wird.
- Deutsche Übersetzungshinweise und Docstrings nutzen echte Umlaute.

## [1.0.0] - YYYY-MM-DD

### Hinzugefügt / Added
- Erstveröffentlichung / Initial release
