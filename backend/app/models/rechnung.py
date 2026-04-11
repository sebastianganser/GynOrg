"""
Rechnung & Rechnungsposition Modelle für die GOÄ-Privatpatientenabrechnung.
"""
from typing import Optional, List
from datetime import date as dt_date, datetime
from decimal import Decimal
from sqlmodel import SQLModel, Field, Relationship
import enum


class RechnungStatus(str, enum.Enum):
    """Lebenszyklus-Status einer Rechnung."""
    ENTWURF = "entwurf"
    GESTELLT = "gestellt"
    BEZAHLT = "bezahlt"
    STORNIERT = "storniert"


# ─── Rechnungsposition ─────────────────────────────────

class RechnungsPositionBase(SQLModel):
    """Basis-Felder einer Leistungsposition."""
    rechnung_id: int = Field(foreign_key="rechnungen.id", index=True)
    goae_ziffer: str = Field(max_length=10, description="GOÄ-Ziffer")
    beschreibung: str = Field(description="Leistungstext")
    datum: dt_date = Field(description="Datum der Leistungserbringung")
    anzahl: int = Field(default=1, ge=1)
    punkte: int = Field(ge=0, description="Punktzahl der Ziffer")
    faktor: Decimal = Field(
        max_digits=4, decimal_places=2,
        description="Angewandter Steigerungsfaktor"
    )
    betrag: Decimal = Field(
        max_digits=10, decimal_places=2,
        description="Berechneter Betrag (Punkte × Punktwert × Faktor × Anzahl)"
    )
    begruendung: Optional[str] = Field(
        default=None,
        description="Begründung bei Überschreitung des Schwellenwerts"
    )


class RechnungsPosition(RechnungsPositionBase, table=True):
    """Einzelposition auf einer GOÄ-Rechnung."""
    __tablename__ = "rechnungs_positionen"

    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    rechnung: Optional["Rechnung"] = Relationship(back_populates="positionen")


class RechnungsPositionCreate(SQLModel):
    """Modell zum Erstellen einer Position (ohne rechnung_id, wird vom Endpoint gesetzt)."""
    goae_ziffer: str
    beschreibung: str
    datum: dt_date
    anzahl: int = 1
    punkte: int
    faktor: Decimal
    betrag: Decimal
    begruendung: Optional[str] = None


class RechnungsPositionRead(RechnungsPositionBase):
    """Modell zum Lesen (Output) einer Position."""
    id: int


# ─── Rechnungsdokument ─────────────────────────────────

class RechnungsDokumentBase(SQLModel):
    """Basis-Felder eines gespeicherten Rechnungs-PDFs."""
    rechnung_id: int = Field(foreign_key="rechnungen.id", index=True)
    dateiname: str = Field(max_length=200)
    mime_type: str = Field(default="application/pdf", max_length=100)
    version: int = Field(default=1, description="Versions-Nr (Storno = neue Version)")


class RechnungsDokument(RechnungsDokumentBase, table=True):
    """Generierte PDF-Dokumente (BYTEA)."""
    __tablename__ = "rechnungs_dokumente"

    id: Optional[int] = Field(default=None, primary_key=True)
    pdf_daten: bytes = Field(description="PDF-Binärdaten (BYTEA)")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    rechnung: Optional["Rechnung"] = Relationship(back_populates="dokumente")


class RechnungsDokumentRead(RechnungsDokumentBase):
    """Modell zum Lesen (Metadaten, ohne Binärdaten)."""
    id: int
    created_at: datetime


# ─── Rechnung ──────────────────────────────────────────

class RechnungBase(SQLModel):
    """Basis-Felder einer Rechnung."""
    patient_id: int = Field(foreign_key="patienten.id", index=True)
    rechnungsnummer: str = Field(
        max_length=20, unique=True, index=True,
        description="Fortlaufende Rechnungsnummer (z.B. RE-2026-0001)"
    )
    rechnungsdatum: dt_date = Field(description="Datum der Rechnungsstellung")
    leistungszeitraum_von: dt_date = Field(description="Beginn Leistungszeitraum")
    leistungszeitraum_bis: dt_date = Field(description="Ende Leistungszeitraum")
    diagnose: str = Field(description="Diagnose (ICD-10 oder Freitext)")

    status: RechnungStatus = Field(
        default=RechnungStatus.ENTWURF,
        description="Aktueller Status der Rechnung"
    )
    gesamtbetrag: Decimal = Field(
        default=Decimal("0.00"),
        max_digits=10, decimal_places=2,
        description="Gesamtbetrag der Rechnung in EUR"
    )

    zahlungsziel_tage: int = Field(
        default=30,
        description="Zahlungsfrist in Tagen"
    )
    bezahlt_am: Optional[dt_date] = Field(
        default=None,
        description="Datum der Zahlung"
    )
    storniert_am: Optional[dt_date] = Field(
        default=None,
        description="Datum der Stornierung"
    )
    storno_grund: Optional[str] = Field(
        default=None,
        description="Begründung der Stornierung"
    )
    notizen: Optional[str] = Field(
        default=None,
        description="Interne Notizen"
    )


class Rechnung(RechnungBase, table=True):
    """Rechnungs-Tabelle."""
    __tablename__ = "rechnungen"

    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None

    positionen: List[RechnungsPosition] = Relationship(back_populates="rechnung")
    dokumente: List[RechnungsDokument] = Relationship(back_populates="rechnung")


class RechnungCreate(SQLModel):
    """Modell zum Erstellen einer Rechnung."""
    patient_id: int
    rechnungsdatum: dt_date
    leistungszeitraum_von: dt_date
    leistungszeitraum_bis: dt_date
    diagnose: str
    zahlungsziel_tage: int = 30
    notizen: Optional[str] = None
    positionen: List[RechnungsPositionCreate] = []


class RechnungUpdate(SQLModel):
    """Modell zum Aktualisieren einer Rechnung (nur im Entwurf-Status)."""
    rechnungsdatum: Optional[dt_date] = None
    leistungszeitraum_von: Optional[dt_date] = None
    leistungszeitraum_bis: Optional[dt_date] = None
    diagnose: Optional[str] = None
    zahlungsziel_tage: Optional[int] = None
    notizen: Optional[str] = None
    positionen: Optional[List[RechnungsPositionCreate]] = None


class RechnungRead(RechnungBase):
    """Modell zum Lesen (Output) einer Rechnung."""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    positionen: List[RechnungsPositionRead] = []
    dokumente: List[RechnungsDokumentRead] = []
