from sqlmodel import Session
from app.core.database import engine
from app.models.federal_state import FederalState
from app.services.holiday_service import HolidayService

def import_holidays():
    with Session(engine) as session:
        service = HolidayService(session)
        print("Importing Bavaria (BY) holidays for 2025...")
        result = service.import_holidays_for_year(2025, federal_states=[FederalState.BAYERN])
        print(f"Result: {result}")

if __name__ == "__main__":
    import_holidays()
