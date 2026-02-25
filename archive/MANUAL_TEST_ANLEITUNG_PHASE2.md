# 🧪 Manual Test Anleitung - Phase 2: Pflichtfelder & Grundfunktionen

**Datum:** 01.08.2025  
**Status:** Phase 1 ✅ **ERFOLGREICH** abgeschlossen  
**Nächste Phase:** Pflichtfelder-Validierung und Grundfunktionen  

## ✅ **Phase 1 - ABGESCHLOSSEN:**
- **Email-Validierung:** Alle 3 Tests erfolgreich
- **Einstellungsdatum:** Beide Tests erfolgreich (neue 1-Jahr-Regel funktioniert!)

---

## 🎯 **Phase 2: Was du jetzt testen sollst**

**Server laufen bereits:** Backend (Port 8000) + Frontend (Port 3000) ✅  
**Browser:** `http://localhost:3000` (bereits geöffnet)

### **PRIORITÄT 2: Pflichtfelder-Validierung (Tests 3.1-3.4)**

#### **Test 3.1: Vorname - Pflichtfeld**
1. **Formular öffnen:** "Neuen Mitarbeiter hinzufügen"
2. **Vorname:** Leer lassen
3. **Andere Pflichtfelder ausfüllen:**
   - Nachname: `Mustermann`
   - Email: `test@example.com`
   - Bundesland: Beliebiges auswählen
4. **Formular absenden versuchen**
5. **ERWARTE:** ❌ Fehlermeldung "Vorname ist erforderlich"

#### **Test 3.2: Nachname - Pflichtfeld**
1. **Nachname:** Leer lassen
2. **Andere Pflichtfelder ausfüllen:**
   - Vorname: `Max`
   - Email: `test@example.com`
   - Bundesland: Beliebiges auswählen
3. **Formular absenden versuchen**
4. **ERWARTE:** ❌ Fehlermeldung "Nachname ist erforderlich"

#### **Test 3.3: Email - Pflichtfeld**
1. **Email:** Leer lassen
2. **Andere Pflichtfelder ausfüllen:**
   - Vorname: `Max`
   - Nachname: `Mustermann`
   - Bundesland: Beliebiges auswählen
3. **Formular absenden versuchen**
4. **ERWARTE:** ❌ Fehlermeldung "E-Mail ist erforderlich"

#### **Test 3.4: Bundesland - Pflichtfeld**
1. **Bundesland:** Nicht auswählen (Standard-Option lassen)
2. **Andere Pflichtfelder ausfüllen:**
   - Vorname: `Max`
   - Nachname: `Mustermann`
   - Email: `test@example.com`
3. **Formular absenden versuchen**
4. **ERWARTE:** ❌ Fehlermeldung "Bundesland ist erforderlich"

---

### **BONUS: Optionale Felder (Tests 4.1-4.3)**

#### **Test 4.1: Titel - Optional**
1. **Titel:** Leer lassen
2. **Alle Pflichtfelder ausfüllen:**
   - Vorname: `Max`
   - Nachname: `Mustermann`
   - Email: `test@example.com`
   - Bundesland: Beliebiges auswählen
3. **Formular absenden**
4. **ERWARTE:** ✅ Formular wird erfolgreich abgesendet

#### **Test 4.2: Position - Optional**
1. **Position:** Leer lassen
2. **Alle Pflichtfelder ausfüllen**
3. **Formular absenden**
4. **ERWARTE:** ✅ Formular wird erfolgreich abgesendet

#### **Test 4.3: Geburtsdatum - Optional**
1. **Geburtsdatum:** Leer lassen
2. **Alle Pflichtfelder ausfüllen**
3. **Formular absenden**
4. **ERWARTE:** ✅ Formular wird erfolgreich abgesendet

---

## 📝 **Dokumentation - Einfaches Format:**

### **Für jeden Test notiere:**
```
Test 3.1: [✅/❌/⚠️] 
Ergebnis: [Beschreibung]

Test 3.2: [✅/❌/⚠️]
Ergebnis: [Beschreibung]

...usw.
```

### **Beispiel:**
```
Test 3.1: ✅ Erfolgreich
Ergebnis: Fehlermeldung "Vorname ist erforderlich" erscheint korrekt

Test 3.2: ❌ Fehlgeschlagen  
Ergebnis: Keine Fehlermeldung, Formular wurde abgesendet
Problem: Nachname-Validierung funktioniert nicht!
```

---

## 🎯 **Zeitaufwand Phase 2:**
- **Pflichtfelder (Tests 3.1-3.4):** 10-15 Min
- **Optionale Felder (Tests 4.1-4.3):** 5-10 Min  
- **Dokumentation:** 5 Min
- **Total:** ~20-30 Min

---

## ⚠️ **Wichtige Hinweise:**

1. **Server laufen bereits** - keine neue Instanz starten!
2. **Browser-Tab beibehalten** - einfach weiter testen
3. **Bei jedem Test:** Formular neu öffnen (F5 oder neue Mitarbeiter-Seite)
4. **Fokus:** Pflichtfeld-Validierung ist wichtig für Datenqualität

---

## 🚀 **Nach Phase 2:**

Falls alle Tests erfolgreich sind, können wir zu **Phase 3** übergehen:
- **Responsive Design Testing** (verschiedene Bildschirmgrößen)
- **Error Handling & Edge Cases**

**Viel Erfolg bei Phase 2! 🎯**

*Melde dich mit den Ergebnissen, dann planen wir die nächsten Schritte.*
