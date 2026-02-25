from typing import Optional, List, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship
from enum import Enum

if TYPE_CHECKING:
    from .absence import Absence


class AbsenceTypeCategory(str, Enum):
    """Categories for absence types"""
    VACATION = "vacation"
    SICK_LEAVE = "sick_leave"
    TRAINING = "training"
    SPECIAL_LEAVE = "special_leave"
    UNPAID_LEAVE = "unpaid_leave"
    OTHER = "other"


class AbsenceTypeBase(SQLModel):
    """Base model for absence type"""
    name: str = Field(max_length=100, description="Name of the absence type")
    category: AbsenceTypeCategory = Field(description="Category of the absence type")
    color: str = Field(max_length=7, default="#3B82F6", description="Hex color code for UI display")
    is_paid: bool = Field(default=True, description="Whether this absence type is paid")
    requires_approval: bool = Field(default=False, description="Whether this absence type requires manual approval")
    max_days_per_request: Optional[int] = Field(default=None, description="Maximum days allowed per single request")
    description: Optional[str] = Field(default=None, max_length=500, description="Description of the absence type")
    active: bool = Field(default=True, description="Whether this absence type is active")


class AbsenceType(AbsenceTypeBase, table=True):
    """Model for absence types"""
    __tablename__ = "absence_types"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # Relationships
    absences: List["Absence"] = Relationship(back_populates="absence_type")


class AbsenceTypeCreate(AbsenceTypeBase):
    """Model for creating absence type"""
    pass


class AbsenceTypeUpdate(SQLModel):
    """Model for updating absence type"""
    name: Optional[str] = Field(default=None, max_length=100)
    category: Optional[AbsenceTypeCategory] = Field(default=None)
    color: Optional[str] = Field(default=None, max_length=7)
    is_paid: Optional[bool] = Field(default=None)
    requires_approval: Optional[bool] = Field(default=None)
    max_days_per_request: Optional[int] = Field(default=None)
    description: Optional[str] = Field(default=None, max_length=500)
    active: Optional[bool] = Field(default=None)


class AbsenceTypeRead(AbsenceTypeBase):
    """Model for reading absence type"""
    id: int
