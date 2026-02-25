# Manual Usability Test Checklist 1: Core Workflow Testing

**Test Phase:** 1 von 4  
**Fokus:** Basis-Funktionalität der Employee Data Model Restructure  
**Datum:** 31.01.2025  
**Tester:** Maria

## Bewertungssystem
- **Status:** ✅ Erfolgreich | ❌ Fehlgeschlagen | ⚠️ Problematisch
- **Rating:** 1 (sehr schlecht) - 5 (sehr gut)
- **Kommentare:** Detaillierte Beschreibung von Problemen oder Verbesserungsvorschlägen

---

## 1. SYSTEM-START UND LOGIN

### 1.1 Anwendung starten
**Aufgabe:** Backend und Frontend starten, Login-Seite aufrufen

**Schritte:**
1. Backend starten: `cd backend && python -m uvicorn app.main:app --reload`
2. Frontend starten: `cd frontend && npm run dev`
3. Browser öffnen: `http://localhost:5173`
4. Login-Seite sollte im Split-Screen Layout erscheinen

**Erwartetes Ergebnis:** 
- Beide Services starten ohne Fehler
- Login-Seite lädt vollständig
- Split-Screen Layout ist korrekt dargestellt

**Test-Ergebnis:**
- Status: ⬜ ✅ | ❌ | ⚠️
- Rating: ⬜ 1 | 2 | 3 | 4 | 5
- Kommentare: ________________________________

### 1.2 Login-Prozess
**Aufgabe:** Mit Benutzer "MGanser" einloggen

**Schritte:**
1. Username: `MGanser` eingeben
2. Password: `password123` eingeben
3. "Anmelden" Button klicken
4. Weiterleitung zur Hauptanwendung

**Erwartetes Ergebnis:**
- Login erfolgreich
- Weiterleitung zur Employee-Liste
- Sidebar-Navigation sichtbar

**Test-Ergebnis:**
- Status: ⬜ ✅ | ❌ | ⚠️
- Rating: ⬜ 1 | 2 | 3 | 4 | 5
- Kommentare: ________________________________

---

## 2. MITARBEITER ERSTELLEN (NEUE FELDER)

### 2.1 Neuen Mitarbeiter anlegen
**Aufgabe:** Mitarbeiter mit allen neuen Stammdaten-Feldern erstellen

**Schritte:**
1. "Neuer Mitarbeiter" Button klicken
2. Formular mit folgenden Daten ausfüllen:
   - **Vorname:** Max
   - **Nachname:** Mustermann
   - **Email:** max.mustermann@example.com
   - **Telefon:** +49 123 456789
   - **Abteilung:** IT
   - **Position:** Software Developer
   - **Bundesland:** Bayern
   - **Einstellungsdatum:** 01.01.2024
   - **Gehalt:** 55000
   - **Wochenstunden:** 40
   - **Status:** Aktiv
3. "Speichern" klicken

**Erwartetes Ergebnis:**
- Alle neuen Felder sind verfügbar
- Bundesland-Dropdown zeigt alle 16 Bundesländer
- Validierung funktioniert korrekt
- Mitarbeiter wird erfolgreich erstellt
- Weiterleitung zur Mitarbeiterliste

**Test-Ergebnis:**
- Status: ✅ ✅ | ❌ | ⚠️
- Rating: ✅ 1 | 2 | 3 | 4 | 5
- Kommentare: Alle neuen Felder funktionieren einwandfrei. Bundesland-Dropdown zeigt alle 16 deutschen Bundesländer korrekt an. Formular-Validierung arbeitet zuverlässig.

### 2.2 Formular-Validierung testen
**Aufgabe:** Ungültige Eingaben testen

**Schritte:**
1. Neues Formular öffnen
2. Ungültige Email eingeben: `invalid-email`
3. Negatives Gehalt eingeben: `-1000`
4. Speichern versuchen

**Erwartetes Ergebnis:**
- Validierungsfehler werden angezeigt
- Formular wird nicht abgesendet
- Fehlermeldungen sind verständlich

**Test-Ergebnis:**
- Status: ✅ ✅ | ❌ | ⚠️
- Rating: ✅ 1 | 2 | 3 | 4 | 5
- Kommentare: Email-Validierung und Datum-Validierung funktionieren perfekt. Ungültige Emails werden erkannt, Fehlermeldungen sind klar und verständlich. Formular wird bei Fehlern nicht abgesendet.

---

## 3. MITARBEITER BEARBEITEN UND LÖSCHEN

### 3.1 Mitarbeiter bearbeiten
**Aufgabe:** Bestehenden Mitarbeiter bearbeiten

**Schritte:**
1. Mitarbeiter aus Liste auswählen
2. "Bearbeiten" Button klicken
3. Folgende Änderungen vornehmen:
   - Position ändern zu: "Senior Developer"
   - Gehalt erhöhen auf: 65000
   - Bundesland ändern zu: "Nordrhein-Westfalen"
4. "Speichern" klicken

**Erwartetes Ergebnis:**
- Formular wird mit aktuellen Daten vorausgefüllt
- Änderungen werden korrekt gespeichert
- Aktualisierte Daten in Liste sichtbar

**Test-Ergebnis:**
- Status: ⬜ ✅ | ❌ | ⚠️
- Rating: ⬜ 1 | 2 | 3 | 4 | 5
- Kommentare: ________________________________

### 3.2 Mitarbeiter löschen
**Aufgabe:** Mitarbeiter löschen mit Bestätigung

**Schritte:**
1. Mitarbeiter auswählen
2. "Löschen" Button klicken
3. Bestätigungsdialog erscheint
4. "Ja, löschen" bestätigen

**Erwartetes Ergebnis:**
- Bestätigungsdialog wird angezeigt
- Nach Bestätigung wird Mitarbeiter gelöscht
- Mitarbeiter verschwindet aus Liste

**Test-Ergebnis:**
- Status: ⬜ ✅ | ❌ | ⚠️
- Rating: ⬜ 1 | 2 | 3 | 4 | 5
- Kommentare: ________________________________

---

## 4. URLAUBSANSPRÜCHE VERWALTEN (CRUD)

### 4.1 Urlaubsanspruch erstellen
**Aufgabe:** Neuen Urlaubsanspruch für Mitarbeiter anlegen

**Schritte:**
1. Mitarbeiter-Detail-Ansicht öffnen
2. "Urlaubsanspruch hinzufügen" klicken
3. Daten eingeben:
   - **Jahr:** 2024
   - **Urlaubstage:** 30
   - **Übertragene Tage:** 5
   - **Genommene Tage:** 10
4. "Speichern" klicken

**Erwartetes Ergebnis:**
- Urlaubsanspruch wird erstellt
- Berechnung der verbleibenden Tage korrekt
- Anzeige in Mitarbeiter-Detail aktualisiert

**Test-Ergebnis:**
- Status: ⬜ ✅ | ❌ | ⚠️
- Rating: ⬜ 1 | 2 | 3 | 4 | 5
- Kommentare: ________________________________

### 4.2 Urlaubsanspruch bearbeiten
**Aufgabe:** Bestehenden Urlaubsanspruch ändern

**Schritte:**
1. Urlaubsanspruch auswählen
2. "Bearbeiten" klicken
3. Genommene Tage auf 15 erhöhen
4. "Speichern" klicken

**Erwartetes Ergebnis:**
- Änderungen werden gespeichert
- Verbleibende Tage werden neu berechnet
- Anzeige wird aktualisiert

**Test-Ergebnis:**
- Status: ⬜ ✅ | ❌ | ⚠️
- Rating: ⬜ 1 | 2 | 3 | 4 | 5
- Kommentare: ________________________________

### 4.3 Urlaubsanspruch löschen
**Aufgabe:** Urlaubsanspruch entfernen

**Schritte:**
1. Urlaubsanspruch auswählen
2. "Löschen" klicken
3. Bestätigung geben

**Erwartetes Ergebnis:**
- Bestätigungsdialog erscheint
- Urlaubsanspruch wird gelöscht
- Anzeige wird aktualisiert

**Test-Ergebnis:**
- Status: ⬜ ✅ | ❌ | ⚠️
- Rating: ⬜ 1 | 2 | 3 | 4 | 5
- Kommentare: ________________________________

---

## 5. SUCH- UND FILTERFUNKTIONEN

### 5.1 Mitarbeiter suchen
**Aufgabe:** Suchfunktion in Mitarbeiterliste testen

**Schritte:**
1. Mehrere Testmitarbeiter erstellen (falls nicht vorhanden)
2. Suchfeld verwenden:
   - Nach Vorname suchen: "Max"
   - Nach Email suchen: "mustermann"
   - Nach Abteilung suchen: "IT"
3. Suchergebnisse prüfen

**Erwartetes Ergebnis:**
- Suche funktioniert in Echtzeit
- Relevante Ergebnisse werden angezeigt
- Keine Ergebnisse = entsprechende Meldung

**Test-Ergebnis:**
- Status: ⬜ ✅ | ❌ | ⚠️
- Rating: ⬜ 1 | 2 | 3 | 4 | 5
- Kommentare: ________________________________

### 5.2 Filter anwenden
**Aufgabe:** Filterfunktionen testen

**Schritte:**
1. Filter nach Abteilung anwenden
2. Filter nach Status anwenden
3. Filter nach Bundesland anwenden
4. Filter kombinieren

**Erwartetes Ergebnis:**
- Filter funktionieren einzeln
- Kombinierte Filter funktionieren
- Filter können zurückgesetzt werden

**Test-Ergebnis:**
- Status: ⬜ ✅ | ❌ | ⚠️
- Rating: ⬜ 1 | 2 | 3 | 4 | 5
- Kommentare: ________________________________

---

## GESAMTBEWERTUNG CORE WORKFLOWS

### Zusammenfassung
**Gesamtstatus:** ⬜ ✅ Alle Tests erfolgreich | ❌ Kritische Fehler | ⚠️ Kleinere Probleme

**Gesamtrating:** ⬜ 1 | 2 | 3 | 4 | 5

**Kritische Probleme:**
_________________________________

**Verbesserungsvorschläge:**
_________________________________

**Positive Aspekte:**
_________________________________

---

## NÄCHSTE SCHRITTE
Nach Abschluss dieser Tests folgt:
**Test-Checkliste 2: Responsive Design Testing**

**Datum der Fertigstellung:** _____________  
**Unterschrift Tester:** _____________
