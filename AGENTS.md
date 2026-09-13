# AGENTS.md — Multi-Agent Governance & Workflow Policy

> **Repository:** `dev-bricks/pythonbox` (`C:\_Local_DEV\repos\pythonbox`)  
> **Status:** ACTIVE / HEALTHY  
> **Frameworks:** Gemini / Antigravity, Claude Code, OpenAI Codex  

---

## 1. Multi-Agent Rollen & Pfad-Autorität

- **Kanonischer Quellpfad (Autorität):** `C:\_Local_DEV\repos\pythonbox`
- **Spiegel-Pfad (OneDrive):** `C:\Users\User\OneDrive\.TOPICS\.SOFTWARE\...` (Nur Read-only Mirror / Backup)
- **Agenten-Rollen:**
  - **Gemini / Antigravity:** Automatisierte Systemwartung, UX/Accessibility Reviews, Bugsweeps, Permission Control, Scheduled Tasks.
  - **Claude / Codex:** Feature-Entwicklung, Refactoring, CI/CD, Test-Entwicklung.

---

## 2. Permission Level & Autonomie-Erwartungen

- **Standard-Berechtigung:** Projekt-Ebene Default / Turbo Mode.
- **Autonome Ausführung:** Automatisierte Aufrufe (Scheduled Tasks, Sidecars) sollen weitestgehend **ohne Nachfragen** laufen, sofern die Qualitäts-Gates und Sicherheitsprotokolle eingehalten werden.
- **Rollback-Garantie:** Maßnahmen an Doku- oder Konfigurationsdateien sind non-breaking. Bei unerwünschten Effekten gilt: Git-Revert oder manuelles Rollback.

---

## 3. Workflow Hooks & Sicherheitsprotokolle

Alle Agenten MÜSSEN folgende Letter Hooks beachten:

1. **`HOOK-DOC-TRAVERSAL-01` (Dokumenten-Traversal):** Vor Beginn der Arbeit `AGENTS.md`, `CLAUDE.md`, `README.md` im Projektstamm lesen.
2. **`HOOK-GARDENER-MEMORY-01` (Preflight Memory):** Bei komplexen Aufgaben `gardener` / Wissensgedächtnis konsultieren.
3. **`HOOK-WORKFLOW-HYGIENE-01` (Lock Security & Git Hygiene):**
   - Vor Dateiedits oder Git-Aktionen `LOCK*.txt` prüfen. Wenn `LOCK*.txt` oder `LOCK.user*.txt` existiert -> **ABSOLUTES TABU** (keine Änderungen, keine Pushes).
   - Qualitäts-Gate: `pytest` ausführen vor Commits.
   - `CHANGELOG.md` aktualisieren.
4. **`HOOK-PATH-VALIDATION-01` (Pfad-Validierung):** Raw-Strings (`r"C:\..."`) oder Forward-Slashes in Python verwenden.
5. **`HOOK-BANNER-ASSET-01` (Banner & Visual Guardrails):** Keine vorhandenen Banners überschreiben oder doppeln.

---

## 4. Testen & Verifizierung

```powershell
pytest
```
- Alle 93+ Pytest-Tests müssen grün bleiben.
