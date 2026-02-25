# Multi-Year Holiday Management System

## Übersicht

Das Multi-Year Holiday Management System ist eine umfassende Lösung für die automatische Verwaltung von Feiertagen über mehrere Jahre hinweg. Es kombiniert automatischen Import beim Serverstart mit einem monatlichen Scheduler und bietet Admin-APIs für manuelle Kontrolle.

## Architektur

### Komponenten

1. **HolidayStartupService** (Task 22.2)
   - Automatischer Import beim Serverstart
   - Erkennt fehlende Jahre
   - Importiert Feiertage für konfigurierten Zeitraum

2. **HolidayScheduler** (Task 22.3)
   - Monatlicher automatischer Import
   - APScheduler-basiert
   - Job-Ausführungshistorie

3. **Holiday Admin API** (Task 22.6)
   - 8 REST-Endpoints für manuelle Kontrolle
   - Authentifizierung erforderlich
   - Import-Trigger und Scheduler-Steuerung

4. **HolidayService**
   - Basis-Service für Feiertage-Import
   - Nutzt feiertage-api.de
   - Unterstützt alle 16 Bundesländer

## Konfiguration

### Umgebungsvariablen (.env)

```env
# Holiday Management Configuration
HOLIDAY_IMPORT_ENABLED=true
HOLIDAY_SCHEDULER_ENABLED=true
HOLIDAY_YEARS_PAST=1
HOLIDAY_YEARS_FUTURE=2
HOLIDAY_SCHEDULER_CRON=0 2 1 * *
HOLIDAY_SCHEDULER_TIMEZONE=Europe/Berlin
```

### Konfigurationsparameter

| Parameter | Typ | Default | Beschreibung |
|-----------|-----|---------|--------------|
| `HOLIDAY_IMPORT_ENABLED` | bool | true | Aktiviert/deaktiviert Startup-Import |
| `HOLIDAY_SCHEDULER_ENABLED` | bool | true | Aktiviert/deaktiviert monatlichen Scheduler |
| `HOLIDAY_YEARS_PAST` | int | 1 | Jahre in der Vergangenheit |
| `HOLIDAY_YEARS_FUTURE` | int | 2 | Jahre in der Zukunft |
| `HOLIDAY_SCHEDULER_CRON` | str | "0 2 1 * *" | Cron-Expression (1. des Monats, 2:00 Uhr) |
| `HOLIDAY_SCHEDULER_TIMEZONE` | str | "Europe/Berlin" | Zeitzone für Scheduler |

## Startup-Verhalten

### Automatischer Import beim Start

Wenn `HOLIDAY_IMPORT_ENABLED=true`:

1. **Server startet** → `HolidayStartupService` wird initialisiert
2. **Prüfung**: Welche Jahre fehlen in der Datenbank?
3. **Import**: Fehlende Jahre werden importiert
4. **Ergebnis**: 
   - `imported` - Neue Daten wurden importiert
   - `up_to_date` - Alle Daten vorhanden

### Beispiel-Ablauf

```
Server Start → HolidayStartupService
  ↓
Prüfe Jahre: 2024, 2025, 2026, 2027
  ↓
Fehlend: 2026, 2027
  ↓
Import 2026: ✓ 150 Feiertage
Import 2027: ✓ 148 Feiertage
  ↓
Ergebnis: {"action": "imported", "total_imported": 298}
```

## Scheduler-Operation

### Monatlicher Import

Wenn `HOLIDAY_SCHEDULER_ENABLED=true`:

1. **Scheduler startet** automatisch mit Server
2. **Job geplant**: Jeden 1. des Monats um 2:00 Uhr
3. **Ausführung**: Import für alle konfigurierten Jahre
4. **Logging**: Jede Ausführung wird protokolliert

### Job-Ausführung

```python
# Automatisch jeden Monat
Job: monthly_holiday_import
Trigger: cron(day=1, hour=2, minute=0)
Timezone: Europe/Berlin

# Ausführung
→ HolidayStartupService.ensure_holiday_data()
→ Ergebnis wird geloggt
→ Historie wird gespeichert
```

## Admin API

### Authentifizierung

Alle Endpoints erfordern Admin-Authentifizierung:

```bash
# Login
POST /api/v1/auth/login
{
  "username": "admin",
  "password": "your_password"
}

# Response
{
  "access_token": "eyJ...",
  "token_type": "bearer"
}

# Verwendung
Authorization: Bearer eyJ...
```

### Endpoints

#### 1. Manueller Import

**POST** `/api/v1/holidays/admin/import`

Triggert manuellen Import im Hintergrund.

```bash
curl -X POST http://localhost:8000/api/v1/holidays/admin/import \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "start_year": 2024,
    "end_year": 2026,
    "federal_states": ["BAYERN", "NORDRHEIN_WESTFALEN"]
  }'
```

**Response:**
```json
{
  "success": true,
  "message": "Manual holiday import started successfully",
  "action": "trigger_import",
  "performed_at": "2025-10-27T14:30:00",
  "performed_by": "admin"
}
```

#### 2. Import-Status

**GET** `/api/v1/holidays/admin/import/status`

Prüft Status des laufenden Imports.

```bash
curl http://localhost:8000/api/v1/holidays/admin/import/status \
  -H "Authorization: Bearer TOKEN"
```

**Response:**
```json
{
  "is_running": false,
  "last_import": "2025-10-27T14:00:00",
  "last_result": {
    "action": "imported",
    "total_imported": 150
  }
}
```

#### 3. Scheduler-Status

**GET** `/api/v1/holidays/admin/scheduler/status`

Zeigt aktuellen Scheduler-Status.

```bash
curl http://localhost:8000/api/v1/holidays/admin/scheduler/status \
  -H "Authorization: Bearer TOKEN"
```

**Response:**
```json
{
  "status": "RUNNING",
  "running": true,
  "jobs_count": 1,
  "next_run_time": "2025-11-01T02:00:00",
  "configuration": {
    "cron_expression": "0 2 1 * *",
    "timezone": "Europe/Berlin"
  }
}
```

#### 4. Scheduler starten

**POST** `/api/v1/holidays/admin/scheduler/start`

```bash
curl -X POST http://localhost:8000/api/v1/holidays/admin/scheduler/start \
  -H "Authorization: Bearer TOKEN"
```

#### 5. Scheduler stoppen

**POST** `/api/v1/holidays/admin/scheduler/stop`

```bash
curl -X POST http://localhost:8000/api/v1/holidays/admin/scheduler/stop \
  -H "Authorization: Bearer TOKEN"
```

#### 6. Manuellen Job triggern

**POST** `/api/v1/holidays/admin/scheduler/trigger`

Führt Import sofort aus (außerhalb des Zeitplans).

```bash
curl -X POST http://localhost:8000/api/v1/holidays/admin/scheduler/trigger \
  -H "Authorization: Bearer TOKEN"
```

#### 7. Jobs auflisten

**GET** `/api/v1/holidays/admin/scheduler/jobs`

```bash
curl http://localhost:8000/api/v1/holidays/admin/scheduler/jobs \
  -H "Authorization: Bearer TOKEN"
```

#### 8. Ausführungshistorie

**GET** `/api/v1/holidays/admin/scheduler/executions?limit=50`

```bash
curl http://localhost:8000/api/v1/holidays/admin/scheduler/executions?limit=50 \
  -H "Authorization: Bearer TOKEN"
```

## Troubleshooting

### Problem: Keine Feiertage werden importiert

**Lösung:**
1. Prüfe Konfiguration: `HOLIDAY_IMPORT_ENABLED=true`
2. Prüfe Logs: `backend/logs/app.log`
3. Teste API manuell: `curl https://feiertage-api.de/api/?jahr=2025`

### Problem: Scheduler läuft nicht

**Lösung:**
1. Prüfe: `HOLIDAY_SCHEDULER_ENABLED=true`
2. Prüfe Status: `GET /api/v1/holidays/admin/scheduler/status`
3. Starte manuell: `POST /api/v1/holidays/admin/scheduler/start`

### Problem: Doppelte Feiertage

**Lösung:**
- System verhindert Duplikate automatisch
- Falls doch vorhanden: Datenbank-Constraint prüfen
- Unique constraint: `(date, name, federal_state, data_source)`

### Problem: Fehlende Jahre

**Lösung:**
1. Manueller Import: `POST /api/v1/holidays/admin/import`
2. Oder: Server neu starten (Startup-Import)
3. Prüfe `HOLIDAY_YEARS_PAST` und `HOLIDAY_YEARS_FUTURE`

## Migration vom alten System

### Schritt 1: Alte Daten sichern

```sql
-- Backup erstellen
SELECT * FROM holidays 
WHERE data_source = 'FEIERTAGE_API' 
INTO OUTFILE '/backup/holidays.csv';
```

### Schritt 2: Konfiguration setzen

```env
HOLIDAY_IMPORT_ENABLED=true
HOLIDAY_SCHEDULER_ENABLED=true
HOLIDAY_YEARS_PAST=1
HOLIDAY_YEARS_FUTURE=2
```

### Schritt 3: Server starten

```bash
python start.py
```

System importiert automatisch alle benötigten Jahre.

### Schritt 4: Validierung

```bash
# Prüfe Import
curl http://localhost:8000/api/v1/holidays/admin/import/status \
  -H "Authorization: Bearer TOKEN"

# Prüfe Scheduler
curl http://localhost:8000/api/v1/holidays/admin/scheduler/status \
  -H "Authorization: Bearer TOKEN"
```

## Best Practices

### 1. Monitoring

- Prüfe regelmäßig `/scheduler/executions`
- Überwache Logs auf Fehler
- Setze Alerts für fehlgeschlagene Imports

### 2. Backup

- Sichere `holidays` Tabelle vor großen Änderungen
- Teste Imports zuerst in Entwicklungsumgebung

### 3. Performance

- Standard-Konfiguration ist optimiert
- Bei vielen Bundesländern: Import kann 30-60s dauern
- Scheduler läuft nachts (2:00 Uhr) → keine User-Impact

### 4. Sicherheit

- Admin-API nur für Admins zugänglich
- Verwende starke Passwörter
- Rotiere Tokens regelmäßig

## Technische Details

### Datenbank-Schema

```sql
CREATE TABLE holidays (
    id INTEGER PRIMARY KEY,
    date DATE NOT NULL,
    name VARCHAR(255) NOT NULL,
    federal_state VARCHAR(50),
    data_source VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(date, name, federal_state, data_source)
);
```

### API-Quelle

- **URL**: https://feiertage-api.de
- **Bundesländer**: Alle 16 deutschen Bundesländer
- **Jahre**: Unbegrenzt (API-abhängig)
- **Rate Limit**: Keine bekannten Limits

### Logging

Alle Operationen werden geloggt:

```
[2025-10-27 14:00:00] INFO: Starting holiday import for years 2024-2027
[2025-10-27 14:00:05] INFO: Imported 150 holidays for year 2024
[2025-10-27 14:00:10] INFO: Import completed: 600 total holidays
```

## Support

Bei Problemen:
1. Prüfe diese Dokumentation
2. Prüfe Logs in `backend/logs/`
3. Teste mit Validierungsskripten: `python validate_task_22_*.py`
4. Kontaktiere Entwickler-Team

---

**Version:** 1.0  
**Letzte Aktualisierung:** 27.10.2025  
**Task:** 22.7 - Multi-Year Holiday Management Documentation
