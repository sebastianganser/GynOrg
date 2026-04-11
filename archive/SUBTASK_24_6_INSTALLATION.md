# Subtask 24.6 - Installationsanleitung

## Neue Dependencies installieren

Für die Team-Kalender-Funktionalität müssen folgende npm-Pakete installiert werden:

### 1. React-Big-Calendar

```bash
npm install react-big-calendar
```

**Version:** ^1.8.5  
**Zweck:** Haupt-Kalender-Komponente mit verschiedenen Ansichten

### 2. Moment.js

```bash
npm install moment
```

**Version:** ^2.29.4  
**Zweck:** Datum-Lokalisierung für deutsche Sprache

### Komplette Installation

Beide Pakete auf einmal installieren:

```bash
cd frontend
npm install react-big-calendar moment
```

### Verifizierung

Nach der Installation sollten die Pakete in `frontend/package.json` erscheinen:

```json
{
  "dependencies": {
    "react-big-calendar": "^1.8.5",
    "moment": "^2.29.4",
    // ... andere Dependencies
  }
}
```

### TypeScript-Typen

Die TypeScript-Typen sind bereits in den Paketen enthalten:
- `react-big-calendar` enthält eigene Type-Definitionen
- `moment` enthält eigene Type-Definitionen

Keine zusätzlichen `@types/*` Pakete erforderlich.

### CSS-Import

Die CSS-Dateien werden automatisch in den Komponenten importiert:

```typescript
// In TeamCalendar.tsx
import 'react-big-calendar/lib/css/react-big-calendar.css';
import '../styles/team-calendar.css';
```

### Entwicklungsserver neu starten

Nach der Installation den Entwicklungsserver neu starten:

```bash
npm run dev
```

### Troubleshooting

**Problem:** Module nicht gefunden  
**Lösung:** 
```bash
rm -rf node_modules package-lock.json
npm install
```

**Problem:** TypeScript-Fehler  
**Lösung:** 
```bash
npm run type-check
```

**Problem:** CSS wird nicht geladen  
**Lösung:** Vite-Cache löschen
```bash
rm -rf node_modules/.vite
npm run dev
```

## Fertig!

Nach erfolgreicher Installation sollte die Kalender-Seite unter `/calendar` verfügbar sein.
