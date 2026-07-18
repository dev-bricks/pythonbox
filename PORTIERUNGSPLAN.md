# Portierungsplan - PythonBox v8

Stand: 2026-07-19

## Bedingungsprüfung

Ein zentraler Portierungsplan war nicht vorhanden. Es gab nur Hinweise in README, AUFGABEN und der Windows-Store-Pipeline. Daher wurde Pfad B ausgeführt: Plan neu erstellen und Aufgaben ergänzen.

## Kurzentscheidung

PythonBox bleibt eine Desktop-App. Sinnvoll sind Windows als Hauptplattform sowie macOS und Linux als Source-Smoke-Ziele aus derselben PySide6-Codebasis. Android, iOS und Web/PWA sind keine aktuellen Ziele, weil die wichtigsten Usecases lokale Dateien, lokale Python-Interpreter, Git, Linter, Debugger und externe Editor-Brücken brauchen.

Ein Companion ist ebenfalls kein sinnvoller nächster Schritt. Der Nutzen der App liegt im direkten Bearbeiten und Ausführen lokaler Python-Dateien; ein mobiler oder browserbasierter Begleiter würde nur einen kleinen Ausschnitt abdecken und die eigentliche IDE-Erfahrung nicht verbessern.

## Automations- und Schnittstellen-Gate (2026-07-19)

**Entscheidung: No-Go für eine REST- oder JSON-RPC-Schnittstelle im aktuellen
Produktscope.** Die vorhandene lokale Prozess-CLI deckt die belegten
Automationsfälle ab. Ein dauerhaft laufender Server würde Authentisierung,
Pfad- und Prozessfreigaben sowie einen zusätzlichen Lebenszyklus benötigen,
ohne dass dafür ein Produktbedarf belegt ist.

| Oberfläche | Ist-Stand | Grenze |
|---|---|---|
| `--open <datei>`, `--open=<datei>`, `<datei>` | implementiert; GUI öffnet die Datei beim Start | lokaler Dateipfad, Nutzerprozess |
| `--theme <theme>` | implementiert; Theme-Override für den GUI-Start | kein Headless-Theme-Dienst |
| `--lint <datei>` | implementiert; headless, stdout, Exitcodes 0/1/2 | eine lokale Datei, kein Server |
| `--run <datei> [argumente]` | implementiert; aktueller Interpreter, Exitcode des Kindprozesses | explizit gestartete lokale Datei; optionartige Argumente nach `--` |
| unbekannte Qt-Argumenttokens | im GUI-Modus an `QApplication` weitergereicht | werttragende Optionen als ein Token, z. B. `-style=fusion` |
| REST/JSON-RPC/OpenAPI/Agentensteuerung | nicht implementiert und nicht behauptet | bewusstes Nicht-Ziel |

Eine Neubewertung braucht einen konkreten, dokumentierten Usecase, den die
Prozess-CLI nicht erfüllt, sowie eine eigene Produkt- und Security-Freigabe.
Erst ein positives Folge-Gate darf loopback-only Binding, standardmäßig
aktivierte Authentisierung, Operations-Allowlist, erlaubte Pfadwurzeln,
Prozess-/Timeout-Grenzen, Logging ohne Secrets und Start-/Stop-Lebenszyklus
planen. Dieses Gate erzeugt keinen Server- oder Schema-Code.

## Windows-Store-Nachfrage-Gate (2026-07-19)

**Entscheidung: No-Go; zurückgestellt.** Der aktuelle Readback zeigt im
öffentlichen Repository 0 Issues insgesamt und damit keinen Store-, MSIX-,
Signierungs- oder Ein-Klick-Installationswunsch. Die kanonische
`WINDOWS_STORE_PIPELINE.md` führt PythonBox weiterhin als GitHub-only, und es
liegt kein separater Nutzerbeleg für Store-Nachfrage vor. Aus diesem Gate wird
kein Store-Artefakt erzeugt.

Eine Neubewertung wird erst durch eine konkrete externe Anfrage mit benanntem
Installationsnutzen ausgelöst. Dann ist ein eigener Folgeplan für Packaging,
Store-Identität, Zertifikat/Signierung, MSIX, WACK, Support- und
Datenschutzmaterialien sowie die weiterhin geltende GitHub-Release-Linie
erforderlich; Partner-Center-Upload und Veröffentlichung bleiben außerhalb
dieses Gates.

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
| Windows Store | No-Go / zurückgestellt | Readback 2026-07-19: 0 Repository-Issues und kein externer Nachfragebeleg; die Pipeline führt PythonBox weiter als GitHub-only. Neubewertung nur nach konkreter Nachfrage. |

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
- [x] Alte Aufgabenclaims zu CLI/REST gegen den tatsächlichen Code geprüft (2026-06-05, CLI-Stand 2026-06-19/27 synchronisiert): `--open`, `--lint`, `--theme` und `--run` sind real vorhanden; REST/OpenAPI/Fernsteuerung bleiben Nicht-Ziel bzw. Zukunfts-Scope.

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
- [x] Windows-Store-Nachfrage-Gate am 2026-07-19 geprüft: 0 Repository-Issues, kein externer Nachfragebeleg, daher No-Go/zurückgestellt und kein Store-Artefakt erzeugt. Nur nach konkreter Nachfrage mit eigenem Packaging-/Identitäts-/Zertifikats-/WACK-/Support-/Datenschutz-Folgeplan neu öffnen.

## Nicht-Ziele

- Keine Android-App.
- Keine iOS-App.
- Keine Web/PWA-Version.
- Keine Companion-App.
- Keine direkte Cloud-Synchronisierung.
- Kein Store-Onboarding ohne neue Nachfrage.
