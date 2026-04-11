from typing import Optional, List
from datetime import date as dt_date, datetime
from sqlmodel import SQLModel, Field, Relationship

class StationBase(SQLModel):
    name: str = Field(max_length=100)
    is_internal: bool = Field(default=True, description="Gibt an, ob die Station eigen- oder fremdverwaltet ist")
    is_active: bool = Field(default=True)

class Station(StationBase, table=True):
    __tablename__ = "stations"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    
    capacities: List["StationCapacity"] = Relationship(back_populates="station")
    daily_entries: List["DailyEntry"] = Relationship(back_populates="station")

class StationCreate(StationBase):
    pass

class StationUpdate(SQLModel):
    name: Optional[str] = None
    is_internal: Optional[bool] = None
    is_active: Optional[bool] = None

class StationRead(StationBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None


class StationCapacityBase(SQLModel):
    station_id: int = Field(foreign_key="stations.id")
    valid_from: dt_date
    valid_to: Optional[dt_date] = None
    plan_beds: int = Field(ge=0)

class StationCapacity(StationCapacityBase, table=True):
    __tablename__ = "station_capacities"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    station: "Station" = Relationship(back_populates="capacities")

class StationCapacityCreate(StationCapacityBase):
    pass

class StationCapacityUpdate(SQLModel):
    valid_from: Optional[dt_date] = None
    valid_to: Optional[dt_date] = None
    plan_beds: Optional[int] = None

class StationCapacityRead(StationCapacityBase):
    id: int
    created_at: datetime
