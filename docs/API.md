# API Spezifikation (REST)

Alle Endpunkte befinden sich unter dem Präfix `/api/v1/`.

## Authentifizierung
- `POST /auth/login`
- `POST /auth/logout`

## Mitarbeiter & Personalverwaltung
- `GET, POST /employees`
- `GET, PUT, DELETE /employees/{id}`
- `GET, POST, PUT, DELETE /job-positions` - Verwaltung der Berufsbezeichnungen

## Abwesenheiten & Urlaub
- `GET, POST /absences`
- `PUT, DELETE /absences/{id}`
- `GET, POST, PUT, DELETE /vacation-allowances` - Jährliche Urlaubskontingente inkl. Resturlaub
- `GET, POST, PUT, DELETE /vacation-entitlements` - Historische Urlaubsansprüche

## Reports & Auswertungen
- `GET /reports/summary`
- `GET /reports/employee/{id}`

## System, Kalender & Synchronisation
- `GET, POST, PUT, DELETE /absence-types`
- `GET, POST, PUT, DELETE /holidays`
- `GET /federal-states` - Liste der Bundesländer
- `GET, PUT /calendar-settings`
- `GET, PUT /system-settings`
- `GET /holiday-admin/*` - Verwaltung der Feiertags-Logik
- `GET, POST /admin-sync/*` - Admin-Synchronisation (z.B. für externe Schulferien-APIs)

## Zusatzmodul: Auslastungsstatistik
- `GET, POST, PUT, DELETE /auslastung/*` - Endpunkte für Belegungsdaten, Stationsverwaltung und Tages-Tags.

## GOÄ Rechnungsmodul (Geplant / In Entwicklung)
- `GET /goae/suche?q={suchbegriff}`
- `GET /patienten/suche?q={name}`
- `GET, POST, PUT /rechnungen`
- `POST /rechnungen/{id}/pdf` - PDF Generierung und Download
- `GET, PUT /einstellungen/praxis`

## Server Health
- `GET /health` - Health Check der gesamten Anwendung
- `GET /` - API-Info

> Alle Endpunkte folgen REST-Konventionen und nutzen HTTP Statuscodes (200/201/400/401 usw.). Interaktive Dokumentation über Swagger UI unter `/docs`.
