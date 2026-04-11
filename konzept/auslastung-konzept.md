# Auslastungsstatistik Gynäkologie – Konzept

> Kurklinik · Sachsen-Anhalt · 3 Stationen · 100 Betten · Ø Verweildauer 21 Tage  
> Stand: März 2026 · Status: Brainstorming / Konzeptphase

---

## 1. Zielsetzung

Aufbau einer anonymisierten, tagesbasierten Auslastungsstatistik für die gynäkologische Abteilung einer Kurklinik. Das System soll:

- die operative Tagessteuerung unterstützen
- historische Muster sichtbar machen
- mittelfristige Prognosen ermöglichen
- als Entscheidungsgrundlage für Klinikleitung und Personalplanung dienen

---

## 2. Erfasste Rohdaten

### 2.1 Tägliche Kerndaten (pro Station)

| Feld | Beschreibung |
|---|---|
| `date` | Erfassungsdatum |
| `occupied` | Aktuell belegte Betten |
| `admissions` | Zugänge des Tages |
| `discharges` | Abgänge des Tages |
| `blocked_beds` | Temporär gesperrte Betten (Hygiene, Reparatur etc.) |

### 2.2 Tägliche Gesamtdaten

| Feld | Beschreibung |
|---|---|
| `fremd_count` | Eigene Patienten, die auf Fremdstationen ausgelagert sind (stationsunabhängig) |

### 2.3 Stammdaten (selten geändert)

| Feld | Beschreibung |
|---|---|
| `station_name` | Bezeichnung der Station |
| `plan_beds` | Planbettenzahl |
| `color` | Visualisierungsfarbe |

---

## 3. Datenbankschema (PostgreSQL 18)

### Tabellen

```sql
stations
  station_id    SERIAL PRIMARY KEY
  name          VARCHAR(100)
  plan_beds     INTEGER
  color         VARCHAR(7)
  active        BOOLEAN DEFAULT TRUE

daily_entries
  entry_id      SERIAL PRIMARY KEY
  station_id    INTEGER REFERENCES stations
  date          DATE
  occupied      INTEGER
  admissions    INTEGER
  discharges    INTEGER
  blocked_beds  INTEGER DEFAULT 0

daily_fremd
  date          DATE PRIMARY KEY
  count         INTEGER DEFAULT 0

calendar_tags
  tag_id        SERIAL PRIMARY KEY
  tag_name      VARCHAR(100)       -- z.B. "Heiligabend", "Sommerferien"
  tag_category  VARCHAR(50)        -- FEIERTAG | SCHULFERIEN | BETRIEBLICH | EXTERN | SONSTIGES
  is_automatic  BOOLEAN DEFAULT FALSE

day_tags
  date          DATE
  tag_id        INTEGER REFERENCES calendar_tags
  source        VARCHAR(10)        -- AUTO | MANUAL
  comment       TEXT               -- optionaler Freitext
  PRIMARY KEY (date, tag_id)
  -- max. 5 Tags pro Tag (per Constraint / App-Logik)

tag_multipliers                    -- systemberechnet, nicht manuell
  tag_id        INTEGER REFERENCES calendar_tags
  metric        VARCHAR(20)        -- AUSLASTUNG | ADMISSIONS | DISCHARGES
  multiplier    NUMERIC(5,3)
  sample_size   INTEGER
  confidence    NUMERIC(4,3)
  last_calculated TIMESTAMP
```

### Technische Hinweise PostgreSQL 18

- `GENERATE_SERIES` für lückenlose Datumsreihen in Reports
- Window Functions (`LAG`, `LEAD`, `AVG OVER`) für Nachholeffekt-Berechnungen
- Materialized Views für vorberechnete Multiplikatoren und Prognosen
- `date_trunc` + `EXTRACT` für Kalenderwochen- und Monatsaggregationen
- `JSONB` für flexible Metadaten in `day_tags` (optional)

---

## 4. Tag-System

### 4.1 Philosophie

Jeder Tag erhält **bis zu 5 Tags**, da Mehrfachbelegungen auftreten können (z.B. Weihnachtsferien + Heiligabend + Samstag). Tags sind **namentlich granular**, da unterschiedliche Events unterschiedliche emotionale Gewichtung bei Patienten haben.

Beispiel:

| Datum | Tags |
|---|---|
| 24.12. | `Heiligabend` · `Weihnachtsferien` · `Samstag` |
| 31.12. | `Silvester` · `Weihnachtsferien` · `Dienstag` |
| 03.10. | `Tag der Deutschen Einheit` · `Mittwoch` |
| Brückentag Fr | `Brückentag` · `Herbstferien` · `Freitag` |

### 4.2 Automatische Tags (aus Datum ableitbar)

**Bundesweite Feiertage** *(einmalig konfiguriert, jährlich berechnet)*

| Feiertag | Typ |
|---|---|
| Neujahr (01.01.) | Fix |
| Karfreitag | Beweglich |
| Ostersonntag | Beweglich |
| Ostermontag | Beweglich |
| Tag der Arbeit (01.05.) | Fix |
| Christi Himmelfahrt | Beweglich |
| Pfingstsonntag | Beweglich |
| Pfingstmontag | Beweglich |
| Tag der Deutschen Einheit (03.10.) | Fix |
| 1. Weihnachtstag (25.12.) | Fix |
| 2. Weihnachtstag (26.12.) | Fix |
| **Heiligabend (24.12.)** | Fix *(kein offizieller Feiertag, aber faktisch gleichwertig)* |

> Regionale Feiertage (Sachsen-Anhalt) werden bewusst **nicht** erfasst, um das System wartbar zu halten.

**Schulferienblöcke** *(Core-Zeiten, jährlich konfigurierbar)*

| Block | Begründung |
|---|---|
| Sommerferien | Stärkster Einbruch – längste Familienreisezeit |
| Osterferien | Traditionell starke Familienreisezeit |
| Herbstferien | Wachsende Bedeutung für 10-Tages-Familienurlaube |
| Winterferien | Ski- und Familienreisezeit |
| Weihnachtsferien | Überlagert sich mit Feiertagen – Sonderfall |

> Patienten sind typischerweise mittleren Alters mit schulpflichtigen Kindern. Ferien bedeuten daher **weniger** Aufnahmen (Familienzeit hat Vorrang), nicht mehr.

**Wochentag** *(immer automatisch gesetzt)*

Einer der stärksten Prädiktoren für Bewegung (Zugänge/Abgänge). Montag und Freitag zeigen typischerweise höhere Bewegung, Wochenenden geringere Aktivität.

**Brückentage** *(automatisch erkennbar)*

Freitag zwischen Feiertag und Wochenende – eigenständiger Tag-Typ.

### 4.3 Manuelle Tags (per Dropdown)

**Betrieblich**
- Aufnahmestopp
- Personalengpass
- Stationsteilschließung / Renovierung
- Verlegungsaktion intern

**Extern**
- Einweiserpause
- Kostenträger-Problem (Genehmigungsstau)
- Epidemische Lage

**Sonstiges**
- Extremwetter
- Freitext-Kommentar *(immer optional verfügbar)*

---

## 5. Datenfluss täglich

```
1. Systemjob (Mitternacht / App-Start)
   → Feiertage und Ferienblöcke des Tages prüfen
   → Wochentag setzen
   → day_tags automatisch befüllen (source = AUTO)

2. Tageseingabe durch Chefärztin (~60 Sekunden)
   → daily_entries pro Station (belegt, Zugänge, Abgänge, gesperrt)
   → daily_fremd eintragen
   → Automatische Tags prüfen / bei Bedarf ergänzen (Dropdown, max. 5 gesamt)
   → Optionaler Freitext-Kommentar

3. Systemjob (nach Speicherung)
   → tag_multipliers neu berechnen (ab min. 5 Datenpunkten pro Tag-Typ)
   → Prognose-Cache aktualisieren
```

### Plausibilitätsprüfungen

- `occupied` sollte `plan_beds` nicht dauerhaft überschreiten → Warnung
- `occupied(t) - occupied(t-1)` sollte grob mit `admissions - discharges` übereinstimmen → Hinweis (keine Blockierung, da interne Verlegungen Abweichungen erklären)
- Fehlende Tage werden im Dashboard markiert, **nicht** interpoliert

---

## 6. Multiplikator-Modell

### Berechnung

```
Multiplikator = Ø Auslastung an [Tag-Typ] / Ø Auslastung Standard-Tag
```

**Beispiel:**

| Situation | Wert |
|---|---|
| Ø Standard-Tag | 88 % |
| Ø Heiligabend | 62 % |
| → Multiplikator Heiligabend | 0,70 |

### Drei separate Multiplikatoren je Tag-Typ

Da die Verweildauer 21 Tage beträgt, reagiert die **Belegung** träge auf Events. Die eigentlichen Ausschläge zeigen sich bei:

- **Zugänge** – brechen an Feiertagen / Ferienstart ein
- **Abgänge** – häufen sich *vor* Feiertagen (Heimkehrdruck)
- **Auslastung** – verändert sich zeitversetzt (~1 Woche nach dem Event)

Daher wird für jede Metrik ein eigener Multiplikator berechnet.

### Konfidenz

Je mehr Datenpunkte pro Tag-Typ vorliegen, desto verlässlicher der Multiplikator. Das System zeigt transparent an, wie viele Datenpunkte dem Wert zugrunde liegen (`sample_size`).

> In Jahr 1 sind Multiplikatoren noch wenig aussagekräftig. Ab Jahr 2 entsteht echte Prognosefähigkeit.

---

## 7. Nutzung der Daten

### 7.1 Rückblickend (Reporting)

**Operative Ebene**
- Tagesauslastung je Station und gesamt
- Wochenverlauf Zugänge / Abgänge / Belegung
- Monats- und Quartalsberichte mit Vorjahresvergleich

**Analytische Ebene**
- Auslastung gefiltert nach Tag-Typ (*"alle Heiligabende"*, *"alle Sommerferienwochen"*)
- Vergleich Standard-Tag vs. getaggte Tage
- **Nachholeffekt-Analyse:** Zugänge in den 7 Tagen nach Ferienende – kommen Patienten vermehrt direkt nach den Ferien?
- Saisonalitätsprofil: Ø-Auslastung je Kalenderwoche über alle Jahre
- Stationsvergleich: Reagieren einzelne Stationen unterschiedlich auf Events?
- Tag-bereinigte Auslastung: *"Bereinigt um Feiertage und Ferien wäre die Auslastung X % statt Y %"*

### 7.2 Vorausschauend (Prognose)

**Kurzfristig (nächste 2 Wochen)**
- Erwartete Auslastung auf Basis Multiplikatoren
- Erwartete Zugänge / Abgänge separat
- Konfidenzband: Wie viele Datenpunkte stützen den Multiplikator?

**Mittelfristig (nächste 3 Monate)**
- Kalender-Vorschau mit automatisch gesetzten Tags
- Identifikation kritischer Zeiträume (drohende Überauslastung / Unterauslastung)
- Planungshilfe: Wann sind Renovierungen oder Bettenreduktionen sinnvoll?

**Langfristig (Jahresplanung)**
- Kapazitätsplanung auf Basis historischer Saisonkurve
- Personalbedarfsprognose abgeleitet aus erwartetem Patientenaufkommen

### 7.3 Strategisch (Klinikleitung)

- Jahresbericht mit tag-bereinigten Kennzahlen
- Trendanalyse: Verändert sich der Herbst- / Winterferieneffekt über die Jahre?
- Frühwarnsystem: Anomalie-Erkennung bei signifikanter Abweichung von der Prognose
- Benchmark-Grundlage für Gespräche mit Kostenträgern und Klinikträger

---

## 8. Offene Fragen / Nächste Schritte

- [ ] DDL-Schema (CREATE TABLE Statements) ausarbeiten
- [ ] Feriendaten-Quelle festlegen (manuell jährlich vs. API)
- [ ] Osterdatum-Berechnung implementieren (bewegliche Feiertage)
- [ ] Mindest-Datenpunkte für Multiplikator-Aktivierung definieren (Empfehlung: 5)
- [ ] Export-Funktion (CSV / Excel) für externe Auswertungen
- [ ] Backup-Strategie für PostgreSQL definieren

---

*Dokument erstellt mit Claude · Anthropic · März 2026*
