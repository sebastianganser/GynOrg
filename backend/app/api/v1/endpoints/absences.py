from typing import List, Optional
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session, select, and_, or_

from app.core.database import get_session
from app.models.absence import (
    Absence,
    AbsenceCreate,
    AbsenceUpdate,
    AbsenceRead,
    AbsenceWithDetails,
    AbsenceStatus
)
from app.models.employee import Employee
from app.models.absence_type import AbsenceType
from app.models.federal_state import FederalState
from app.services.absence_calculation_service import AbsenceCalculationService

router = APIRouter()


def check_absence_conflicts(
    session: Session,
    employee_id: int,
    start_date: date,
    end_date: date,
    exclude_absence_id: Optional[int] = None
) -> List[Absence]:
    """Check for conflicting absences for an employee in the given date range"""
    statement = select(Absence).where(
        and_(
            Absence.employee_id == employee_id,
            Absence.status.in_([AbsenceStatus.PENDING, AbsenceStatus.APPROVED]),
            or_(
                # New absence starts during existing absence
                and_(Absence.start_date <= start_date, Absence.end_date >= start_date),
                # New absence ends during existing absence
                and_(Absence.start_date <= end_date, Absence.end_date >= end_date),
                # New absence completely contains existing absence
                and_(Absence.start_date >= start_date, Absence.end_date <= end_date),
                # Existing absence completely contains new absence
                and_(Absence.start_date <= start_date, Absence.end_date >= end_date)
            )
        )
    )
    
    if exclude_absence_id:
        statement = statement.where(Absence.id != exclude_absence_id)
    
    return session.exec(statement).all()


@router.get("/", response_model=List[AbsenceRead])
def get_absences(
    *,
    session: Session = Depends(get_session),
    skip: int = 0,
    limit: int = 100,
    employee_id: Optional[int] = Query(None),
    status: Optional[AbsenceStatus] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None)
):
    """Get all absences with optional filtering"""
    statement = select(Absence)
    
    if employee_id:
        statement = statement.where(Absence.employee_id == employee_id)
    
    if status:
        statement = statement.where(Absence.status == status)
    
    if start_date:
        statement = statement.where(Absence.end_date >= start_date)
    
    if end_date:
        statement = statement.where(Absence.start_date <= end_date)
    
    statement = statement.offset(skip).limit(limit).order_by(Absence.start_date.desc())
    absences = session.exec(statement).all()
    
    return absences


@router.get("/{absence_id}", response_model=AbsenceWithDetails)
def get_absence(
    *,
    session: Session = Depends(get_session),
    absence_id: int
):
    """Get a specific absence by ID"""
    absence = session.get(Absence, absence_id)
    if not absence:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Absence not found"
        )
    
    # Load relationships
    employee = session.get(Employee, absence.employee_id)
    absence_type = session.get(AbsenceType, absence.absence_type_id)
    
    # Create response with proper schema models
    from app.models.absence import EmployeeBasic, AbsenceTypeBasic
    
    employee_basic = None
    if employee:
        employee_basic = EmployeeBasic(
            id=employee.id,
            first_name=employee.first_name,
            last_name=employee.last_name,
            email=employee.email
        )
    
    absence_type_basic = None
    if absence_type:
        absence_type_basic = AbsenceTypeBasic(
            id=absence_type.id,
            name=absence_type.name,
            is_vacation=absence_type.is_vacation,
            is_paid=absence_type.is_paid,
            requires_approval=absence_type.requires_approval
        )
    
    return AbsenceWithDetails(
        id=absence.id,
        employee_id=absence.employee_id,
        absence_type_id=absence.absence_type_id,
        start_date=absence.start_date,
        end_date=absence.end_date,
        comment=absence.comment,
        status=absence.status,
        created_at=absence.created_at,
        updated_at=absence.updated_at,
        employee=employee_basic,
        absence_type=absence_type_basic
    )


@router.post("/", response_model=AbsenceRead, status_code=status.HTTP_201_CREATED)
def create_absence(
    *,
    session: Session = Depends(get_session),
    absence_in: AbsenceCreate
):
    """Create a new absence"""
    # Validate employee exists
    employee = session.get(Employee, absence_in.employee_id)
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found"
        )
    
    # Validate absence type exists
    absence_type = session.get(AbsenceType, absence_in.absence_type_id)
    if not absence_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Absence type not found"
        )
    
    # Check for conflicts
    conflicts = check_absence_conflicts(
        session, 
        absence_in.employee_id, 
        absence_in.start_date, 
        absence_in.end_date
    )
    
    if conflicts:
        conflict_details = [
            f"Konflikt mit Abwesenheit vom {conflict.start_date} bis {conflict.end_date}"
            for conflict in conflicts
        ]
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Überschneidung mit bestehenden Abwesenheiten: {'; '.join(conflict_details)}"
        )
    
    # Calculate duration
    calc_service = AbsenceCalculationService(session)
    duration_days = calc_service.calculate_absence_duration(
        start_date=absence_in.start_date,
        end_date=absence_in.end_date,
        half_day_time=getattr(absence_in, 'half_day_time', None)
    )

    # Validate max days per request if set
    if absence_type.max_days_per_request:
        if duration_days > absence_type.max_days_per_request:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Maximale Anzahl Tage pro Antrag überschritten: {duration_days} > {absence_type.max_days_per_request}"
            )
    
    # Determine initial status: use explicit client status if provided, 
    # otherwise fallback to auto-approve logic
    explicit_fields = absence_in.model_dump(exclude_unset=True)
    if "status" in explicit_fields:
        initial_status = absence_in.status
    else:
        initial_status = AbsenceStatus.PENDING
        if not absence_type.requires_approval:
            initial_status = AbsenceStatus.APPROVED
    
    # Create absence instance directly with proper field mapping
    absence = Absence(
        employee_id=absence_in.employee_id,
        absence_type_id=absence_in.absence_type_id,
        start_date=absence_in.start_date,
        end_date=absence_in.end_date,
        comment=absence_in.comment,
        status=initial_status,
        half_day_time=getattr(absence_in, 'half_day_time', None),
        duration_days=duration_days
    )
    
    session.add(absence)
    session.commit()
    session.refresh(absence)
    return absence


@router.put("/{absence_id}", response_model=AbsenceRead)
def update_absence(
    *,
    session: Session = Depends(get_session),
    absence_id: int,
    absence_in: AbsenceUpdate
):
    """Update an absence"""
    absence = session.get(Absence, absence_id)
    if not absence:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Absence not found"
        )
    
    # Get update data
    absence_data = absence_in.model_dump(exclude_unset=True)
    
    # If dates are being updated, check for conflicts
    new_start_date = absence_data.get("start_date", absence.start_date)
    new_end_date = absence_data.get("end_date", absence.end_date)
    
    if "start_date" in absence_data or "end_date" in absence_data:
        conflicts = check_absence_conflicts(
            session,
            absence.employee_id,
            new_start_date,
            new_end_date,
            exclude_absence_id=absence_id
        )
        
        if conflicts:
            conflict_details = [
                f"Konflikt mit Abwesenheit vom {conflict.start_date} bis {conflict.end_date}"
                for conflict in conflicts
            ]
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Überschneidung mit bestehenden Abwesenheiten: {'; '.join(conflict_details)}"
            )
    
    new_half_day_time = absence_data.get("half_day_time", absence.half_day_time)
    
    # Recalculate duration if significant fields changed
    if "start_date" in absence_data or "end_date" in absence_data or "half_day_time" in absence_data:
        calc_service = AbsenceCalculationService(session)
        absence_data["duration_days"] = calc_service.calculate_absence_duration(
            start_date=new_start_date,
            end_date=new_end_date,
            half_day_time=new_half_day_time
        )
    
    # If absence type is being updated, validate max days
    if "absence_type_id" in absence_data:
        absence_type = session.get(AbsenceType, absence_data["absence_type_id"])
        if not absence_type:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Absence type not found"
            )
        
        if absence_type.max_days_per_request:
            duration = absence_data.get("duration_days", absence.duration_days)
            if duration > absence_type.max_days_per_request:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Maximale Anzahl Tage pro Antrag überschritten: {duration} > {absence_type.max_days_per_request}"
                )
    
    # Update absence
    for field, value in absence_data.items():
        setattr(absence, field, value)
    
    session.add(absence)
    session.commit()
    session.refresh(absence)
    return absence


@router.delete("/{absence_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_absence(
    *,
    session: Session = Depends(get_session),
    absence_id: int
):
    """Delete an absence"""
    absence = session.get(Absence, absence_id)
    if not absence:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Absence not found"
        )
    
    session.delete(absence)
    session.commit()
    return None


@router.post("/{absence_id}/approve", response_model=AbsenceRead)
def approve_absence(
    *,
    session: Session = Depends(get_session),
    absence_id: int
):
    """Approve an absence"""
    absence = session.get(Absence, absence_id)
    if not absence:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Absence not found"
        )
    
    if absence.status != AbsenceStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only pending absences can be approved"
        )
    
    absence.status = AbsenceStatus.APPROVED
    session.add(absence)
    session.commit()
    session.refresh(absence)
    return absence


@router.post("/{absence_id}/reject", response_model=AbsenceRead)
def reject_absence(
    *,
    session: Session = Depends(get_session),
    absence_id: int
):
    """Reject an absence"""
    absence = session.get(Absence, absence_id)
    if not absence:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Absence not found"
        )
    
    if absence.status != AbsenceStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only pending absences can be rejected"
        )
    
    absence.status = AbsenceStatus.REJECTED
    session.add(absence)
    session.commit()
    session.refresh(absence)
    return absence


@router.get("/conflicts/check")
def check_conflicts(
    *,
    session: Session = Depends(get_session),
    employee_id: int = Query(...),
    start_date: date = Query(...),
    end_date: date = Query(...),
    exclude_absence_id: Optional[int] = Query(None)
):
    """Check for absence conflicts without creating an absence"""
    conflicts = check_absence_conflicts(
        session, employee_id, start_date, end_date, exclude_absence_id
    )
    
    return {
        "has_conflicts": len(conflicts) > 0,
        "conflicts": [
            {
                "id": conflict.id,
                "start_date": conflict.start_date,
                "end_date": conflict.end_date,
                "status": conflict.status
            }
            for conflict in conflicts
        ]
    }


@router.get("/vacation-balance/{employee_id}")
def get_vacation_balance(
    *,
    session: Session = Depends(get_session),
    employee_id: int,
    year: Optional[int] = Query(None)
):
    """Get vacation balance for an employee"""
    calc_service = AbsenceCalculationService(session)
    
    target_date = None
    if year:
        target_date = date(year, 12, 31)
    
    balance = calc_service.get_vacation_balance(employee_id, target_date)
    
    if not balance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No vacation allowance found for employee"
        )
    
    return {
        "employee_id": balance.employee_id,
        "year": balance.year,
        "annual_allowance": balance.annual_allowance,
        "carryover_days": balance.carryover_days,
        "total_allowance": balance.total_allowance,
        "used_days": balance.used_days,
        "pending_days": balance.pending_days,
        "available_days": balance.available_days
    }


@router.get("/vacation-balance/{employee_id}/multi-year")
def get_vacation_balance_multi_year(
    *,
    session: Session = Depends(get_session),
    employee_id: int,
    start_year: int = Query(...),
    end_year: int = Query(...)
):
    """Get vacation balances across multiple years"""
    if start_year > end_year:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Start year must be before or equal to end year"
        )
    
    if end_year - start_year > 10:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum 10 years can be requested at once"
        )
    
    calc_service = AbsenceCalculationService(session)
    balances = calc_service.get_vacation_balance_across_years(
        employee_id, start_year, end_year
    )
    
    return {
        "employee_id": employee_id,
        "start_year": start_year,
        "end_year": end_year,
        "balances": {
            str(year): {
                "year": balance.year,
                "annual_allowance": balance.annual_allowance,
                "carryover_days": balance.carryover_days,
                "total_allowance": balance.total_allowance,
                "used_days": balance.used_days,
                "pending_days": balance.pending_days,
                "available_days": balance.available_days
            }
            for year, balance in balances.items()
        }
    }


@router.post("/validate-with-holidays")
def validate_absence_with_holidays(
    *,
    session: Session = Depends(get_session),
    employee_id: int = Query(...),
    absence_type_id: int = Query(...),
    start_date: date = Query(...),
    end_date: date = Query(...),
    federal_state: Optional[FederalState] = Query(None),
    exclude_absence_id: Optional[int] = Query(None)
):
    """Comprehensive absence validation including holiday integration"""
    calc_service = AbsenceCalculationService(session)
    
    validation = calc_service.validate_absence_with_holidays(
        employee_id=employee_id,
        absence_type_id=absence_type_id,
        start_date=start_date,
        end_date=end_date,
        federal_state=federal_state,
        exclude_absence_id=exclude_absence_id
    )
    
    result = {
        "is_valid": validation.is_valid,
        "errors": validation.errors,
        "warnings": validation.warnings,
        "working_days": validation.working_days,
        "affected_holidays": [
            {
                "date": holiday.date,
                "name": holiday.name,
                "federal_state": holiday.federal_state,
                "is_nationwide": holiday.is_nationwide
            }
            for holiday in validation.affected_holidays
        ]
    }
    
    if validation.vacation_impact:
        result["vacation_impact"] = {
            "employee_id": validation.vacation_impact.employee_id,
            "year": validation.vacation_impact.year,
            "total_allowance": validation.vacation_impact.total_allowance,
            "used_days": validation.vacation_impact.used_days,
            "pending_days": validation.vacation_impact.pending_days,
            "available_days": validation.vacation_impact.available_days
        }
    
    return result


@router.get("/working-days-calculator")
def calculate_working_days(
    *,
    session: Session = Depends(get_session),
    start_date: date = Query(...),
    end_date: date = Query(...),
    federal_state: Optional[FederalState] = Query(None)
):
    """Calculate working days in a date range, excluding weekends and holidays"""
    calc_service = AbsenceCalculationService(session)
    
    try:
        calculation = calc_service.calculate_working_days_in_range(
            start_date, end_date, federal_state
        )
        
        return {
            "start_date": start_date,
            "end_date": end_date,
            "federal_state": federal_state.value if federal_state else None,
            "total_days": calculation.total_days,
            "working_days": calculation.working_days,
            "weekend_days": calculation.weekend_days,
            "holiday_days": calculation.holiday_days,
            "holidays": [
                {
                    "date": holiday.date,
                    "name": holiday.name,
                    "federal_state": holiday.federal_state,
                    "is_nationwide": holiday.is_nationwide
                }
                for holiday in calculation.holidays
            ]
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/suggest-alternative-dates")
def suggest_alternative_dates(
    *,
    session: Session = Depends(get_session),
    employee_id: int = Query(...),
    desired_start: date = Query(...),
    desired_end: date = Query(...),
    federal_state: Optional[FederalState] = Query(None),
    max_suggestions: int = Query(5)
):
    """Suggest alternative dates when desired dates have conflicts"""
    if max_suggestions > 10:
        max_suggestions = 10
    
    calc_service = AbsenceCalculationService(session)
    
    suggestions = calc_service.suggest_alternative_dates(
        employee_id=employee_id,
        desired_start=desired_start,
        desired_end=desired_end,
        federal_state=federal_state,
        max_suggestions=max_suggestions
    )
    
    return {
        "desired_start": desired_start,
        "desired_end": desired_end,
        "suggestions": [
            {
                "start_date": start,
                "end_date": end,
                "duration_days": (end - start).days + 1
            }
            for start, end in suggestions
        ]
    }


@router.get("/statistics")
def get_absence_statistics(
    *,
    session: Session = Depends(get_session),
    employee_id: Optional[int] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None)
):
    """Get comprehensive absence statistics"""
    calc_service = AbsenceCalculationService(session)
    
    stats = calc_service.get_absence_statistics(
        employee_id=employee_id,
        start_date=start_date,
        end_date=end_date
    )
    
    return {
        "filters": {
            "employee_id": employee_id,
            "start_date": start_date,
            "end_date": end_date
        },
        "statistics": stats
    }
