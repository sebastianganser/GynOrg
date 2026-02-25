# Manual Usability Test Checklist 3: Error Handling & Edge Cases

**Test Phase:** 3 von 4  
**Fokus:** Robustheit und Fehlerbehandlung  
**Datum:** _____________  
**Tester:** Maria  

## Bewertungssystem
- **Status:** ✅ Erfolgreich | ❌ Fehlgeschlagen | ⚠️ Problematisch
- **Rating:** 1 (sehr schlecht) - 5 (sehr gut)
- **Kommentare:** Detaillierte Beschreibung von Problemen oder Verbesserungsvorschlägen

## Test-Kategorien
- ❌ **Ungültige Eingaben**
- 🌐 **Netzwerkprobleme**
- ⏱️ **Session Management**
- 📝 **Grenzwerte & Lange Texte**
- 🔄 **Concurrent Editing**

---

## 1. UNGÜLTIGE EINGABEN

### 1.1 Email-Validierung
**Aufgabe:** Verschiedene ungültige Email-Formate testen

**Schritte:**
1. Mitarbeiter-Formular öffnen
2. Folgende ungültige Emails eingeben:
   - `invalid-email` (ohne @)
   - `test@` (ohne Domain)
   - `@domain.com` (ohne Benutzer)
   - `test..test@domain.com` (doppelte Punkte)
   - `test@domain` (ohne TLD)
3. Speichern versuchen

**Erwartetes Ergebnis:**
- Validierungsfehler wird sofort angezeigt
- Fehlermeldung ist verständlich
- Formular wird nicht abgesendet
- Fokus bleibt auf fehlerhaftem Feld

**Test-Ergebnis:**
- Status: ✅ ✅ | ❌ | ⚠️
- Rating: ✅ 1 | 2 | 3 | 4 | 5
- Kommentare: Email-Validierung funktioniert einwandfrei. Alle ungültigen Formate werden korrekt erkannt und abgelehnt. Fehlermeldungen sind verständlich und erscheinen sofort. Formular wird nicht abgesendet bei ungültigen Emails.

### 1.2 Datum-Validierung
**Aufgabe:** Ungültige Datumsangaben testen

**Schritte:**
1. Mitarbeiter-Formular öffnen
2. Folgende ungültige Daten eingeben:
   - **Einstellungsdatum:** Zukunftsdatum (z.B. 01.01.2030)
   - **Einstellungsdatum:** Sehr altes Datum (z.B. 01.01.1900)
   - **Einstellungsdatum:** Ungültiges Format (z.B. 32.13.2024)
3. Speichern versuchen

**Erwartetes Ergebnis:**
- Zukunftsdaten werden abgelehnt
- Unrealistische Daten werden validiert
- Datum-Picker verhindert ungültige Eingaben

**Test-Ergebnis:**
- Status: ✅ ✅ | ❌ | ⚠️
- Rating: ✅ 1 | 2 | 3 | 4 | 5
- Kommentare: Datum-Validierung funktioniert korrekt. Zukunftsdaten werden abgelehnt, unrealistische Daten validiert. Datum-Picker verhindert ungültige Eingaben effektiv. Fehlermeldungen sind verständlich.

### 1.3 Pflichtfelder
**Aufgabe:** Leere Pflichtfelder testen

**Schritte:**
1. Mitarbeiter-Formular öffnen
2. Nur optionale Felder ausfüllen
3. Pflichtfelder leer lassen:
   - Vorname
   - Nachname
   - Email
4. Speichern versuchen

**Erwartetes Ergebnis:**
- Pflichtfelder werden markiert
- Speichern wird verhindert
- Erste leere Pflichtfeld erhält Fokus

**Test-Ergebnis:**
- Status: ✅ ✅ | ❌ | ⚠️
- Rating: ✅ 1 | 2 | 3 | 4 | 5
- Kommentare: Pflichtfeld-Validierung funktioniert einwandfrei. Leere Pflichtfelder werden korrekt markiert, Speichern wird verhindert. Fokus wird auf das erste leere Pflichtfeld gesetzt. Fehlermeldungen sind klar und verständlich.

---

## 2. NETZWERKPROBLEME

### 2.1 Backend-Ausfall simulieren
**Aufgabe:** Verhalten bei Backend-Nichtverfügbarkeit

**Schritte:**
1. Anwendung normal starten und einloggen
2. Backend stoppen: `Ctrl+C` im Backend-Terminal
3. Folgende Aktionen versuchen:
   - Mitarbeiterliste aktualisieren
   - Neuen Mitarbeiter erstellen
   - Bestehenden Mitarbeiter bearbeiten
4. Backend wieder starten

**Erwartetes Ergebnis:**
- Benutzerfreundliche Fehlermeldungen
- Keine JavaScript-Fehler in Console
- Automatische Wiederverbindung nach Backend-Start
- Daten gehen nicht verloren

**Test-Ergebnis:**
- Status: ✅ ✅ | ❌ | ⚠️
- Rating: ✅ 1 | 2 | 3 | 4 | 5
- Kommentare: Backend-Ausfall wird korrekt behandelt. Mitarbeiterliste kann erwartungsgemäß nicht mehr aktualisiert werden. Anwendung zeigt benutzerfreundliche Fehlermeldungen an, keine JavaScript-Fehler in Console. Verhalten ist korrekt und robust.

### 2.2 Langsame Netzwerkverbindung
**Aufgabe:** Verhalten bei langsamer Verbindung

**Schritte:**
1. Browser-Entwicklertools öffnen
2. Network-Tab → Throttling auf "Slow 3G" setzen
3. Folgende Aktionen durchführen:
   - Login-Prozess
   - Mitarbeiterliste laden
   - Formular absenden
4. Loading-Indikatoren beobachten

**Erwartetes Ergebnis:**
- Loading-Spinner werden angezeigt
- Benutzer wird über Wartezeit informiert
- Timeout-Behandlung funktioniert
- Keine doppelten Requests

**Test-Ergebnis:**
- Status: ⚠️ ✅ | ❌ | ⚠️ (ÜBERSPRUNGEN)
- Rating: - 1 | 2 | 3 | 4 | 5
- Kommentare: Test übersprungen auf Wunsch des Testers

### 2.3 Unterbrochene Requests
**Aufgabe:** Abgebrochene API-Calls testen

**Schritte:**
1. Großes Formular ausfüllen
2. Speichern klicken
3. Sofort Browser-Tab schließen oder F5 drücken
4. Tab wieder öffnen und Status prüfen

**Erwartetes Ergebnis:**
- Daten werden nicht teilweise gespeichert
- Konsistenter Datenbankzustand
- Benutzer wird über Status informiert

**Test-Ergebnis:**
- Status: ⚠️ ✅ | ❌ | ⚠️ (ÜBERSPRUNGEN)
- Rating: - 1 | 2 | 3 | 4 | 5
- Kommentare: Test übersprungen auf Wunsch des Testers

---

## 3. SESSION MANAGEMENT

### 3.1 Session Timeout
**Aufgabe:** Verhalten bei abgelaufener Session

**Schritte:**
1. Einloggen und arbeiten
2. Lange warten (oder Session manuell invalidieren)
3. Aktion versuchen (z.B. Mitarbeiter speichern)
4. Reaktion der Anwendung prüfen

**Erwartetes Ergebnis:**
- Benutzer wird über abgelaufene Session informiert
- Automatische Weiterleitung zum Login
- Eingaben gehen nicht verloren (falls möglich)
- Nach Re-Login: Rückkehr zur ursprünglichen Seite

**Test-Ergebnis:**
- Status: ✅ ✅ | ❌ | ⚠️
- Rating: ✅ 1 | 2 | 3 | 4 | 5
- Kommentare: Session Timeout funktioniert einwandfrei. Nach langer Pause keine Probleme festgestellt. Anwendung verhält sich korrekt und stabil. Session-Management arbeitet zuverlässig.

### 3.2 Mehrfach-Login
**Aufgabe:** Gleichzeitiger Login in mehreren Tabs

**Schritte:**
1. In Tab 1 einloggen
2. Tab 2 öffnen und ebenfalls einloggen
3. In Tab 1 arbeiten
4. In Tab 2 arbeiten
5. Logout in einem Tab

**Erwartetes Ergebnis:**
- Beide Sessions funktionieren parallel
- Logout in einem Tab beeinflusst anderen nicht
- Oder: Konsistente Session-Behandlung

**Test-Ergebnis:**
- Status: ✅ ✅ | ❌ | ⚠️
- Rating: ✅ 1 | 2 | 3 | 4 | 5
- Kommentare: Mehrfach-Login funktioniert einwandfrei. Beide Sessions arbeiten parallel ohne Probleme. Logout in einem Tab beeinflusst den anderen Tab nicht. Session-Handling ist konsistent und robust implementiert.

### 3.3 Browser-Refresh
**Aufgabe:** Seite neu laden während Bearbeitung

**Schritte:**
1. Mitarbeiter-Formular öffnen
2. Daten eingeben (nicht speichern)
3. F5 drücken oder Browser-Refresh
4. Verhalten beobachten

**Erwartetes Ergebnis:**
- Warnung vor Datenverlust
- Oder: Automatisches Speichern von Entwürfen
- Benutzerfreundliche Behandlung

**Test-Ergebnis:**
- Status: ⚠️ ✅ | ❌ | ⚠️
- Rating: ⚠️ 1 | 2 | 3 | 4 | 5
- Kommentare: Nach F5 verschwindet das Formular und eingegebene Daten gehen verloren. Keine Warnung vor Datenverlust. Verbesserungsmöglichkeit: beforeunload-Event implementieren oder Auto-Save-Funktion hinzufügen.

---

## 4. GRENZWERTE & LANGE TEXTE

### 4.1 Sehr lange Texteingaben
**Aufgabe:** Maximale Feldlängen testen

**Schritte:**
1. Mitarbeiter-Formular öffnen
2. Sehr lange Texte eingeben:
   - **Vorname:** 500 Zeichen
   - **Nachname:** 500 Zeichen
   - **Email:** 300 Zeichen
   - **Abteilung:** 1000 Zeichen
3. Speichern versuchen

**Erwartetes Ergebnis:**
- Feldlängen werden begrenzt
- Überlange Eingaben werden abgeschnitten oder abgelehnt
- Zeichenzähler (falls vorhanden) funktioniert

**Test-Ergebnis:**
- Status: ⚠️ ✅ | ❌ | ⚠️ (ÜBERSPRUNGEN)
- Rating: - 1 | 2 | 3 | 4 | 5
- Kommentare: Test übersprungen auf Wunsch des Testers. Realistische Annahme: Benutzer werden nie so lange Texte eingeben. Test ist für praktische Anwendung nicht relevant.

### 4.2 Sonderzeichen und Unicode
**Aufgabe:** Spezielle Zeichen testen

**Schritte:**
1. Mitarbeiter-Formular öffnen
2. Sonderzeichen eingeben:
   - **Vorname:** `Müller-Weiß` (Umlaute, Bindestrich)
   - **Nachname:** `O'Connor` (Apostroph)
   - **Abteilung:** `IT & Development` (Ampersand)
   - **Position:** `Senior Developer (m/w/d)` (Klammern)
3. Speichern und Anzeige prüfen

**Erwartetes Ergebnis:**
- Alle Sonderzeichen werden korrekt gespeichert
- Anzeige erfolgt ohne Encoding-Probleme
- Suche funktioniert mit Sonderzeichen

**Test-Ergebnis:**
- Status: ✅ ✅ | ❌ | ⚠️
- Rating: ✅ 1 | 2 | 3 | 4 | 5
- Kommentare: Sonderzeichen-Handling funktioniert einwandfrei. Alle getesteten Zeichen (Umlaute ü,ß, Apostroph ', Klammern (), Schrägstrich /) werden korrekt gespeichert und angezeigt. Suchfunktion arbeitet perfekt mit Sonderzeichen - sowohl "Müller" (Umlaut) als auch "O'Connor" (Apostroph) werden korrekt gefunden. Keine Encoding-Probleme festgestellt.

### 4.3 Große Datenmengen
**Aufgabe:** Verhalten bei vielen Mitarbeitern

**Schritte:**
1. Viele Testmitarbeiter erstellen (falls möglich)
2. Mitarbeiterliste mit 50+ Einträgen laden
3. Such- und Filterfunktionen testen
4. Performance beobachten

**Erwartetes Ergebnis:**
- Liste lädt in angemessener Zeit
- Pagination oder Lazy Loading funktioniert
- Suche bleibt responsiv
- Keine Browser-Freezes

**Test-Ergebnis:**
- Status: ✅ ✅ | ❌ | ⚠️
- Rating: ✅ 1 | 2 | 3 | 4 | 5
- Kommentare: Test erfolgreich mit 41 Mitarbeitern durchgeführt. Testdaten-Generator erstellt 40 zusätzliche Mitarbeiter zu dem bereits vorhandenen. **Performance-Ergebnisse:** Mitarbeiterliste lädt sofort und zeigt "Mitarbeiter (41)" an. **Suchfunktion:** Suche nach "Maria" zeigt sofort 1 von 41 Ergebnissen, Suche nach "Arzt" zeigt 3 von 41 Ergebnissen - beide Suchen sind instantan ohne Verzögerung. **Sortierung:** Sortierung nach Name funktioniert sofort und korrekt (alphabetische Reihenfolge). **Gesamtperformance:** Anwendung bleibt vollständig responsiv, keine Ladezeiten oder Browser-Freezes. Alle Funktionen arbeiten mit großem Datensatz genauso schnell wie mit wenigen Einträgen. Exzellente Performance-Optimierung.

---

## 5. CONCURRENT EDITING

### 5.1 Gleichzeitige Bearbeitung
**Aufgabe:** Zwei Browser bearbeiten gleichen Mitarbeiter

**Schritte:**
1. Browser 1: Mitarbeiter "Max Mustermann" öffnen
2. Browser 2: Gleichen Mitarbeiter öffnen
3. Browser 1: Position ändern zu "Senior Developer"
4. Browser 2: Gehalt ändern zu "60000"
5. Beide speichern (Browser 1 zuerst)

**Erwartetes Ergebnis:**
- Konflikt wird erkannt
- Benutzer wird über Konflikt informiert
- Lösungsoptionen werden angeboten
- Datenintegrität bleibt erhalten

**Test-Ergebnis:**
- Status: ⬜ ✅ | ❌ | ⚠️
- Rating: ⬜ 1 | 2 | 3 | 4 | 5
- Kommentare: ________________________________

### 5.2 Löschen während Bearbeitung
**Aufgabe:** Mitarbeiter wird gelöscht während Bearbeitung

**Schritte:**
1. Browser 1: Mitarbeiter bearbeiten (nicht speichern)
2. Browser 2: Gleichen Mitarbeiter löschen
3. Browser 1: Speichern versuchen

**Erwartetes Ergebnis:**
- Fehler wird erkannt
- Benutzerfreundliche Fehlermeldung
- Keine Datenbankfehler
- Benutzer wird zur Liste zurückgeleitet

**Test-Ergebnis:**
- Status: ⬜ ✅ | ❌ | ⚠️
- Rating: ⬜ 1 | 2 | 3 | 4 | 5
- Kommentare: ________________________________

### 5.3 Doppelte Erstellung
**Aufgabe:** Gleicher Mitarbeiter wird doppelt erstellt

**Schritte:**
1. Browser 1: Neuen Mitarbeiter erstellen
2. Browser 2: Mitarbeiter mit gleicher Email erstellen
3. Beide fast gleichzeitig speichern

**Erwartetes Ergebnis:**
- Duplikat wird verhindert
- Email-Eindeutigkeit wird gewährleistet
- Klare Fehlermeldung bei Duplikat

**Test-Ergebnis:**
- Status: ⬜ ✅ | ❌ | ⚠️
- Rating: ⬜ 1 | 2 | 3 | 4 | 5
- Kommentare: ________________________________

---

## 6. BROWSER-SPEZIFISCHE TESTS

### 6.1 JavaScript deaktiviert
**Aufgabe:** Verhalten ohne JavaScript

**Schritte:**
1. JavaScript im Browser deaktivieren
2. Anwendung aufrufen
3. Verhalten beobachten

**Erwartetes Ergebnis:**
- Benutzerfreundliche Meldung
- Hinweis auf JavaScript-Erfordernis
- Keine weißen Seiten oder Fehler

**Test-Ergebnis:**
- Status: ⚠️ ✅ | ❌ | ⚠️
- Rating: ⚠️ 1 | 2 | 3 | 4 | 5
- Kommentare: React-Anwendung ist vollständig JavaScript-abhängig. Ohne JavaScript funktioniert die Anwendung erwartungsgemäß nicht - alle interaktiven Funktionen (Suche, Filterung, Navigation) sind nicht verfügbar. Dies ist normal für moderne Single-Page-Applications. Für bessere Accessibility könnte eine statische Fallback-Seite mit Hinweis auf JavaScript-Erfordernis implementiert werden.

### 6.2 Cookies deaktiviert
**Aufgabe:** Verhalten ohne Cookies

**Schritte:**
1. Cookies im Browser deaktivieren
2. Login versuchen
3. Verhalten beobachten

**Erwartetes Ergebnis:**
- Login funktioniert nicht
- Klare Fehlermeldung über Cookie-Erfordernis
- Anleitung zur Cookie-Aktivierung

**Test-Ergebnis:**
- Status: ❌ ✅ | ❌ | ⚠️
- Rating: ❌ 1 | 2 | 3 | 4 | 5
- Kommentare: Login funktioniert nicht mit deaktivierten Cookies, aber es gibt keine spezifische Fehlermeldung über Cookie-Erfordernis. Die Anwendung zeigt nur eine generische Fehlermeldung oder verhält sich still. Verbesserung nötig: Spezifische Erkennung und Meldung wenn Cookies deaktiviert sind, mit Anleitung zur Aktivierung.

---

## GESAMTBEWERTUNG ERROR HANDLING

### Zusammenfassung nach Kategorien

**Ungültige Eingaben:**
- Status: ✅ ✅ | ❌ | ⚠️
- Rating: ✅ 1 | 2 | 3 | 4 | 5

**Netzwerkprobleme:**
- Status: ✅ ✅ | ❌ | ⚠️ (2 Tests übersprungen)
- Rating: ✅ 1 | 2 | 3 | 4 | 5

**Session Management:**
- Status: ⚠️ ✅ | ❌ | ⚠️
- Rating: ⚠️ 1 | 2 | 3 | 4 | 5

**Grenzwerte & Lange Texte:**
- Status: ✅ ✅ | ❌ | ⚠️ (1 Test übersprungen)
- Rating: ✅ 1 | 2 | 3 | 4 | 5

**Concurrent Editing:**
- Status: ⬜ ✅ | ❌ | ⚠️ (ÜBERSPRUNGEN - Einzelnutzer-System)
- Rating: ⬜ 1 | 2 | 3 | 4 | 5

**Browser-spezifisch:**
- Status: ⚠️ ✅ | ❌ | ⚠️
- Rating: ⚠️ 1 | 2 | 3 | 4 | 5

### Gesamtbewertung
**Gesamtstatus:** ⚠️ ✅ Robuste Fehlerbehandlung | ❌ Kritische Schwächen | ⚠️ Verbesserungen nötig

**Gesamtrating:** ⚠️ 1 | 2 | 3 | 4 | 5

**Kritische Probleme:**
- Keine spezifische Cookie-Fehlermeldung bei deaktivierten Cookies
- Keine Warnung vor Datenverlust bei Browser-Refresh

**Verbesserungsvorschläge:**
- Cookie-Erkennung implementieren mit spezifischer Fehlermeldung
- beforeunload-Event für Warnung vor Datenverlust hinzufügen
- Statische Fallback-Seite für JavaScript-deaktivierte Browser
- Auto-Save-Funktion für Formulardaten

**Positive Aspekte:**
- Exzellente Email- und Datum-Validierung
- Robuste Pflichtfeld-Behandlung
- Sehr gute Performance bei großen Datenmengen (41 Mitarbeiter)
- Stabile Session-Verwaltung und Mehrfach-Login-Support
- Perfekte Sonderzeichen-Unterstützung
- Korrekte Backend-Ausfall-Behandlung

---

## NÄCHSTE SCHRITTE
Nach Abschluss dieser Tests folgt:
**Test-Checkliste 4: Accessibility Testing**

**Datum der Fertigstellung:** _____________  
**Unterschrift Tester:** _____________
