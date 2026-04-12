# Python Code Architect (PythonBox) v8

Eine leichtgewichtige Python-IDE mit modernem Dark Theme. Schneller Start, niedriger RAM-Verbrauch, integrierter Debugger.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![PySide6](https://img.shields.io/badge/PySide6-6.5+-green.svg)
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
- PySide6 6.5+
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

## English

A lightweight Python IDE with dark theme, debugging integration, and code folding.

### Features

- Syntax highlighting
- Dark/light themes
- Debugging integration
- Code folding
- Auto-completion

### Installation

```bash
git clone https://github.com/lukisch/REL_Editor_PythonBox.git
cd REL_Editor_PythonBox
pip install -r requirements.txt
python "PythonBox_v8.py"
```

### License

See [LICENSE](LICENSE) for details.

---

## Haftung / Liability

Dieses Projekt ist eine **unentgeltliche Open-Source-Schenkung** im Sinne der §§ 516 ff. BGB. Die Haftung des Urhebers ist gemäß **§ 521 BGB** auf **Vorsatz und grobe Fahrlässigkeit** beschränkt. Ergänzend gelten die Haftungsausschlüsse aus GPL-3.0 / MIT / Apache-2.0 §§ 15–16 (je nach gewählter Lizenz).

Nutzung auf eigenes Risiko. Keine Wartungszusage, keine Verfügbarkeitsgarantie, keine Gewähr für Fehlerfreiheit oder Eignung für einen bestimmten Zweck.

This project is an unpaid open-source donation. Liability is limited to intent and gross negligence (§ 521 German Civil Code). Use at your own risk. No warranty, no maintenance guarantee, no fitness-for-purpose assumed.

