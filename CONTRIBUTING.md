# Beitragsrichtlinie / Contributing Guide

## Deutsch

Vielen Dank für Ihr Interesse an PythonBox.

### Beiträge

1. Bugs als GitHub Issue mit reproduzierbaren Schritten melden.
2. Feature-Vorschläge als Issue mit erwarteter Nutzung beschreiben.
3. Codeänderungen über Pull Requests einreichen.

### Pull Requests

1. Repository forken.
2. Feature-Branch erstellen: `git checkout -b feature/mein-feature`
3. Änderungen lokal testen.
4. Commit erstellen: `git commit -m "Beschreibung der Änderung"`
5. Branch pushen und Pull Request öffnen.

### Lokaler Start

```bash
git clone https://github.com/dev-bricks/pythonbox.git
cd pythonbox
pip install -r requirements.txt
python PythonBox_v8.py
```

### Code-Richtlinien

- Python-Code folgt PEP 8.
- GUI-Code nutzt PySide6.
- Dokumente und Quelltexte werden als UTF-8 gespeichert.
- Keine hardcodierten privaten Pfade, Tokens, Passwörter oder API-Keys.
- Interne Dateien wie `AUFGABEN.txt`, Test-Locks, Build-Artefakte und lokale Releases bleiben unversioniert.
- Dokumentation aktualisieren, wenn sich Bedienung, Installation oder Build-Prozess ändern.

### Lizenz

Mit dem Einreichen eines Pull Requests bestätigen Sie, dass Sie die Rechte an Ihrem Beitrag besitzen und ihn unter der MIT-Lizenz dieses Projekts bereitstellen können.

---

## English

Thank you for your interest in PythonBox.

### Contributions

1. Report bugs as GitHub issues with reproducible steps.
2. Describe feature requests as issues with the expected workflow.
3. Submit code changes through pull requests.

### Pull Requests

1. Fork the repository.
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Test the changes locally.
4. Commit: `git commit -m "Description of change"`
5. Push the branch and open a pull request.

### Local Setup

```bash
git clone https://github.com/dev-bricks/pythonbox.git
cd pythonbox
pip install -r requirements.txt
python PythonBox_v8.py
```

### Code Guidelines

- Follow PEP 8 for Python code.
- Use PySide6 for GUI code.
- Store documents and source files as UTF-8.
- Do not commit private paths, tokens, passwords, or API keys.
- Keep internal task files, test locks, build artifacts, and local releases out of Git.
- Update documentation when usage, installation, or build behavior changes.

### License

By submitting a pull request, you confirm that you have the rights to your contribution and can provide it under this project's MIT license.
