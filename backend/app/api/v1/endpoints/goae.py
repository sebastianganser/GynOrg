"""
GOÄ-Ziffern API-Endpunkte – Suche und Einzelabruf.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select, or_, col, func
from typing import Any, List

from app.core.database import get_session
from app.models.goae_ziffer import (
    GoaeZiffer, GoaeZifferRead, GoaeZifferCreate, GoaeZifferUpdate,
    GOAE_PUNKTWERT, GOAE_ABSCHNITTE
)
from decimal import Decimal

router = APIRouter()


def _to_read(z: GoaeZiffer) -> dict:
    """GoaeZiffer → GoaeZifferRead inkl. berechneter Euro-Werte."""
    data = z.model_dump()
    data["einfachsatz"] = round(Decimal(z.punkte) * GOAE_PUNKTWERT, 2)
    data["regelhoechstsatz"] = round(data["einfachsatz"] * z.faktor_regelhöchst, 2)
    data["hoechstsatz"] = round(data["einfachsatz"] * z.faktor_höchst, 2)
    # Abschnitt-Bezeichnung ergänzen
    data["abschnitt_label"] = GOAE_ABSCHNITTE.get(z.abschnitt, z.abschnitt)
    return data


@router.get("/suche", response_model=List[GoaeZifferRead])
def suche_goae_ziffern(
    *,
    db: Session = Depends(get_session),
    q: str = Query("", min_length=0, description="Suchbegriff (Ziffer oder Leistungstext)"),
    abschnitt: str = Query(None, description="Abschnitt-Filter (z.B. H)"),
    limit: int = Query(20, ge=1, le=100),
    nur_aktive: bool = Query(True, description="Nur aktive Ziffern anzeigen")
) -> Any:
    """
    Volltextsuche über GOÄ-Ziffern.
    Sucht in Ziffer und Beschreibung.
    """
    statement = select(GoaeZiffer)

    if nur_aktive:
        statement = statement.where(GoaeZiffer.aktiv == True)

    if abschnitt:
        # Multi-Filter: komma-separiert (z.B. 'H,I,J')
        abschnitt_list = [a.strip().upper() for a in abschnitt.split(',') if a.strip()]
        if len(abschnitt_list) == 1:
            statement = statement.where(GoaeZiffer.abschnitt == abschnitt_list[0])
        else:
            statement = statement.where(GoaeZiffer.abschnitt.in_(abschnitt_list))

    if q:
        search_term = f"%{q}%"
        statement = statement.where(
            or_(
                col(GoaeZiffer.ziffer).ilike(search_term),
                col(GoaeZiffer.beschreibung).ilike(search_term)
            )
        )

    statement = statement.order_by(GoaeZiffer.ziffer).limit(limit)
    results = db.exec(statement).all()

    return [_to_read(z) for z in results]


@router.get("/ziffer/{ziffer}", response_model=GoaeZifferRead)
def get_goae_ziffer(
    *,
    db: Session = Depends(get_session),
    ziffer: str
) -> Any:
    """
    Einzelne GOÄ-Ziffer abrufen.
    """
    z = db.exec(
        select(GoaeZiffer).where(GoaeZiffer.ziffer == ziffer)
    ).first()
    if not z:
        raise HTTPException(status_code=404, detail=f"GOÄ-Ziffer {ziffer} nicht gefunden")
    return _to_read(z)


@router.get("/abschnitte")
def get_abschnitte(
    db: Session = Depends(get_session)
) -> Any:
    """
    Alle verfügbaren GOÄ-Abschnitte mit Bezeichnung abrufen.
    """
    results = db.exec(
        select(GoaeZiffer.abschnitt)
        .distinct()
        .order_by(GoaeZiffer.abschnitt)
    ).all()
    # Sortierung in offizieller GOÄ-Reihenfolge
    reihenfolge = ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','ANALOG']
    return sorted(
        [{"key": a, "label": GOAE_ABSCHNITTE.get(a, a)} for a in results],
        key=lambda x: reihenfolge.index(x['key']) if x['key'] in reihenfolge else 99
    )


# ─── GOÄ-Datenstand & Import ──────────────────────────────────────────────────

@router.get("/import-status")
def get_import_status(
    db: Session = Depends(get_session)
) -> dict:
    """Datenstand der GOÄ-Ziffern: Anzahl und Datum des letzten Imports."""
    total = db.exec(select(func.count(GoaeZiffer.id))).one()
    aktive = db.exec(
        select(func.count(GoaeZiffer.id)).where(GoaeZiffer.aktiv == True)
    ).one()
    # Letztes Update = max(updated_at) oder max(created_at)
    letztes_created = db.exec(select(func.max(GoaeZiffer.created_at))).one()
    letztes_updated = db.exec(select(func.max(GoaeZiffer.updated_at))).one()
    
    # Das neuere der beiden Zeitstempel wählen
    letztes_update = letztes_updated or letztes_created
    if letztes_created and letztes_updated:
        letztes_update = max(letztes_created, letztes_updated)

    return {
        "total": total,
        "aktive": aktive,
        "letztes_update": letztes_update.isoformat() if letztes_update else None,
    }


@router.post("/import")
def trigger_goae_import(
    db: Session = Depends(get_session)
) -> dict:
    """GOÄ-Ziffern aus der JSON-Datei importieren/aktualisieren."""
    from app.data.goae_import import import_goae_ziffern
    try:
        import_goae_ziffern()

        # Status nach Import lesen
        total = db.exec(select(func.count(GoaeZiffer.id))).one()
        return {
            "success": True,
            "message": f"Import erfolgreich abgeschlossen ({total} Ziffern)",
            "total": total,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Import fehlgeschlagen: {str(e)}")
