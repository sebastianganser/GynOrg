from typing import Optional
from datetime import date as dt_date, datetime
from sqlmodel import SQLModel, Field, Relationship
from .station import Station

class DailyEntryBase(SQLModel):
    station_id: int = Field(foreign_key="stations.id")
    date: dt_date
    occupied: int = Field(default=0, ge=0)
    admissions: int = Field(default=0, ge=0)
    discharges: int = Field(default=0, ge=0)
    blocked_beds: int = Field(default=0, ge=0)

class DailyEntry(DailyEntryBase, table=True):
    __tablename__ = "daily_entries"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    
    station: "Station" = Relationship(back_populates="daily_entries")

class DailyEntryCreate(DailyEntryBase):
    pass

class DailyEntryUpdate(SQLModel):
    occupied: Optional[int] = None
    admissions: Optional[int] = None
    discharges: Optional[int] = None
    blocked_beds: Optional[int] = None

class DailyEntryRead(DailyEntryBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None


class DailyFremdBase(SQLModel):
    date: dt_date = Field(primary_key=True)
    count: int = Field(default=0, ge=0)

class DailyFremd(DailyFremdBase, table=True):
    __tablename__ = "daily_fremd"
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None

class DailyFremdCreate(DailyFremdBase):
    pass

class DailyFremdUpdate(SQLModel):
    count: Optional[int] = None

class DailyFremdRead(DailyFremdBase):
    created_at: datetime
    updated_at: Optional[datetime] = None
