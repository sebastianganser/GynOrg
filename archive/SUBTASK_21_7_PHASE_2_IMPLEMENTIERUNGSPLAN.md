# 🚀 Subtask 21.7 Phase 2 - Implementierungsplan

**Datum:** 22. September 2025  
**Status:** Planungsphase  
**Ziel:** API-Endpoints & Frontend-Integration für Multi-Bundesland Employee-Profile System

## 📋 Übersicht Phase 2

Phase 2 baut auf der vollständig implementierten Backend-Infrastruktur aus Phase 1 auf und erstellt die API-Schnittstellen sowie Frontend-Komponenten für das Multi-Bundesland-System.

## 🎯 Hauptziele Phase 2

1. **REST-API-Endpoints** für Employee-Präferenzen-Management
2. **Frontend-Komponenten** für Präferenzen-Einstellungen
3. **Integration** in bestehende Employee-Profile
4. **Erweiterte Kalender-Features** mit Multi-Bundesland-Support
5. **Testing & Validation** der neuen Features

## 🏗️ Implementierungsschritte

### 1. Backend API-Endpoints (Priorität: Hoch)

#### 1.1 Employee Preferences API
```python
# backend/app/api/v1/endpoints/employee_preferences.py
GET    /api/v1/employees/{employee_id}/school-holiday-preferences
POST   /api/v1/employees/{employee_id}/school-holiday-preferences
PUT    /api/v1/employees/{employee_id}/school-holiday-preferences
DELETE /api/v1/employees/{employee_id}/school-holiday-preferences

# Bulk-Operationen
POST   /api/v1/employees/school-holiday-preferences/bulk-create-defaults
GET    /api/v1/employees/school-holiday-preferences/summary
GET    /api/v1/employees/school-holiday-preferences/statistics
```

#### 1.2 Preferences Options API
```python
GET    /api/v1/school-holiday-preferences/options
# Liefert: federal_states, vacation_types, notification_days_options
```

#### 1.3 Enhanced Holidays API
```python
# Erweiterte Holiday-Endpoints mit Präferenzen-Filterung
GET    /api/v1/employees/{employee_id}/holidays/filtered
GET    /api/v1/employees/{employee_id}/holidays/relevant
```

#### 1.4 Notifications API (Grundlage)
```python
# backend/app/api/v1/endpoints/school_holiday_notifications.py
GET    /api/v1/employees/{employee_id}/school-holiday-notifications
POST   /api/v1/employees/{employee_id}/school-holiday-notifications
PUT    /api/v1/school-holiday-notifications/{notification_id}
DELETE /api/v1/school-holiday-notifications/{notification_id}
```

### 2. Frontend-Komponenten (Priorität: Hoch)

#### 2.1 Employee Preferences Components
```typescript
// frontend/src/components/EmployeePreferences/
├── EmployeeSchoolHolidayPreferences.tsx     // Haupt-Komponente
├── FederalStateSelector.tsx                 // Multi-Select für Bundesländer
├── VacationTypeSelector.tsx                 // Checkbox-Gruppe für Ferientypen
├── NotificationSettings.tsx                 // Notification-Einstellungen
└── PreferencesPreview.tsx                   // Vorschau der Auswirkungen
```

#### 2.2 Enhanced Calendar Components
```typescript
// frontend/src/components/Calendar/
├── MultiStateCalendarView.tsx               // Erweiterte Kalender-Ansicht
├── FederalStateFilter.tsx                   // Bundesland-Filter
├── HolidayTypeFilter.tsx                    // Ferientyp-Filter
└── PersonalizedHolidayList.tsx             // Personalisierte Holiday-Liste
```

#### 2.3 Integration Components
```typescript
// Integration in bestehende Komponenten
├── EmployeeProfile.tsx                      // Erweitert um Preferences-Tab
├── AbsenceCalendar.tsx                      // Erweitert um Multi-State-Support
└── EmployeeForm.tsx                         // Erweitert um Preferences-Sektion
```

### 3. Frontend Services & Hooks (Priorität: Mittel)

#### 3.1 API Services
```typescript
// frontend/src/services/
├── employeePreferencesService.ts            // API-Calls für Präferenzen
├── enhancedHolidayService.ts               // Erweiterte Holiday-API-Calls
└── notificationService.ts                   // Notification-API-Calls
```

#### 3.2 React Hooks
```typescript
// frontend/src/hooks/
├── useEmployeePreferences.ts                // Hook für Präferenzen-Management
├── usePersonalizedHolidays.ts              // Hook für personalisierte Holidays
├── useFederalStateOptions.ts               // Hook für Bundesland-Optionen
└── useNotificationSettings.ts              // Hook für Notification-Settings
```

### 4. Enhanced Calendar Features (Priorität: Mittel)

#### 4.1 Multi-State Calendar View
- **Bundesland-Switcher**: Schneller Wechsel zwischen Bundesländern
- **Overlay-Modus**: Mehrere Bundesländer gleichzeitig anzeigen
- **Color-Coding**: Verschiedene Farben für verschiedene Bundesländer
- **Legend**: Legende für Bundesland-Zuordnung

#### 4.2 Advanced Filtering
- **Smart Filters**: Basierend auf Employee-Präferenzen
- **Quick Filters**: Vordefinierte Filter-Kombinationen
- **Custom Filters**: Benutzer-definierte Filter
- **Filter Persistence**: Gespeicherte Filter-Einstellungen

#### 4.3 Personalized Views
- **My Holidays**: Nur relevante Holidays für aktuellen User
- **Family View**: Holidays für Kinder-Bundesländer
- **Team View**: Holidays für Team-Mitglieder
- **Comparison View**: Vergleich verschiedener Bundesländer

### 5. Integration & Enhancement (Priorität: Mittel)

#### 5.1 Employee Profile Integration
```typescript
// Erweiterte Employee-Profile mit Preferences-Tab
interface EmployeeProfileTabs {
  basic: BasicInfo;
  preferences: SchoolHolidayPreferences;  // NEU
  absences: AbsenceHistory;
  vacation: VacationAllowances;
}
```

#### 5.2 Calendar Integration
```typescript
// Erweiterte AbsenceCalendar mit Multi-State-Support
interface CalendarProps {
  employeeId?: number;                     // Für personalisierte Ansicht
  federalStates?: string[];               // Multi-State-Anzeige
  showPersonalized?: boolean;             // Personalisierte Filterung
  allowStateSwitch?: boolean;             // Bundesland-Switcher
}
```

#### 5.3 Dashboard Integration
- **Preferences Widget**: Schnell-Einstellungen im Dashboard
- **Upcoming Holidays Widget**: Personalisierte nächste Holidays
- **Notification Center**: Zentrale Benachrichtigungen

## 📊 Technische Spezifikationen

### API-Design Patterns
```python
# Konsistente API-Struktur
@router.get("/employees/{employee_id}/school-holiday-preferences")
async def get_employee_preferences(
    employee_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> EmployeeSchoolHolidayPreferencesResponse:
    # Implementation mit Service-Layer
```

### Frontend State Management
```typescript
// Zustand-Management mit React Query
const useEmployeePreferences = (employeeId: number) => {
  return useQuery({
    queryKey: ['employee-preferences', employeeId],
    queryFn: () => employeePreferencesService.getPreferences(employeeId),
    staleTime: 5 * 60 * 1000, // 5 Minuten
  });
};
```

### Component Architecture
```typescript
// Modulare Komponenten-Struktur
interface EmployeeSchoolHolidayPreferencesProps {
  employeeId: number;
  onSave?: (preferences: Preferences) => void;
  onCancel?: () => void;
  readOnly?: boolean;
  showPreview?: boolean;
}
```

## 🎨 UI/UX Design Konzept

### 1. Preferences Settings Page
```
┌─────────────────────────────────────────┐
│ 🏠 Schulferien-Einstellungen           │
├─────────────────────────────────────────┤
│ Haupt-Bundesland: [NRW ▼]              │
│                                         │
│ Zusätzliche Bundesländer:               │
│ ☑ Bayern  ☑ Hessen  ☐ Berlin          │
│                                         │
│ Kinder-Bundesländer:                    │
│ ☑ Baden-Württemberg  ☐ Sachsen        │
│                                         │
│ Relevante Ferientypen:                  │
│ ☑ Sommerferien  ☑ Winterferien         │
│ ☑ Osterferien   ☐ Herbstferien         │
│                                         │
│ 🔔 Benachrichtigungen:                  │
│ ☑ Aktiviert  [14 Tage ▼] im Voraus    │
│                                         │
│ [Vorschau anzeigen] [Speichern]        │
└─────────────────────────────────────────┘
```

### 2. Enhanced Calendar View
```
┌─────────────────────────────────────────┐
│ 📅 Kalender - Personalisiert           │
├─────────────────────────────────────────┤
│ Bundesland: [Meine Einstellungen ▼]    │
│ Filter: [Alle ▼] [Schulferien ▼]       │
│                                         │
│     September 2025                      │
│ Mo Di Mi Do Fr Sa So                    │
│  1  2  3  4  5  6  7                   │
│  8  9 10 11 12 13 14                   │
│ 15 16 17 18 19 20 21                   │
│ 22 23 24 25 26 27 28                   │
│ 29 30                                   │
│                                         │
│ 🟦 NRW  🟨 Bayern  🟩 Hessen          │
└─────────────────────────────────────────┘
```

### 3. Employee Profile Integration
```
┌─────────────────────────────────────────┐
│ 👤 Mitarbeiter: Max Mustermann         │
├─────────────────────────────────────────┤
│ [Basis] [Präferenzen] [Abwesenheit]    │
│                                         │
│ 🏠 Schulferien-Präferenzen             │
│ ├─ Haupt-Bundesland: NRW               │
│ ├─ Zusätzliche: Bayern, Hessen         │
│ ├─ Kinder: Baden-Württemberg           │
│ └─ Benachrichtigungen: Aktiviert       │
│                                         │
│ [Bearbeiten]                            │
└─────────────────────────────────────────┘
```

## 🧪 Testing-Strategie

### 1. Backend API Tests
```python
# backend/test_employee_preferences_api.py
def test_create_employee_preferences()
def test_get_employee_preferences()
def test_update_employee_preferences()
def test_delete_employee_preferences()
def test_bulk_create_defaults()
def test_preferences_filtering()
```

### 2. Frontend Component Tests
```typescript
// frontend/src/test/EmployeePreferences.test.tsx
describe('EmployeeSchoolHolidayPreferences', () => {
  test('renders preferences form correctly');
  test('handles federal state selection');
  test('validates form inputs');
  test('saves preferences successfully');
});
```

### 3. Integration Tests
```typescript
// frontend/src/test/integration/preferences-integration.test.tsx
describe('Preferences Integration', () => {
  test('preferences affect calendar display');
  test('preferences persist across sessions');
  test('preferences sync with backend');
});
```

## 📈 Performance Considerations

### 1. Backend Optimizations
- **Caching**: Redis-Cache für häufig abgerufene Präferenzen
- **Database Indexing**: Optimierte Indizes für Präferenzen-Queries
- **Lazy Loading**: Präferenzen nur bei Bedarf laden

### 2. Frontend Optimizations
- **React Query**: Intelligentes Caching und Background-Updates
- **Code Splitting**: Lazy Loading für Preferences-Komponenten
- **Memoization**: React.memo für Performance-kritische Komponenten

### 3. API Optimizations
- **Batch Requests**: Mehrere Präferenzen in einem Request
- **Selective Loading**: Nur benötigte Felder übertragen
- **Compression**: GZIP-Kompression für API-Responses

## 🔄 Implementierungsreihenfolge

### Woche 1: Backend API Foundation
1. **Tag 1-2**: Employee Preferences API-Endpoints
2. **Tag 3**: Preferences Options API
3. **Tag 4**: Enhanced Holidays API
4. **Tag 5**: API-Tests und Dokumentation

### Woche 2: Frontend Components
1. **Tag 1-2**: Core Preferences Components
2. **Tag 3**: Calendar Enhancement Components
3. **Tag 4**: Integration Components
4. **Tag 5**: Component Tests

### Woche 3: Integration & Polish
1. **Tag 1-2**: Employee Profile Integration
2. **Tag 3**: Calendar Integration
3. **Tag 4**: End-to-End Testing
4. **Tag 5**: UI/UX Polish und Bug Fixes

## 🎯 Erfolgskriterien Phase 2

### Funktionale Kriterien
- ✅ Vollständige CRUD-API für Employee-Präferenzen
- ✅ Intuitive Frontend-Komponenten für Präferenzen-Management
- ✅ Nahtlose Integration in bestehende Employee-Profile
- ✅ Erweiterte Kalender-Funktionalität mit Multi-State-Support
- ✅ Personalisierte Holiday-Filterung basierend auf Präferenzen

### Technische Kriterien
- ✅ API-Response-Zeit < 200ms für Präferenzen-Abfragen
- ✅ Frontend-Komponenten laden < 1s
- ✅ 100% Test-Coverage für neue API-Endpoints
- ✅ 90% Test-Coverage für neue Frontend-Komponenten
- ✅ Responsive Design für alle Bildschirmgrößen

### Benutzerfreundlichkeit
- ✅ Intuitive Benutzeroberfläche ohne Schulung nutzbar
- ✅ Sofortige Vorschau der Präferenzen-Auswirkungen
- ✅ Konsistente UI/UX mit bestehender Anwendung
- ✅ Barrierefreie Bedienung (WCAG 2.1 AA)

## 🚀 Bereit für Implementierung

Phase 2 ist vollständig geplant und kann sofort implementiert werden. Die Grundlage aus Phase 1 bietet eine solide Basis für alle geplanten Features.

---

**Geplant von:** AI Assistant  
**Implementierungsstart:** Bereit  
**Geschätzte Dauer:** 3 Wochen  
**Nächster Schritt:** Backend API-Endpoints implementieren
