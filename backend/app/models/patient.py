"""
Patient Modell – Privatpatienten-Stammdaten für die GOÄ-Abrechnung.
"""
from typing import Optional
from datetime import date as dt_date, datetime
from sqlmodel import SQLModel, Field
import enum


class Anrede(str, enum.Enum):
    HERR = "Herr"
    FRAU = "Frau"
    DIVERS = "Divers"


class PatientBase(SQLModel):
    """Basis-Felder eines Privatpatienten."""
    anrede: Anrede = Field(description="Anrede des Patienten")
    titel: Optional[str] = Field(
        default=None, max_length=50,
        description="Akademischer Titel (z.B. Dr., Prof.)"
    )
    vorname: str = Field(max_length=100)
    nachname: str = Field(max_length=100, index=True)
    geburtsdatum: dt_date = Field(description="Geburtsdatum des Patienten")

    # Adresse
    strasse: str = Field(max_length=200)
    hausnummer: str = Field(max_length=10)
    plz: str = Field(max_length=10)
    ort: str = Field(max_length=100)

    # Kontakt
    telefon: Optional[str] = Field(default=None, max_length=30)
    email: Optional[str] = Field(default=None, max_length=150)

    # Versicherung
    versicherung: Optional[str] = Field(
        default=None, max_length=200,
        description="Name der privaten Krankenversicherung"
    )
    versicherungsnummer: Optional[str] = Field(
        default=None, max_length=50,
        description="Versicherungsnummer / Policennummer"
    )

    # Sonstiges
    notizen: Optional[str] = Field(
        default=None,
        description="Interne Notizen zum Patienten"
    )
    aufnahme_datum: Optional[dt_date] = Field(
        default=None,
        description="Aufnahme-Datum in der Klinik"
    )
    aktiv: bool = Field(default=True)


class Patient(PatientBase, table=True):
    """Privatpatienten-Tabelle."""
    __tablename__ = "patienten"

    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None


class PatientCreate(PatientBase):
    """Modell zum Erstellen eines Patienten."""
    pass


class PatientUpdate(SQLModel):
    """Modell zum Aktualisieren eines Patienten."""
    anrede: Optional[Anrede] = None
    titel: Optional[str] = None
    vorname: Optional[str] = None
    nachname: Optional[str] = None
    geburtsdatum: Optional[dt_date] = None
    strasse: Optional[str] = None
    hausnummer: Optional[str] = None
    plz: Optional[str] = None
    ort: Optional[str] = None
    telefon: Optional[str] = None
    email: Optional[str] = None
    versicherung: Optional[str] = None
    versicherungsnummer: Optional[str] = None
    notizen: Optional[str] = None
    aufnahme_datum: Optional[dt_date] = None
    aktiv: Optional[bool] = None


class PatientRead(PatientBase):
    """Modell zum Lesen (Output) eines Patienten."""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
