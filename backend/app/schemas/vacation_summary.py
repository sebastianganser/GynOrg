from sqlmodel import SQLModel

class VacationSummaryRead(SQLModel):
    total_allowance: float
    taken_days: float
    remaining_days: float
