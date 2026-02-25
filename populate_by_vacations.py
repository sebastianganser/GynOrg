from datetime import date, timedelta
from sqlmodel import Session, create_engine, select
from app.models.holiday import Holiday, HolidayType, SchoolVacationType, FederalState, DataSource

# Use the configured database (backend/data/gynorg.db)
# Absolute path to avoid confusion
db_path = "sqlite:///d:/Sebastian/Dokumente/Privat/Maria/Arbeit/GynOrg/backend/data/gynorg.db"
engine = create_engine(db_path)

VACATIONS_BY_2025 = [
    ("Winterferien", date(2025, 3, 3), date(2025, 3, 7), SchoolVacationType.WINTER),
    ("Osterferien", date(2025, 4, 14), date(2025, 4, 25), SchoolVacationType.EASTER),
    ("Pfingstferien", date(2025, 6, 10), date(2025, 6, 20), SchoolVacationType.PENTECOST),
    ("Sommerferien", date(2025, 8, 1), date(2025, 9, 15), SchoolVacationType.SUMMER),
    ("Herbstferien", date(2025, 11, 3), date(2025, 11, 7), SchoolVacationType.AUTUMN),
    ("Buß- und Bettag", date(2025, 11, 19), date(2025, 11, 19), SchoolVacationType.AUTUMN), # Often treated as school holiday
    ("Weihnachtsferien", date(2025, 12, 22), date(2025, 12, 31), SchoolVacationType.CHRISTMAS), # End date extends to Jan 2026, handled separately if needed
]

# Add start of 2025 leftovers from Dec 2024
VACATIONS_BY_2025_LEFTOVERS = [
    ("Weihnachtsferien", date(2025, 1, 1), date(2025, 1, 3), SchoolVacationType.CHRISTMAS)
]

def populate_holidays():
    with Session(engine) as session:
        count = 0
        all_ranges = VACATIONS_BY_2025 + VACATIONS_BY_2025_LEFTOVERS
        
        print(f"Populating Bavaria (BY) School Vacations for 2025...")
        
        for name, start, end, vac_type in all_ranges:
            current = start
            while current <= end:
                # Check if exists
                exists = session.exec(select(Holiday).where(
                    Holiday.date == current,
                    Holiday.federal_state == FederalState.BAYERN,
                    Holiday.holiday_type == HolidayType.SCHOOL_VACATION
                )).first()
                
                if not exists:
                    # Create holiday entry
                    holiday = Holiday(
                        name=name,
                        date=current,
                        federal_state=FederalState.BAYERN,
                        federal_state_code="BY",
                        is_nationwide=False,
                        year=current.year,
                        holiday_type=HolidayType.SCHOOL_VACATION,
                        school_vacation_type=vac_type,
                        data_source=DataSource.MANUAL,
                        notes="Imported via script"
                    )
                    session.add(holiday)
                    count += 1
                
                current += timedelta(days=1)
        
        session.commit()
        print(f"Successfully inserted {count} school vacation days for Bavaria 2025.")

if __name__ == "__main__":
    populate_holidays()
