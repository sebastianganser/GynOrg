import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from sqlmodel import Session, select, create_engine
from app.models.holiday import Holiday, HolidayType, SchoolVacationType
from app.core.config import settings
from datetime import date

# Adjust database URL if needed, assuming sqlite
sqlite_url = "sqlite:///./backend/app.db"
engine = create_engine(sqlite_url)

def check_holidays():
    with Session(engine) as session:
        # Check for School Vacations in Sachsen-Anhalt (ST) in Dec 2025
        # Note: FederalState enum might be stored as string "ST" or "SACHSEN_ANHALT"?
        # Let's check generally for Dec 2025 first.
        
        start_date = date(2025, 12, 1)
        end_date = date(2025, 12, 31)
        
        statement = select(Holiday).where(
            Holiday.date >= start_date,
            Holiday.date <= end_date,
            Holiday.holiday_type == HolidayType.SCHOOL_VACATION
        )
        
        results = session.exec(statement).all()
        
        print(f"Found {len(results)} school vacation days in Dec 2025.")
        for h in results:
            print(f" - {h.date}: {h.name} ({h.federal_state})")

if __name__ == "__main__":
    check_holidays()
