from typing import Optional
from sqlmodel import Field, SQLModel
from datetime import datetime

class JobPositionBase(SQLModel):
    name: str = Field(max_length=100, index=True, description="Name der Position")
    description: Optional[str] = Field(default=None, description="Beschreibung")
    active: bool = Field(default=True, description="Ist die Position aktiv wählbar?")

class JobPosition(JobPositionBase, table=True):
    __tablename__ = "job_positions" # type: ignore
    
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)

class JobPositionCreate(JobPositionBase):
    pass

class JobPositionUpdate(SQLModel):
    name: Optional[str] = Field(default=None, max_length=100)
    description: Optional[str] = Field(default=None)
    active: Optional[bool] = Field(default=None)

class JobPositionRead(JobPositionBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
