# AI Guidelines & Development Rules (GynOrg)

Diese Datei enthält die wichtigsten Regeln für KI-Assistenten (Claude, Cursor, etc.), die in diesem Projekt arbeiten.

## 1. Development Workflow & Taskmaster
- Für detaillierte Informationen zur Taskmaster-Nutzung siehe:
  - [DEV_WORKFLOW.md](./docs/DEV_WORKFLOW.md)
  - [TASKMASTER.md](./docs/TASKMASTER.md)
- Nutze das **Tagged Task Lists System** für komplexere Features, um Aufgabenkontexte isoliert voneinander zu halten (z. B. `feature-xyz`).
- Nutze den `research`-Befehl, um frisches Wissen und aktuelle Best Practices einzuholen.
- Halte die Task-Detail-Beschreibungen stets auf dem aktuellen Stand (`update_subtask`), um den iterativen Fortschritt zu dokumentieren.

## 2. Selbstverbesserung (Self-Improve)
- **Neue Patterns erkennen:** Wenn neue Architektur-Patterns, Bibliotheken oder Fehlerbehebungen standardisiert werden, dokumentiere diese.
- **Code Reviews:** Analysiere häufiges Feedback oder Fehler in der Codebase und halte dich in Zukunft an den korrigierten Stil.
- **Konsistenz:** Achte bei neuen Komponenten auf das etablierte Designsystem (Tailwind, shadcn/ui, Farben der GynOrg-App).

## 3. Dateistruktur & Dokumentation
- Es gelten strikte Vorgaben für die Dokumentation:
  - Hauptdokumentation: `README.md` und `claude.md` im Projektstamm.
  - Projektdokumentation: Alle weiteren Konzepte, Architekturentscheidungen und Module liegen modular aufgeteilt in `/docs`.
  - Namenskonvention in `/docs`: Ausschließlich Großbuchstaben für `.md`-Dateien (z. B. `ARCHITECTURE.md`, `FEATURES.md`).
- Achte auf saubere Referenzen zwischen den Dateien (Links relativ zum aktuellen Dokument).

## 4. UI & Code-Styling
- **Frontend:** React, TypeScript, TailwindCSS.
- **Backend:** FastAPI, Python, SQLModel.
- Nutze klare, aussagekräftige Commits und halte dich an das Single-Responsibility-Prinzip.
