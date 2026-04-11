"""
GOÄ-Ziffern Seed-Import Skript.

Liest goae_seed_data.json und importiert die Ziffern in die Datenbank.
Idempotent: Vorhandene Ziffern werden aktualisiert, neue eingefügt.

Nutzung:
  cd backend
  python -m tools.goae_import
"""
import json
import os
import sys
from pathlib import Path
from datetime import datetime

# Backend ins sys.path aufnehmen
backend_dir = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

from sqlmodel import Session, select
from app.core.database import engine
from app.models.goae_ziffer import GoaeZiffer


def import_goae_data(json_path: str = None):
    """GOÄ-Ziffern aus JSON-Datei in die Datenbank importieren."""
    if json_path is None:
        json_path = Path(__file__).parent / "goae_seed_data.json"

    with open(json_path, "r", encoding="utf-8") as f:
        ziffern_data = json.load(f)

    print(f"📋 Importiere {len(ziffern_data)} GOÄ-Ziffern...")

    created = 0
    updated = 0

    with Session(engine) as db:
        for entry in ziffern_data:
            existing = db.exec(
                select(GoaeZiffer).where(GoaeZiffer.ziffer == entry["ziffer"])
            ).first()

            if existing:
                # Update
                existing.beschreibung = entry["beschreibung"]
                existing.punkte = entry["punkte"]
                existing.abschnitt = entry["abschnitt"]
                existing.faktor_regelhöchst = entry["faktor_regelhöchst"]
                existing.faktor_höchst = entry["faktor_höchst"]
                existing.updated_at = datetime.utcnow()
                db.add(existing)
                updated += 1
            else:
                # Insert
                ziffer = GoaeZiffer(
                    ziffer=entry["ziffer"],
                    beschreibung=entry["beschreibung"],
                    punkte=entry["punkte"],
                    abschnitt=entry["abschnitt"],
                    faktor_regelhöchst=entry["faktor_regelhöchst"],
                    faktor_höchst=entry["faktor_höchst"],
                )
                db.add(ziffer)
                created += 1

        db.commit()

    print(f"✅ Import abgeschlossen: {created} neu, {updated} aktualisiert")
    return created, updated


if __name__ == "__main__":
    json_file = sys.argv[1] if len(sys.argv) > 1 else None
    import_goae_data(json_file)
