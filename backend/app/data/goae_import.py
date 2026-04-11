"""
GOÄ-Datenimport: Lädt die vollständigen GOÄ-Ziffern aus goae_komplett.json
in die Datenbank (goae_ziffern Tabelle).

Verwendung:
    docker exec gynorg_backend python -m app.data.goae_import
"""
import json
import sys
from pathlib import Path
from decimal import Decimal
from datetime import datetime

from sqlmodel import Session, select
from app.core.database import engine
from app.models.goae_ziffer import GoaeZiffer


def import_goae_ziffern():
    """Importiert GOÄ-Ziffern aus der JSON-Datei."""
    json_path = Path(__file__).parent / "goae_komplett.json"

    if not json_path.exists():
        json_path = Path(__file__).parent / "goae_seed_data.json"

    if not json_path.exists():
        print(f"FEHLER: Keine GOÄ-Datendatei gefunden!")
        sys.exit(1)

    with open(json_path, "r", encoding="utf-8") as f:
        ziffern_data = json.load(f)

    print(f"Lade {len(ziffern_data)} GOÄ-Ziffern aus {json_path.name}...")

    created = 0
    updated = 0

    with Session(engine) as session:
        for item in ziffern_data:
            ziffer_nr = str(item["ziffer"])

            # Ausschlussziffern: Liste → komma-separierter String
            ausschluss_raw = item.get("ausschlussziffern")
            ausschluss_str = None
            if ausschluss_raw and isinstance(ausschluss_raw, list):
                ausschluss_str = ", ".join(ausschluss_raw)

            # Prüfen ob Ziffer schon existiert
            existing = session.exec(
                select(GoaeZiffer).where(GoaeZiffer.ziffer == ziffer_nr)
            ).first()

            if existing:
                existing.beschreibung = item["beschreibung"]
                existing.punkte = item.get("punkte", 0) or 0
                existing.abschnitt = item.get("abschnitt", "?")
                existing.faktor_regelhöchst = Decimal(str(item.get("faktor_regelhöchst", 2.3)))
                existing.faktor_höchst = Decimal(str(item.get("faktor_höchst", 3.5)))
                existing.aktiv = True
                existing.ausschlussziffern = ausschluss_str
                existing.hinweistext = item.get("hinweistext")
                existing.detail_url = item.get("detail_url")
                existing.updated_at = datetime.utcnow()
                session.add(existing)
                updated += 1
            else:
                ziffer = GoaeZiffer(
                    ziffer=ziffer_nr,
                    beschreibung=item["beschreibung"],
                    punkte=item.get("punkte", 0) or 0,
                    abschnitt=item.get("abschnitt", "?"),
                    faktor_regelhöchst=Decimal(str(item.get("faktor_regelhöchst", 2.3))),
                    faktor_höchst=Decimal(str(item.get("faktor_höchst", 3.5))),
                    aktiv=True,
                    ausschlussziffern=ausschluss_str,
                    hinweistext=item.get("hinweistext"),
                    detail_url=item.get("detail_url"),
                )
                session.add(ziffer)
                created += 1

        session.commit()

    print(f"Import abgeschlossen: {created} neu, {updated} aktualisiert "
          f"(Gesamt: {created + updated})")


if __name__ == "__main__":
    import_goae_ziffern()
