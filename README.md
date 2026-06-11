# PythonBox - lightweight Python IDE for Windows

PythonBox is a local-first Python IDE for Windows developers who want a focused editor with PySide6, PDB debugging, code folding, linting, Git status, and optional handoff to VS Code or PyCharm.

PythonBox ist eine lokale Python-IDE für Windows-Entwicklerinnen und -Entwickler, die einen fokussierten Editor mit PySide6, PDB-Debugging, Code Folding, Linting, Git-Status und optionaler Übergabe an VS Code oder PyCharm suchen.

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![PySide6](https://img.shields.io/badge/PySide6-6.5+-green.svg)
![PythonBox tests](https://github.com/dev-bricks/pythonbox/actions/workflows/tests.yml/badge.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## Start here

| If you want to... | Start with |
|---|---|
| Try the IDE from source | `python PythonBox_v8.py` |
| Build a local Windows EXE | `build_exe.bat` |
| Check the regression suite | `python -m unittest discover -s tests -v` |
| Understand the platform boundary | [PORTIERUNGSPLAN.md](PORTIERUNGSPLAN.md) |
| Give an LLM or crawler the repo context | [llms.txt](llms.txt) |

## Why PythonBox?

PythonBox is built for small Python scripts, local automation tools, learning workflows, and LLM-assisted coding sessions where a full IDE can feel too heavy. It keeps the core loop in one desktop window: open a file, edit Python, run it with the current interpreter, inspect output, debug with breakpoints, and check Git changes before handing the file to a larger IDE when needed.

## Screenshot

![PythonBox dark-theme Python IDE with editor, minimap, output panel, and local debugging controls](README/screenshots/main.png)

## Funktionen / Features

### Editor
- Python-Syntax-Highlighting
- Auto-Completion für Keywords, Builtins und Snippets
- Code Folding für Klassen und Funktionen
- Minimap und Bracket Matching
- Mehrere Dateien über Tabs

### Debugging und Entwicklung
- Ausführen über `sys.executable`
- PDB-Debugger im Output-Panel
- Breakpoints über die Zeilennummern
- Debug-Toolbar mit Step In, Step Over und Step Out
- Linter-Integration für Pylint und Flake8
- Git-Status, Diff und Modified-Markierung
- Kombinierte Git-Statuscodes werden lesbar angezeigt; ersetzte Diff-Zeilen werden als geändert statt nur als hinzugefügt markiert
- Qt6-kompatible Editor-Metriken und F5-Ausführung über das Debug-Output-Panel
- `Speichern unter` behält bei abgebrochenem Dialog den bisherigen Dateipfad
- Die Minimap-Einstellung bleibt zwischen Ansicht-Menü und Einstellungsdialog synchron, inklusive Fallback für ältere Konfigurationen
- Snippet-Bibliothek und portable Editor-Einstellungen lassen sich optional als JSON importieren und exportieren (`pythonbox-snippets-v1.json`, `pythonbox-settings-v1.json`)

### Windows-Paketierung
- `PythonBox.ico` wird als App- und Fenstericon verwendet, wenn die Datei vorhanden ist.
- `build_exe.bat` erstellt eine kompakte Windows-EXE mit PyInstaller.
- `START_PythonBox_v8.bat` startet die Anwendung direkt aus dem Checkout.

### Plattformstrategie
- Windows bleibt die primäre Desktop-Plattform.
- macOS und Linux sind sinnvolle Source-Smoke-Ziele aus derselben PySide6-Codebasis.
- Android, iOS und Web/PWA sind keine aktuellen Ziele, weil PythonBox lokale Dateien, lokale Interpreter, Debugger, Linter und Git direkt nutzt.

## Installation

### Voraussetzungen / Requirements
- Python 3.10+
- PySide6 6.5+
- Optional: Git, Pylint, Flake8, VS Code, PyCharm

### Start aus dem Quellcode / Run from source

```bash
git clone https://github.com/dev-bricks/pythonbox.git
cd pythonbox
pip install -r requirements.txt
python PythonBox_v8.py
```

Unter Windows kann alternativ `START_PythonBox_v8.bat` per Doppelklick gestartet werden.

Optional kann direkt beim Start eine Datei geöffnet werden:

```bash
python PythonBox_v8.py --open demo.py
python PythonBox_v8.py demo.py
```

Weitere Headless-CLI-Befehle oder eine REST-API sind aktuell nicht Teil des Projekts.

### Windows-EXE bauen / Build Windows EXE

```bash
pip install pyinstaller
build_exe.bat
```

Das Build-Ergebnis liegt anschließend in `dist/`. Build-Artefakte und lokale Releases sind bewusst nicht Teil des Git-Repositories.

## Tests

Die Regressionstests prüfen die Qt6-API-Kompatibilität, die F5-Ausführung über `debug_output.run_normal`, die externe Terminal-Ausführung mit dem aktuellen Python-Interpreter, die Minimap-Einstellungssynchronisation, Git-Status-/Diff-Erkennung, den JSON-Austausch für Snippets und Einstellungen, `Speichern unter`-Abbruchverhalten und einen Offscreen-Smoke-Test für das Hauptfenster.

```bash
python -m unittest discover -s tests -v
```

GitHub Actions führt diese Prüfungen unter Windows für Python 3.10 bis 3.12 aus.

## Tastenkürzel / Keyboard Shortcuts

| Shortcut | Funktion / Action |
|---|---|
| `Ctrl+F` | Suchen / Find |
| `Ctrl+H` | Ersetzen / Replace |
| `Ctrl+G` | Gehe zu Zeile / Go to line |
| `Ctrl+/` | Kommentieren / Toggle comment |
| `F5` | Ausführen / Run |
| `F9` | Breakpoint umschalten / Toggle breakpoint |
| `F10` | Step Over |
| `F11` | Step Into |

## Datenschutz / Privacy

PythonBox arbeitet lokal. Es gibt keine Telemetrie, keinen Cloud-Sync und keine eingebauten externen API-Aufrufe. Dateien werden nur geöffnet, gespeichert oder ausgeführt, wenn Nutzerinnen und Nutzer diese Aktionen in der App auslösen.

PythonBox runs locally. It does not include telemetry, cloud sync, or built-in external API calls. Files are opened, saved, or executed only when users trigger those actions in the app.

## Repository-Hygiene

Nicht versioniert werden interne Aufgabenlisten, Test-Locks, lokale Build-Artefakte, Release-Ordner, virtuelle Umgebungen, Datenbanken, Secrets und IDE-/OS-Metadaten. Details stehen in `.gitignore`.

## Roadmap

PythonBox bleibt als schlanke Python-IDE erhalten. Die geplante Multi-Language-Erweiterung läuft separat unter CodeBox.

## Discovery keywords

`python ide`, `lightweight python editor`, `pyside6 code editor`, `windows python ide`, `local-first developer tool`, `pdb debugger gui`, `python linting`, `code folding`, `git diff editor`, `vs code handoff`, `pycharm handoff`, `offline python editor`

## Lizenz / License

MIT License, siehe [LICENSE](LICENSE).

## Haftung / Liability

Dieses Projekt wird unentgeltlich als Open Source bereitgestellt. Nutzung auf eigenes Risiko. Es gibt keine Wartungszusage, keine Verfügbarkeitsgarantie und keine Gewähr für Fehlerfreiheit oder Eignung für einen bestimmten Zweck. Ergänzend gilt der Haftungsausschluss der MIT-Lizenz.

This project is provided as free open source software. Use it at your own risk. There is no maintenance commitment, availability guarantee, or warranty of fitness for a particular purpose. The MIT license disclaimer also applies.
