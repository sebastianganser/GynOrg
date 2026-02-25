from sqlmodel import Session, create_engine, select
from app.models.holiday import Holiday, HolidayType, FederalState

# Connect to the source DB
engine = create_engine("sqlite:///../data/gynorg.db")

def check_holidays():
    with Session(engine) as session:
        # Check specific states
        state = FederalState.BAYERN
        years = [2025]
        
        print(f"\n--- Checking {state.value} ({state.name}) ---")
        for year in years:
            query = select(Holiday).where(
                Holiday.year == year,
                Holiday.federal_state == state,
                Holiday.holiday_type == HolidayType.SCHOOL_VACATION
            )
            results = session.exec(query).all()
            print(f"Year {year}: Found {len(results)} school vacations")
            if results:
                print(f"  Sample: {results[0].name} ({results[0].date})")

if __name__ == "__main__":
    check_holidays()
