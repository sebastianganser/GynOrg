import traceback
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from sqlmodel import Session, select
from sqlalchemy import func, extract
from app.core.database import engine
from app.models.employee import Employee
from app.models.vacation_entitlement import VacationEntitlement
from app.models.absence import Absence, AbsenceStatus
from app.models.absence_type import AbsenceType, AbsenceTypeCategory

def test_query():
    try:
        with Session(engine) as session:
            employee_id = 2
            year = 2026
            
            # Get total allowance
            statement = (
                select(VacationEntitlement)
                .where(
                    VacationEntitlement.employee_id == employee_id,
                    extract('year', VacationEntitlement.from_date) <= year
                )
                .order_by(VacationEntitlement.from_date.desc())
            )
            entitlement = session.exec(statement).first()
            total_allowance = float(entitlement.days) if entitlement else 0.0

            # Get taken days
            try:
                statement = (
                    select(Absence)
                    .join(AbsenceType, Absence.absence_type_id == AbsenceType.id)
                    .where(
                        Absence.employee_id == employee_id,
                        extract('year', Absence.start_date) == year,
                        Absence.status.in_([AbsenceStatus.APPROVED, AbsenceStatus.PENDING]),
                        AbsenceType.category == AbsenceTypeCategory.VACATION
                    )
                )
                absences = session.exec(statement).all()
                taken_days = sum(absence.duration_days for absence in absences)
                taken_days = float(taken_days)
                
                print(f"Success! Allowance: {total_allowance}, Taken: {taken_days}")
            except Exception as e:
                print("Query Error:")
                traceback.print_exc()

    except Exception as e:
        print("Setup Error:")
        traceback.print_exc()

test_query()
