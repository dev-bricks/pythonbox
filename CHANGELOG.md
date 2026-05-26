# Changelog / Änderungsprotokoll

Alle wesentlichen Änderungen an diesem Projekt werden hier dokumentiert.
Format basiert auf [Keep a Changelog](https://keepachangelog.com/de/1.1.0/).

## [Unreleased]

### Hinzugefügt / Added
- App- und Fenstericon über `PythonBox.ico`.
- `build_exe.bat` für lokale PyInstaller-Builds.
- Regressionstests für Qt6-Editor-APIs, F5-Ausführung, externe Python-Kommandos und Offscreen-Fensteraufbau.
- GitHub Actions Workflow für Windows-Regressionstests auf Python 3.10 bis 3.12.

### Geändert / Changed
- README, Security Policy, Contributing Guide und Code of Conduct auf das aktuelle Repository `dev-bricks/pythonbox` und die MIT-Lizenz ausgerichtet.
- `.gitignore` um interne Steuerungsdateien, Secrets, Datenbanken, Logs, Test-Locks und Windows-/Build-Artefakte erweitert.
- Dokumentierte Mindestversion auf Python 3.10+ vereinheitlicht, passend zur Startdatei und Testmatrix.

### Behoben / Fixed
- Veraltete Clone-Pfade und `main.py`-Startbefehle in der Repository-Dokumentation entfernt.
- Öffentliche E-Mail-Adresse aus dem Code of Conduct entfernt.
- Doppelte `run_script`-Definition in `PythonArchitect` beseitigt, damit F5 wieder konsistent über das Debug-Output-Panel läuft.
- Entfernte Qt6-APIs `fontMetrics().width()` und `setTabStopWidth()` durch aktuelle Alternativen ersetzt.
- Externe Python-Skripte starten jetzt mit `sys.executable` statt einem hardcodierten `python`/`python3`.
- Die Minimap-Option im Einstellungsdialog nutzt jetzt denselben `show_minimap`-Key wie das Ansicht-Menü und wird auch über den Apply-Button direkt auf die Hauptansicht angewendet.
- Kombinierte Git-Porcelain-Statuscodes wie `AM` werden in der Statusleiste lesbar zusammengefasst.
- Git-Diff-Markierungen behandeln ersetzte Zeilen als geändert statt als reine Hinzufügung.
- `Speichern unter` stellt den bisherigen Dateipfad wieder her, wenn der Dialog abgebrochen wird.
- Deutsche Übersetzungshinweise und Docstrings nutzen echte Umlaute.

## [1.0.0] - YYYY-MM-DD

### Hinzugefügt / Added
- Erstveröffentlichung / Initial release
