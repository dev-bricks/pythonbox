# CLAUDE.md — Project Technical Guidelines

> **Project:** PythonBox (`dev-bricks/pythonbox`)  
> **Path:** `C:\_Local_DEV\repos\pythonbox`  
> **Delegation:** See [AGENTS.md](AGENTS.md) for Multi-Agent Governance and Letter Hooks.

---

## 1. Overview & Architecture
PythonBox is a desktop IDE and environment for executing, testing, and managing Python scripts with dynamic linter, status indicators, and full accessibility support.

## 2. Test Commands & Quality Gates
- **Run Unit & Integration Tests:**
  ```powershell
  pytest
  ```
- **Translation Management:**
  ```powershell
  python manage_translations.py
  ```

## 3. Coding & Accessibility Standards
- **German Umlaute:** All German user interface strings must render native UTF-8 Umlaute (`ä`, `ö`, `ü`, `ß`). No replacement substitutions (`ae`, `oe`, `ue`) or corrupt encoding.
- **UX & Accessibility:** Statusbar and linter UI elements must expose proper `AccessibleName`, `AccessibleDescription`, and `ToolTip` properties with dynamic screenreader updates.
- **Git & Lock Safety:** Check for `LOCK*.txt` files before modifying code or performing git commits.
