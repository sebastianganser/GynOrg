# GynOrg - Mitarbeiterverwaltung & Abwesenheitsplanung

Eine moderne, browserbasierte Mitarbeiterverwaltungsanwendung mit integrierter Abwesenheitsplanung, entwickelt mit FastAPI (Backend) und React (Frontend).

## 🚀 Quick Start (≤ 90 Sekunden)

### Voraussetzungen
- Python 3.11+
- Node.js 18+
- Poetry (für Python-Abhängigkeiten)

### 1. Repository klonen und Setup
```bash
git clone <repository-url>
cd GynOrg

# Environment-Datei kopieren und anpassen
cp .env.example .env
# Bearbeite .env mit deinen API-Schlüsseln
```

### 2. Backend starten
```bash
cd backend
poetry install
poetry run uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 3. Frontend starten (neues Terminal)
```bash
cd frontend
npm install
npm run dev
```

### 4. Anwendung öffnen
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

**Login-Daten:** `MGanser` / `M4rvelf4n`

## 📋 Funktionsübersicht

### ✅ **Vollständig implementiert:**

#### **Mitarbeiterverwaltung**
- **CRUD-Operationen**: Erstellen, Bearbeiten, Löschen von Mitarbeitern
- **Erweiterte Suchfunktion**: Suche nach Name und Position
- **Intelligente Filter**: Status-Filter (Aktiv/Inaktiv/Alle)
- **Flexible Sortierung**: Sortierung nach allen Spalten (Name, Position, Einstellungsdatum, Status)
- **Responsive Design**: Optimiert für Desktop und Mobile
- **Mitarbeiterdaten**:
  - Name und Position
  - Einstellungsdatum
  - Urlaubsanspruch (Tage pro Jahr)
  - Aktiv/Inaktiv Status

#### **Benutzeroberfläche**
- **Moderne UI**: shadcn/ui Komponenten mit TailwindCSS
- **Responsive Layout**: Kollabierbare Sidebar-Navigation
- **Modal-Dialoge**: Für Erstellen, Bearbeiten und Löschen
- **Intuitive Navigation**: Klare Menüstruktur
- **Visuelles Feedback**: Status-Indikatoren und Hover-Effekte

#### **Authentifizierung & Sicherheit**
- **JWT-basierte Authentifizierung**: Sichere Token-Verwaltung
- **Single-User System**: Hardcoded Admin-Benutzer
- **Automatische Session-Verwaltung**: Token-Refresh und Logout
- **Sichere API-Kommunikation**: CORS-konfiguriert

### 🟡 **Vorbereitet/In Entwicklung:**
- **Abwesenheitsverwaltung**: Navigation vorhanden, Implementierung folgt
- **Einstellungen**: Grundstruktur vorhanden
- **Kalenderansicht**: Geplant für Abwesenheitsübersicht

### 📅 **Geplante Features:**
- Urlaubsplanung und -genehmigung
- Krankheitstage-Verwaltung
- Kalenderansicht für Abwesenheiten
- Berichtsfunktionen und Statistiken
- Backup/Export-Funktionalität

## 🏗️ Technische Architektur

### **Frontend (React/TypeScript)**
```
frontend/src/
├── components/
│   ├── ui/                    # shadcn/ui Basis-Komponenten
│   │   ├── button.tsx         # Button-Komponente
│   │   ├── table.tsx          # Tabellen-Komponente
│   │   └── modal.tsx          # Modal-Dialog
│   ├── CreateEmployeeForm.tsx # Mitarbeiter erstellen
│   ├── EditEmployeeForm.tsx   # Mitarbeiter bearbeiten
│   ├── DeleteEmployeeDialog.tsx # Lösch-Bestätigung
│   ├── EmployeeList.tsx       # Mitarbeiterliste mit Such-/Filterfunktionen
│   ├── LoginForm.tsx          # Anmelde-Formular
│   ├── Layout.tsx             # Haupt-Layout
│   ├── Sidebar.tsx            # Navigation
│   └── Header.tsx             # Kopfzeile
├── pages/
│   └── Employees.tsx          # Mitarbeiter-Hauptseite
├── services/
│   ├── authService.ts         # Authentifizierung
│   ├── employeeService.ts     # Mitarbeiter-API
│   └── config.ts              # Konfiguration
├── hooks/
│   └── useEmployees.ts        # React Query Hooks
├── types/
│   └── employee.ts            # TypeScript Typen
└── utils/                     # Hilfsfunktionen
```

### **Backend (FastAPI/Python)**
```
backend/app/
├── api/v1/endpoints/
│   ├── auth.py               # Authentifizierung-Endpoints
│   └── employees.py          # Mitarbeiter-API-Endpoints
├── core/
│   ├── auth.py               # JWT-Token-Management
│   ├── config.py             # App-Konfiguration
│   └── database.py           # Datenbankverbindung
├── models/
│   └── employee.py           # SQLModel Datenmodelle
├── services/
│   ├── llm_service.py        # AI-Integration (vorbereitet)
│   ├── context7_client.py    # Context7-Integration
│   └── taskmaster_client.py  # Taskmaster-Integration
└── main.py                   # FastAPI App
```

## 🛠️ Technologie-Stack

### **Core Technologies**
- **Backend**: FastAPI 0.104+, SQLModel, SQLite, bcrypt
- **Frontend**: React 18, TypeScript 5, Vite 4
- **UI Framework**: TailwindCSS 3, shadcn/ui, Lucide Icons
- **State Management**: React Query (TanStack Query)
- **Authentication**: JWT Tokens, bcrypt Hashing

### **Development Tools**
- **Package Management**: Poetry (Python), npm (Node.js)
- **Code Quality**: ESLint, TypeScript Strict Mode
- **Build Tools**: Vite (Frontend), uvicorn (Backend)
- **API Documentation**: FastAPI Swagger/OpenAPI

### **AI/ML Integration (Vorbereitet)**
- **OpenRouter**: Claude AI für erweiterte Funktionen
- **Perplexity AI**: Research und aktuelle Informationen
- **Context7**: Dokumentations-Integration
- **Taskmaster**: Task-Management-Integration

## 🔧 Entwicklung

### **Backend-Entwicklung**
```bash
cd backend

# Abhängigkeiten installieren
poetry install

# Entwicklungsserver starten
poetry run uvicorn main:app --reload

# Tests ausführen
poetry run pytest

# Code-Qualität prüfen
poetry run black .
poetry run isort .
poetry run flake8
```

### **Frontend-Entwicklung**
```bash
cd frontend

# Abhängigkeiten installieren
npm install

# Entwicklungsserver starten
npm run dev

# Build für Produktion
npm run build

# Code-Qualität prüfen
npm run lint
npm run lint:fix
```

### **Datenbank-Management**
```bash
# Datenbank-Schema anzeigen
cd backend
poetry run python -c "from app.core.database import engine; from sqlmodel import SQLModel; SQLModel.metadata.create_all(engine)"

# Datenbank zurücksetzen (Entwicklung)
rm -f data/gynorg.db
poetry run python -c "from app.core.database import create_db_and_tables; create_db_and_tables()"
```

## 🧪 Testing & Qualitätssicherung

### **Manuelle Tests**
```bash
# Backend API testen
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "MGanser", "password": "M4rvelf4n"}'

# Frontend-Funktionen testen
# 1. Login mit MGanser/M4rvelf4n
# 2. Mitarbeiter erstellen/bearbeiten/löschen
# 3. Such- und Filterfunktionen testen
# 4. Responsive Design prüfen
```

### **Automatisierte Tests (Geplant)**
```bash
# Backend Tests
cd backend
poetry run pytest -v

# Frontend Tests
cd frontend
npm run test

# E2E Tests
npm run test:e2e
```

## 🔐 Sicherheit & Konfiguration

### **Authentifizierung**
- **Single User System**: Hardcoded Benutzer `MGanser`
- **Passwort**: Bcrypt-Hash von `M4rvelf4n`
- **JWT Tokens**: 30 Minuten Gültigkeit
- **Automatischer Logout**: Bei Token-Ablauf

### **API-Konfiguration**
Erforderliche Umgebungsvariablen in `.env`:
```bash
# AI-Services (Optional)
OPENROUTER_API_KEY=your_openrouter_key
PERPLEXITY_API_KEY=your_perplexity_key

# Backend-Konfiguration
SECRET_KEY=your_secret_key
DEBUG=true
CORS_ORIGINS=http://localhost:3000
```

### **CORS-Konfiguration**
```python
# Entwicklung: localhost:3000
# Produktion: Ihre Domain
```

## 📊 API-Dokumentation

### **Authentifizierung**
- `POST /api/v1/auth/login` - Benutzer-Login
- `POST /api/v1/auth/logout` - Benutzer-Logout

### **Mitarbeiterverwaltung**
- `GET /api/v1/employees` - Alle Mitarbeiter abrufen
- `POST /api/v1/employees` - Neuen Mitarbeiter erstellen
- `GET /api/v1/employees/{id}` - Mitarbeiter-Details abrufen
- `PUT /api/v1/employees/{id}` - Mitarbeiter aktualisieren
- `DELETE /api/v1/employees/{id}` - Mitarbeiter löschen

### **System**
- `GET /health` - Health Check
- `GET /` - API-Info

### **Interaktive Dokumentation**
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🚀 Deployment

### **Lokale Produktion**
```bash
# Frontend Build
cd frontend
npm run build

# Backend für Produktion
cd backend
poetry run uvicorn main:app --host 0.0.0.0 --port 8000

# Statische Dateien servieren
# Frontend-Build in backend/static/ kopieren
```

### **Docker Compose (Unraid / Production)**
Das Projekt bietet eine fertige `docker-compose.yml` zur einfachen Bereitstellung.

```bash
# Projekt klonen
git clone https://github.com/sebastianganser/GynOrg
cd GynOrg

# Backend .env anpassen oder Variablen im compose-File setzen
# WICHTIG: Die DATABASE_URL in der docker-compose.yml ggf. auf deine externe Postgres DB anpassen!

# Container bauen und im Hintergrund starten
docker-compose up -d --build

# Logs einsehen
docker-compose logs -f
```

Nach dem Start ist das Frontend über Port `80` und das Backend via Port `8000` erreichbar.

## 📈 Roadmap

### **Version 1.1 (Nächste Schritte)**
- [ ] Abwesenheitsverwaltung implementieren
- [ ] Kalenderansicht für Abwesenheiten
- [ ] Urlaubsanträge und Genehmigungen
- [ ] Krankheitstage-Tracking

### **Version 1.2 (Erweiterte Features)**
- [ ] Berichtsfunktionen und Statistiken
- [ ] Export-Funktionalität (PDF, Excel)
- [ ] Backup/Restore-System
- [ ] E-Mail-Benachrichtigungen

### **Version 2.0 (Zukunft)**
- [ ] Multi-User-System
- [ ] Rollen und Berechtigungen
- [ ] Team-Management
- [ ] Mobile App

## 🤝 Entwicklung & Beitragen

### **Code-Standards**
- **Python**: PEP 8, Type Hints, Docstrings
- **TypeScript**: Strict Mode, ESLint, Prettier
- **Commits**: Conventional Commits Format
- **Komponenten**: Funktionale React-Komponenten mit Hooks

### **Entwicklungsworkflow**
1. Feature Branch erstellen
2. Implementierung mit Tests
3. Code Review
4. Merge nach Approval

## 🆘 Troubleshooting

### **Häufige Probleme**

**Backend startet nicht:**
```bash
# Port bereits belegt?
lsof -i :8000
# Abhängigkeiten installiert?
cd backend && poetry install
```

**Frontend Build-Fehler:**
```bash
# Node Modules neu installieren
rm -rf node_modules package-lock.json
npm install
```

**Login funktioniert nicht:**
```bash
# Korrekte Anmeldedaten verwenden:
# Benutzername: MGanser
# Passwort: M4rvelf4n
```

**API-Verbindung fehlgeschlagen:**
```bash
# Backend läuft auf Port 8000?
curl http://localhost:8000/health
# CORS-Konfiguration prüfen
```

## 📞 Support & Dokumentation

- **API-Dokumentation**: http://localhost:8000/docs
- **Entwickler-Dokumentation**: `/docs` Verzeichnis
- **Issues**: GitHub Issues für Bug Reports
- **Code-Beispiele**: Siehe `/examples` (geplant)

---

**Entwickelt mit ❤️ für effiziente Mitarbeiterverwaltung und Abwesenheitsplanung**

*Letzte Aktualisierung: Januar 2025*
