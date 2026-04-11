from typing import Optional, List, TYPE_CHECKING
from datetime import date, timedelta
import re
from sqlmodel import SQLModel, Field, Relationship
from pydantic import field_validator
from .federal_state import FederalState

if TYPE_CHECKING:
    from .vacation_allowance import VacationAllowance
    from .vacation_entitlement import VacationEntitlement
    from .absence import Absence

    from .school_holiday_notification import SchoolHolidayNotification


class EmployeeBase(SQLModel):
    title: Optional[str] = Field(default=None, max_length=50, description="Titel wie Dr., Prof., etc.")
    first_name: str = Field(max_length=100, description="Vorname")
    last_name: str = Field(max_length=100, description="Nachname")
    email: str = Field(max_length=255, description="E-Mail-Adresse")
    position: Optional[str] = Field(default=None, max_length=100, description="Position/Stelle")
    birth_date: Optional[date] = Field(default=None, description="Geburtsdatum")
    date_hired: Optional[date] = Field(default=None, description="Einstellungsdatum")
    federal_state: str = Field(description="Bundesland")
    active: bool = Field(default=True, description="Aktiv/Inaktiv Status")
    initials: Optional[str] = Field(default=None, max_length=3, description="Initialen für Avatar")
    profile_image_path: Optional[str] = Field(default=None, max_length=255, description="Pfad zum Profilbild")
    calendar_color: str = Field(default="#3B82F6", max_length=7, description="Kalenderfarbe im Hex-Format (z.B. #3B82F6)")
    school_children: bool = Field(default=False, description="Hat schulpflichtige Kinder")
    youngest_child_birth_year: Optional[int] = Field(default=None, ge=1900, le=2100, description="Geburtsjahr des jüngsten Kindes")

    @field_validator('calendar_color')
    @classmethod
    def validate_calendar_color(cls, v):
        if v and not re.match(r'^#[0-9A-Fa-f]{6}$', v):
            raise ValueError('Kalenderfarbe muss im Hex-Format sein (z.B. #3B82F6)')
        return v

    @field_validator('email')
    @classmethod
    def validate_email_address(cls, v):
        if v:
            if not re.match(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', v):
                raise ValueError('Ungültige E-Mail-Adresse')
        return v

    @field_validator('birth_date')
    @classmethod
    def validate_birth_date(cls, v):
        if v and v > date.today():
            raise ValueError('Geburtsdatum darf nicht in der Zukunft liegen')
        return v

    @field_validator('date_hired')
    @classmethod
    def validate_date_hired(cls, v, info):
        if v:
            today = date.today()
            max_future_date = today + timedelta(days=365)  # 1 Jahr in die Zukunft
            
            if v > max_future_date:
                raise ValueError('Einstellungsdatum darf maximal 1 Jahr in der Zukunft liegen')
        
        # Prüfe ob Geburtsdatum vorhanden ist und Einstellungsdatum nicht davor liegt
        birth_date = info.data.get('birth_date')
        if v and birth_date and v < birth_date:
            raise ValueError('Einstellungsdatum darf nicht vor dem Geburtsdatum liegen')
        return v

    @property
    def full_name(self) -> str:
        """Vollständiger Name mit optionalem Titel"""
        parts = []
        if self.title:
            parts.append(self.title)
        parts.extend([self.first_name, self.last_name])
        return " ".join(parts)

    @property
    def display_name(self) -> str:
        """Anzeigename: Nachname, Vorname"""
        return f"{self.last_name}, {self.first_name}"


class Employee(EmployeeBase, table=True):
    __tablename__ = "employees"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # Relationships
    vacation_allowances: List["VacationAllowance"] = Relationship(
        back_populates="employee",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
    vacation_entitlements: List["VacationEntitlement"] = Relationship(
        back_populates="employee",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
    absences: List["Absence"] = Relationship(
        back_populates="employee",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
    # school_holiday_preferences and notifications removed per user request


class EmployeeCreate(EmployeeBase):
    pass


class EmployeeUpdate(SQLModel):
    title: Optional[str] = Field(default=None, max_length=50)
    first_name: Optional[str] = Field(default=None, max_length=100)
    last_name: Optional[str] = Field(default=None, max_length=100)
    email: Optional[str] = Field(default=None, max_length=255)
    position: Optional[str] = Field(default=None, max_length=100)
    birth_date: Optional[date] = Field(default=None)
    date_hired: Optional[date] = Field(default=None)
    federal_state: Optional[str] = Field(default=None)
    active: Optional[bool] = Field(default=None)
    initials: Optional[str] = Field(default=None, max_length=3)
    profile_image_path: Optional[str] = Field(default=None, max_length=255)
    calendar_color: Optional[str] = Field(default=None, max_length=7)
    school_children: Optional[bool] = Field(default=None)
    youngest_child_birth_year: Optional[int] = Field(default=None, ge=1900, le=2100)

    @field_validator('calendar_color')
    @classmethod
    def validate_calendar_color(cls, v):
        if v and not re.match(r'^#[0-9A-Fa-f]{6}$', v):
            raise ValueError('Kalenderfarbe muss im Hex-Format sein (z.B. #3B82F6)')
        return v

    @field_validator('birth_date')
    @classmethod
    def validate_birth_date(cls, v):
        if v and v > date.today():
            raise ValueError('Geburtsdatum darf nicht in der Zukunft liegen')
        return v

    @field_validator('date_hired')
    @classmethod
    def validate_date_hired(cls, v, info):
        if v:
            today = date.today()
            max_future_date = today + timedelta(days=365)  # 1 Jahr in die Zukunft
            
            if v > max_future_date:
                raise ValueError('Einstellungsdatum darf maximal 1 Jahr in der Zukunft liegen')
        
        # Prüfe ob Geburtsdatum vorhanden ist und Einstellungsdatum nicht davor liegt
        birth_date = info.data.get('birth_date')
        if v and birth_date and v < birth_date:
            raise ValueError('Einstellungsdatum darf nicht vor dem Geburtsdatum liegen')
        return v
