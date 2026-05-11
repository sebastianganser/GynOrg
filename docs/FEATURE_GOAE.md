# GynOrg – GOÄ-Rechnungsmodul: Projektspezifikation für KI-Assistenten

> **Zweck dieser Datei:** Vollständige Kontextbeschreibung für Claude Code, Codex oder andere KI-Programmierassistenten zur Implementierung des GOÄ-Rechnungsmoduls in die bestehende GynOrg-Webanwendung. Details werden beim Programmieren iterativ verfeinert.

---

## 1. Projektüberblick

**Anwendung:** GynOrg – browserbasiertes Verwaltungsprogramm für die Gynäkologie-Abteilung einer Rehabilitationsklinik in Sachsen-Anhalt.

**Betreiberin:** Chefärztin Gynäkologie, 3 Stationen, ca. 100 Betten.

**Bestehende Module:**
- Mitarbeiterverwaltung (Stammdaten, Positionen, Status)
- Abwesenheitsplanung / Urlaubsplanung des Teams
- Belegungsstatistik der 3 Stationen

**Neues Modul (diese Spec):** GOÄ-Privatpatientenabrechnung mit ZUGFeRD-eRechnung und EPC-QR-Code.

---

## 2. Technischer Stack

### Ist-Zustand (bestehende App)
- **Frontend:** Browserbasierte Single-Page-Application (HTML/CSS/JS)
- **Datenbank:** PostgreSQL 18
- **Deployment:** Docker auf Unraid-Heimserver
- **UI-Design:** Dunkle Sidebar (`#1a1f2e` ca.), heller Content-Bereich (weiß/hellgrau), Primärfarbe Blau (`#2563eb` ca.), grüne Status-Badges, Avatar-Initialen-Kreise bunt

### Neu hinzukommend (dieses Modul)
- **Backend:** Python mit FastAPI (neu, für dieses Modul)
- **PDF-Rendering:** WeasyPrint (serverseitig, headless)
- **eRechnung:** `factur-x` Python-Bibliothek → ZUGFeRD 2.3, Profil EN 16931
- **QR-Code:** `qrcode` Python-Bibliothek → EPC-QR-Code (GiroCode, SEPA)
- **E-Mail-Versand:** SMTP (Konfiguration via Umgebungsvariablen)
- **DB-Zugriff:** `psycopg3` (nativer PostgreSQL 18 Treiber)

### Docker-Compose-Erweiterung
Das neue FastAPI-Backend wird als zusätzlicher Service in den bestehenden Docker-Stack integriert.

---

## 3. UI-Design-Vorgaben

### Designsprache (aus Screenshot ableiten)
Das neue Modul muss nahtlos in die bestehende GynOrg-UI integriert werden:

```
Layout:
├── Linke Sidebar (dunkel, ~160px breit, kollabierbar)
│   ├── Logo "GynOrg" oben links (blau)
│   ├── Navigation: Icon + Label, aktiver Item blau hinterlegt
│   └── "Abmelden" unten links
└── Content-Bereich (hell, flex-grow)
    ├── Header-Zeile: Seitentitel links, User-Info rechts
    └── Hauptinhalt mit weißen Cards / Tabellen
```

**Neue Sidebar-Einträge hinzufügen:**
- `💶 Privatrechnungen` (Icon: Dokument mit Euro oder ähnlich)

**Farbpalette (approximiert aus Screenshot):**
| Element | Farbe |
|---|---|
| Sidebar Hintergrund | `#1e2235` |
| Sidebar Aktiv | `#2563eb` |
| Content Hintergrund | `#f3f4f6` |
| Card/Table Hintergrund | `#ffffff` |
| Primär-Blau | `#2563eb` |
| Text dunkel | `#111827` |
| Text grau | `#6b7280` |
| Badge Aktiv | `#22c55e` (grün) |
| Badge Inaktiv | `#9ca3af` (grau) |

---

## 4. Datenbankschema (PostgreSQL 18)

### 4.1 Neue Tabellen

```sql
-- GOÄ-Zifferndatenbank (Stammdaten, read-only im Betrieb)
CREATE TABLE goae_ziffern (
    id              SERIAL PRIMARY KEY,
    ziffer          VARCHAR(10) NOT NULL UNIQUE,   -- z.B. "1", "5", "415a"
    leistungstext   TEXT NOT NULL,                  -- Offizieller GOÄ-Text
    punkte          NUMERIC(8,2) NOT NULL,           -- Punktzahl
    einfachsatz     NUMERIC(8,4) GENERATED ALWAYS AS (punkte * 0.0582873) STORED,
    max_faktor_regel NUMERIC(4,2) DEFAULT 2.30,     -- 2,3 / 1,8 / 1,15
    max_faktor_abs   NUMERIC(4,2) DEFAULT 3.50,     -- 3,5 / 2,5 / 1,3
    kapitel         VARCHAR(10),                    -- GOÄ-Kapitel (A, B, C, ... O)
    abschnitt       VARCHAR(100),                   -- Abschnittsbezeichnung
    begruendung_pflicht BOOLEAN DEFAULT FALSE,      -- True wenn >Regelsatz Begründung nötig
    analog_bewertung BOOLEAN DEFAULT FALSE,         -- §6 Abs.2 Analogleistung
    aktiv           BOOLEAN DEFAULT TRUE,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_goae_ziffer ON goae_ziffern(ziffer);
CREATE INDEX idx_goae_fulltext ON goae_ziffern USING gin(to_tsvector('german', leistungstext));

-- Patienten (Privatpatienten, pro Rechnung erfasst, wiederverwendbar)
CREATE TABLE patienten (
    id              SERIAL PRIMARY KEY,
    anrede          VARCHAR(20),                    -- "Herr", "Frau", "Divers"
    titel           VARCHAR(50),                    -- "Dr.", "Prof. Dr." etc.
    vorname         VARCHAR(100) NOT NULL,
    nachname        VARCHAR(100) NOT NULL,
    geburtsdatum    DATE,
    strasse         VARCHAR(200),
    plz             VARCHAR(10),
    ort             VARCHAR(100),
    land            VARCHAR(100) DEFAULT 'Deutschland',
    email           VARCHAR(200),
    telefon         VARCHAR(50),
    versicherung    VARCHAR(200),                   -- PKV-Name oder "Beihilfe"
    versicherungs_nr VARCHAR(100),
    beihilfe_satz   NUMERIC(5,2),                  -- Beihilfesatz in % (z.B. 50.00)
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_patienten_name ON patienten(nachname, vorname);
CREATE INDEX idx_patienten_search ON patienten USING gin(
    to_tsvector('german', nachname || ' ' || vorname)
);

-- Rechnungsköpfe
CREATE TABLE rechnungen (
    id                  SERIAL PRIMARY KEY,
    rechnungsnummer     VARCHAR(30) NOT NULL UNIQUE, -- Format: RG-YYYY-MM-NNN
    rechnungsdatum      DATE NOT NULL DEFAULT CURRENT_DATE,
    faelligkeitsdatum   DATE GENERATED ALWAYS AS (rechnungsdatum + INTERVAL '30 days') STORED,
    patient_id          INTEGER NOT NULL REFERENCES patienten(id),
    
    -- Ausstellerin (Ärztin)
    arzt_name           VARCHAR(200) NOT NULL,       -- "Dr. med. Maria Ganser"
    arzt_facharzt       VARCHAR(200),               -- "Fachärztin für Gynäkologie und Geburtshilfe"
    arzt_strasse        VARCHAR(200),
    arzt_plz            VARCHAR(10),
    arzt_ort            VARCHAR(100),
    arzt_telefon        VARCHAR(50),
    arzt_email          VARCHAR(200),
    arzt_lanr           VARCHAR(20),                 -- Lebenslange Arztnummer
    arzt_iban           VARCHAR(34) NOT NULL,        -- Für SEPA/QR-Code
    arzt_bic            VARCHAR(11),
    arzt_bank           VARCHAR(200),
    arzt_steuernr       VARCHAR(50),                -- Oder USt-IdNr (bei Befreiung leer lassen)
    
    -- Behandlung
    behandlungszeitraum_von DATE,
    behandlungszeitraum_bis DATE,
    diagnose            TEXT,                        -- ICD-10 oder Freitext
    behandlungsort      VARCHAR(200),               -- Name der Klinik
    
    -- Beträge (berechnet, zur Kontrolle denormalisiert)
    betrag_netto        NUMERIC(10,2),
    betrag_mwst         NUMERIC(10,2) DEFAULT 0.00, -- §4 Nr.14 UStG: ärztl. Leistungen MwSt-frei
    betrag_brutto       NUMERIC(10,2),
    
    -- Status
    status              VARCHAR(20) DEFAULT 'entwurf'
                        CHECK (status IN ('entwurf','gestellt','gesendet','bezahlt','storniert')),
    bezahlt_am          DATE,
    
    -- ZUGFeRD / eRechnung
    zugferd_profil      VARCHAR(50) DEFAULT 'EN 16931',
    
    -- Interne Felder
    notizen             TEXT,
    erstellt_von        VARCHAR(100),               -- Username aus Session
    created_at          TIMESTAMPTZ DEFAULT NOW(),
    updated_at          TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_rechnungen_patient ON rechnungen(patient_id);
CREATE INDEX idx_rechnungen_datum ON rechnungen(rechnungsdatum DESC);
CREATE INDEX idx_rechnungen_status ON rechnungen(status);

-- Automatische Rechnungsnummer-Sequenz pro Monat
CREATE SEQUENCE rechnungen_seq START 1;

-- Trigger für auto-Rechnungsnummer
CREATE OR REPLACE FUNCTION generate_rechnungsnummer()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.rechnungsnummer IS NULL OR NEW.rechnungsnummer = '' THEN
        NEW.rechnungsnummer := 'RG-' || 
            TO_CHAR(NOW(), 'YYYY-MM') || '-' ||
            LPAD(nextval('rechnungen_seq')::TEXT, 4, '0');
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_rechnungsnummer
    BEFORE INSERT ON rechnungen
    FOR EACH ROW EXECUTE FUNCTION generate_rechnungsnummer();

-- Rechnungspositionen (GOÄ-Leistungen)
CREATE TABLE rechnungs_positionen (
    id                  SERIAL PRIMARY KEY,
    rechnung_id         INTEGER NOT NULL REFERENCES rechnungen(id) ON DELETE CASCADE,
    position_nr         SMALLINT NOT NULL,           -- Reihenfolge in der Rechnung
    
    -- GOÄ-Referenz
    goae_ziffer_id      INTEGER REFERENCES goae_ziffern(id),
    goae_ziffer         VARCHAR(10),                 -- Denormalisiert (auch für Analogziffern)
    leistungstext       TEXT NOT NULL,               -- Kann vom GOÄ-Text abweichen (Analog)
    
    -- Leistungsdaten
    leistungsdatum      DATE NOT NULL,
    anzahl              SMALLINT DEFAULT 1 CHECK (anzahl > 0),
    
    -- GOÄ-Berechnung
    punkte              NUMERIC(8,2),
    einfachsatz         NUMERIC(8,4),               -- Punktwert × 0,0582873
    steigerungsfaktor   NUMERIC(4,2) DEFAULT 2.30,
    betrag              NUMERIC(10,2) NOT NULL,      -- einfachsatz × faktor × anzahl
    
    -- Pflichtfelder GOÄ §12
    begruendung         TEXT,                        -- Pflicht wenn Faktor > Regelsatz
    analog_nach         VARCHAR(10),                 -- Bei Analogleistung: Ursprungsziffer
    
    created_at          TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_positionen_rechnung ON rechnungs_positionen(rechnung_id, position_nr);

-- Rechnungsdokumente (generierte PDFs, Versandlog)
CREATE TABLE rechnungs_dokumente (
    id              SERIAL PRIMARY KEY,
    rechnung_id     INTEGER NOT NULL REFERENCES rechnungen(id) ON DELETE CASCADE,
    dokument_typ    VARCHAR(20) DEFAULT 'pdf'
                    CHECK (dokument_typ IN ('pdf','zugferd','storno')),
    dateiname       VARCHAR(200),
    pdf_daten       BYTEA,                          -- ZUGFeRD-PDF als Binary
    pdf_groesse     INTEGER,                        -- Bytes
    zugferd_xml     TEXT,                           -- Eingebettetes XML (zur Referenz)
    
    -- Versand
    gesendet_an     VARCHAR(200),                   -- E-Mail-Adresse
    gesendet_am     TIMESTAMPTZ,
    versand_status  VARCHAR(20) DEFAULT 'ausstehend'
                    CHECK (versand_status IN ('ausstehend','gesendet','fehlgeschlagen')),
    versand_fehler  TEXT,
    
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- Konfiguration / Arztprofil (für Vorausfüllung)
CREATE TABLE einstellungen_praxis (
    id              SERIAL PRIMARY KEY,
    schluessel      VARCHAR(100) NOT NULL UNIQUE,
    wert            TEXT,
    beschreibung    TEXT,
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

-- Seed: Standard-Einstellungen
INSERT INTO einstellungen_praxis (schluessel, wert, beschreibung) VALUES
    ('arzt_name', 'Dr. med. Maria Ganser', 'Vollständiger Name mit Titel'),
    ('arzt_facharzt', 'Fachärztin für Gynäkologie und Geburtshilfe', 'Fachbezeichnung'),
    ('arzt_lanr', '', 'Lebenslange Arztnummer (9-stellig)'),
    ('arzt_iban', '', 'IBAN für Zahlungseingang'),
    ('arzt_bic', '', 'BIC/SWIFT'),
    ('arzt_bank', '', 'Name der Bank'),
    ('arzt_strasse', '', 'Praxisadresse Straße'),
    ('arzt_plz', '', 'PLZ'),
    ('arzt_ort', '', 'Ort'),
    ('arzt_telefon', '', 'Telefonnummer'),
    ('arzt_email', '', 'E-Mail für Rechnungsversand'),
    ('behandlungsort', 'Reha-Klinik Sachsen-Anhalt', 'Name der Einrichtung'),
    ('smtp_host', '', 'SMTP-Server'),
    ('smtp_port', '587', 'SMTP-Port'),
    ('smtp_user', '', 'SMTP-Benutzername'),
    ('smtp_pass', '', 'SMTP-Passwort (verschlüsselt speichern!)'),
    ('goae_punktwert', '0.0582873', 'GOÄ-Punktwert in Euro (Stand 1996, gültig bis GOÄ-Reform)');
```

---

## 5. GOÄ-Grundregeln (Pflichtimplementierung)

```
Punktwert:          5,82873 Cent pro Punkt (§5 GOÄ, unveränderter Wert seit 1996)

Steigerungssätze:
  Allgemeine Leistungen (§5 Abs.2):   Regelhöchstsatz 2,3-fach, absolutes Maximum 3,5-fach
  Laborleistungen (§5 Abs.3):         Regelhöchstsatz 1,8-fach, absolutes Maximum 2,5-fach
  Radiologische Leistungen (§5 Abs.3): Regelhöchstsatz 1,15-fach, absolutes Maximum 1,3-fach

Begründungspflicht: Bei Überschreitung des Regelhöchstsatzes MUSS eine
                    schriftliche Begründung in der Rechnung erscheinen (§12 Abs.3 GOÄ)

Pflichtangaben Rechnung (§12 GOÄ):
  1. Datum der Erbringung jeder Leistung
  2. GOÄ-Ziffer und Leistungsbezeichnung
  3. Anzahl der Leistungen
  4. Einfachsatz und Steigerungsfaktor
  5. Berechneter Betrag je Position
  6. Name und Anschrift des Arztes
  7. Name und Anschrift des Patienten / Zahlungspflichtigen
  8. Rechnungsdatum und Zahlungsfrist (§12 Abs.1: 30 Tage Verzug ohne Mahnung)

Umsatzsteuer: Ärztliche Heilbehandlungsleistungen sind nach §4 Nr.14 UStG
              von der Umsatzsteuer BEFREIT. Kein MwSt-Ausweis auf der Rechnung.
              Hinweis: "Gemäß §4 Nr. 14 UStG umsatzsteuerbefreit" angeben.

Analogbewertungen (§6 Abs.2): Nicht im Verzeichnis enthaltene Leistungen werden
              nach einer gleichwertigen Ziffer berechnet. Kennzeichnung mit "entsprechend"
              oder "analog" erforderlich.
```

---

## 6. API-Endpunkte (FastAPI)

### 6.1 GOÄ-Ziffern
```
GET  /api/goae/suche?q={suchbegriff}&limit=20
     → Volltextsuche in Ziffer-Nummer UND Leistungstext
     → Rückgabe: [{ziffer, leistungstext, punkte, einfachsatz, max_faktor_regel}, ...]

GET  /api/goae/ziffer/{ziffer}
     → Einzelne Ziffer mit allen Details
```

### 6.2 Patienten
```
GET  /api/patienten/suche?q={name}
     → Fuzzy-Suche in Vorname + Nachname für Autovervollständigung

GET  /api/patienten/{id}
POST /api/patienten              → Neuen Patienten anlegen
PUT  /api/patienten/{id}        → Patientendaten aktualisieren
```

### 6.3 Rechnungen
```
GET  /api/rechnungen             → Liste mit Filter (status, patient, datum)
GET  /api/rechnungen/{id}        → Rechnung mit Positionen
POST /api/rechnungen             → Neue Rechnung erstellen (mit Positionen)
PUT  /api/rechnungen/{id}        → Rechnung aktualisieren (nur Entwurf)
DELETE /api/rechnungen/{id}      → Entwurf löschen

POST /api/rechnungen/{id}/stellen     → Status: entwurf → gestellt
POST /api/rechnungen/{id}/pdf         → PDF generieren und in DB speichern
GET  /api/rechnungen/{id}/pdf         → PDF als Datei-Download streamen
POST /api/rechnungen/{id}/senden      → PDF per E-Mail versenden
POST /api/rechnungen/{id}/bezahlt     → Als bezahlt markieren mit Datum
POST /api/rechnungen/{id}/stornieren  → Stornorechnung erstellen
```

### 6.4 Einstellungen
```
GET  /api/einstellungen/praxis   → Praxisdaten für Vorausfüllung
PUT  /api/einstellungen/praxis   → Praxisdaten speichern
```

---

## 7. PDF / ZUGFeRD / QR-Code Generierung

### 7.1 Prozess (serverseitig in FastAPI)

```python
# Grober Ablauf in /api/rechnungen/{id}/pdf

1. Rechnungsdaten aus DB laden (rechnung + positionen + patient)
2. EPC-QR-Code generieren:
   - Format: EPC006 Version 002
   - BCD\n002\n1\nSCT\n{BIC}\n{Empfaenger}\n{IBAN}\nEUR{Betrag}\n\n\n{Verwendungszweck}
   - Als PNG Base64 für HTML-Einbettung
3. HTML-Template rendern (Jinja2) mit allen Rechnungsdaten + QR-Code
4. WeasyPrint: HTML → PDF (DIN A4, Druckoptimiert)
5. ZUGFeRD-XML generieren via factur-x:
   - Profil: EN 16931 (vollständige Rechnungsdaten maschinenlesbar)
   - Pflichtfelder: BuyerReference, alle Positionen, Steuerkategorie "E" (steuerbefreit)
6. factur-x: XML in PDF einbetten → ZUGFeRD-konformes PDF/A-3
7. PDF in DB speichern (rechnungs_dokumente.pdf_daten)
8. PDF als Response streamen
```

### 7.2 EPC-QR-Code Format

```
BCD
002
1
SCT
{BIC}
{Arzt Vollname}
{IBAN}
EUR{Betrag mit Punkt als Dezimaltrennzeichen, z.B. EUR123.45}
                    ← leer (Verwendungszweck Kategorie)
                    ← leer (Verwendungszweck Text, optional: Rechnungsnummer)
{Rechnungsnummer}   ← Referenz
```

### 7.3 ZUGFeRD-Pflichtfelder

```python
# Steuercode für steuerbefreite Arztleistungen:
tax_category_code = "E"          # Exempt from VAT
tax_exemption_reason = "Gemäß §4 Nr. 14 UStG umsatzsteuerbefreit"
tax_rate = 0.0
tax_amount = 0.0

# Dokumenttyp:
type_code = "380"                # Commercial Invoice
```

### 7.4 PDF-Layout (DIN A4)

```
┌─────────────────────────────────────────┐
│ [Praxis-Logo optional]    RECHNUNG      │  ← Header
│ Dr. med. Maria Ganser                   │
│ Fachärztin Gynäkologie                  │
│ Adresse, Tel, E-Mail, LANR              │
├─────────────────────────────────────────┤
│ An:                    Rechnungs-Nr:    │  ← Adressblock
│ Patient Name           RG-2025-06-0042  │
│ Adresse                Datum: 15.06.25  │
│                        Fällig: 15.07.25 │
├─────────────────────────────────────────┤
│ Diagnose: [Text]                        │
│ Behandlungszeitraum: [Von] – [Bis]      │
│ Behandlungsort: [Klinik]                │
├──────┬────────────────────┬───┬────┬────┤
│ Datum│ Leistung (GOÄ-Zif.)│ n │Fkt │ € │  ← Positionen
│      │                    │   │    │   │
│      │ [Begründung falls  │   │    │   │
│      │  Faktor > Regelmax]│   │    │   │
├──────┴────────────────────┴───┴────┴────┤
│                          Gesamt: XXX,XX │  ← Summe
│         Gemäß §4 Nr.14 UStG befreit    │
├─────────────────────────────────────────┤
│ Bitte überweisen Sie den Betrag         │  ← Zahlungsinfos
│ innerhalb von 30 Tagen auf:             │
│ IBAN: DE... │ BIC: ... │ Bank: ...      │
│                                         │
│ [EPC-QR-Code]  Verwendungszweck:        │
│                RG-2025-06-0042          │
├─────────────────────────────────────────┤
│ Steuer-Nr: ... │ LANR: ...              │  ← Footer
│ Diese Rechnung enthält eine eingebettete│
│ eRechnung (ZUGFeRD 2.3)                │
└─────────────────────────────────────────┘
```

---

## 8. Frontend-Modul (Browser-UI)

### 8.1 Neue Seiten / Views

```
/rechnungen              → Übersicht aller Rechnungen (Liste mit Filter)
/rechnungen/neu          → Neue Rechnung erstellen (Haupt-Workflow)
/rechnungen/{id}         → Rechnungsdetail / Vorschau
/rechnungen/{id}/bearbeiten → Entwurf bearbeiten
/einstellungen/praxis    → Praxisdaten pflegen (einmalig)
```

### 8.2 Rechnungs-Erstellungsformular (Workflow)

```
Schritt 1: Patient
├── Suchfeld: Autovervollständigung aus bestehenden Patienten
├── "Neuer Patient" Button → Inline-Formular aufklappt
└── Felder: Anrede, Titel, Vorname, Nachname, Geburtsdatum,
            Adresse, E-Mail, Telefon, Versicherung, Versicherungs-Nr

Schritt 2: Rechnungskopf
├── Rechnungsdatum (default: heute)
├── Behandlungszeitraum Von/Bis
├── Diagnose (Freitext)
└── Behandlungsort (vorausgefüllt aus Einstellungen)

Schritt 3: Leistungen (GOÄ-Positionen)
├── GOÄ-Suche: Eingabefeld → Live-Suche (Ziffer ODER Stichwort)
│   → Treffer als Dropdown mit Ziffer + Kurztext + Einfachsatz
├── Pro Position:
│   ├── Leistungsdatum (Date-Picker)
│   ├── GOÄ-Ziffer + Leistungstext (editierbar für Analogleistungen)
│   ├── Anzahl (Standard: 1)
│   ├── Steigerungsfaktor (Standard: 2,30)
│   │   → Warnung wenn > Regelhöchstsatz
│   │   → Begründungsfeld erscheint automatisch wenn > Regelhöchstsatz
│   └── Betrag (automatisch berechnet, read-only)
├── "Position hinzufügen" Button
├── Summe live berechnet
└── Positionen sortierbar / löschbar

Schritt 4: Vorschau & Ausgabe
├── Kompakte Vorschau der Rechnung (HTML-Rendering)
├── [PDF generieren & herunterladen] Button
├── [Drucken] Button → window.print() mit Print-CSS
└── [Per E-Mail senden] Button → Modal mit Empfänger-Adresse
```

### 8.3 Rechnungsübersicht

```
Spalten: Rechnungs-Nr | Patient | Datum | Betrag | Status | Aktionen
Filter: Status (Alle / Entwurf / Gestellt / Gesendet / Bezahlt / Storniert)
Suche: Patient-Name oder Rechnungsnummer
Aktionen pro Zeile:
  - Ansehen (Auge)
  - Bearbeiten (Stift, nur Entwurf)
  - PDF herunterladen
  - Als bezahlt markieren (Haken)
  - Stornieren (X, nur nach Stellung)
```

---

## 9. GOÄ-Seed-Daten (gynäkologischer Kern)

> Die vollständige GOÄ-Datenbank (~2.800 Positionen) kann separat importiert werden.
> Als Minimalset für den Start sind folgende Kapitel priorisiert:

```
Kapitel A: Allgemeine Leistungen (Nr. 1, 3, 4, 5, 6, 7, 8, 10, 15, 16, 17, 18, 75, 76, 80)
Kapitel B: Grundleistungen und allgemeine Leistungen (Nr. 100–109, ausgewählt)
Kapitel C: Schmerztherapie (Nr. 490–497, ausgewählt)
Kapitel E: Physikalisch-medizinische Leistungen (Nr. 510–558, ausgewählt)
Kapitel G: Neurologie, Psychiatrie, Psychotherapie (Auswahl für Konsile)
Kapitel L: Chirurgie, Orthopädie (Nr. 2000–2005, kleine Eingriffe)
Kapitel O: Gynäkologie und Geburtshilfe (Nr. 1000–1136, vollständig)
```

**Import-Format:**
```sql
INSERT INTO goae_ziffern (ziffer, leistungstext, punkte, max_faktor_regel, max_faktor_abs, kapitel)
VALUES ('1', 'Beratung, auch telefonisch', 80, 2.30, 3.50, 'A');
-- ... weitere Einträge
```

---

## 10. Projektstruktur (empfohlen)

```
gynorg/
├── backend/
│   ├── main.py                    # FastAPI App
│   ├── routers/
│   │   ├── goae.py               # GOÄ-Ziffern Endpunkte
│   │   ├── patienten.py          # Patienten Endpunkte
│   │   └── rechnungen.py         # Rechnungs-Endpunkte
│   ├── services/
│   │   ├── pdf_generator.py      # WeasyPrint PDF-Rendering
│   │   ├── zugferd_service.py    # factur-x ZUGFeRD-Generierung
│   │   ├── qr_service.py         # EPC-QR-Code Generierung
│   │   └── mail_service.py       # SMTP E-Mail-Versand
│   ├── models/
│   │   ├── rechnung.py           # Pydantic-Schemas
│   │   └── patient.py
│   ├── templates/
│   │   └── rechnung.html         # Jinja2-Template für PDF
│   ├── db.py                     # PostgreSQL-Verbindung (psycopg3)
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── pages/
│   │   ├── rechnungen.html       # Rechnungsübersicht
│   │   ├── rechnung-neu.html     # Erstellungsformular
│   │   └── rechnung-detail.html  # Detailansicht
│   ├── js/
│   │   ├── rechnungen.js
│   │   └── goae-suche.js         # Autovervollständigung GOÄ
│   └── css/
│       └── rechnung-print.css    # @media print Styles
├── db/
│   ├── migrations/
│   │   └── 001_goae_modul.sql    # Schema (diese Spec, Abschnitt 4)
│   └── seeds/
│       └── goae_ziffern_kern.sql # Gynäkologisches Kern-Set
└── docker-compose.yml            # Erweiterung um FastAPI-Service
```

---

## 11. Docker-Compose-Erweiterung

```yaml
# Ergänzung zur bestehenden docker-compose.yml

  gynorg-api:
    build: ./backend
    container_name: gynorg_api
    restart: unless-stopped
    ports:
      - "7392:8000"          # Anpassen an bestehenden Port-Bereich
    environment:
      DATABASE_URL: postgresql+psycopg://user:pass@postgres:5432/gynorg
      SMTP_HOST: ${SMTP_HOST}
      SMTP_PORT: ${SMTP_PORT:-587}
      SMTP_USER: ${SMTP_USER}
      SMTP_PASS: ${SMTP_PASS}
    volumes:
      - gynorg_pdfs:/app/pdfs
    depends_on:
      - postgres
    networks:
      - gynorg_net
```

---

## 12. Offene Punkte / Iterationspunkte

Diese Punkte werden beim Programmieren on-the-fly entschieden:

- [ ] **GOÄ-Datenbank-Vollimport:** Quelle und Format der vollständigen GOÄ-Daten klären (DIMDI/BfArM, CSV-Import-Skript notwendig)
- [ ] **Logo/Briefkopf:** Soll ein Klinik-Logo in den PDF-Briefkopf eingebunden werden?
- [ ] **Benutzerrollen:** Darf nur die Chefärztin Rechnungen stellen, oder auch die Sekretärin?
- [ ] **Stornorechnungen:** Komplettes Storno oder Teilkorrektur?
- [ ] **Mahnwesen:** Soll eine einfache Mahnfunktion (1. Mahnung nach 30 Tagen) ergänzt werden?
- [ ] **Statistik-Integration:** Sollen Privatpatientenzahlen in die Belegungsstatistik einfließen?
- [ ] **GOÄ-Reform 2025/2026:** Die neue GOÄ ist in Vorbereitung; Datenbankstruktur ist so ausgelegt, dass ein Parallelbetrieb (alter/neuer Punktwert) möglich wäre
- [ ] **LANR-Validierung:** Prüfziffer-Validierung der Arztnummer implementieren?
- [ ] **Backup der PDFs:** BYTEA in DB vs. Filesystem-Mount — je nach Präferenz anpassen

---

## 13. Referenzen

- GOÄ-Text: [Bundesärztekammer GOÄ-Kommentar](https://www.bundesaerztekammer.de/fileadmin/user_upload/downloads/GOAe_Kommentar.pdf)
- ZUGFeRD: [FeRD-Spezifikation 2.3](https://www.ferd-net.de/standards/zugferd-2.3/)
- EPC-QR-Code: [EPC069-12 v2.1 Specification](https://www.europeanpaymentscouncil.eu/document-library/guidance-documents/quick-response-code-guidelines-enable-data-capture-initiation)
- factur-x Python: [github.com/akretion/factur-x](https://github.com/akretion/factur-x)
- WeasyPrint: [doc.courtbouillon.org/weasyprint](https://doc.courtbouillon.org/weasyprint/stable/)

---

*Erstellt: Juni 2025 | Projekt: GynOrg | Modul: GOÄ-Privatpatientenabrechnung*
*Diese Spec ist als lebendiges Dokument konzipiert — beim Programmieren iterativ erweitern.*
