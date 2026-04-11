from typing import Optional, List, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship
from enum import Enum

if TYPE_CHECKING:
    from .absence import Absence





class AbsenceTypeBase(SQLModel):
    """Base model for absence type"""
    name: str = Field(max_length=100, description="Name of the absence type")
    is_vacation: bool = Field(default=False, description="Whether this absence type deducts from vacation allowance")
    is_paid: bool = Field(default=True, description="Whether this absence type is paid")
    requires_approval: bool = Field(default=False, description="Whether this absence type requires manual approval")
    max_days_per_request: Optional[int] = Field(default=None, description="Maximum days allowed per single request")
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
    is_vacation: Optional[bool] = Field(default=None)
    is_paid: Optional[bool] = Field(default=None)
    requires_approval: Optional[bool] = Field(default=None)
    max_days_per_request: Optional[int] = Field(default=None)
    active: Optional[bool] = Field(default=None)


class AbsenceTypeRead(AbsenceTypeBase):
    """Model for reading absence type"""
    id: int
