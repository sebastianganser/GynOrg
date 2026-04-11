from sqlmodel import SQLModel
from typing import Optional

class VacationSummaryRead(SQLModel):
    total_allowance: float
    taken_days: float
    remaining_days: float
    carryover_days: float = 0.0
    annual_allowance: float = 0.0
    approved_days: float = 0.0
    pending_days: float = 0.0
    available_days: float = 0.0
