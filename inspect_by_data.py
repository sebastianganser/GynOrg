import sys
import os
from sqlmodel import Session, create_engine, select
from app.models.holiday import Holiday, FederalState

# Add backend to path
sys.path.append(os.path.abspath("backend"))

db_path = "sqlite:///d:/Sebastian/Dokumente/Privat/Maria/Arbeit/GynOrg/backend/data/gynorg.db"
engine = create_engine(db_path)

with Session(engine) as session:
    # Check Bavaria 2025 School Vacations
    stmt = select(Holiday).where(
        Holiday.federal_state_code == "BY",
        Holiday.year == 2025,
        Holiday.holiday_type == "SCHOOL_VACATION"
    )
    results = session.exec(stmt).all()
    
    print(f"Found {len(results)} vacations for BY 2025:")
    for h in results:
        print(f"{h.name}: {h.date} -> {h.end_date} (Code: {h.federal_state_code})")
