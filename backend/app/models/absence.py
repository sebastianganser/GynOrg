from typing import Optional, TYPE_CHECKING
from datetime import date, datetime
from sqlmodel import SQLModel, Field, Relationship
from pydantic import field_validator
from enum import Enum

if TYPE_CHECKING:
    from .employee import Employee
    from .absence_type import AbsenceType


class AbsenceStatus(str, Enum):
    """Status of an absence request"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    CANCELLED = "cancelled"


class AbsenceBase(SQLModel):
    """Base model for absence"""
    start_date: date = Field(description="Start date of the absence")
    end_date: date = Field(description="End date of the absence")
    comment: Optional[str] = Field(default=None, max_length=1000, description="Optional comment for the absence")
    status: AbsenceStatus = Field(default=AbsenceStatus.PENDING, description="Status of the absence")

    @field_validator('end_date')
    @classmethod
    def validate_end_date(cls, v, info):
        """Validate that end_date is not before start_date"""
        start_date = info.data.get('start_date')
        if start_date and v < start_date:
            raise ValueError('Enddatum darf nicht vor dem Startdatum liegen')
        return v

    @field_validator('start_date')
    @classmethod
    def validate_start_date(cls, v):
        """Validate that start_date is not too far in the past"""
        if v < date.today().replace(year=date.today().year - 2):
            raise ValueError('Startdatum darf nicht mehr als 2 Jahre in der Vergangenheit liegen')
        return v

    @property
    def duration_days(self) -> int:
        """Calculate the duration in working days (Monday-Friday, inclusive)"""
        if not self.start_date or not self.end_date:
            return 0
        from datetime import timedelta
        days = 0
        current_date = self.start_date
        while current_date <= self.end_date:
            # 0 = Monday, 1 = Tuesday, ..., 5 = Saturday, 6 = Sunday
            if current_date.weekday() < 5:
                days += 1
            current_date += timedelta(days=1)
        return days

    @property
    def is_active(self) -> bool:
        """Check if the absence is currently active"""
        today = date.today()
        return self.start_date <= today <= self.end_date and self.status == AbsenceStatus.APPROVED


class Absence(AbsenceBase, table=True):
    """Model for employee absences"""
    __tablename__ = "absences"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    employee_id: int = Field(foreign_key="employees.id")
    absence_type_id: int = Field(foreign_key="absence_types.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    employee: Optional["Employee"] = Relationship(back_populates="absences")
    absence_type: Optional["AbsenceType"] = Relationship(back_populates="absences")


class AbsenceCreate(AbsenceBase):
    """Model for creating absence"""
    employee_id: int
    absence_type_id: int


class AbsenceUpdate(SQLModel):
    """Model for updating absence"""
    start_date: Optional[date] = Field(default=None)
    end_date: Optional[date] = Field(default=None)
    absence_type_id: Optional[int] = Field(default=None)
    comment: Optional[str] = Field(default=None, max_length=1000)
    status: Optional[AbsenceStatus] = Field(default=None)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    @field_validator('end_date')
    @classmethod
    def validate_end_date(cls, v, info):
        """Validate that end_date is not before start_date"""
        start_date = info.data.get('start_date')
        if start_date and v and v < start_date:
            raise ValueError('Enddatum darf nicht vor dem Startdatum liegen')
        return v


class AbsenceRead(AbsenceBase):
    """Model for reading absence with computed fields"""
    id: int
    employee_id: int
    absence_type_id: int
    created_at: datetime
    updated_at: datetime


class EmployeeBasic(SQLModel):
    """Basic employee info for absence details"""
    id: int
    first_name: str
    last_name: str
    email: str
    
    @property
    def display_name(self) -> str:
        """Anzeigename: Nachname, Vorname"""
        return f"{self.last_name}, {self.first_name}"


class AbsenceTypeBasic(SQLModel):
    """Basic absence type info for absence details"""
    id: int
    name: str
    category: str
    color: str
    is_paid: bool
    requires_approval: bool


class AbsenceWithDetails(AbsenceRead):
    """Model for reading absence with related data"""
    employee: Optional[EmployeeBasic] = None
    absence_type: Optional[AbsenceTypeBasic] = None
