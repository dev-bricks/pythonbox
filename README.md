# Python Code Architect (PythonBox) v8

A lightweight Python IDE with a modern dark theme. Fast startup, low RAM usage, integrated debugger.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![PyQt5](https://img.shields.io/badge/PyQt5-5.15+-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## Features

### Debugging
- **VS Code Integration** - Open and debug directly in VS Code
- **PDB Debugger** - Interactive debugger in the output panel
- **Breakpoints** - Visual breakpoint management (click on line numbers)
- **Debug Toolbar** - Step In/Out/Over controls
- **PyCharm Integration** - Optional

### Editor
- **Syntax Highlighting** - Python-specific
- **Auto-Completion** - Keywords, builtins, snippets
- **Code Folding** - Collapse classes/functions
- **Minimap** - Code preview on the right
- **Bracket Matching** - Bracket highlighting

### Development
- **Linter Integration** - Pylint/Flake8 error display
- **Git Integration** - Status, diff, modified markers
- **Error Markers** - Red squiggly lines
- **Tab System** - Multiple files simultaneously

## Installation

```bash
# Clone the repository
git clone https://github.com/lukisch/pythonbox.git
cd pythonbox

# Install dependencies
pip install -r requirements.txt

# Run
python PythonBox_v8.py
```

### Windows
Alternatively, run `START_PythonBox_v8.bat`.

## Keyboard Shortcuts

| Shortcut | Function |
|----------|----------|
| `Ctrl+F` | Search |
| `Ctrl+H` | Replace |
| `Ctrl+G` | Go to line |
| `Ctrl+/` | Toggle comment |
| `F5` | Run |
| `F9` | Toggle breakpoint |
| `F10` | Step Over |
| `F11` | Step Into |

## Screenshots

The dark theme is based on the Fusion style with a VS Code-like color palette.

## System Requirements

- Python 3.8+
- PyQt5 5.15+
- Windows / Linux / macOS

### Optional Integrations
- VS Code (for "Open in VS Code")
- PyCharm (for "Open in PyCharm")
- Pylint / Flake8 (for linter support)
- Git (for Git integration)

## Roadmap

Planned expansion to a multi-language IDE "CodeBox":
- JavaScript/TypeScript support
- C/C++ support (with GDB)
- Rust support
- Go support
- Plugin system for languages

## License

MIT License - see [LICENSE](LICENSE)

## Author

Lukas Geiger ([@lukisch](https://github.com/lukisch))

---

Deutsche Version: [README.de.md](README.de.md)
