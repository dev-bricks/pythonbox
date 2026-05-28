# Portierungsplan - PythonBox v8

Stand: 2026-05-28

## Bedingungsprüfung

Ein zentraler Portierungsplan war nicht vorhanden. Es gab nur Hinweise in README, AUFGABEN und der Windows-Store-Pipeline. Daher wurde Pfad B ausgeführt: Plan neu erstellen und Aufgaben ergänzen.

## Kurzentscheidung

PythonBox bleibt eine Desktop-App. Sinnvoll sind Windows als Hauptplattform sowie macOS und Linux als Source-Smoke-Ziele aus derselben PySide6-Codebasis. Android, iOS und Web/PWA sind keine aktuellen Ziele, weil die wichtigsten Usecases lokale Dateien, lokale Python-Interpreter, Git, Linter, Debugger und externe Editor-Brücken brauchen.

Ein Companion ist ebenfalls kein sinnvoller nächster Schritt. Der Nutzen der App liegt im direkten Bearbeiten und Ausführen lokaler Python-Dateien; ein mobiler oder browserbasierter Begleiter würde nur einen kleinen Ausschnitt abdecken und die eigentliche IDE-Erfahrung nicht verbessern.

## Features der besten ausgebauten Version

- Mehrdatei-Editor mit Tabs, Python-Syntax-Highlighting, Suche, Ersetzen, Gehe-zu-Zeile, Kommentieren, Code Folding, Minimap und Bracket Matching.
- Python-Ausführung über den aktuell laufenden Interpreter.
- PDB-Debugging mit Breakpoints, Step In, Step Over und Step Into.
- Linter-Integration für Flake8, Pylint und AST-Syntaxprüfung.
- Git-Status, Diff-Ansicht und Zeilenmarkierung für geänderte Dateien.
- Snippet-/Bibliotheksverwaltung für wiederkehrende Python-Bausteine.
- Optionale Übergabe an VS Code oder PyCharm.
- Lokaler Windows-Start und Windows-EXE-Build über PyInstaller.

## Usecase-Settings

### Setting 1: Desktop-Entwicklung und Lernen

Nutzergruppe: Einzelne Entwicklerinnen, Entwickler, Lernende und LLM-unterstützte Arbeitsläufe, die Python-Dateien lokal bearbeiten, prüfen und ausführen.

Usecases:

- Eine Python-Datei schnell öffnen, bearbeiten und ausführen, ohne eine große IDE zu starten.
- Kleine Skripte debuggen und Breakpoints direkt im Editor setzen.
- Linter- und Syntaxfehler während der Bearbeitung erkennen.
- Änderungen in Git-Arbeitsbäumen sichtbar prüfen.
- Snippets wiederverwenden und kleine Werkzeuge aus der IDE heraus starten.
- Bei Bedarf zu VS Code oder PyCharm wechseln, ohne den aktuellen Arbeitskontext zu verlieren.

Dieses Setting ist für Windows, macOS und Linux dasselbe. Die passende Strategie ist daher eine eigenständige Desktop-App pro Desktop-Plattform, aber aus derselben Codebasis.

### Nicht eigenes Setting: Mobile Kurzansicht

Eine mobile Kurzansicht wäre ein anderes Setting, erfüllt aber nur einen Randnutzen. Code lesen, Debugger bedienen, lokale Python-Interpreter nutzen und Git-Diffs prüfen sind auf Smartphone/Tablet deutlich schwächer als am Desktop. Für diesen Randnutzen reicht GitHub, ein mobiler Editor oder eine Notiz-App; PythonBox braucht dafür keine eigene Companion-App.

## Plattformentscheidungen

| Plattform | Entscheidung | Begründung |
|---|---|---|
| Windows | Primärplattform | Aktuelle Entwicklung, PyInstaller-EXE, Batch-Start und GitHub-Release sind bereits darauf ausgerichtet. |
| macOS | Source-Smoke P1 | PySide6 und die Kernlogik sind grundsätzlich portabel; externe Editorpfade, Terminalstart und Dateidialoge müssen geprüft werden. |
| Linux | Source-Smoke P1 | PySide6 und Python-Ausführung sind geeignet; `xdg-open`, Terminalstart, Git-Integration und Linter-Erkennung brauchen einen sauberen Smoke-Test. |
| Web/PWA | Nicht-Ziel | Browser kann lokale Interpreter, PDB, Git und externe Editor-Brücken nicht gleichwertig bedienen. |
| Android | Nicht-Ziel | Der Kernnutzen ist Desktop-Entwicklung; mobiles Debugging lokaler Python-Dateien ist kein realistischer Hauptusecase. |
| iOS | Nicht-Ziel | Gleiche Einschränkung wie Android, zusätzlich eingeschränkter Dateisystem- und Prozesszugriff. |
| Windows Store | Nicht aktiv | Der Store bleibt wegen Nischenposition und VS-Code-Konkurrenz kein aktueller Kanal. GitHub bleibt der kanonische Release-Ort. |

## Austausch und Datenhaltung

Direkte Synchronisierung ist nicht erforderlich. Nutzer wechseln Plattformen über normale Projektdateien und Git. Snippets und Einstellungen sollten langfristig optional als einfache Datei exportierbar werden, aber das ist ein Desktop-Komfortthema und kein Companion-Sync.

Empfohlene Austauschwege:

- Quellcode: Git, ZIP oder normale Projektordner.
- Einstellungen: später optional `pythonbox-settings-v1.json`.
- Snippets: später optional `pythonbox-snippets-v1.json`.

## Umsetzungsplan

### P0 - Dokumentierte Plattformgrenze

- `PORTIERUNGSPLAN.md` als verbindliche Entscheidung pflegen.
- README und Changelog mit Desktop-only-Strategie synchron halten.
- Alte Aufgabenclaims zu CLI/REST bei Gelegenheit gegen den tatsächlichen Code prüfen, weil die aktuelle Codebasis vor allem eine GUI-App ist.

### P1 - macOS/Linux-Smokes

- Source-Start auf macOS testen: `python PythonBox_v8.py`.
- Source-Start auf Linux testen: `python PythonBox_v8.py`.
- Externe Prozessstarts prüfen: Ausführen, PDB, Linter, Git-Diff und externe Editor-Brücken.
- Pfad- und Terminalunterschiede dokumentieren, ohne neue Plattformordner anzulegen.

### P2 - Desktop-Portabilität verbessern

- Snippet- und Einstellungsdaten optional als JSON exportieren und importieren.
- Linter-Erkennung pro Plattform robuster dokumentieren.
- README um macOS-/Linux-Startnotizen ergänzen, sobald die Smokes bestätigt sind.

### P3 - Distribution

- Windows-GitHub-Release als Hauptartefakt beibehalten.
- macOS/Linux erst nach bestandenen Smokes als direkte GitHub-Artefakte prüfen.
- Windows Store nur neu bewerten, wenn es konkrete Nachfrage nach signierter Ein-Klick-Installation gibt.

## Nicht-Ziele

- Keine Android-App.
- Keine iOS-App.
- Keine Web/PWA-Version.
- Keine Companion-App.
- Keine direkte Cloud-Synchronisierung.
- Kein Store-Onboarding ohne neue Nachfrage.
