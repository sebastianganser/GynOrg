from sqlmodel import SQLModel, Field, UniqueConstraint, Relationship
from typing import Optional, TYPE_CHECKING
from datetime import datetime

if TYPE_CHECKING:
    from .employee import Employee


class VacationAllowanceBase(SQLModel):
    """Base model for vacation allowance"""
    year: int
    annual_allowance: int = Field(default=30, description="Annual vacation allowance in days")
    carryover_days: int = Field(default=0, description="Days carried over from previous year")


class VacationAllowance(VacationAllowanceBase, table=True):
    """Model for vacation allowance per employee per year"""
    __tablename__ = "vacation_allowances"
    __table_args__ = (
        UniqueConstraint("employee_id", "year", name="unique_employee_year"),
    )
    
    id: Optional[int] = Field(default=None, primary_key=True)
    employee_id: int = Field(foreign_key="employees.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    employee: Optional["Employee"] = Relationship(back_populates="vacation_allowances")
    
    @property
    def total_allowance(self) -> int:
        """Calculate total allowance (annual + carryover)"""
        return self.annual_allowance + self.carryover_days
    
    class Config:
        from_attributes = True


class VacationAllowanceCreate(VacationAllowanceBase):
    """Model for creating vacation allowance"""
    employee_id: int


class VacationAllowanceUpdate(SQLModel):
    """Model for updating vacation allowance"""
    annual_allowance: Optional[int] = None
    carryover_days: Optional[int] = None
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class VacationAllowanceRead(VacationAllowanceBase):
    """Model for reading vacation allowance with computed fields"""
    id: int
    total_allowance: int
    created_at: datetime
    updated_at: datetime
