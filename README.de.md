# Python Code Architect (PythonBox) v8

Eine leichtgewichtige Python-IDE mit modernem Dark Theme. Schneller Start, niedriger RAM-Verbrauch, integrierter Debugger.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![PyQt5](https://img.shields.io/badge/PyQt5-5.15+-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## Features

### Debugging
- **VS Code Integration** - Direkt in VS Code oeffnen/debuggen
- **PDB Debugger** - Interaktiver Debugger im Output-Panel
- **Breakpoints** - Visuelle Breakpoint-Verwaltung (Klick auf Zeilennummer)
- **Debug-Toolbar** - Step In/Out/Over Controls
- **PyCharm Integration** - Optional

### Editor
- **Syntax-Highlighting** - Python-spezifisch
- **Auto-Completion** - Keywords, Builtins, Snippets
- **Code Folding** - Klassen/Funktionen einklappen
- **Minimap** - Code-Vorschau rechts
- **Bracket Matching** - Klammer-Hervorhebung

### Entwicklung
- **Linter-Integration** - Pylint/Flake8 Fehleranzeige
- **Git-Integration** - Status, Diff, Modified-Markierung
- **Error-Markierungen** - Rote Wellenlinien
- **Tab-System** - Mehrere Dateien gleichzeitig

## Installation

```bash
# Repository klonen
git clone https://github.com/lukisch/pythonbox.git
cd pythonbox

# Dependencies installieren
pip install -r requirements.txt

# Starten
python PythonBox_v8.py
```

### Windows
Alternativ: `START_PythonBox_v8.bat` ausfuehren.

## Keyboard Shortcuts

| Shortcut | Funktion |
|----------|----------|
| `Ctrl+F` | Suchen |
| `Ctrl+H` | Ersetzen |
| `Ctrl+G` | Gehe zu Zeile |
| `Ctrl+/` | Kommentieren |
| `F5` | Ausfuehren |
| `F9` | Breakpoint Toggle |
| `F10` | Step Over |
| `F11` | Step Into |

## Screenshots

Das Dark Theme basiert auf dem Fusion-Style mit VS Code-aehnlicher Farbpalette.

## Systemanforderungen

- Python 3.8+
- PyQt5 5.15+
- Windows / Linux / macOS

### Optionale Integrationen
- VS Code (fuer "In VS Code oeffnen")
- PyCharm (fuer "In PyCharm oeffnen")
- Pylint / Flake8 (fuer Linter-Support)
- Git (fuer Git-Integration)

## Roadmap

Geplante Erweiterung zur Multi-Language IDE "CodeBox":
- JavaScript/TypeScript Support
- C/C++ Support (mit GDB)
- Rust Support
- Go Support
- Plugin-System fuer Sprachen

## Lizenz

MIT License - siehe [LICENSE](LICENSE)

## Autor

Lukas Geiger ([@lukisch](https://github.com/lukisch))

---

English version: [README.md](README.md)
