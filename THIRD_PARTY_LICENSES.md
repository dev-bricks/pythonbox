# Third-Party Software & Licenses (SBOM)

**Repository:** `dev-bricks/pythonbox`  
**Product:** PythonBox — Lightweight Local-First Python IDE for Windows  
**Release Version:** 1.0.1  
**Author / Maintainer:** dev-bricks  
**Primary License:** MIT License ([LICENSE](LICENSE))  
**SPDX-License-Identifier:** MIT  

---

## 1. Overview & Architectural Isolation

PythonBox is engineered as a local-first desktop IDE for Python developers. It runs 100% locally on the user's workstation without requiring cloud infrastructure, background telemetry, or mandatory remote network access.

### Invariant Guarantee (INV-LOCAL-01 through INV-SLA-10)

| Invariant | Category | Description | Status |
|---|---|---|---|
| **INV-LOCAL-01** | Offline Operation | 100% offline runtime; zero mandatory external network egress during editing, linting, or debugging. | **PASS** |
| **INV-LOCAL-02** | Telemetry & Privacy | Zero telemetry, analytics tracking, or behavioral phone-home mechanisms. | **PASS** |
| **INV-LOCAL-03** | Secrets & Auth | Zero hardcoded API keys, bearer tokens, or sensitive credentials. | **PASS** |
| **INV-LOCAL-04** | Atomic Persistence | Editor save and export operations write to temporary files before atomic rename to prevent corruption. | **PASS** |
| **INV-LOCAL-05** | Least-Privilege Execution | Standard unprivileged user execution (`RunAsInvoker`); no Windows UAC elevation required. | **PASS** |
| **INV-LOCAL-06** | User-Consent Handoff | External tool handoffs (VS Code, PyCharm, Git, PyInstaller) execute only upon explicit user action. | **PASS** |
| **INV-LOCAL-07** | UTF-8 & Umlaut Integrity | Full preservation of UTF-8 encoding and German umlauts across source files and diagnostics. | **PASS** |
| **INV-LOCAL-08** | Accessibility (a11y) | Status bar indicators, editor controls, and linter panels expose full screen reader metadata. | **PASS** |
| **INV-SLA-09** | Vulnerability Triage | Confirmed vulnerability reports triaged and acknowledged within 5 business days. | **PASS** |
| **INV-SLA-10** | 48-Hour Response SLA | Initial response and assessment for security reports provided within 48 hours. | **PASS** |

---

## 2. Runtime Dependencies (SBOM)

| Package | Version Range | License | SPDX Identifier | Component Type | Usage / Linking Mode |
|---|---|---|---|---|---|
| **PySide6** | `>=6.5.0` | GNU LGPL v3.0 | `LGPL-3.0-only` | Runtime Dependency | Dynamic linking via Python C-extension; unmodified Qt binaries |
| **Python Standard Library** | `>=3.10` | Python Software Foundation | `PSF-2.0` | Runtime Standard | Standard library modules (`ast`, `pdb`, `subprocess`, `argparse`, etc.) |

### PySide6 & LGPL-3.0 Compliance Notice

PythonBox utilizes PySide6 (the official Python bindings for Qt) under the GNU Lesser General Public License version 3.0 (`LGPL-3.0-only`).

- **Dynamic Linking:** PythonBox interacts with PySide6 and Qt exclusively via dynamic linking through Python import statements and compiled shared libraries/DLLs.
- **Unmodified Qt Libraries:** PythonBox does not modify, patch, or statically incorporate Qt or PySide6 C++ source code.
- **Relinking Freedom:** End users are free to replace or upgrade the PySide6 package in their Python virtual environment or system installation with any compatible version of PySide6 without affecting PythonBox licensing terms.
- **Source Code Availability:** Source code for PySide6 and Qt is available from The Qt Company at [https://wiki.qt.io/Qt_for_Python](https://wiki.qt.io/Qt_for_Python) and [https://code.qt.io/cgit/](https://code.qt.io/cgit/).

---

## 3. Zero-Copyleft Contagion Guarantee

1. **User Intellectual Property:** All Python scripts, applications, and assets authored, edited, debugged, or formatted inside PythonBox remain the sole and exclusive intellectual property of the author. PythonBox exerts **zero copyleft claim or licensing obligations** over user scripts.
2. **Editor Permissiveness:** PythonBox itself is distributed under the permissive MIT License.

---

## 4. Development & Testing Dependencies

| Package | Version Range | License | SPDX Identifier | Scope |
|---|---|---|---|---|
| **pytest** | `>=7.0.0` | MIT License | `MIT` | Automated regression and contract test execution |
| **ruff** | `>=0.4.0` | MIT / Apache-2.0 | `MIT OR Apache-2.0` | Code formatting and static lint analysis |

---

## 5. License Texts

### MIT License (PythonBox)

```text
MIT License

Copyright (c) 2026 dev-bricks

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

### GNU Lesser General Public License v3.0 (PySide6 / Qt)

```text
PySide6 is licensed under the GNU Lesser General Public License (LGPL) version 3.
Complete text available at: https://www.gnu.org/licenses/lgpl-3.0.html
```

### Python Software Foundation License version 2.0 (Python stdlib)

```text
The Python Standard Library is licensed under the Python Software Foundation License Version 2.
Complete text available at: https://docs.python.org/3/license.html
```
