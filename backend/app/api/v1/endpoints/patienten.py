"""
Patienten API-Endpunkte – CRUD + Autovervollständigung.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select, or_, col
from typing import Any, List, Optional
from datetime import datetime, date, timedelta

from app.core.database import get_session
from app.models.patient import Patient, PatientCreate, PatientUpdate, PatientRead

router = APIRouter()


@router.get("/", response_model=List[PatientRead])
def get_patienten(
    *,
    db: Session = Depends(get_session),
    nur_aktive: bool = Query(True),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500)
) -> Any:
    """Alle Patienten abrufen."""
    statement = select(Patient)
    if nur_aktive:
        statement = statement.where(Patient.aktiv == True)
    statement = statement.order_by(Patient.nachname, Patient.vorname).offset(skip).limit(limit)
    return db.exec(statement).all()

@router.get("/aktuell", response_model=List[PatientRead])
def get_aktuelle_patienten(
    *,
    db: Session = Depends(get_session),
    tage: int = Query(30, ge=1, le=365, description="Aufnahme innerhalb der letzten N Tage")
) -> Any:
    """Patienten mit Aufnahme-Datum innerhalb der letzten N Tage."""
    stichtag = date.today() - timedelta(days=tage)
    statement = (
        select(Patient)
        .where(
            Patient.aktiv == True,
            Patient.aufnahme_datum != None,
            Patient.aufnahme_datum >= stichtag
        )
        .order_by(Patient.aufnahme_datum.desc())
    )
    return db.exec(statement).all()


@router.get("/suche", response_model=List[PatientRead])
def suche_patienten(
    *,
    db: Session = Depends(get_session),
    q: str = Query("", min_length=0, description="Suchbegriff (Name, Vorname)"),
    limit: int = Query(10, ge=1, le=50)
) -> Any:
    """
    Autovervollständigung – sucht in Vor- und Nachname.
    """
    if not q:
        return []

    search_term = f"%{q}%"
    statement = (
        select(Patient)
        .where(
            Patient.aktiv == True,
            or_(
                col(Patient.nachname).ilike(search_term),
                col(Patient.vorname).ilike(search_term)
            )
        )
        .order_by(Patient.nachname, Patient.vorname)
        .limit(limit)
    )
    return db.exec(statement).all()


@router.get("/{patient_id}", response_model=PatientRead)
def get_patient(
    *,
    db: Session = Depends(get_session),
    patient_id: int
) -> Any:
    """Einzelnen Patienten abrufen."""
    patient = db.get(Patient, patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient nicht gefunden")
    return patient


@router.post("/", response_model=PatientRead, status_code=201)
def create_patient(
    *,
    db: Session = Depends(get_session),
    patient_in: PatientCreate
) -> Any:
    """Neuen Patienten anlegen."""
    patient = Patient.model_validate(patient_in)
    db.add(patient)
    db.commit()
    db.refresh(patient)
    return patient


@router.put("/{patient_id}", response_model=PatientRead)
def update_patient(
    *,
    db: Session = Depends(get_session),
    patient_id: int,
    patient_in: PatientUpdate
) -> Any:
    """Patienten aktualisieren."""
    patient = db.get(Patient, patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient nicht gefunden")

    update_data = patient_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(patient, field, value)
    patient.updated_at = datetime.utcnow()

    db.add(patient)
    db.commit()
    db.refresh(patient)
    return patient


@router.delete("/{patient_id}", status_code=204)
def delete_patient(
    *,
    db: Session = Depends(get_session),
    patient_id: int
) -> None:
    """Patient deaktivieren (Soft-Delete)."""
    patient = db.get(Patient, patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient nicht gefunden")

    patient.aktiv = False
    patient.updated_at = datetime.utcnow()
    db.add(patient)
    db.commit()
