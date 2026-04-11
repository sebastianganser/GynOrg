"""
VacationAllowance Pydantic schemas for API request/response models.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, computed_field


class VacationAllowanceBase(BaseModel):
    """Base vacation allowance schema with common fields."""
    year: int = Field(..., ge=2020, le=2050, description="Calendar year")
    annual_allowance: int = Field(..., ge=0, le=365, description="Annual vacation allowance in days")
    carryover_days: int = Field(0, ge=0, le=365, description="Carryover days from previous year")


class VacationAllowanceCreate(VacationAllowanceBase):
    """Schema for creating a new vacation allowance."""
    employee_id: int = Field(..., description="Employee ID")


class VacationAllowanceUpdate(BaseModel):
    """Schema for updating an existing vacation allowance."""
    year: Optional[int] = Field(None, ge=2020, le=2050)
    annual_allowance: Optional[int] = Field(None, ge=0, le=365)
    carryover_days: Optional[int] = Field(None, ge=0, le=365)


class VacationAllowanceRead(VacationAllowanceBase):
    """Schema for reading vacation allowance data."""
    id: int
    employee_id: int
    created_at: datetime
    updated_at: datetime
    
    @computed_field
    @property
    def total_allowance(self) -> int:
        """Calculate total allowance (annual + carryover)."""
        return self.annual_allowance + self.carryover_days
    
    class Config:
        from_attributes = True


class VacationAllowanceListResponse(BaseModel):
    """Schema for vacation allowance list responses."""
    vacation_allowances: list[VacationAllowanceRead]
    total: int
    employee_id: int
