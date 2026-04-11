"""
Employee Pydantic schemas for API request/response models.
"""
from datetime import date, timedelta
from typing import Optional, List, TYPE_CHECKING
from pydantic import BaseModel, EmailStr, Field, computed_field, field_validator
from app.models.federal_state import FederalState

if TYPE_CHECKING:
    from .vacation_allowance import VacationAllowanceRead


class EmployeeBase(BaseModel):
    """Base employee schema with common fields."""
    title: Optional[str] = Field(None, max_length=50, description="Title (e.g., Dr., Prof.)")
    first_name: str = Field(..., min_length=1, max_length=100, description="First name")
    last_name: str = Field(..., min_length=1, max_length=100, description="Last name")
    email: EmailStr = Field(..., description="Email address")
    position: Optional[str] = Field(None, max_length=100, description="Job position")
    birth_date: Optional[date] = Field(None, description="Date of birth")
    date_hired: Optional[date] = Field(None, description="Date hired")
    federal_state: FederalState = Field(..., description="Federal state")
    active: bool = Field(True, description="Whether the employee is active")

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


class EmployeeCreate(EmployeeBase):
    """Schema for creating a new employee."""
    pass


class EmployeeUpdate(BaseModel):
    """Schema for updating an existing employee."""
    title: Optional[str] = Field(None, max_length=50)
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    position: Optional[str] = Field(None, max_length=100)
    birth_date: Optional[date] = None
    date_hired: Optional[date] = None
    federal_state: Optional[FederalState] = None
    active: Optional[bool] = None

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


class EmployeeRead(EmployeeBase):
    """Schema for reading employee data."""
    id: int
    
    @computed_field
    @property
    def full_name(self) -> str:
        """Get the full name of the employee."""
        if self.title:
            return f"{self.title} {self.first_name} {self.last_name}"
        return f"{self.first_name} {self.last_name}"
    
    @computed_field
    @property
    def display_name(self) -> str:
        """Get a display-friendly name."""
        return f"{self.last_name}, {self.first_name}"
    
    class Config:
        from_attributes = True


class EmployeeWithVacation(EmployeeRead):
    """Schema for employee with vacation allowances."""
    vacation_allowances: List['VacationAllowanceRead'] = Field(default_factory=list, description="Employee's vacation allowances")
    
    class Config:
        from_attributes = True


class EmployeeListResponse(BaseModel):
    """Schema for employee list responses."""
    employees: List[EmployeeRead]
    total: int
    page: int = 1
    per_page: int = 50
