"""
One-time script to recalculate duration_days for all existing absences.
This fixes entries that were incorrectly calculated due to school vacations
being counted as public holidays.

Run with:  python -m scripts.recalculate_durations
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlmodel import Session, select
from app.core.database import engine
from app.models.absence import Absence
from app.services.absence_calculation_service import AbsenceCalculationService


def recalculate_all():
    with Session(engine) as session:
        calc_service = AbsenceCalculationService(session)
        
        absences = session.exec(select(Absence)).all()
        print(f"Found {len(absences)} absences to check.")
        
        updated = 0
        for absence in absences:
            new_duration = calc_service.calculate_absence_duration(
                start_date=absence.start_date,
                end_date=absence.end_date,
                half_day_time=absence.half_day_time
            )
            
            if abs(absence.duration_days - new_duration) > 0.001:
                print(
                    f"  ID {absence.id}: employee_id={absence.employee_id} "
                    f"{absence.start_date} -> {absence.end_date} | "
                    f"old={absence.duration_days} -> new={new_duration}"
                )
                absence.duration_days = new_duration
                updated += 1
        
        if updated > 0:
            session.commit()
            print(f"\nUpdated {updated} absences.")
        else:
            print("\nAll durations are already correct. No changes needed.")


if __name__ == "__main__":
    recalculate_all()
