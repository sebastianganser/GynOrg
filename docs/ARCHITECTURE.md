# Architektur & Systemübersicht

## 1. Systemübersicht
- **Ziel und Nutzerkreis:** Browserbasiertes Abwesenheitsplanungstool für einen einzelnen Nutzer (Chefarzt) zur Verwaltung der Abwesenheiten seines Teams. Mitarbeiter selbst haben keinen eigenen Zugang – alle Eingaben erfolgen ausschließlich durch den Chefarzt.
- **Einzelbenutzer-Betrieb:** Keine Rollen, Rechtevergaben oder Stellvertretungen im System. Der Chefarzt hat Vollzugriff auf alle Funktionen.
- **Einfaches Login:** Authentifizierung über einen einzigen Benutzeraccount (Chefarzt) mittels Benutzername/Passwort. Passwort wird sicher (gehasht) in der Datenbank gespeichert.
- **Kernmodule der Anwendung:** Übersichts-Dashboard, Team-Kalender und Berichtssektion. (Mitarbeiter-Verwaltungsseite zur Pflege der Personaldaten kommt hinzu).
- **Kein Benachrichtigungssystem:** Das System versendet keine Mails, da ein Genehmigungsworkflow im Tool nicht erforderlich ist.
- **Zukunftssicherheit:** Bereits auf Erweiterungen ausgelegt (z. B. Rechnungsmodul).

## 2. Technische Architektur
- **Client-Server-Struktur:** Trennung von Frontend und Backend. Das Frontend ist eine Single-Page Application (SPA), die über eine definierte API mit dem Backend kommuniziert.
- **Frontend:** Umsetzung mit React und TypeScript. Styling mit Tailwind CSS. Komponenten aus shadcn/ui.
- **State-Management:** Verwendung von React Query / Zustand.
- **Routing:** Client-seitiges Routing (React Router). Geschützte Routen verhindern unautorisierten Zugriff.
- **Backend:** Python mit FastAPI.
- **ORM & Datenbankzugriff:** SQLModel zur Abstraktion der Datenbank.
- **Datenbank:** PostgreSQL (produktiv) oder SQLite (Entwicklung).
- **Session-Handling:** JWT-Token (Authorization-Header).
- **Deployment & Containerisierung:** Docker-Betrieb. Docker-Compose orchestriert Backend, Frontend und DB als separate Services.
- **Konfiguration:** Environment-Variablen (`.env`).
- **Build/Run Automatisierung:** Scripts für Container-Build und Migrationen.

## 3. UI-Komponenten
- **Hauptnavigation:** Dashboard, Kalender, Mitarbeiter, Berichte, Einstellungen, Logout. (Neue Einträge wie Privatrechnungen werden modular ergänzt).
- **Login-Seite:** Einfaches Formular, Weiterleitung zum Dashboard.
- **Dashboard:** Info-Kacheln, Tabelle kommende Abwesenheiten, Quick-Action-Button.
- **Kalender-Komponente:** Scroll-/Zoomfähiger Gantt-Chart, Tooltip, Drag-and-Drop optional.
- **Mitarbeiterverwaltung:** Formular + Tabelle mit Aktionen.
- **Abwesenheits-Formular:** Datumsfelder, Dropdowns, Kommentar.
- **Berichte:** Interaktive Diagramme, Filter-Controls.
- **Responsive Design:** Sidebar collapsing.
- **Designsystem:** Einheitliche Farben (Sidebar `#1a1f2e`, Primär `#2563eb`), Icons, modulare Komponenten.

## 4. Erweiterbarkeit & Wartbarkeit
- **Modularität:** Rechnungsmodul, Multi-User, Benachrichtigungen, Tech-Updates – Architektur ist modular, ORM abstrahiert DB.
- **Wartbarkeit:** README, Coding Standards, klare Dokumentation.
- **Resümee:** Robustes Fundament, erfüllt aktuelle Anforderungen, zukunftssicher und erweiterbar.
