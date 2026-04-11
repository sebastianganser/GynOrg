# 🧪 Manual Test Anleitung - Prioritäre Tests

**Datum:** 01.08.2025  
**Fokus:** Verifikation der gestrigen Usability-Verbesserungen  

## 🎯 **Was du testen sollst:**

### **PRIORITÄT 1: Gestrige Verbesserungen verifizieren**

#### ✅ **Email-Validierung (Tests 1.1-1.3):**

**Test 1.1: Doppelte Punkte in Email**
1. Formular öffnen → "Neuen Mitarbeiter hinzufügen"
2. Email eingeben: `test..test@domain.com`
3. Formular absenden versuchen
4. **ERWARTE:** Fehlermeldung "E-Mail-Adresse darf keine aufeinanderfolgenden Punkte enthalten"

**Test 1.2: Fehlende Top-Level-Domain**
1. Email eingeben: `test@domain`
2. Formular absenden versuchen  
3. **ERWARTE:** Fehlermeldung "Domain muss eine Top-Level-Domain enthalten"

**Test 1.3: Fehlender Benutzername**
1. Email eingeben: `@domain.com`
2. Formular absenden versuchen
3. **ERWARTE:** Fehlermeldung "E-Mail-Adresse benötigt einen Benutzernamen vor dem @"

#### ✅ **Einstellungsdatum-Validierung (Tests 2.1-2.2):**

**Test 2.1: Zukünftiges Datum (6 Monate) - NEUE FUNKTION!**
1. Einstellungsdatum eingeben: **Datum in 6 Monaten** (z.B. 01.02.2026)
2. Alle anderen Pflichtfelder ausfüllen
3. Formular absenden
4. **ERWARTE:** ✅ **Formular wird akzeptiert** (Das ist neu!)

**Test 2.2: Zu weit zukünftiges Datum (2 Jahre)**
1. Einstellungsdatum eingeben: **Datum in 2 Jahren** (z.B. 01.08.2027)
2. Formular absenden versuchen  
3. **ERWARTE:** ❌ Fehlermeldung "Einstellungsdatum darf maximal 1 Jahr in der Zukunft liegen"

### **PRIORITÄT 2: Grundfunktionen testen**

#### **Pflichtfelder-Validierung (Tests 3.1-3.4):**

**Test 3.1: Vorname leer**
1. Vorname leer lassen, andere Pflichtfelder ausfüllen
2. **ERWARTE:** "Vorname ist erforderlich"

**Test 3.2: Nachname leer**
1. Nachname leer lassen, andere Pflichtfelder ausfüllen
2. **ERWARTE:** "Nachname ist erforderlich"

**Test 3.3: Email leer**
1. Email leer lassen, andere Pflichtfelder ausfüllen
2. **ERWARTE:** "E-Mail ist erforderlich"

**Test 3.4: Bundesland nicht gewählt**
1. Bundesland nicht auswählen, andere Pflichtfelder ausfüllen
2. **ERWARTE:** "Bundesland ist erforderlich"

---

## 🚀 **Vorbereitung (5 Min):**

### **1. System starten:**
```bash
# Backend starten
python start.py

# Frontend starten (neues Terminal)
cd frontend
npm run dev
```

### **2. Browser öffnen:**
- URL: `http://localhost:5173`
- Login durchführen
- Zu "Mitarbeiter" navigieren
- "Neuen Mitarbeiter hinzufügen" klicken

---

## 📝 **Dokumentation:**

### **Für jeden Test notiere:**
- **Status:** ✅ Erfolgreich / ❌ Fehlgeschlagen / ⚠️ Problematisch
- **Tatsächliche Fehlermeldung** (falls abweichend von erwartet)
- **Screenshots** bei Problemen
- **Besonderheiten** oder unerwartetes Verhalten

### **Beispiel-Dokumentation:**
```
Test 1.1: ✅ Erfolgreich
- Email: test..test@domain.com
- Fehlermeldung: "E-Mail-Adresse darf keine aufeinanderfolgenden Punkte enthalten"
- Verhalten: Formular wurde korrekt blockiert

Test 2.1: ❌ Fehlgeschlagen  
- Datum: 01.02.2026 (6 Monate)
- Problem: Formular wurde abgelehnt statt akzeptiert
- Fehlermeldung: "Einstellungsdatum darf nicht in der Zukunft liegen"
- → Backend-Fix funktioniert nicht!
```

---

## ⚠️ **Besonders wichtig:**

**Tests 2.1 & 2.2** sind die **kritischsten**, da hier gestern das Backend geändert wurde:
- **Test 2.1** muss ✅ **funktionieren** (zukünftige Daten bis 1 Jahr erlaubt)
- **Test 2.2** muss ❌ **fehlschlagen** (Daten > 1 Jahr blockiert)

Falls diese Tests nicht wie erwartet funktionieren, ist das Backend-Fix nicht korrekt implementiert!

---

## 🎯 **Zeitaufwand:**
- **Vorbereitung:** 5 Min
- **Priorität 1 Tests:** 15-20 Min  
- **Priorität 2 Tests:** 10-15 Min
- **Dokumentation:** 5-10 Min
- **Total:** ~30-45 Min

---

**Viel Erfolg beim Testen! 🚀**

*Bei Problemen oder Fragen: Entwicklungsteam kontaktieren*
