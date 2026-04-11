"""
Rechnungen API – CRUD, Workflow (stellen/bezahlen/stornieren), PDF, Export.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response
from sqlmodel import Session, select, col
from typing import Any, List, Optional
from datetime import date, datetime
from decimal import Decimal

from app.core.database import get_session
from app.models.rechnung import (
    Rechnung, RechnungCreate, RechnungUpdate, RechnungRead, RechnungStatus,
    RechnungsPosition, RechnungsPositionCreate, RechnungsPositionRead,
    RechnungsDokument, RechnungsDokumentRead
)
from app.models.patient import Patient
from app.models.praxis_einstellungen import PraxisEinstellungen

router = APIRouter()


def _generate_rechnungsnummer(db: Session) -> str:
    """Nächste Rechnungsnummer generieren und Zähler hochsetzen."""
    settings = db.exec(select(PraxisEinstellungen)).first()
    if not settings:
        settings = PraxisEinstellungen()
        db.add(settings)
        db.commit()
        db.refresh(settings)

    praefix = settings.rechnungsnummer_praefix or "RE"
    nr = settings.naechste_rechnungsnummer
    jahr = datetime.now().year
    rechnungsnummer = f"{praefix}-{jahr}-{nr:04d}"

    settings.naechste_rechnungsnummer = nr + 1
    settings.updated_at = datetime.utcnow()
    db.add(settings)
    # commit passiert im aufrufenden Endpoint
    return rechnungsnummer


@router.get("/", response_model=List[RechnungRead])
def get_rechnungen(
    *,
    db: Session = Depends(get_session),
    status: Optional[RechnungStatus] = Query(None, description="Statusfilter"),
    patient_id: Optional[int] = Query(None),
    jahr: Optional[int] = Query(None, description="Rechnungsjahr"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200)
) -> Any:
    """Rechnungen auflisten mit optionalen Filtern."""
    statement = select(Rechnung)

    if status:
        statement = statement.where(Rechnung.status == status)
    if patient_id:
        statement = statement.where(Rechnung.patient_id == patient_id)
    if jahr:
        statement = statement.where(
            Rechnung.rechnungsdatum >= date(jahr, 1, 1),
            Rechnung.rechnungsdatum <= date(jahr, 12, 31)
        )

    statement = (
        statement
        .order_by(Rechnung.rechnungsdatum.desc())
        .offset(skip)
        .limit(limit)
    )
    return db.exec(statement).all()


@router.get("/{rechnung_id}", response_model=RechnungRead)
def get_rechnung(
    *,
    db: Session = Depends(get_session),
    rechnung_id: int
) -> Any:
    """Einzelne Rechnung mit Positionen und Dokumenten laden."""
    rechnung = db.get(Rechnung, rechnung_id)
    if not rechnung:
        raise HTTPException(status_code=404, detail="Rechnung nicht gefunden")
    return rechnung


@router.post("/", response_model=RechnungRead, status_code=201)
def create_rechnung(
    *,
    db: Session = Depends(get_session),
    rechnung_in: RechnungCreate
) -> Any:
    """
    Neue Rechnung als Entwurf erstellen.
    Rechnungsnummer wird automatisch vergeben.
    """
    # Patient prüfen
    patient = db.get(Patient, rechnung_in.patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient nicht gefunden")

    # Rechnungsnummer generieren
    rechnungsnummer = _generate_rechnungsnummer(db)

    # Rechnung erstellen
    rechnung = Rechnung(
        patient_id=rechnung_in.patient_id,
        rechnungsnummer=rechnungsnummer,
        rechnungsdatum=rechnung_in.rechnungsdatum,
        leistungszeitraum_von=rechnung_in.leistungszeitraum_von,
        leistungszeitraum_bis=rechnung_in.leistungszeitraum_bis,
        diagnose=rechnung_in.diagnose,
        zahlungsziel_tage=rechnung_in.zahlungsziel_tage,
        notizen=rechnung_in.notizen,
        status=RechnungStatus.ENTWURF,
    )
    db.add(rechnung)
    db.flush()  # um rechnung.id zu erhalten

    # Positionen hinzufügen
    gesamtbetrag = Decimal("0.00")
    for pos_in in rechnung_in.positionen:
        position = RechnungsPosition(
            rechnung_id=rechnung.id,
            goae_ziffer=pos_in.goae_ziffer,
            beschreibung=pos_in.beschreibung,
            datum=pos_in.datum,
            anzahl=pos_in.anzahl,
            punkte=pos_in.punkte,
            faktor=pos_in.faktor,
            betrag=pos_in.betrag,
            begruendung=pos_in.begruendung,
        )
        db.add(position)
        gesamtbetrag += pos_in.betrag

    rechnung.gesamtbetrag = gesamtbetrag
    db.add(rechnung)
    db.commit()
    db.refresh(rechnung)
    return rechnung


@router.put("/{rechnung_id}", response_model=RechnungRead)
def update_rechnung(
    *,
    db: Session = Depends(get_session),
    rechnung_id: int,
    rechnung_in: RechnungUpdate
) -> Any:
    """
    Rechnung aktualisieren – nur im Status ENTWURF möglich.
    Bei Angabe von Positionen werden alle bestehenden ersetzt.
    """
    rechnung = db.get(Rechnung, rechnung_id)
    if not rechnung:
        raise HTTPException(status_code=404, detail="Rechnung nicht gefunden")

    if rechnung.status != RechnungStatus.ENTWURF:
        raise HTTPException(
            status_code=400,
            detail="Nur Entwürfe können bearbeitet werden"
        )

    update_data = rechnung_in.model_dump(exclude_unset=True, exclude={"positionen"})
    for field, value in update_data.items():
        setattr(rechnung, field, value)

    # Positionen ersetzen, falls übergeben
    if rechnung_in.positionen is not None:
        # Alte Positionen löschen
        for pos in rechnung.positionen:
            db.delete(pos)

        gesamtbetrag = Decimal("0.00")
        for pos_in in rechnung_in.positionen:
            position = RechnungsPosition(
                rechnung_id=rechnung.id,
                goae_ziffer=pos_in.goae_ziffer,
                beschreibung=pos_in.beschreibung,
                datum=pos_in.datum,
                anzahl=pos_in.anzahl,
                punkte=pos_in.punkte,
                faktor=pos_in.faktor,
                betrag=pos_in.betrag,
                begruendung=pos_in.begruendung,
            )
            db.add(position)
            gesamtbetrag += pos_in.betrag

        rechnung.gesamtbetrag = gesamtbetrag

    rechnung.updated_at = datetime.utcnow()
    db.add(rechnung)
    db.commit()
    db.refresh(rechnung)
    return rechnung


@router.post("/{rechnung_id}/stellen", response_model=RechnungRead)
def rechnung_stellen(
    *,
    db: Session = Depends(get_session),
    rechnung_id: int
) -> Any:
    """
    Rechnung stellen – ändert Status von ENTWURF → GESTELLT.
    Ab hier ist die Rechnung nicht mehr änderbar.
    """
    rechnung = db.get(Rechnung, rechnung_id)
    if not rechnung:
        raise HTTPException(status_code=404, detail="Rechnung nicht gefunden")

    if rechnung.status != RechnungStatus.ENTWURF:
        raise HTTPException(
            status_code=400,
            detail="Nur Entwürfe können gestellt werden"
        )

    if not rechnung.positionen:
        raise HTTPException(
            status_code=400,
            detail="Rechnung hat keine Positionen"
        )

    rechnung.status = RechnungStatus.GESTELLT
    rechnung.updated_at = datetime.utcnow()
    db.add(rechnung)
    db.commit()
    db.refresh(rechnung)
    return rechnung


@router.post("/{rechnung_id}/bezahlt", response_model=RechnungRead)
def rechnung_bezahlt(
    *,
    db: Session = Depends(get_session),
    rechnung_id: int,
    datum: Optional[date] = Query(None, description="Zahlungsdatum (default: heute)")
) -> Any:
    """Rechnung als bezahlt markieren."""
    rechnung = db.get(Rechnung, rechnung_id)
    if not rechnung:
        raise HTTPException(status_code=404, detail="Rechnung nicht gefunden")

    if rechnung.status != RechnungStatus.GESTELLT:
        raise HTTPException(
            status_code=400,
            detail="Nur gestellte Rechnungen können als bezahlt markiert werden"
        )

    rechnung.status = RechnungStatus.BEZAHLT
    rechnung.bezahlt_am = datum or date.today()
    rechnung.updated_at = datetime.utcnow()
    db.add(rechnung)
    db.commit()
    db.refresh(rechnung)
    return rechnung


@router.post("/{rechnung_id}/stornieren", response_model=RechnungRead)
def rechnung_stornieren(
    *,
    db: Session = Depends(get_session),
    rechnung_id: int,
    grund: str = Query(description="Stornierungsgrund")
) -> Any:
    """Rechnung stornieren (komplettes Storno)."""
    rechnung = db.get(Rechnung, rechnung_id)
    if not rechnung:
        raise HTTPException(status_code=404, detail="Rechnung nicht gefunden")

    if rechnung.status == RechnungStatus.STORNIERT:
        raise HTTPException(
            status_code=400,
            detail="Rechnung ist bereits storniert"
        )

    if rechnung.status == RechnungStatus.ENTWURF:
        raise HTTPException(
            status_code=400,
            detail="Entwürfe können gelöscht werden, Storno nicht nötig"
        )

    rechnung.status = RechnungStatus.STORNIERT
    rechnung.storniert_am = date.today()
    rechnung.storno_grund = grund
    rechnung.updated_at = datetime.utcnow()
    db.add(rechnung)
    db.commit()
    db.refresh(rechnung)
    return rechnung


@router.post("/{rechnung_id}/pdf", response_model=RechnungsDokumentRead)
def generate_rechnung_pdf_endpoint(
    *,
    db: Session = Depends(get_session),
    rechnung_id: int
) -> Any:
    """
    PDF für eine Rechnung generieren und speichern.
    Funktioniert für Entwürfe und gestellte Rechnungen.
    """
    from app.services.pdf_generator import generate_rechnung_pdf

    rechnung = db.get(Rechnung, rechnung_id)
    if not rechnung:
        raise HTTPException(status_code=404, detail="Rechnung nicht gefunden")

    patient = db.get(Patient, rechnung.patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient nicht gefunden")

    praxis = db.exec(select(PraxisEinstellungen)).first()
    if not praxis:
        raise HTTPException(
            status_code=400,
            detail="Praxiseinstellungen müssen zuerst konfiguriert werden"
        )

    # PDF generieren
    pdf_bytes = generate_rechnung_pdf(
        rechnung=rechnung,
        patient=patient,
        positionen=rechnung.positionen,
        praxis=praxis,
    )

    # Nächste Versionsnummer ermitteln
    existing_docs = [d for d in rechnung.dokumente]
    next_version = max((d.version for d in existing_docs), default=0) + 1

    # In DB speichern
    dokument = RechnungsDokument(
        rechnung_id=rechnung.id,
        dateiname=f"{rechnung.rechnungsnummer}_v{next_version}.pdf",
        version=next_version,
        pdf_daten=pdf_bytes,
    )
    db.add(dokument)
    db.commit()
    db.refresh(dokument)

    return dokument


@router.get("/{rechnung_id}/pdf/download")
def download_rechnung_pdf(
    *,
    db: Session = Depends(get_session),
    rechnung_id: int,
    version: Optional[int] = Query(None, description="Version (default: neueste)")
) -> Any:
    """
    PDF einer Rechnung herunterladen.
    """
    rechnung = db.get(Rechnung, rechnung_id)
    if not rechnung:
        raise HTTPException(status_code=404, detail="Rechnung nicht gefunden")

    # Dokument laden
    statement = select(RechnungsDokument).where(
        RechnungsDokument.rechnung_id == rechnung_id
    )
    if version:
        statement = statement.where(RechnungsDokument.version == version)
    else:
        statement = statement.order_by(RechnungsDokument.version.desc())

    dokument = db.exec(statement).first()
    if not dokument:
        raise HTTPException(
            status_code=404,
            detail="Kein PDF vorhanden. Bitte zuerst generieren."
        )

    return Response(
        content=dokument.pdf_daten,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'inline; filename="{dokument.dateiname}"'
        }
    )


@router.delete("/{rechnung_id}", status_code=204)
def delete_rechnung(
    *,
    db: Session = Depends(get_session),
    rechnung_id: int
) -> None:
    """
    Entwurf löschen. Nur Entwürfe können gelöscht werden.
    Gestellte Rechnungen müssen storniert werden.
    """
    rechnung = db.get(Rechnung, rechnung_id)
    if not rechnung:
        raise HTTPException(status_code=404, detail="Rechnung nicht gefunden")

    if rechnung.status != RechnungStatus.ENTWURF:
        raise HTTPException(
            status_code=400,
            detail="Nur Entwürfe können gelöscht werden. Gestellte Rechnungen müssen storniert werden."
        )

    # Positionen löschen
    for pos in rechnung.positionen:
        db.delete(pos)
    # Dokumente löschen
    for dok in rechnung.dokumente:
        db.delete(dok)

    db.delete(rechnung)
    db.commit()


@router.get("/export/csv")
def export_rechnungen_csv(
    *,
    db: Session = Depends(get_session),
    jahr_von: int = Query(description="Start-Jahr"),
    jahr_bis: int = Query(description="End-Jahr")
) -> Any:
    """
    Rechnungen als CSV exportieren (für 5-Jahres-Archivierung).
    """
    import csv
    import io

    statement = (
        select(Rechnung)
        .where(
            Rechnung.rechnungsdatum >= date(jahr_von, 1, 1),
            Rechnung.rechnungsdatum <= date(jahr_bis, 12, 31)
        )
        .order_by(Rechnung.rechnungsdatum)
    )
    rechnungen = db.exec(statement).all()

    output = io.StringIO()
    writer = csv.writer(output, delimiter=";")
    writer.writerow([
        "Rechnungsnummer", "Datum", "Patient_ID", "Status",
        "Gesamtbetrag", "Diagnose", "Bezahlt_Am", "Storniert_Am"
    ])
    for r in rechnungen:
        writer.writerow([
            r.rechnungsnummer, r.rechnungsdatum.isoformat(), r.patient_id,
            r.status.value, str(r.gesamtbetrag), r.diagnose,
            r.bezahlt_am.isoformat() if r.bezahlt_am else "",
            r.storniert_am.isoformat() if r.storniert_am else ""
        ])

    csv_content = output.getvalue()
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=rechnungen_{jahr_von}-{jahr_bis}.csv"
        }
    )
