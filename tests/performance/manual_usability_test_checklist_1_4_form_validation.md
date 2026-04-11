# Manual Usability Test Checklist 1.4: Formular-Validierung

**Test Phase:** 1.4 - Detaillierte Formular-Validierung  
**Fokus:** Eingabe-Validierung im CreateEmployeeForm  
**Datum:** 31.01.2025  
**Tester:** Maria  

## Bewertungssystem
- **Status:** ✅ Erfolgreich | ❌ Fehlgeschlagen | ⚠️ Problematisch | 🔧 Behoben
- **Rating:** 1 (sehr schlecht) - 5 (sehr gut)

---

## 1. EMAIL-VALIDIERUNG (VERBESSERT)

### Test 1.1: Email-Validierung - Doppelte Punkte
**Ziel:** Überprüfung der verbesserten Email-Validierung

**Schritte:**
1. Formular öffnen
2. Email eingeben: `test..test@domain.com`
3. Formular absenden versuchen

**Erwartetes Verhalten:**
- ❌ Formular wird nicht abgesendet
- ✅ Spezifische Fehlermeldung: "E-Mail-Adresse darf keine aufeinanderfolgenden Punkte enthalten"
- ✅ Email-Feld wird rot umrandet

**Status:** 🔧 **BEHOBEN** (Implementierung abgeschlossen)
**Ergebnis:** Verbesserte Validierung implementiert
**Notizen:** Spezifische Fehlermeldungen für verschiedene Email-Fehlertypen

### Test 1.2: Email-Validierung - Fehlende TLD
**Schritte:**
1. Email eingeben: `test@domain`
2. Formular absenden versuchen

**Erwartetes Verhalten:**
- ❌ Formular wird nicht abgesendet
- ✅ Fehlermeldung: "Domain muss eine Top-Level-Domain enthalten (z.B. .com, .de)"

**Status:** 🔧 **BEHOBEN**
**Ergebnis:** ⏳ Ausstehend (manuelle Verifikation)

### Test 1.3: Email-Validierung - Fehlender lokaler Teil
**Schritte:**
1. Email eingeben: `@domain.com`
2. Formular absenden versuchen

**Erwartetes Verhalten:**
- ❌ Formular wird nicht abgesendet
- ✅ Fehlermeldung: "E-Mail-Adresse benötigt einen Benutzernamen vor dem @"

**Status:** 🔧 **BEHOBEN**
**Ergebnis:** ⏳ Ausstehend (manuelle Verifikation)

---

## 2. DATUM-VALIDIERUNG (VERBESSERT)

### Test 2.1: Einstellungsdatum - Zukünftige Daten (VERBESSERT)
**Ziel:** Überprüfung der flexibleren Einstellungsdatum-Validierung

**Schritte:**
1. Formular öffnen
2. Einstellungsdatum eingeben: Datum in 6 Monaten
3. Formular absenden

**Erwartetes Verhalten:**
- ✅ Formular wird erfolgreich abgesendet
- ✅ Keine Fehlermeldung
- ✅ Unterstützt vorbereitende Personalarbeit

**Status:** 🔧 **BEHOBEN** (Zukünftige Daten bis 1 Jahr erlaubt)
**Ergebnis:** ⏳ Ausstehend (manuelle Verifikation)

### Test 2.2: Einstellungsdatum - Zu weit in der Zukunft
**Schritte:**
1. Einstellungsdatum eingeben: Datum in 2 Jahren
2. Formular absenden versuchen

**Erwartetes Verhalten:**
- ❌ Formular wird nicht abgesendet
- ✅ Fehlermeldung: "Einstellungsdatum darf maximal 1 Jahr in der Zukunft liegen"

**Status:** 🔧 **BEHOBEN**
**Ergebnis:** ⏳ Ausstehend (manuelle Verifikation)

### Test 2.3: Geburtsdatum - Zukunftsdaten
**Schritte:**
1. Geburtsdatum eingeben: Datum in der Zukunft
2. Formular absenden versuchen

**Erwartetes Verhalten:**
- ❌ Formular wird nicht abgesendet
- ✅ Fehlermeldung: "Geburtsdatum darf nicht in der Zukunft liegen"

**Status:** ✅ **UNVERÄNDERT** (korrekte Validierung beibehalten)
**Ergebnis:** ⏳ Ausstehend (manuelle Verifikation)

---

## 3. PFLICHTFELDER-VALIDIERUNG

### Test 3.1: Vorname - Pflichtfeld
**Schritte:**
1. Formular öffnen
2. Vorname leer lassen
3. Andere Pflichtfelder ausfüllen
4. Formular absenden versuchen

**Erwartetes Verhalten:**
- ❌ Formular wird nicht abgesendet
- ✅ Fehlermeldung: "Vorname ist erforderlich"
- ✅ Vorname-Feld wird rot umrandet

**Status:** ⏳ Ausstehend
**Ergebnis:** 
**Notizen:**

### Test 3.2: Nachname - Pflichtfeld
**Schritte:**
1. Nachname leer lassen
2. Andere Pflichtfelder ausfüllen
3. Formular absenden versuchen

**Erwartetes Verhalten:**
- ❌ Formular wird nicht abgesendet
- ✅ Fehlermeldung: "Nachname ist erforderlich"

**Status:** ⏳ Ausstehend
**Ergebnis:** 
**Notizen:**

### Test 3.3: Email - Pflichtfeld
**Schritte:**
1. Email leer lassen
2. Andere Pflichtfelder ausfüllen
3. Formular absenden versuchen

**Erwartetes Verhalten:**
- ❌ Formular wird nicht abgesendet
- ✅ Fehlermeldung: "E-Mail ist erforderlich"

**Status:** ⏳ Ausstehend
**Ergebnis:** 
**Notizen:**

### Test 3.4: Bundesland - Pflichtfeld
**Schritte:**
1. Bundesland nicht auswählen (falls möglich)
2. Andere Pflichtfelder ausfüllen
3. Formular absenden versuchen

**Erwartetes Verhalten:**
- ❌ Formular wird nicht abgesendet
- ✅ Fehlermeldung: "Bundesland ist erforderlich"

**Status:** ⏳ Ausstehend
**Ergebnis:** 
**Notizen:**

---

## 4. OPTIONALE FELDER

### Test 4.1: Titel - Optional
**Schritte:**
1. Titel leer lassen
2. Alle Pflichtfelder ausfüllen
3. Formular absenden

**Erwartetes Verhalten:**
- ✅ Formular wird erfolgreich abgesendet
- ✅ Mitarbeiter wird ohne Titel erstellt

**Status:** ⏳ Ausstehend
**Ergebnis:** 
**Notizen:**

### Test 4.2: Position - Optional
**Schritte:**
1. Position leer lassen
2. Alle Pflichtfelder ausfüllen
3. Formular absenden

**Erwartetes Verhalten:**
- ✅ Formular wird erfolgreich abgesendet
- ✅ Mitarbeiter wird ohne Position erstellt

**Status:** ⏳ Ausstehend
**Ergebnis:** 
**Notizen:**

### Test 4.3: Geburtsdatum - Optional
**Schritte:**
1. Geburtsdatum leer lassen
2. Alle Pflichtfelder ausfüllen
3. Formular absenden

**Erwartetes Verhalten:**
- ✅ Formular wird erfolgreich abgesendet
- ✅ Mitarbeiter wird ohne Geburtsdatum erstellt

**Status:** ⏳ Ausstehend
**Ergebnis:** 
**Notizen:**

---

## 5. FELDLÄNGEN-VALIDIERUNG

### Test 5.1: Position - Maximallänge
**Schritte:**
1. Position eingeben: Text mit 101 Zeichen
2. Formular absenden versuchen

**Erwartetes Verhalten:**
- ❌ Formular wird nicht abgesendet
- ✅ Fehlermeldung: "Position darf maximal 100 Zeichen lang sein"

**Status:** ⏳ Ausstehend
**Ergebnis:** 
**Notizen:**

### Test 5.2: Vorname - Maximallänge
**Schritte:**
1. Vorname eingeben: Text mit 51 Zeichen
2. Formular absenden versuchen

**Erwartetes Verhalten:**
- ❌ Eingabe wird auf 50 Zeichen begrenzt (maxLength Attribut)
- ✅ Formular kann abgesendet werden

**Status:** ⏳ Ausstehend
**Ergebnis:** 
**Notizen:**

---

## ZUSAMMENFASSUNG DER VERBESSERUNGEN

### ✅ Implementierte Verbesserungen:
1. **Email-Validierung:** Spezifische Fehlermeldungen für verschiedene Fehlertypen
2. **Einstellungsdatum:** Zukünftige Daten bis 1 Jahr erlaubt

### ⏳ Ausstehende Tests:
1. Manuelle Verifikation der Email-Verbesserungen
2. Manuelle Verifikation der Datum-Verbesserungen
3. Vollständige Pflichtfeld-Tests
4. Optionale Feld-Tests
5. Feldlängen-Tests

### 🎯 Nächste Schritte:
1. **Sofort:** Manuelle Tests der implementierten Verbesserungen
2. **Dann:** Vollständige Durchführung der Tests 3.1-5.2
3. **Abschließend:** Dokumentation der Ergebnisse

---

**Datum der Erstellung:** 31.01.2025  
**Status:** 🔧 Teilweise implementiert, Tests ausstehend
