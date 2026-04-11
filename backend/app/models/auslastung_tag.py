from typing import Optional, List
from datetime import date as dt_date, datetime
from sqlmodel import SQLModel, Field, Relationship
from enum import Enum

class TagCategory(str, Enum):
    FEIERTAG = "FEIERTAG"
    SCHULFERIEN = "SCHULFERIEN"
    BETRIEBLICH = "BETRIEBLICH"
    EXTERN = "EXTERN"
    SONSTIGES = "SONSTIGES"
    WOCHENTAG = "WOCHENTAG"

class TagSource(str, Enum):
    AUTO = "AUTO"
    MANUAL = "MANUAL"

class MetricType(str, Enum):
    AUSLASTUNG = "AUSLASTUNG"
    ADMISSIONS = "ADMISSIONS"
    DISCHARGES = "DISCHARGES"

class CalendarTagBase(SQLModel):
    tag_name: str = Field(max_length=100)
    tag_category: TagCategory
    is_automatic: bool = Field(default=False)

class CalendarTag(CalendarTagBase, table=True):
    __tablename__ = "calendar_tags"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    day_tags: List["DayTag"] = Relationship(back_populates="tag")
    multipliers: List["TagMultiplier"] = Relationship(back_populates="tag")

class CalendarTagCreate(CalendarTagBase):
    pass

class CalendarTagRead(CalendarTagBase):
    id: int
    created_at: datetime


class DayTagBase(SQLModel):
    date: dt_date = Field(primary_key=True)
    tag_id: int = Field(foreign_key="calendar_tags.id", primary_key=True)
    source: TagSource = Field(default=TagSource.AUTO)
    comment: Optional[str] = Field(default=None)

class DayTag(DayTagBase, table=True):
    __tablename__ = "day_tags"
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    tag: "CalendarTag" = Relationship(back_populates="day_tags")

class DayTagCreate(DayTagBase):
    pass

class DayTagRead(DayTagBase):
    created_at: datetime


class TagMultiplierBase(SQLModel):
    tag_id: int = Field(foreign_key="calendar_tags.id")
    metric: MetricType
    multiplier: float
    sample_size: int = Field(default=0)
    confidence: float = Field(default=0.0)

class TagMultiplier(TagMultiplierBase, table=True):
    __tablename__ = "tag_multipliers"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    last_calculated: datetime = Field(default_factory=datetime.utcnow)
    
    tag: "CalendarTag" = Relationship(back_populates="multipliers")

class TagMultiplierRead(TagMultiplierBase):
    id: int
    last_calculated: datetime
