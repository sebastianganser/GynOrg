from typing import Optional, List
from datetime import date, datetime
from sqlmodel import SQLModel, Field
from enum import Enum
from .federal_state import FederalState


class HolidayType(str, Enum):
    """Typ des Feiertags/Ferientags"""
    PUBLIC_HOLIDAY = "PUBLIC_HOLIDAY"
    SCHOOL_VACATION = "SCHOOL_VACATION"


class SchoolVacationType(str, Enum):
    """Arten von Schulferien"""
    WINTER = "WINTER"
    EASTER = "EASTER"
    PENTECOST = "PENTECOST"
    SUMMER = "SUMMER"
    AUTUMN = "AUTUMN"
    CHRISTMAS = "CHRISTMAS"


class DataSource(str, Enum):
    """Datenquelle für Feiertage/Schulferien"""
    MANUAL = "MANUAL"
    MEHR_SCHULFERIEN_API = "MEHR_SCHULFERIEN_API"
    LEGACY_IMPORT = "LEGACY_IMPORT"


class HolidayBase(SQLModel):
    name: str = Field(max_length=100)
    date: date
    end_date: Optional[date] = None
    federal_state: Optional[str] = Field(default=None, max_length=50)  # Geändert von FederalState Enum zu String
    is_nationwide: bool = False
    year: int
    notes: str = Field(default="", max_length=255)
    
    # Neue Felder für Schulferien-Support
    holiday_type: HolidayType = Field(default=HolidayType.PUBLIC_HOLIDAY)
    federal_state_code: Optional[str] = Field(default=None, max_length=2)
    school_vacation_type: Optional[SchoolVacationType] = None
    data_source: DataSource = Field(default=DataSource.MANUAL)
    last_updated: Optional[datetime] = Field(default_factory=datetime.utcnow)
    api_id: Optional[str] = Field(default=None, max_length=50)


class Holiday(HolidayBase, table=True):
    __tablename__ = "holidays"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None

    def __str__(self):
        state_info = f" ({self.federal_state.value})" if self.federal_state else " (bundesweit)"
        return f"{self.name} - {self.date}{state_info}"


class HolidayCreate(HolidayBase):
    pass


class HolidayUpdate(SQLModel):
    name: Optional[str] = None
    date: Optional[date] = None
    federal_state: Optional[FederalState] = None
    is_nationwide: Optional[bool] = None
    notes: Optional[str] = None
    holiday_type: Optional[HolidayType] = None
    federal_state_code: Optional[str] = None
    school_vacation_type: Optional[SchoolVacationType] = None
    data_source: Optional[DataSource] = None
    api_id: Optional[str] = None


class HolidayRead(HolidayBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    @property
    def federal_state_name(self) -> str:
        """Gibt den vollständigen Namen des Bundeslandes zurück"""
        if self.federal_state:
            return self.federal_state.value
        return "Bundesweit"


class HolidayFilter(SQLModel):
    year: Optional[int] = None
    federal_state: Optional[FederalState] = None
    include_nationwide: bool = True
    month: Optional[int] = None
    
    # Neue Filter für Schulferien
    holiday_type: Optional[HolidayType] = None
    federal_state_code: Optional[str] = None
    school_vacation_type: Optional[SchoolVacationType] = None
    data_source: Optional[DataSource] = None
    include_school_vacations: bool = True


# Neue Schema-Klassen für Schulferien-spezifische Operationen
class SchoolHolidayCreate(SQLModel):
    """Schema für das Erstellen von Schulferien über API-Sync"""
    name: str = Field(max_length=100)
    date: date
    federal_state_code: str = Field(max_length=2)
    school_vacation_type: SchoolVacationType
    api_id: str = Field(max_length=50)
    year: int
    notes: str = Field(default="", max_length=255)


class SchoolHolidayBulkCreate(SQLModel):
    """Schema für Bulk-Import von Schulferien"""
    holidays: list[SchoolHolidayCreate]
    federal_state_code: str = Field(max_length=2)
    year: int
    data_source: DataSource = Field(default=DataSource.MEHR_SCHULFERIEN_API)
