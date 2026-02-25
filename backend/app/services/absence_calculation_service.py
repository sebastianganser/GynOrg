"""
Absence Calculation Service for Multi-Year Holiday Support

This service provides comprehensive absence calculation functionality that integrates
with the multi-year holiday system implemented in subtasks 18.1-18.5.
"""

from typing import List, Optional, Dict, Any, Tuple
from datetime import date, datetime, timedelta
from sqlmodel import Session, select, and_, or_, func
from dataclasses import dataclass

from app.models.absence import Absence, AbsenceStatus
from app.models.vacation_allowance import VacationAllowance
from app.models.employee import Employee
from app.models.absence_type import AbsenceType, AbsenceTypeCategory
from app.models.holiday import Holiday
from app.models.federal_state import FederalState
from app.services.holiday_service import HolidayService


@dataclass
class VacationBalance:
    """Vacation balance information for an employee"""
    employee_id: int
    year: int
    annual_allowance: int
    carryover_days: int
    total_allowance: int
    used_days: int
    pending_days: int
    available_days: int
    
    
@dataclass
class WorkingDaysCalculation:
    """Result of working days calculation"""
    total_days: int
    working_days: int
    weekend_days: int
    holiday_days: int
    holidays: List[Holiday]


@dataclass
class AbsenceValidationResult:
    """Result of absence validation"""
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    working_days: int
    affected_holidays: List[Holiday]
    vacation_impact: Optional[VacationBalance] = None


class AbsenceCalculationService:
    """Service for calculating absence-related metrics with multi-year holiday support"""
    
    def __init__(self, session: Session):
        self.session = session
        self.holiday_service = HolidayService(session)
    
    def calculate_working_days_in_range(
        self, 
        start_date: date, 
        end_date: date, 
        federal_state: Optional[FederalState] = None
    ) -> WorkingDaysCalculation:
        """
        Calculate working days in a date range, excluding weekends and holidays.
        
        Args:
            start_date: Start date of the range
            end_date: End date of the range (inclusive)
            federal_state: Federal state for holiday calculation
            
        Returns:
            WorkingDaysCalculation with detailed breakdown
        """
        if start_date > end_date:
            raise ValueError("Start date must be before or equal to end date")
        
        # Get holidays in the date range
        holidays = self.holiday_service.get_holidays_in_date_range(
            start_date, end_date, federal_state
        )
        
        # Create set of holiday dates for fast lookup
        holiday_dates = {holiday.date for holiday in holidays}
        
        # Calculate day by day
        current_date = start_date
        total_days = 0
        working_days = 0
        weekend_days = 0
        holiday_days = 0
        
        while current_date <= end_date:
            total_days += 1
            
            # Check if it's a weekend (Saturday = 5, Sunday = 6)
            if current_date.weekday() >= 5:
                weekend_days += 1
            # Check if it's a holiday
            elif current_date in holiday_dates:
                holiday_days += 1
            else:
                working_days += 1
            
            current_date += timedelta(days=1)
        
        return WorkingDaysCalculation(
            total_days=total_days,
            working_days=working_days,
            weekend_days=weekend_days,
            holiday_days=holiday_days,
            holidays=holidays
        )
    
    def get_holidays_in_absence_range(
        self, 
        start_date: date, 
        end_date: date, 
        federal_state: Optional[FederalState] = None
    ) -> List[Holiday]:
        """
        Get holidays that fall within an absence date range.
        
        Args:
            start_date: Start date of absence
            end_date: End date of absence
            federal_state: Federal state for holiday filtering
            
        Returns:
            List of holidays in the date range
        """
        return self.holiday_service.get_holidays_in_date_range(
            start_date, end_date, federal_state
        )
    
    def get_vacation_balance(
        self, 
        employee_id: int, 
        target_date: Optional[date] = None
    ) -> Optional[VacationBalance]:
        """
        Calculate vacation balance for an employee at a specific date.
        
        Args:
            employee_id: Employee ID
            target_date: Date for balance calculation (defaults to today)
            
        Returns:
            VacationBalance or None if no allowance found
        """
        if target_date is None:
            target_date = date.today()
        
        year = target_date.year
        
        # Get vacation allowance for the year
        allowance_stmt = select(VacationAllowance).where(
            and_(
                VacationAllowance.employee_id == employee_id,
                VacationAllowance.year == year
            )
        )
        allowance = self.session.exec(allowance_stmt).first()
        
        if not allowance:
            return None
        
        # Calculate used vacation days (approved absences)
        used_stmt = select(func.sum(
            func.julianday(Absence.end_date) - func.julianday(Absence.start_date) + 1
        )).select_from(
            Absence.__table__.join(AbsenceType.__table__)
        ).where(
            and_(
                Absence.employee_id == employee_id,
                Absence.start_date >= date(year, 1, 1),
                Absence.end_date <= target_date,
                Absence.status == AbsenceStatus.APPROVED,
                AbsenceType.category == AbsenceTypeCategory.VACATION
            )
        )
        used_days = self.session.exec(used_stmt).first() or 0
        
        # Calculate pending vacation days
        pending_stmt = select(func.sum(
            func.julianday(Absence.end_date) - func.julianday(Absence.start_date) + 1
        )).select_from(
            Absence.__table__.join(AbsenceType.__table__)
        ).where(
            and_(
                Absence.employee_id == employee_id,
                Absence.start_date >= date(year, 1, 1),
                Absence.status == AbsenceStatus.PENDING,
                AbsenceType.category == AbsenceTypeCategory.VACATION
            )
        )
        pending_days = self.session.exec(pending_stmt).first() or 0
        
        available_days = allowance.total_allowance - used_days - pending_days
        
        return VacationBalance(
            employee_id=employee_id,
            year=year,
            annual_allowance=allowance.annual_allowance,
            carryover_days=allowance.carryover_days,
            total_allowance=allowance.total_allowance,
            used_days=int(used_days),
            pending_days=int(pending_days),
            available_days=int(available_days)
        )
    
    def get_vacation_balance_across_years(
        self, 
        employee_id: int, 
        start_year: int, 
        end_year: int
    ) -> Dict[int, VacationBalance]:
        """
        Get vacation balances across multiple years.
        
        Args:
            employee_id: Employee ID
            start_year: Start year (inclusive)
            end_year: End year (inclusive)
            
        Returns:
            Dictionary mapping year to VacationBalance
        """
        balances = {}
        
        for year in range(start_year, end_year + 1):
            balance = self.get_vacation_balance(
                employee_id, 
                date(year, 12, 31)
            )
            if balance:
                balances[year] = balance
        
        return balances
    
    def validate_absence_with_holidays(
        self, 
        employee_id: int,
        absence_type_id: int,
        start_date: date, 
        end_date: date,
        federal_state: Optional[FederalState] = None,
        exclude_absence_id: Optional[int] = None
    ) -> AbsenceValidationResult:
        """
        Comprehensive absence validation including holiday integration.
        
        Args:
            employee_id: Employee ID
            absence_type_id: Absence type ID
            start_date: Start date of absence
            end_date: End date of absence
            federal_state: Federal state for holiday calculation
            exclude_absence_id: Absence ID to exclude from conflict checking
            
        Returns:
            AbsenceValidationResult with validation details
        """
        errors = []
        warnings = []
        
        # Validate basic date logic
        if start_date > end_date:
            errors.append("Start date must be before or equal to end date")
            return AbsenceValidationResult(
                is_valid=False,
                errors=errors,
                warnings=warnings,
                working_days=0,
                affected_holidays=[]
            )
        
        # Get absence type
        absence_type = self.session.get(AbsenceType, absence_type_id)
        if not absence_type:
            errors.append("Absence type not found")
            return AbsenceValidationResult(
                is_valid=False,
                errors=errors,
                warnings=warnings,
                working_days=0,
                affected_holidays=[]
            )
        
        # Calculate working days and holidays
        working_calc = self.calculate_working_days_in_range(
            start_date, end_date, federal_state
        )
        
        # Check max days per request
        if absence_type.max_days_per_request:
            total_days = (end_date - start_date).days + 1
            if total_days > absence_type.max_days_per_request:
                errors.append(
                    f"Maximum days per request exceeded: {total_days} > {absence_type.max_days_per_request}"
                )
        
        # Check for conflicts with existing absences
        conflicts = self._check_absence_conflicts(
            employee_id, start_date, end_date, exclude_absence_id
        )
        
        if conflicts:
            conflict_details = [
                f"Conflict with absence from {conflict.start_date} to {conflict.end_date}"
                for conflict in conflicts
            ]
            errors.append(f"Overlapping absences: {'; '.join(conflict_details)}")
        
        # Vacation-specific validation
        vacation_impact = None
        if absence_type.category == AbsenceTypeCategory.VACATION:
            vacation_impact = self._validate_vacation_request(
                employee_id, start_date, end_date, working_calc.working_days
            )
            
            if vacation_impact and vacation_impact.available_days < working_calc.working_days:
                errors.append(
                    f"Insufficient vacation days: {working_calc.working_days} requested, "
                    f"{vacation_impact.available_days} available"
                )
        
        # Add warnings for holidays
        if working_calc.holidays:
            holiday_names = [h.name for h in working_calc.holidays]
            warnings.append(
                f"Absence includes {len(working_calc.holidays)} holiday(s): {', '.join(holiday_names)}"
            )
        
        return AbsenceValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            working_days=working_calc.working_days,
            affected_holidays=working_calc.holidays,
            vacation_impact=vacation_impact
        )
    
    def suggest_alternative_dates(
        self, 
        employee_id: int,
        desired_start: date,
        desired_end: date,
        federal_state: Optional[FederalState] = None,
        max_suggestions: int = 5
    ) -> List[Tuple[date, date]]:
        """
        Suggest alternative dates when the desired dates have conflicts.
        
        Args:
            employee_id: Employee ID
            desired_start: Desired start date
            desired_end: Desired end date
            federal_state: Federal state for holiday calculation
            max_suggestions: Maximum number of suggestions
            
        Returns:
            List of (start_date, end_date) tuples
        """
        suggestions = []
        duration = (desired_end - desired_start).days + 1
        
        # Try dates before the desired period
        for offset in range(1, 30):  # Try up to 30 days before
            alt_start = desired_start - timedelta(days=offset)
            alt_end = alt_start + timedelta(days=duration - 1)
            
            validation = self.validate_absence_with_holidays(
                employee_id, 1, alt_start, alt_end, federal_state  # Assuming vacation type ID 1
            )
            
            if validation.is_valid:
                suggestions.append((alt_start, alt_end))
                if len(suggestions) >= max_suggestions:
                    break
        
        # Try dates after the desired period
        for offset in range(1, 30):  # Try up to 30 days after
            alt_start = desired_end + timedelta(days=offset)
            alt_end = alt_start + timedelta(days=duration - 1)
            
            validation = self.validate_absence_with_holidays(
                employee_id, 1, alt_start, alt_end, federal_state  # Assuming vacation type ID 1
            )
            
            if validation.is_valid:
                suggestions.append((alt_start, alt_end))
                if len(suggestions) >= max_suggestions:
                    break
        
        return suggestions[:max_suggestions]
    
    def _check_absence_conflicts(
        self, 
        employee_id: int, 
        start_date: date, 
        end_date: date,
        exclude_absence_id: Optional[int] = None
    ) -> List[Absence]:
        """Check for conflicting absences (internal method)"""
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
        
        return self.session.exec(statement).all()
    
    def _validate_vacation_request(
        self, 
        employee_id: int, 
        start_date: date, 
        end_date: date,
        working_days: int
    ) -> Optional[VacationBalance]:
        """Validate vacation request against allowance (internal method)"""
        # For multi-year requests, check each year separately
        years = set()
        current_date = start_date
        while current_date <= end_date:
            years.add(current_date.year)
            current_date += timedelta(days=1)
        
        # For simplicity, use the start year for validation
        # In a more complex implementation, you might split the request across years
        return self.get_vacation_balance(employee_id, start_date)
    
    def get_absence_statistics(
        self, 
        employee_id: Optional[int] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """
        Get comprehensive absence statistics.
        
        Args:
            employee_id: Optional employee filter
            start_date: Optional start date filter
            end_date: Optional end date filter
            
        Returns:
            Dictionary with absence statistics
        """
        statement = select(Absence)
        
        if employee_id:
            statement = statement.where(Absence.employee_id == employee_id)
        
        if start_date:
            statement = statement.where(Absence.end_date >= start_date)
        
        if end_date:
            statement = statement.where(Absence.start_date <= end_date)
        
        absences = self.session.exec(statement).all()
        
        # Calculate statistics
        total_absences = len(absences)
        approved_absences = len([a for a in absences if a.status == AbsenceStatus.APPROVED])
        pending_absences = len([a for a in absences if a.status == AbsenceStatus.PENDING])
        rejected_absences = len([a for a in absences if a.status == AbsenceStatus.REJECTED])
        
        total_days = sum((a.end_date - a.start_date).days + 1 for a in absences)
        
        return {
            "total_absences": total_absences,
            "approved_absences": approved_absences,
            "pending_absences": pending_absences,
            "rejected_absences": rejected_absences,
            "total_days": total_days,
            "average_duration": total_days / total_absences if total_absences > 0 else 0
        }
