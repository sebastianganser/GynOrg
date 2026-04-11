"""
Praxiseinstellungen API – Einzel-Record laden/speichern.

Der Nutzer bearbeitet diese Daten im Einstellungsbereich
"Modul: Rechnungslegung".
"""
from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from typing import Any
from datetime import datetime

from app.core.database import get_session
from app.models.praxis_einstellungen import (
    PraxisEinstellungen,
    PraxisEinstellungenUpdate,
    PraxisEinstellungenRead
)

router = APIRouter()


def _get_or_create(db: Session) -> PraxisEinstellungen:
    """Einstellungen laden oder Default-Record erstellen."""
    settings = db.exec(select(PraxisEinstellungen)).first()
    if not settings:
        settings = PraxisEinstellungen()
        db.add(settings)
        db.commit()
        db.refresh(settings)
    return settings


@router.get("/", response_model=PraxisEinstellungenRead)
def get_praxis_einstellungen(
    db: Session = Depends(get_session)
) -> Any:
    """
    Praxiseinstellungen laden.
    Erstellt automatisch einen Default-Record, falls noch keiner existiert.
    """
    return _get_or_create(db)


@router.put("/", response_model=PraxisEinstellungenRead)
def update_praxis_einstellungen(
    *,
    db: Session = Depends(get_session),
    settings_in: PraxisEinstellungenUpdate
) -> Any:
    """
    Praxiseinstellungen aktualisieren.
    Nur übergebene Felder werden geändert (partial update).
    """
    settings = _get_or_create(db)

    update_data = settings_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(settings, field, value)
    settings.updated_at = datetime.utcnow()

    db.add(settings)
    db.commit()
    db.refresh(settings)
    return settings
