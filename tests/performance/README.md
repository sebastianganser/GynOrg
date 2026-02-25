# Performance Test Suite - Phase 1

Automatisierte Performance Tests für das GynOrg Abwesenheitsplanungstool.

## Übersicht

Diese Test Suite implementiert **Task 17.13 - Performance & Usability Test - Phase 1: Automated Performance Tests**.

### Test-Kategorien

1. **API Load Testing** - Locust-basierte Last-Tests
2. **Database Performance** - Datenbankabfrage-Performance
3. **Frontend Performance** - Core Web Vitals und Bundle-Größe
4. **Memory & Resource Testing** - Speicher- und Ressourcenverbrauch

## Schnellstart

### 1. Setup Verifikation

```bash
cd tests/performance
python verify_test_setup.py
```

### 2. Performance Tests ausführen

```bash
python run_phase1_tests.py
```

### 3. Reports anzeigen

Reports werden automatisch generiert in:
- `tests/performance/reports/` - JSON und HTML Reports
- `tests/performance/logs/` - Detaillierte Logs
- `tests/performance/screenshots/` - Frontend Screenshots

## Konfiguration

### Environment Setup

1. **Backend starten:**
   ```bash
   cd backend
   python main.py
   ```

2. **Frontend starten:**
   ```bash
   cd frontend
   npm run dev
   ```

3. **Konfiguration anpassen** in `config.py`:
   ```python
   base_url = "http://localhost:8000"
   frontend_url = "http://localhost:5173"
   auth_username = "admin"
   auth_password = "admin123"
   ```

### Dependencies installieren

```bash
pip install -r requirements.txt
```

Benötigte Pakete:
- `requests` - HTTP Client
- `faker` - Test-Daten Generierung
- `locust` - Load Testing
- `psutil` - System Monitoring
- `playwright` - Frontend Testing

## Test-Daten Management

### Automatisches Cleanup

Die Tests führen automatisch ein **Pre-Cleanup** durch:

1. **Vor Test-Start:** Alle Test-Mitarbeiter werden gelöscht
2. **Nach Test-Ende:** Cleanup zur Wiederherstellung des ursprünglichen Zustands

### Erwartete Ergebnisse

- **Vor Tests:** 1 Standard-Mitarbeiter
- **Während Tests:** 101 Mitarbeiter (1 Standard + 100 Test)
- **Nach Tests:** 1 Standard-Mitarbeiter

### Manuelle Daten-Operationen

```python
from test_data_generator import TestDataGenerator

generator = TestDataGenerator()
generator.authenticate()

# Test-Daten erstellen
generator.generate_full_dataset(
    employee_count=100,
    vacation_entries_per_employee=2,
    cleanup_before=True
)

# Cleanup
generator.cleanup_test_data()
```

## Performance Targets

### API Performance
- **Response Time (95th percentile):** ≤ 300ms
- **Error Rate:** ≤ 1%
- **Peak Users:** ≥ 50 concurrent users

### Frontend Performance
- **Largest Contentful Paint (LCP):** ≤ 2.5s
- **Bundle Size:** ≤ 500KB
- **Performance Score:** ≥ 90/100

### Database Performance
- **Query Response Time:** ≤ 100ms (simple queries)
- **Large Dataset Queries:** ≤ 500ms
- **Concurrent Access:** Stable unter 10 parallelen Verbindungen

### Memory & Resources
- **Backend Memory:** ≤ 200MB peak
- **Frontend Memory:** ≤ 100MB peak
- **System CPU:** ≤ 80% average

## Test-Module

### 1. `run_phase1_tests.py`
Haupt-Test-Runner für alle Performance Tests.

**Features:**
- Vollständige Test-Suite Orchestrierung
- Automatisches Test-Daten Management
- Report-Generierung (JSON + HTML)
- Exit-Code basierte Erfolgs-/Fehler-Behandlung

### 2. `test_data_generator.py`
Test-Daten Generierung und Management.

**Features:**
- Realistische Mitarbeiter-Daten (Faker)
- Urlaubsansprüche mit korrekten Bundesland-Zuordnungen
- Pre-Cleanup für saubere Test-Starts
- Batch-Operations für Performance

### 3. `locustfile.py`
Load Testing Szenarien mit Locust.

**Szenarien:**
- Employee CRUD Operations
- Vacation Allowance Management
- Authentication Flows
- Mixed Workload Simulation

### 4. `db_performance.py`
Database Performance Testing.

**Tests:**
- Query Response Times
- Large Dataset Handling
- Concurrent Access Patterns
- Index Performance

### 5. `frontend_performance.py`
Frontend Performance mit Playwright.

**Metriken:**
- Core Web Vitals (LCP, FID, CLS)
- Bundle Size Analysis
- Loading Performance
- Memory Usage

### 6. `memory_monitor.py`
System Resource Monitoring.

**Monitoring:**
- Backend Memory Usage
- Frontend Memory Usage
- System CPU/Memory
- Memory Leak Detection

### 7. `config.py`
Zentrale Konfiguration für alle Tests.

**Konfiguriert:**
- API/Frontend URLs
- Authentication
- Performance Targets
- Load Test Parameter

## Troubleshooting

### Häufige Probleme

1. **Authentication Failed**
   ```bash
   # Prüfen ob Backend läuft
   curl http://localhost:8000/docs
   
   # Credentials in config.py prüfen
   ```

2. **Frontend nicht erreichbar**
   ```bash
   # Frontend starten
   cd frontend && npm run dev
   
   # URL in config.py prüfen
   ```

3. **Locust Import Error**
   ```bash
   pip install locust
   ```

4. **Playwright Browser fehlt**
   ```bash
   playwright install chromium
   ```

### Debug-Modus

Für detaillierte Logs:

```python
# In config.py
DEBUG = True
VERBOSE_LOGGING = True
```

### Test-Daten Probleme

```bash
# Manuelle Cleanup
python -c "
from test_data_generator import TestDataGenerator
gen = TestDataGenerator()
gen.authenticate()
gen.cleanup_test_data()
print('Cleanup complete')
"
```

## Reports

### JSON Report Struktur

```json
{
  "timestamp": "2025-01-24T14:30:00",
  "duration_seconds": 120.5,
  "all_tests_passed": true,
  "api_load_tests": {
    "passed": true,
    "summary": {
      "peak_users": 50,
      "avg_response_time": 150.5,
      "error_rate": 0.2
    }
  },
  "database_tests": { ... },
  "frontend_tests": { ... },
  "memory_tests": { ... }
}
```

### HTML Report

Interaktiver HTML Report mit:
- Übersichtliche Zusammenfassung
- Detaillierte Metriken
- Performance Target Vergleich
- Nächste Schritte

## Integration

### CI/CD Integration

```yaml
# GitHub Actions Beispiel
- name: Run Performance Tests
  run: |
    cd tests/performance
    python verify_test_setup.py
    python run_phase1_tests.py
  
- name: Upload Reports
  uses: actions/upload-artifact@v3
  with:
    name: performance-reports
    path: tests/performance/reports/
```

### Monitoring Integration

Reports können in Monitoring-Systeme integriert werden:
- JSON Format für automatische Auswertung
- Metriken für Trend-Analyse
- Alerts bei Performance-Verschlechterung

## Nächste Schritte

Nach erfolgreichem Abschluss von Phase 1:

1. **Phase 2:** Manual Usability Tests
2. **Detaillierte Test-Checklisten** für manuelle Tests
3. **User Experience Evaluation**
4. **Accessibility Testing**

## Support

Bei Problemen oder Fragen:
1. Prüfen Sie die Logs in `tests/performance/logs/`
2. Führen Sie `verify_test_setup.py` aus
3. Überprüfen Sie die Konfiguration in `config.py`
