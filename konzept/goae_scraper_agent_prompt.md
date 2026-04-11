# GOÄ-Ziffern Web-Scraping → PostgreSQL: Agent-Runbook

> **Zweck:** Dieses Dokument beschreibt Schritt für Schritt, wie alle GOÄ-Ziffern
> (Gebührenordnung für Ärzte) von `abrechnungsstelle.com` extrahiert und in eine
> PostgreSQL-Datenbank geschrieben werden. Es ist als ausführbares Runbook für einen
> KI-gestützten Coding-Agent (Claude Code, Codex, Gemini CLI o.ä.) verfasst.

---

## 1. Ausgangslage & Ziel

| Eigenschaft | Wert |
|---|---|
| Quelle | `https://abrechnungsstelle.com/goae/ziffern/` |
| Anzahl Einträge | ~2.525 GOÄ-Ziffern (Stand 2026) |
| Ziel | PostgreSQL-Tabelle `goae_ziffern` |
| Stack | Python 3.10+, Playwright (async), asyncpg oder psycopg3 |

---

## 2. Website-Struktur

Die Hauptseite `https://abrechnungsstelle.com/goae/ziffern/` enthält einen
**Ziffernindex** mit Links zu 16 Unterseiten. Jede Unterseite listet einen
Ziffernbereich als HTML-Kacheln.

### 2.1 Alle Unterseiten-URLs (vollständige Liste)

```python
SUBPAGE_URLS = [
    "https://abrechnungsstelle.com/goae/1-498/",
    "https://abrechnungsstelle.com/goae/500-887/",
    "https://abrechnungsstelle.com/goae/1001-1386/",
    "https://abrechnungsstelle.com/goae/1400-1860/",
    "https://abrechnungsstelle.com/goae/2000-2358/",
    "https://abrechnungsstelle.com/goae/2380-2732/",
    "https://abrechnungsstelle.com/goae/2750-3097/",
    "https://abrechnungsstelle.com/goae/3120-3321/",
    "https://abrechnungsstelle.com/goae/3500-3615/",
    "https://abrechnungsstelle.com/goae/3630h-4014/",   # Achtung: kein Bindestrich vor 'h'
    "https://abrechnungsstelle.com/goae/4020-4469/",
    "https://abrechnungsstelle.com/goae/4500-4787/",
    "https://abrechnungsstelle.com/goae/4800-5380/",
    "https://abrechnungsstelle.com/goae/5400-6018/",
    "https://abrechnungsstelle.com/goae/goae-abschnitt/analog/",  # Analogziffern
]
```

> **Hinweis:** Die URL für Ziffern 3630.H bis 4014 lautet `3630h-4014/`
> (nicht `3630-h-4014/` oder `3630.h-4014/`).

### 2.2 HTML-Struktur einer Einzel-Kachel (vollständig)

Jede GOÄ-Ziffer wird als `.w-grid-item` gerendert. Die Kachel enthält
**drei inhaltliche Blöcke**: Gebühren, Ausschlussziffern und Hinweistext.

```html
<div class="w-grid-item">

  <!-- ── Block 1: Gebühren ─────────────────────────────────────── -->

  <!-- Label-Badge -->
  <div class="w-html usg_html_2 label-go">
    GOÄ-Ziffer: <span class="w-post-elm-value">3500</span>
  </div>

  <!-- Titel mit Detaillink -->
  <h3 class="entry-title">
    <a href="https://abrechnungsstelle.com/goae/goae-3500/">
      GOÄ 3500: Blut im Stuhl, dreimalige Untersuchung
    </a>
  </h3>

  <!-- Gebühren-Felder (sequenzierte .w-html divs): -->
  <!-- Index 0: "GOÄ-Ziffer: 3500"  (Label, class: usg_html_2)   -->
  <!-- Index 1: "90 Punkte"         (Label, class: usg_html_8)   -->
  <!-- Index 2: ""                  (leer,  class: usg_html_13)  -->
  <!-- Index 3: "90"                (Punktzahl numerisch, usg_html_7)   -->
  <!-- Index 4: "1,0"               (Einfachfaktor,       usg_html_1)  -->
  <!-- Index 5: "5,25 €"            (Einfachsatz,         usg_html_12) -->
  <!-- Index 6: "1,15"              (Regelhöchstfaktor,   usg_html_9)  -->
  <!-- Index 7: "6,03 €"            (Regelhöchstsatz,     usg_html_5)  -->
  <!-- Index 8: "1,3"               (Höchstfaktor,        usg_html_3)  -->
  <!-- Index 9: "6,82 €"            (Höchstsatz,          usg_html_6)  -->
  <!-- Index 10: ""                 (leer,  class: usg_html_11)  -->

  <!-- ── Block 2: Ausschlussziffern ──────────────────────────────
       Selektor: .usg_html_4  (→ Index 11, WENN vorhanden)
       Leer (""), wenn keine Ausschlussziffern existieren.
       Format: "Ausschlussziffern: GOÄ 27, GOÄ 28"
  -->
  <div class="w-html usg_html_4">
    Ausschlussziffern: GOÄ 27, GOÄ 28
  </div>

  <!-- ── Block 3: Hinweistext ─────────────────────────────────────
       Selektor: p  (ein oder mehrere <p>-Tags innerhalb der Kachel)
       Fehlt vollständig, wenn kein Hinweis vorhanden.
  -->
  <p>Die Kosten für ausgegebenes Testmaterial sind anstelle der Leistung
     nach Nummer 3500 berechnungsfähig, wenn die Auswertung aus Gründen
     unterbleibt, die der Arzt nicht zu vertreten hat.</p>

</div>
```

> **Wichtig – variable Faktoren:** Die Multiplikatoren (Regelhöchst- und
> Höchstfaktor) sind **nicht fix**. Während GOÄ-Abschnitt A (allgemeine
> Leistungen) 2,3 / 3,5 verwendet, nutzen Laborleistungen (Abschnitt M)
> 1,15 / 1,3. Der Agent muss die Faktoren aus Index 4 / 6 / 8 lesen,
> **nicht hartcodieren**.

### 2.3 CSS-Selektoren (verifiziert in Chrome DevTools)

| Feld | Selektor | Anmerkung |
|---|---|---|
| Container pro Ziffer | `.w-grid-item` | Ein Element pro Ziffer |
| Ziffernummer | `.ziffer .w-post-elm-value` | Auch alphanumerisch: "250a", "K1" |
| Vollständiger Titel | `h3.entry-title a` (textContent) | Enthält Präfix "GOÄ X: " |
| Detail-URL | `h3.entry-title a` (href-Attribut) | Link zur Einzelseite |
| Punktzahl (numerisch) | `.w-html` Index 3 | Ganzzahl als String |
| Einfachfaktor | `.w-html` Index 4 | z.B. "1,0" |
| Einfachsatz (€) | `.w-html` Index 5 | z.B. "5,25 €" |
| Regelhöchstfaktor | `.w-html` Index 6 | z.B. "1,15" oder "2,3" |
| Regelhöchstsatz (€) | `.w-html` Index 7 | z.B. "6,03 €" |
| Höchstfaktor | `.w-html` Index 8 | z.B. "1,3" oder "3,5" |
| Höchstsatz (€) | `.w-html` Index 9 | z.B. "6,82 €" |
| **Ausschlussziffern** | **`.usg_html_4`** | **Leerstring wenn keine vorhanden** |
| **Hinweistext** | **`p`** (alle innerhalb `.w-grid-item`) | **Fehlt vollständig wenn kein Hinweis** |

---

## 3. Datenmodell & PostgreSQL-Schema

### 3.1 CREATE TABLE

```sql
CREATE TABLE IF NOT EXISTS goae_ziffern (
    id                SERIAL PRIMARY KEY,
    ziffer            VARCHAR(20)   NOT NULL,
        -- z.B. "1", "250a", "3630.H", "K1", "A"–"D"
    beschreibung      TEXT          NOT NULL,
        -- Leistungsbeschreibung ohne Präfix "GOÄ X: "
    punktzahl         INTEGER,
        -- GOÄ-Punktzahl; NULL wenn nicht angegeben
    einfachfaktor     NUMERIC(4, 2),
        -- Immer 1,0 – trotzdem aus Seite lesen für Konsistenz
    einfachsatz       NUMERIC(10, 2),
        -- Gebühr bei Faktor 1,0 in Euro; NULL bei Analogziffern ohne Satz
    regelfaktor       NUMERIC(4, 2),
        -- z.B. 2,3 (Allgemein) oder 1,15 (Labor); NULL wenn nicht angegeben
    regelhoechstsatz  NUMERIC(10, 2),
        -- Gebühr beim Regelfaktor; NULL wenn nicht angegeben
    hoechstfaktor     NUMERIC(4, 2),
        -- z.B. 3,5 (Allgemein) oder 1,3 (Labor); NULL wenn nicht angegeben
    hoechstsatz       NUMERIC(10, 2),
        -- Gebühr beim Höchstfaktor; NULL wenn nicht angegeben
    ausschlussziffern TEXT[],
        -- Array der Ziffernummern, z.B. ARRAY['27','28']; NULL wenn keine
    hinweistext       TEXT,
        -- Freitext-Anmerkung aus <p>-Tag(s); NULL wenn kein Hinweis;
        -- mehrere <p>-Tags werden mit Zeilenumbruch konkateniert
    detail_url        TEXT,
        -- Link zur Detailseite der Ziffer
    created_at        TIMESTAMPTZ   DEFAULT NOW(),
    UNIQUE (ziffer)
);

-- Index: schnelle Suche nach Ziffernummer
CREATE INDEX IF NOT EXISTS idx_goae_ziffer
    ON goae_ziffern (ziffer);

-- Index: Volltextsuche Beschreibung
CREATE INDEX IF NOT EXISTS idx_goae_beschreibung_fts
    ON goae_ziffern
    USING gin(to_tsvector('german', beschreibung));

-- Index: Volltextsuche Hinweistext (für Ziffern mit Anmerkung)
CREATE INDEX IF NOT EXISTS idx_goae_hinweis_fts
    ON goae_ziffern
    USING gin(to_tsvector('german', coalesce(hinweistext, '')));

-- Index: Abfrage "welche Ziffern schließen Ziffer X aus?"
CREATE INDEX IF NOT EXISTS idx_goae_ausschluss
    ON goae_ziffern
    USING gin(ausschlussziffern);
```

### 3.2 Datentypen & Besonderheiten

- **`ziffer` ist `VARCHAR`**, keine Zahl – Sonderfälle: `"250a"`, `"3630.H"`,
  `"K1"`, `"A"`, `"B"`, `"C"`, `"D"`.
- **Geldbeträge** kommen im deutschen Format: `"5,25 €"`. Konvertierung:
  `.replace(' €','').replace(',','.')` → `float()`. Bei `"-"` oder Leerstring
  → `NULL`.
- **Faktoren** sind ebenfalls kommagetrennt: `"1,15"` → `1.15`.
- **Ausschlussziffern** werden als `TEXT[]`-Array gespeichert – das erlaubt
  effiziente Abfragen wie `'27' = ANY(ausschlussziffern)`.
  Parsing: `"Ausschlussziffern: GOÄ 27, GOÄ 28"` → `['27', '28']`
  (Präfix entfernen, nach Komma splitten, `"GOÄ "` entfernen).
  Selektor: `.usg_html_4` (stabiler Class-Name, nicht Index-abhängig).
- **Hinweistext** stammt aus `<p>`-Tags innerhalb der Kachel. Mehrere
  Absätze werden mit `"\n\n"` verbunden. Bei vielen Ziffern fehlt das
  `<p>`-Tag komplett → `NULL`.
- **Analogziffern** haben oft kein Regel- oder Höchstsatz → `NULL`.

---

## 4. Vollständiges Python-Skript

```python
#!/usr/bin/env python3
"""
goae_scraper.py

Scrapet alle GOÄ-Ziffern (inkl. Ausschlussziffern und Hinweistexte)
von abrechnungsstelle.com und schreibt sie in eine PostgreSQL-Datenbank.

Abhängigkeiten:
    pip install playwright asyncpg
    playwright install chromium
"""

import asyncio
import re
import logging
from typing import Optional
from dataclasses import dataclass, field

import asyncpg
from playwright.async_api import async_playwright, Page

# ─── Konfiguration ────────────────────────────────────────────────────────────

DB_DSN = "postgresql://user:password@localhost:5432/dbname"

SUBPAGE_URLS = [
    "https://abrechnungsstelle.com/goae/1-498/",
    "https://abrechnungsstelle.com/goae/500-887/",
    "https://abrechnungsstelle.com/goae/1001-1386/",
    "https://abrechnungsstelle.com/goae/1400-1860/",
    "https://abrechnungsstelle.com/goae/2000-2358/",
    "https://abrechnungsstelle.com/goae/2380-2732/",
    "https://abrechnungsstelle.com/goae/2750-3097/",
    "https://abrechnungsstelle.com/goae/3120-3321/",
    "https://abrechnungsstelle.com/goae/3500-3615/",
    "https://abrechnungsstelle.com/goae/3630h-4014/",  # kein Bindestrich vor 'h'!
    "https://abrechnungsstelle.com/goae/4020-4469/",
    "https://abrechnungsstelle.com/goae/4500-4787/",
    "https://abrechnungsstelle.com/goae/4800-5380/",
    "https://abrechnungsstelle.com/goae/5400-6018/",
    "https://abrechnungsstelle.com/goae/goae-abschnitt/analog/",
]

REQUEST_DELAY_SECONDS = 1.5
HEADLESS = True

# ─── Datenklasse ──────────────────────────────────────────────────────────────

@dataclass
class GoaeZiffer:
    ziffer: str
    beschreibung: str
    punktzahl: Optional[int]               = None
    einfachfaktor: Optional[float]         = None
    einfachsatz: Optional[float]           = None
    regelfaktor: Optional[float]           = None
    regelhoechstsatz: Optional[float]      = None
    hoechstfaktor: Optional[float]         = None
    hoechstsatz: Optional[float]           = None
    ausschlussziffern: Optional[list[str]] = None  # z.B. ['27', '28']
    hinweistext: Optional[str]             = None
    detail_url: Optional[str]              = None

# ─── Hilfsfunktionen ──────────────────────────────────────────────────────────

def parse_euro(text: str) -> Optional[float]:
    """'5,25 €' → 5.25  |  '' / '-' → None"""
    cleaned = text.replace('\xa0', '').replace(' €', '').replace('€', '') \
                  .replace(',', '.').strip()
    if not cleaned or cleaned == '-':
        return None
    try:
        return float(cleaned)
    except ValueError:
        return None

def parse_int(text: str) -> Optional[int]:
    """'90' → 90  |  '' → None"""
    text = text.strip()
    if not text:
        return None
    try:
        return int(text)
    except ValueError:
        return None

def parse_factor(text: str) -> Optional[float]:
    """'1,15' → 1.15  |  '' / '-' → None"""
    text = text.strip()
    if not text or text == '-':
        return None
    try:
        return float(text.replace(',', '.'))
    except ValueError:
        return None

def parse_ausschluss(raw: str) -> Optional[list[str]]:
    """
    'Ausschlussziffern: GOÄ 27, GOÄ 28'  →  ['27', '28']
    ''                                    →  None
    """
    raw = raw.strip()
    if not raw or 'Ausschlussziffern' not in raw:
        return None
    body = raw.replace('Ausschlussziffern:', '').strip()
    ziffern = [
        z.strip().replace('GOÄ ', '').strip()
        for z in body.split(',')
        if z.strip()
    ]
    return ziffern if ziffern else None

def extract_description(full_title: str) -> str:
    """'GOÄ 3500: Blut im Stuhl ...' → 'Blut im Stuhl ...'"""
    return re.sub(r'^GOÄ\s+\S+:\s*', '', full_title).strip()

# ─── Scraping ─────────────────────────────────────────────────────────────────

async def extract_entries_from_page(page: Page, url: str) -> list[GoaeZiffer]:
    """Extrahiert alle GOÄ-Einträge von einer Unterseite."""
    logging.info(f"Lade: {url}")
    await page.goto(url, wait_until="domcontentloaded", timeout=30_000)
    await page.wait_for_selector('.w-grid-item', timeout=15_000)

    raw_entries = await page.evaluate("""
        () => {
            const results = [];
            document.querySelectorAll('.w-grid-item').forEach(card => {
                try {
                    // Ziffernummer
                    const ziffer = card.querySelector('.ziffer .w-post-elm-value')
                                       ?.textContent?.trim() || '';
                    if (!ziffer) return;

                    // Titel & Detail-URL
                    const titleEl = card.querySelector('h3.entry-title a');
                    const title   = titleEl?.textContent?.trim() || '';
                    const href    = titleEl?.href || '';

                    // Gebühren-Felder (sequenzierte .w-html divs)
                    const divs = Array.from(card.querySelectorAll('.w-html'))
                                      .map(d => d.textContent.trim());

                    // Ausschlussziffern: stabiler Klassen-Selektor .usg_html_4
                    // (ist leer "" wenn keine Ausschlüsse vorhanden)
                    const ausschlussRaw = card.querySelector('.usg_html_4')
                                             ?.textContent?.trim() || '';

                    // Hinweistext: alle <p>-Tags innerhalb der Kachel
                    // (fehlen komplett wenn kein Hinweis vorhanden)
                    const pTags = Array.from(card.querySelectorAll('p'))
                                       .map(p => p.textContent.trim())
                                       .filter(t => t.length > 0);
                    const hinweistext = pTags.length > 0
                        ? pTags.join('\\n\\n')
                        : '';

                    results.push({
                        ziffer,
                        title,
                        href,
                        punktzahl:        divs[3]  || '',
                        einfachFaktor:    divs[4]  || '',
                        einfachsatz:      divs[5]  || '',
                        regelFaktor:      divs[6]  || '',
                        regelhoechstsatz: divs[7]  || '',
                        hoechstFaktor:    divs[8]  || '',
                        hoechstsatz:      divs[9]  || '',
                        ausschlussRaw,
                        hinweistext,
                    });
                } catch (_) {}
            });
            return results;
        }
    """)

    entries = []
    for r in raw_entries:
        entries.append(GoaeZiffer(
            ziffer            = r['ziffer'],
            beschreibung      = extract_description(r['title']),
            punktzahl         = parse_int(r['punktzahl']),
            einfachfaktor     = parse_factor(r['einfachFaktor']),
            einfachsatz       = parse_euro(r['einfachsatz']),
            regelfaktor       = parse_factor(r['regelFaktor']),
            regelhoechstsatz  = parse_euro(r['regelhoechstsatz']),
            hoechstfaktor     = parse_factor(r['hoechstFaktor']),
            hoechstsatz       = parse_euro(r['hoechstsatz']),
            ausschlussziffern = parse_ausschluss(r['ausschlussRaw']),
            hinweistext       = r['hinweistext'] or None,
            detail_url        = r['href'] or None,
        ))

    logging.info(f"  → {len(entries)} Einträge")
    return entries

# ─── Datenbank ────────────────────────────────────────────────────────────────

async def create_table(conn: asyncpg.Connection) -> None:
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS goae_ziffern (
            id                SERIAL PRIMARY KEY,
            ziffer            VARCHAR(20)   NOT NULL,
            beschreibung      TEXT          NOT NULL,
            punktzahl         INTEGER,
            einfachfaktor     NUMERIC(4, 2),
            einfachsatz       NUMERIC(10, 2),
            regelfaktor       NUMERIC(4, 2),
            regelhoechstsatz  NUMERIC(10, 2),
            hoechstfaktor     NUMERIC(4, 2),
            hoechstsatz       NUMERIC(10, 2),
            ausschlussziffern TEXT[],
            hinweistext       TEXT,
            detail_url        TEXT,
            created_at        TIMESTAMPTZ   DEFAULT NOW(),
            UNIQUE (ziffer)
        );
        CREATE INDEX IF NOT EXISTS idx_goae_ziffer
            ON goae_ziffern (ziffer);
        CREATE INDEX IF NOT EXISTS idx_goae_beschreibung_fts
            ON goae_ziffern
            USING gin(to_tsvector('german', beschreibung));
        CREATE INDEX IF NOT EXISTS idx_goae_hinweis_fts
            ON goae_ziffern
            USING gin(to_tsvector('german', coalesce(hinweistext, '')));
        CREATE INDEX IF NOT EXISTS idx_goae_ausschluss
            ON goae_ziffern
            USING gin(ausschlussziffern);
    """)
    logging.info("Tabelle goae_ziffern sichergestellt.")

async def upsert_entries(conn: asyncpg.Connection,
                         entries: list[GoaeZiffer]) -> int:
    sql = """
        INSERT INTO goae_ziffern (
            ziffer, beschreibung, punktzahl,
            einfachfaktor, einfachsatz,
            regelfaktor, regelhoechstsatz,
            hoechstfaktor, hoechstsatz,
            ausschlussziffern, hinweistext, detail_url
        ) VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11,$12)
        ON CONFLICT (ziffer) DO UPDATE SET
            beschreibung      = EXCLUDED.beschreibung,
            punktzahl         = EXCLUDED.punktzahl,
            einfachfaktor     = EXCLUDED.einfachfaktor,
            einfachsatz       = EXCLUDED.einfachsatz,
            regelfaktor       = EXCLUDED.regelfaktor,
            regelhoechstsatz  = EXCLUDED.regelhoechstsatz,
            hoechstfaktor     = EXCLUDED.hoechstfaktor,
            hoechstsatz       = EXCLUDED.hoechstsatz,
            ausschlussziffern = EXCLUDED.ausschlussziffern,
            hinweistext       = EXCLUDED.hinweistext,
            detail_url        = EXCLUDED.detail_url
    """
    rows = [
        (
            e.ziffer, e.beschreibung, e.punktzahl,
            e.einfachfaktor, e.einfachsatz,
            e.regelfaktor, e.regelhoechstsatz,
            e.hoechstfaktor, e.hoechstsatz,
            e.ausschlussziffern, e.hinweistext, e.detail_url,
        )
        for e in entries
    ]
    await conn.executemany(sql, rows)
    return len(rows)

# ─── Haupt-Orchestrierung ─────────────────────────────────────────────────────

async def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s  %(levelname)-8s  %(message)s",
        datefmt="%H:%M:%S",
    )

    all_entries: list[GoaeZiffer] = []

    # 1. Scraping
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=HEADLESS)
        context = await browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            )
        )
        page = await context.new_page()

        for url in SUBPAGE_URLS:
            try:
                entries = await extract_entries_from_page(page, url)
                all_entries.extend(entries)
            except Exception as exc:
                logging.error(f"Fehler bei {url}: {exc}")
            await asyncio.sleep(REQUEST_DELAY_SECONDS)

        await browser.close()

    logging.info(f"Scraping abgeschlossen: {len(all_entries)} GOÄ-Ziffern total")

    # 2. Datenbankimport
    conn = await asyncpg.connect(DB_DSN)
    try:
        await create_table(conn)
        count = await upsert_entries(conn, all_entries)
        logging.info(f"Import abgeschlossen: {count} Zeilen eingefügt/aktualisiert")
    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(main())
```

---

## 5. Schritt-für-Schritt-Anleitung für den Agent

### Schritt 1 – Abhängigkeiten installieren
```bash
pip install playwright asyncpg
playwright install chromium
```

### Schritt 2 – Datenbankverbindung konfigurieren
`DB_DSN` in `goae_scraper.py` anpassen:
```
postgresql://<user>:<password>@<host>:<port>/<database>
```

### Schritt 3 – Skript ausführen
```bash
python goae_scraper.py
```

**Erwartete Log-Ausgabe:**
```
10:00:00  INFO      Lade: https://abrechnungsstelle.com/goae/1-498/
10:00:03  INFO        → 271 Einträge
10:00:05  INFO      Lade: https://abrechnungsstelle.com/goae/500-887/
...
10:01:30  INFO      Scraping abgeschlossen: 2525 GOÄ-Ziffern total
10:01:30  INFO      Tabelle goae_ziffern sichergestellt.
10:01:31  INFO      Import abgeschlossen: 2525 Zeilen eingefügt/aktualisiert
```

### Schritt 4 – Ergebnis verifizieren
```sql
-- Gesamtanzahl
SELECT COUNT(*) FROM goae_ziffern;
-- Erwartet: ~2525

-- Stichprobe (inkl. der neuen Felder)
SELECT ziffer,
       LEFT(beschreibung, 55)       AS beschreibung,
       punktzahl,
       regelfaktor,
       regelhoechstsatz,
       ausschlussziffern,
       LEFT(hinweistext, 60)        AS hinweis
FROM goae_ziffern
WHERE ziffer IN ('1', '3500', '3501', 'K1')
ORDER BY id;

-- NULL-Checks
SELECT
    COUNT(*) FILTER (WHERE punktzahl        IS NULL) AS ohne_punktzahl,
    COUNT(*) FILTER (WHERE einfachsatz      IS NULL) AS ohne_einfachsatz,
    COUNT(*) FILTER (WHERE ausschlussziffern IS NULL) AS ohne_ausschluss,
    COUNT(*) FILTER (WHERE hinweistext      IS NULL) AS ohne_hinweis
FROM goae_ziffern;

-- Array-Abfrage: Welche Ziffern schließen GOÄ 27 aus?
SELECT ziffer, LEFT(beschreibung, 60) AS beschreibung
FROM goae_ziffern
WHERE '27' = ANY(ausschlussziffern);

-- Volltextsuche im Hinweistext
SELECT ziffer, LEFT(hinweistext, 100) AS hinweis
FROM goae_ziffern
WHERE to_tsvector('german', coalesce(hinweistext,''))
      @@ plainto_tsquery('german', 'Testmaterial');
```

---

## 6. Bekannte Sonderfälle & Fallstricke

| Problem | Ursache | Lösung |
|---|---|---|
| URL `3630h-4014` | Webseiten-Slug ohne Bindestrich vor 'h' | Exakte URL aus Liste in §2.1 verwenden |
| Variable Faktoren (1,15 / 1,3 vs. 2,3 / 3,5) | Je nach GOÄ-Abschnitt unterschiedlich | Faktoren immer aus Index 4/6/8 lesen – nie hartcodieren |
| Alphanumerische Ziffern (`"250a"`, `"K1"`, `"A"`–`"D"`) | GOÄ-Nomenklatur | `ziffer` als `VARCHAR`, **nicht** `INTEGER` |
| Seite lädt langsam | JavaScript-schwere WordPress-Seite | `wait_for_selector('.w-grid-item')` vor Extraktion |
| Gebühr `"-"` oder leer | Analogziffern ohne feste Vergütung | `parse_euro()` liefert `None` → `NULL` in DB |
| Ausschlussziffern-Feld leer | Kein Ausschluss für diese Ziffer | `parse_ausschluss()` liefert `None` → `NULL[]` in DB |
| Mehrere `<p>`-Tags pro Kachel | Längere Anmerkungen, mehrteilig | Alle `<p>`-Inhalte mit `"\n\n"` verbinden |
| Duplikate beim Re-Run | Skript mehrfach ausgeführt | `ON CONFLICT (ziffer) DO UPDATE` – idempotent |

---

## 7. Optionale Erweiterung: Detailseiten scrapen

Jede Ziffer hat eine `detail_url` (bereits in der DB), die erweiterte Inhalte
enthält (Gerichtsurteile, Kommentare, GOÄ-Ratgeber-Texte). In einem zweiten
Durchlauf können diese ergänzt werden:

```python
# Zusätzliche Spalte anlegen
ALTER TABLE goae_ziffern ADD COLUMN IF NOT EXISTS beschreibung_lang TEXT;

# Zweiter Scraping-Pass: detail_url aus DB lesen, Detailseite öffnen,
# Hauptinhalt extrahieren (Selektor auf Detailseite prüfen),
# beschreibung_lang per UPDATE befüllen.
```

---

## 8. Automatisierte Aktualisierung (Cron)

```bash
# Monatlich am 1. um 02:00 Uhr
0 2 1 * * /pfad/zur/venv/bin/python /pfad/zu/goae_scraper.py \
    >> /var/log/goae_scraper.log 2>&1
```

---

## 9. Abhängigkeiten & Versionen

```
playwright>=1.44.0
asyncpg>=0.29.0
Python>=3.10
```

Alternativ mit `psycopg3` (synchron, kein asyncio nötig):
```bash
pip install "psycopg[binary]"
```
Dann `asyncpg.connect()` → `psycopg.connect()` und alle `await`-Aufrufe
durch synchrone Pendants ersetzen.

---

*Aktualisiert am 02.04.2026 · Datenbasis: abrechnungsstelle.com/goae/ziffern/ (Stand 2026)*
*Änderung gegenüber v1: Ausschlussziffern und Hinweistexte als Pflichtfelder ergänzt;*
*Selektor `.usg_html_4` statt fragiler Index-Adressierung; variable Faktoren dokumentiert.*
