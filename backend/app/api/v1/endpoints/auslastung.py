from typing import List, Optional
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session, select
from app.core.database import get_session
from app.core.auth import get_current_user

from app.models.station import (
    Station, StationCreate, StationUpdate, StationRead,
    StationCapacity, StationCapacityCreate, StationCapacityUpdate, StationCapacityRead
)
from app.models.auslastung import (
    DailyEntry, DailyEntryCreate, DailyEntryUpdate, DailyEntryRead,
    DailyFremd, DailyFremdCreate, DailyFremdUpdate, DailyFremdRead
)
from app.models.auslastung_tag import (
    CalendarTag, CalendarTagCreate, CalendarTagRead,
    DayTag, DayTagCreate, DayTagRead, TagMultiplier, TagMultiplierRead
)

router = APIRouter()

# --- Stations ---

@router.get("/stations", response_model=List[Station])
def get_stations(
    active_only: bool = Query(True, description="Filter for active stations only"),
    session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user)
):
    statement = select(Station)
    if active_only:
        statement = statement.where(Station.is_active == True)
    statement = statement.order_by(Station.is_internal.desc(), Station.name.asc())
    return session.exec(statement).all()

@router.post("/stations", response_model=Station, status_code=status.HTTP_201_CREATED)
def create_station(
    station_data: StationCreate,
    session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user)
):
    station = Station(**station_data.model_dump())
    session.add(station)
    session.commit()
    session.refresh(station)
    return station

@router.put("/stations/{station_id}", response_model=Station)
def update_station(
    station_id: int,
    station_data: StationUpdate,
    session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user)
):
    station = session.get(Station, station_id)
    if not station:
        raise HTTPException(status_code=404, detail="Station not found")
    
    update_data = station_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(station, field, value)
    
    session.add(station)
    session.commit()
    session.refresh(station)
    return station

@router.delete("/stations/{station_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_station(
    station_id: int,
    session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user)
):
    station = session.get(Station, station_id)
    if not station:
        raise HTTPException(status_code=404, detail="Station not found")
        
    # Delete dependent daily entries
    statement_entries = select(DailyEntry).where(DailyEntry.station_id == station_id)
    entries = session.exec(statement_entries).all()
    for entry in entries:
        session.delete(entry)
        
    # Delete dependent capacities
    statement_capacities = select(StationCapacity).where(StationCapacity.station_id == station_id)
    capacities = session.exec(statement_capacities).all()
    for capacity in capacities:
        session.delete(capacity)
        
    # Finally delete the station
    session.delete(station)
    session.commit()
    return None

# --- Station Capacities ---

@router.get("/stations/{station_id}/capacities", response_model=List[StationCapacity])
def get_station_capacities(
    station_id: int,
    session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user)
):
    station = session.get(Station, station_id)
    if not station:
        raise HTTPException(status_code=404, detail="Station not found")
    
    statement = select(StationCapacity).where(StationCapacity.station_id == station_id).order_by(StationCapacity.valid_from.desc())
    return session.exec(statement).all()

@router.post("/stations/{station_id}/capacities", response_model=StationCapacity, status_code=status.HTTP_201_CREATED)
def create_station_capacity(
    station_id: int,
    capacity_data: StationCapacityCreate,
    session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user)
):
    if capacity_data.station_id != station_id:
        raise HTTPException(status_code=400, detail="Path station_id and body station_id do not match")
        
    station = session.get(Station, station_id)
    if not station:
        raise HTTPException(status_code=404, detail="Station not found")
        
    capacity = StationCapacity(**capacity_data.model_dump())
    session.add(capacity)
    session.commit()
    session.refresh(capacity)
    return capacity

# --- Daily Entries ---

@router.get("/daily", response_model=List[DailyEntry])
def get_daily_entries(
    start_date: date = Query(..., description="Start date"),
    end_date: date = Query(..., description="End date"),
    station_id: Optional[int] = Query(None, description="Filter by station ID"),
    session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user)
):
    statement = select(DailyEntry).where(
        DailyEntry.date >= start_date,
        DailyEntry.date <= end_date
    )
    if station_id:
        statement = statement.where(DailyEntry.station_id == station_id)
        
    return session.exec(statement).all()

@router.post("/daily", response_model=DailyEntry)
def upsert_daily_entry(
    entry_data: DailyEntryCreate,
    session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user)
):
    # Check if entry already exists
    statement = select(DailyEntry).where(
        DailyEntry.station_id == entry_data.station_id,
        DailyEntry.date == entry_data.date
    )
    existing_entry = session.exec(statement).first()
    
    if existing_entry:
        for field, value in entry_data.model_dump().items():
            setattr(existing_entry, field, value)
        entry = existing_entry
    else:
        entry = DailyEntry(**entry_data.model_dump())
        
    session.add(entry)
    session.commit()
    session.refresh(entry)
    return entry

# --- Daily Fremd ---

@router.get("/fremd", response_model=List[DailyFremd])
def get_daily_fremd(
    start_date: date = Query(..., description="Start date"),
    end_date: date = Query(..., description="End date"),
    session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user)
):
    statement = select(DailyFremd).where(
        DailyFremd.date >= start_date,
        DailyFremd.date <= end_date
    )
    return session.exec(statement).all()

@router.post("/fremd", response_model=DailyFremd)
def upsert_daily_fremd(
    fremd_data: DailyFremdCreate,
    session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user)
):
    existing = session.get(DailyFremd, fremd_data.date)
    if existing:
        existing.count = fremd_data.count
        fremd = existing
    else:
        fremd = DailyFremd(**fremd_data.model_dump())
        
    session.add(fremd)
    session.commit()
    session.refresh(fremd)
    return fremd

# --- Calculation Trigger ---
from app.services.auslastung_service import AuslastungService

@router.post("/calculate-multipliers")
def calculate_multipliers(
    session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user)
):
    """Manuliell die Multiplikatoren-Berechnung anstoßen"""
    result = AuslastungService.calculate_multipliers(session)
    return result
