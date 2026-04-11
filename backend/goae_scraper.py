#!/usr/bin/env python3
"""
goae_scraper.py

Scrapet alle GOÄ-Ziffern von abrechnungsstelle.com
und speichert sie als JSON-Datei für den Datenbank-Import.

Basierend auf: konzept/goae_scraper_agent_prompt.md
"""

import asyncio
import json
import re
import logging
from typing import Optional
from dataclasses import dataclass, field, asdict
from pathlib import Path

from playwright.async_api import async_playwright, Page

# ─── Konfiguration ────────────────────────────────────────────────────────────

OUTPUT_FILE = Path(__file__).parent / "app" / "data" / "goae_komplett.json"

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
    "https://abrechnungsstelle.com/goae/3630h-4014/",
    "https://abrechnungsstelle.com/goae/4020-4469/",
    "https://abrechnungsstelle.com/goae/4500-4787/",
    "https://abrechnungsstelle.com/goae/4800-5380/",
    "https://abrechnungsstelle.com/goae/5400-6018/",
    "https://abrechnungsstelle.com/goae/goae-abschnitt/analog/",
]

REQUEST_DELAY_SECONDS = 1.5
HEADLESS = True

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

def parse_ausschluss(raw: str) -> Optional[list]:
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

def detect_abschnitt(ziffer: str, url: str) -> str:
    """Abschnitt aus der URL oder Ziffernbereich ableiten (offizielle GOÄ-Struktur)."""
    # Analoge Ziffern
    if 'analog' in url:
        return 'ANALOG'
    
    # Buchstaben-Ziffern → Abschnitt A (Gebühren in besonderen Fällen)
    if ziffer in ('A', 'B', 'C', 'D'):
        return 'A'
    if ziffer.startswith('K'):
        return 'A'
    
    # Numerischen Teil extrahieren
    try:
        num = int(re.match(r'^(\d+)', ziffer).group(1))
    except (AttributeError, ValueError):
        return 'A'  # Fallback statt '?'
    
    # Offizielle GOÄ-Abschnitte laut Gebührenverzeichnis
    if num <= 109:    return 'B'       # Grundleistungen und allgemeine Leistungen
    elif num <= 199:  return 'B'       # Noch Abschnitt B (110-199)
    elif num <= 449:  return 'C'       # Nichtgebietsbezogene Sonderleistungen
    elif num <= 498:  return 'D'       # Anästhesieleistungen
    elif num <= 569:  return 'E'       # Physikalisch-medizinische Leistungen
    elif num <= 599:  return 'E'       # Noch Abschnitt E
    elif num <= 793:  return 'F'       # Innere Medizin, Kinderheilkunde, Dermatologie
    elif num <= 887:  return 'G'       # Neurologie, Psychiatrie und Psychotherapie
    elif num <= 999:  return 'G'       # Noch Abschnitt G
    elif num <= 1168: return 'H'       # Geburtshilfe und Gynäkologie
    elif num <= 1199: return 'H'       # Noch Abschnitt H
    elif num <= 1386: return 'I'       # Augenheilkunde
    elif num <= 1399: return 'I'       # Noch Abschnitt I
    elif num <= 1639: return 'J'       # Hals-, Nasen-, Ohrenheilkunde
    elif num <= 1699: return 'J'       # Noch Abschnitt J
    elif num <= 1860: return 'K'       # Urologie
    elif num <= 1999: return 'K'       # Noch Abschnitt K
    elif num <= 3321: return 'L'       # Chirurgie, Orthopädie
    elif num <= 3499: return 'L'       # Noch Abschnitt L
    elif num <= 4787: return 'M'       # Laboratoriumsuntersuchungen
    elif num <= 4873: return 'N'       # Histologie, Zytologie und Zytogenetik
    elif num <= 4999: return 'N'       # Noch Abschnitt N
    elif num <= 5855: return 'O'       # Strahlendiagnostik, MRT, Strahlentherapie
    elif num <= 5999: return 'O'       # Noch Abschnitt O
    elif num <= 6018: return 'P'       # Sektionsleistungen
    else:             return 'P'       # Fallback

# ─── Scraping ─────────────────────────────────────────────────────────────────

async def extract_entries_from_page(page: Page, url: str) -> list:
    """Extrahiert alle GOÄ-Einträge von einer Unterseite."""
    logging.info(f"Lade: {url}")
    await page.goto(url, wait_until="domcontentloaded", timeout=30_000)
    
    try:
        await page.wait_for_selector('.w-grid-item', timeout=15_000)
    except Exception:
        logging.warning(f"  Keine .w-grid-item gefunden auf {url}")
        return []

    raw_entries = await page.evaluate("""
        () => {
            const results = [];
            document.querySelectorAll('.w-grid-item').forEach(card => {
                try {
                    const ziffer = card.querySelector('.ziffer .w-post-elm-value')
                                       ?.textContent?.trim() || '';
                    if (!ziffer) return;

                    const titleEl = card.querySelector('h3.entry-title a');
                    const title   = titleEl?.textContent?.trim() || '';
                    const href    = titleEl?.href || '';

                    const divs = Array.from(card.querySelectorAll('.w-html'))
                                      .map(d => d.textContent.trim());

                    const ausschlussRaw = card.querySelector('.usg_html_4')
                                             ?.textContent?.trim() || '';

                    const pTags = Array.from(card.querySelectorAll('p'))
                                       .map(p => p.textContent.trim())
                                       .filter(t => t.length > 0);
                    const hinweistext = pTags.length > 0
                        ? pTags.join('\\n\\n')
                        : '';

                    // Katalog-Einträge für gebündelte Ziffern extrahieren
                    const katalogItems = [];
                    const repeaterRows = card.querySelectorAll('.repeater-row');
                    repeaterRows.forEach(row => {
                        const subZiffer = row.querySelector('.katalog-ziffer')
                                             ?.textContent?.trim() || '';
                        const subBeschreibung = row.querySelector('.katalog-text')
                                                   ?.textContent?.trim() || '';
                        if (subZiffer && /^\d+/.test(subZiffer)) {
                            katalogItems.push({
                                ziffer: subZiffer,
                                beschreibung: subBeschreibung
                            });
                        }
                    });

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
                        katalogItems,
                    });
                } catch (_) {}
            });
            return results;
        }
    """)

    entries = []
    for r in raw_entries:
        abschnitt = detect_abschnitt(r['ziffer'], url)
        punkte = parse_int(r['punktzahl'])
        regel_faktor = parse_factor(r['regelFaktor'])
        hoechst_faktor = parse_factor(r['hoechstFaktor'])
        ausschluss = parse_ausschluss(r['ausschlussRaw'])
        hinweis = r['hinweistext'] or None
        detail_url = r['href'] or None
        parent_beschreibung = extract_description(r['title'])
        
        katalog = r.get('katalogItems', [])
        
        if katalog and '-' in r['ziffer']:
            # Gebündelte Ziffer → in Einzeleinträge auflösen
            for sub in katalog:
                sub_abschnitt = detect_abschnitt(sub['ziffer'], url)
                entry = {
                    "ziffer": sub['ziffer'],
                    "beschreibung": sub['beschreibung'],
                    "punkte": punkte if punkte is not None else 0,
                    "abschnitt": sub_abschnitt,
                    "faktor_regelhöchst": regel_faktor if regel_faktor else 2.3,
                    "faktor_höchst": hoechst_faktor if hoechst_faktor else 3.5,
                    "ausschlussziffern": ausschluss,
                    "hinweistext": hinweis,
                    "detail_url": detail_url,
                }
                entries.append(entry)
            logging.info(f"    Bündel {r['ziffer']} → {len(katalog)} Einzelziffern aufgelöst")
        else:
            # Normale Einzelziffer
            entry = {
                "ziffer": r['ziffer'],
                "beschreibung": parent_beschreibung,
                "punkte": punkte if punkte is not None else 0,
                "abschnitt": abschnitt,
                "faktor_regelhöchst": regel_faktor if regel_faktor else 2.3,
                "faktor_höchst": hoechst_faktor if hoechst_faktor else 3.5,
                "ausschlussziffern": ausschluss,
                "hinweistext": hinweis,
                "detail_url": detail_url,
            }
            entries.append(entry)

    logging.info(f"  → {len(entries)} Einträge")
    return entries

# ─── Haupt-Orchestrierung ─────────────────────────────────────────────────────

async def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s  %(levelname)-8s  %(message)s",
        datefmt="%H:%M:%S",
    )

    all_entries = []

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

    # Deduplizierung (letzte Version gewinnt)
    seen = {}
    for entry in all_entries:
        seen[entry['ziffer']] = entry
    unique = list(seen.values())
    logging.info(f"Nach Deduplizierung: {len(unique)} eindeutige Ziffern")

    # JSON speichern
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(unique, f, ensure_ascii=False, indent=2)

    logging.info(f"Gespeichert: {OUTPUT_FILE}")

if __name__ == "__main__":
    asyncio.run(main())
