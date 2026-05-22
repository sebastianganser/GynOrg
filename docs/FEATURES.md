# Funktionen & Features

## 1. Kernfunktionen
- **Benutzer-Authentifizierung:** Einfaches Login für den Chefarzt. Nach erfolgreicher Anmeldung Zugriff auf alle Bereiche (keine Rollen/Rechte-Verwaltung).
- **Mitarbeiterverwaltung:** Erfassung von Mitarbeiterdaten. Die Positionen (`job_positions`) werden als separate Stammdaten gepflegt.
- **Erweiterte Urlaubsverwaltung:** Das System trennt zwischen historischem Urlaubsanspruch (`vacation_entitlement`, z.B. 30 Tage ab 2020) und dem konkreten jährlichen Kontingent (`vacation_allowance`), in das auch Resturlaubstage aus dem Vorjahr einfließen.
- **Abwesenheitsverwaltung:** Planen und Verwalten von Abwesenheiten. Alle Einträge werden vom Chefarzt vorgenommen und gelten direkt als genehmigt.
- **Abwesenheitstypen:** Vordefinierte Abwesenheitsarten wie Urlaub, Krankmeldung, Fortbildung mit Farbcodes.
- **Konfliktprüfung:** Prüfung auf Überschneidungen beim Eintragen von Abwesenheiten.

## 2. System- & Kalender-Administration
- **Feiertage & Schulferien:** Das System verwaltet regionale Feiertage nach Bundesländern (`federal_states`).
- **Admin-Sync:** Eine integrierte Synchronisations-Engine (inkl. Admin-UI `AdminSync.tsx`), um Schulferien oder externe Kalenderdaten automatisiert über APIs (z.B. Mehr-Schulferien-API) abzugleichen.

## 3. Benutzeroberfläche
- **Team-Kalenderansicht:** Grafische Kalenderübersicht (Gantt-Chart-ähnlich). Umschaltbar zwischen Monats- und Wochenansicht mit Scroll/Zoom-Funktion. Visuelle Kennzeichnung von Wochenenden, Feiertagen und Schulferien.
- **Dashboard (Übersichtsseite):** Kacheln mit Kennzahlen, Resturlaubsübersicht pro Mitarbeiter, Schnellzugriff.
- **Berichte und Auswertungen / Berichtansicht:**
  - **Jahresabrechnung (Bericht):** Paginiertes, druckoptimiertes Layout ("Urlaubsabrechnung") zur Darstellung der Jahres-Urlaubsbilanz jedes Mitarbeiters, vorbereitet für PDF-Export.
  - **Statistiken:** Visuelle Diagramme und interaktive Filter (generelle Jahresübersicht, Abwesenheitsverteilung).
- **Einstellungen:** Zentrale Verwaltung von Systemeinstellungen, Praxisdaten und Kalender-Konfigurationen.

## 4. Erweiterungsmodule
- **Auslastungsstatistik:** System zur tagesbasierten Auslastungsmessung der Stationen (siehe [FEATURE_AUSLASTUNG.md](./FEATURE_AUSLASTUNG.md)).
- **GOÄ-Rechnungsmodul:** Privatpatientenabrechnung mit eRechnung/ZUGFeRD und EPC-QR-Code. Ein eigener Scraper (`goae_scraper.py`) ermöglicht den automatisierten Import der Ziffern (siehe [FEATURE_GOAE.md](./FEATURE_GOAE.md)).
