"""
GOÄ-Ziffer Modell (Gebührenordnung für Ärzte).

Enthält den Leistungskatalog – Punktzahlen und Steigerungsfaktoren.
Eurobeträge werden zur Laufzeit berechnet (Punktwert × Punkte × Faktor).
"""
from typing import Optional, List
from datetime import datetime
from sqlmodel import SQLModel, Field
from decimal import Decimal


# Offizieller GOÄ-Punktwert (seit 1996 unverändert)
GOAE_PUNKTWERT = Decimal("0.0582873")

# Abschnitt-Bezeichnungen laut GOÄ
GOAE_ABSCHNITTE = {
    "A": "Gebühren in besonderen Fällen",
    "B": "Grundleistungen und allgemeine Leistungen",
    "C": "Nichtgebietsbezogene Sonderleistungen",
    "D": "Anästhesieleistungen",
    "E": "Physikalisch-medizinische Leistungen",
    "F": "Innere Medizin, Kinderheilkunde, Dermatologie",
    "G": "Neurologie, Psychiatrie und Psychotherapie",
    "H": "Geburtshilfe und Gynäkologie",
    "I": "Augenheilkunde",
    "J": "Hals-, Nasen-, Ohrenheilkunde",
    "K": "Urologie",
    "L": "Chirurgie, Orthopädie",
    "M": "Laboratoriumsuntersuchungen",
    "N": "Histologie, Zytologie und Zytogenetik",
    "O": "Strahlendiagnostik, Nuklearmedizin, MRT und Strahlentherapie",
    "P": "Sektionsleistungen",
    "ANALOG": "Analoge Bewertungen",
}


class GoaeZifferBase(SQLModel):
    """Basis-Felder einer GOÄ-Ziffer."""
    ziffer: str = Field(
        max_length=10, index=True, unique=True,
        description="GOÄ-Ziffer (z.B. '1', '7', '1001', 'A', 'K1')"
    )
    beschreibung: str = Field(
        description="Leistungstext / Beschreibung der Ziffer"
    )
    punkte: int = Field(
        ge=0,
        description="Punktzahl laut GOÄ-Gebührenverzeichnis"
    )
    abschnitt: str = Field(
        max_length=10,
        description="GOÄ-Abschnitt (z.B. 'B', 'C', 'H', 'ANALOG')"
    )
    # Steigerungsfaktoren je nach Gebührenrahmen
    faktor_regelhöchst: Decimal = Field(
        default=Decimal("2.3"),
        max_digits=4, decimal_places=2,
        description="Regelhöchstsatz / Schwellenwert (2.3 für ärztlich, 1.8 für technisch, 1.15 für Labor)"
    )
    faktor_höchst: Decimal = Field(
        default=Decimal("3.5"),
        max_digits=4, decimal_places=2,
        description="Höchstsatz (3.5 für ärztlich, 2.5 für technisch, 1.3 für Labor)"
    )
    aktiv: bool = Field(
        default=True,
        description="Ob die Ziffer in der Auswahl angezeigt wird"
    )
    # Zusätzliche Felder aus dem Scraping
    ausschlussziffern: Optional[str] = Field(
        default=None,
        description="Komma-separierte Ausschlussziffern (z.B. '27,28,1050')"
    )
    hinweistext: Optional[str] = Field(
        default=None,
        description="Hinweistext / Anmerkungen zur Ziffer"
    )
    detail_url: Optional[str] = Field(
        default=None,
        description="URL zur Detailseite der Ziffer"
    )


class GoaeZiffer(GoaeZifferBase, table=True):
    """GOÄ-Ziffern-Tabelle."""
    __tablename__ = "goae_ziffern"

    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None

    @property
    def einfachsatz(self) -> Decimal:
        """Einfachsatz = Punkte × Punktwert"""
        return Decimal(self.punkte) * GOAE_PUNKTWERT

    @property
    def regelhoechstsatz(self) -> Decimal:
        """Regelhöchstsatz = Einfachsatz × Regelfaktor"""
        return self.einfachsatz * self.faktor_regelhöchst

    @property
    def hoechstsatz(self) -> Decimal:
        """Höchstsatz = Einfachsatz × Höchstfaktor"""
        return self.einfachsatz * self.faktor_höchst

    def betrag_mit_faktor(self, faktor: Decimal) -> Decimal:
        """Berechnet den Betrag für einen beliebigen Faktor."""
        return self.einfachsatz * faktor


class GoaeZifferCreate(GoaeZifferBase):
    """Modell zum Erstellen einer GOÄ-Ziffer."""
    pass


class GoaeZifferUpdate(SQLModel):
    """Modell zum Aktualisieren einer GOÄ-Ziffer."""
    beschreibung: Optional[str] = None
    punkte: Optional[int] = None
    abschnitt: Optional[str] = None
    faktor_regelhöchst: Optional[Decimal] = None
    faktor_höchst: Optional[Decimal] = None
    aktiv: Optional[bool] = None
    ausschlussziffern: Optional[str] = None
    hinweistext: Optional[str] = None
    detail_url: Optional[str] = None


class GoaeZifferRead(GoaeZifferBase):
    """Modell zum Lesen (Output) einer GOÄ-Ziffer."""
    id: int
    einfachsatz: Decimal
    regelhoechstsatz: Decimal
    hoechstsatz: Decimal
