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

## [1.0.0] - YYYY-MM-DD

### Hinzugefügt / Added
- Erstveröffentlichung / Initial release
