from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING
from datetime import date, datetime

if TYPE_CHECKING:
    from .employee import Employee

class VacationEntitlementBase(SQLModel):
    """Base model for vacation entitlement"""
    from_date: date = Field(description="Date from which this entitlement applies")
    days: int = Field(description="Annual entitlement in days")

class VacationEntitlement(VacationEntitlementBase, table=True):
    """Model for vacation entitlement history"""
    __tablename__ = "vacation_entitlements"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    employee_id: int = Field(foreign_key="employees.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    employee: Optional["Employee"] = Relationship(back_populates="vacation_entitlements")

class VacationEntitlementCreate(VacationEntitlementBase):
    """Model for creating vacation entitlement"""
    employee_id: int

class VacationEntitlementRead(VacationEntitlementBase):
    """Model for reading vacation entitlement"""
    id: int
    employee_id: int
    created_at: datetime
    updated_at: datetime

class VacationEntitlementUpdate(SQLModel):
    """Model for updating vacation entitlement"""
    from_date: Optional[date] = None
    days: Optional[int] = None
