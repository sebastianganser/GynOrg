"""
Praxiseinstellungen Modell – typisierter Einzel-Record für Praxis-/Arztdaten.

Wird im Einstellungsbereich „Modul: Rechnungslegung" bearbeitet.
Dient als Absender-Daten auf den GOÄ-Rechnungen.
"""
from typing import Optional
from datetime import datetime
from decimal import Decimal
from sqlmodel import SQLModel, Field


class PraxisEinstellungenBase(SQLModel):
    """Alle Felder der Praxiseinstellungen."""

    # Arzt / Leistungserbringer
    arzt_titel: Optional[str] = Field(
        default=None, max_length=50,
        description="Akademischer Titel (Dr. med., Prof. Dr. etc.)"
    )
    arzt_vorname: str = Field(
        default="", max_length=100,
        description="Vorname des Arztes"
    )
    arzt_nachname: str = Field(
        default="", max_length=100,
        description="Nachname des Arztes"
    )
    fachrichtung: str = Field(
        default="", max_length=200,
        description="Fachbezeichnung (z.B. Fachärztin für Gynäkologie und Geburtshilfe)"
    )

    # Praxis-Adresse
    praxis_name: Optional[str] = Field(
        default=None, max_length=200,
        description="Praxisbezeichnung (falls abweichend vom Arztnamen)"
    )
    strasse: str = Field(default="", max_length=200)
    hausnummer: str = Field(default="", max_length=10)
    plz: str = Field(default="", max_length=10)
    ort: str = Field(default="", max_length=100)

    # Kontakt
    telefon: str = Field(default="", max_length=30)
    fax: Optional[str] = Field(default=None, max_length=30)
    email: str = Field(default="", max_length=150)
    website: Optional[str] = Field(default=None, max_length=200)

    # Abrechnungsrelevant
    lanr: Optional[str] = Field(
        default=None, max_length=20,
        description="Lebenslange Arztnummer (LANR)"
    )
    steuernummer: Optional[str] = Field(
        default=None, max_length=30,
        description="Steuernummer oder USt-IdNr."
    )
    ust_befreit: bool = Field(
        default=True,
        description="Umsatzsteuerbefreit nach §4 Nr. 14 UStG"
    )

    # Bankverbindung
    bank_name: str = Field(default="", max_length=200)
    iban: str = Field(default="", max_length=34)
    bic: Optional[str] = Field(default=None, max_length=11)
    kontoinhaber: Optional[str] = Field(
        default=None, max_length=200,
        description="Kontoinhaber (falls abweichend vom Arztnamen)"
    )

    # Abrechnungs-Defaults
    standard_zahlungsziel_tage: int = Field(
        default=30,
        description="Standard-Zahlungsfrist in Tagen"
    )
    rechnungsnummer_praefix: str = Field(
        default="RE",
        max_length=10,
        description="Präfix für Rechnungsnummern (z.B. RE → RE-2026-0001)"
    )
    naechste_rechnungsnummer: int = Field(
        default=1,
        description="Nächste fortlaufende Rechnungsnummer"
    )


class PraxisEinstellungen(PraxisEinstellungenBase, table=True):
    """Praxiseinstellungen-Tabelle (genau ein Record)."""
    __tablename__ = "praxis_einstellungen"

    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class PraxisEinstellungenUpdate(SQLModel):
    """Modell zum Aktualisieren der Praxiseinstellungen (alle Felder optional)."""
    arzt_titel: Optional[str] = None
    arzt_vorname: Optional[str] = None
    arzt_nachname: Optional[str] = None
    fachrichtung: Optional[str] = None
    praxis_name: Optional[str] = None
    strasse: Optional[str] = None
    hausnummer: Optional[str] = None
    plz: Optional[str] = None
    ort: Optional[str] = None
    telefon: Optional[str] = None
    fax: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    lanr: Optional[str] = None
    steuernummer: Optional[str] = None
    ust_befreit: Optional[bool] = None
    bank_name: Optional[str] = None
    iban: Optional[str] = None
    bic: Optional[str] = None
    kontoinhaber: Optional[str] = None
    standard_zahlungsziel_tage: Optional[int] = None
    rechnungsnummer_praefix: Optional[str] = None
    naechste_rechnungsnummer: Optional[int] = None


class PraxisEinstellungenRead(PraxisEinstellungenBase):
    """Modell zum Lesen (Output) der Praxiseinstellungen."""
    id: int
    created_at: datetime
    updated_at: datetime
