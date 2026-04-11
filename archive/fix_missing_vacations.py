import asyncio
import sys
import os
import logging
from datetime import date, datetime, timedelta
import httpx

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from app.core.database import get_session
from app.models.federal_state import FederalState
from app.models.holiday import Holiday
from sqlmodel import Session, select

# Config logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Handle DB connection explicitly
from sqlmodel import create_engine
# Point to the likely real DB
sqlite_url = "sqlite:///backend/app.db"
engine = create_engine(sqlite_url)

def get_session_manual():
    with Session(engine) as session:
        yield session

async def import_school_vacations():
    # session = next(get_session()) 
    session = next(get_session_manual())
    
    # Import for 2025 and 2026 for Sachsen-Anhalt
    years = [2025, 2026]
    state_code = "sachsen-anhalt"
    federal_state_enum = FederalState.SACHSEN_ANHALT
    
    logger.info(f"Starting manual import for {state_code} years: {years}")
    
    # Mappings
    VACATION_TYPE_MAPPING = {
        "Winter": "WINTER",
        "Winterferien": "WINTER",
        "Ostern": "EASTER",
        "Osterferien": "EASTER",
        "Pfingsten": "PENTECOST",
        "Pfingstferien": "PENTECOST",
        "Sommer": "SUMMER",
        "Sommerferien": "SUMMER",
        "Herbst": "AUTUMN",
        "Herbstferien": "AUTUMN",
        "Weihnachten": "CHRISTMAS",
        "Weihnachtsferien": "CHRISTMAS",
    }
    
    total_count = 0
    
    try:
        async with httpx.AsyncClient() as client:
            for year in years:
                url = f"https://www.mehr-schulferien.de/api/v2.1/federal-states/{state_code}/periods"
                params = {
                    "start_date": f"{year}-01-01",
                    "end_date": f"{year}-12-31"
                }
                
                logger.info(f"Fetching {url}...")
                response = await client.get(url, params=params)
                
                if response.status_code != 200:
                    logger.error(f"Failed to fetch: {response.status_code}")
                    continue
                    
                data = response.json()
                if not isinstance(data, dict) or 'data' not in data:
                    logger.error("Invalid response format")
                    continue
                    
                items = data['data']
                logger.info(f"Found {len(items)} items for {year}")
                
                for item in items:
                    # Filter for school vacations
                    if not item.get("is_school_vacation", False):
                        continue
                    if item.get("is_public_holiday", False):
                        continue
                        
                    name = item.get("name")
                    starts_on = datetime.strptime(item.get("starts_on"), "%Y-%m-%d").date()
                    ends_on = datetime.strptime(item.get("ends_on"), "%Y-%m-%d").date()
                    
                    # Map type
                    vacation_type = "SUMMER" # Default
                    for k, v in VACATION_TYPE_MAPPING.items():
                        if k.lower() in name.lower():
                            vacation_type = v
                            break
                    
                    # Expand range
                    current_date = starts_on
                    while current_date <= ends_on:
                        # Check exist
                        stmt = select(Holiday).where(
                            Holiday.date == current_date,
                            Holiday.federal_state == federal_state_enum,
                            Holiday.holiday_type == "SCHOOL_VACATION"
                        )
                        existing = session.exec(stmt).first()
                        
                        if not existing:
                            holiday = Holiday(
                                name=name,
                                date=current_date,
                                federal_state=federal_state_enum,
                                federal_state_code=federal_state_enum.value,
                                is_nationwide=False,
                                year=year,
                                notes="Manual Import",
                                holiday_type="SCHOOL_VACATION",
                                school_vacation_type=vacation_type,
                                data_source="MANUAL",
                                api_id=f"{item.get('id')}_{current_date.strftime('%Y%m%d')}"
                            )
                            session.add(holiday)
                            total_count += 1
                        
                        current_date += timedelta(days=1)
                
                session.commit()
                logger.info(f"Committed {total_count} days so far...")
                
    except Exception as e:
        logger.error(f"Error: {e}")
        import traceback
        traceback.print_exc()
        
    logger.info(f"Total imported: {total_count}")

if __name__ == "__main__":
    asyncio.run(import_school_vacations())
