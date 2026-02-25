from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session, select
from app.core.database import get_session
from app.core.auth import get_current_user_optional, get_current_user
from app.models.employee import Employee
from app.models.vacation_allowance import VacationAllowance
from app.schemas.vacation_allowance import (
    VacationAllowanceCreate,
    VacationAllowanceUpdate,
    VacationAllowanceRead
)

router = APIRouter()


@router.get("/", response_model=List[VacationAllowanceRead])
def get_vacation_allowances(
    year: Optional[int] = Query(None, description="Filter by year"),
    employee_id: Optional[int] = Query(None, description="Filter by employee ID"),
    session: Session = Depends(get_session),
    current_user: Optional[str] = Depends(get_current_user_optional)
):
    """Get vacation allowances with optional filtering"""
    statement = select(VacationAllowance)
    
    if year:
        statement = statement.where(VacationAllowance.year == year)
    
    if employee_id:
        statement = statement.where(VacationAllowance.employee_id == employee_id)
    
    allowances = session.exec(statement).all()
    return allowances


@router.get("/{allowance_id}", response_model=VacationAllowanceRead)
def get_vacation_allowance(
    allowance_id: int,
    session: Session = Depends(get_session),
    current_user: Optional[str] = Depends(get_current_user_optional)
):
    """Get a specific vacation allowance by ID"""
    allowance = session.get(VacationAllowance, allowance_id)
    if not allowance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vacation allowance not found"
        )
    return allowance


@router.post("/", response_model=VacationAllowanceRead, status_code=status.HTTP_201_CREATED)
def create_vacation_allowance(
    allowance_data: VacationAllowanceCreate,
    session: Session = Depends(get_session),
    current_user: Optional[str] = Depends(get_current_user_optional)
):
    """Create a new vacation allowance"""
    # Check if employee exists
    employee = session.get(Employee, allowance_data.employee_id)
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found"
        )
    
    # Check if allowance for this employee and year already exists
    existing_allowance = session.exec(
        select(VacationAllowance).where(
            VacationAllowance.employee_id == allowance_data.employee_id,
            VacationAllowance.year == allowance_data.year
        )
    ).first()
    
    if existing_allowance:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Vacation allowance for employee {allowance_data.employee_id} and year {allowance_data.year} already exists"
        )
    
    allowance = VacationAllowance(**allowance_data.model_dump())
    session.add(allowance)
    session.commit()
    session.refresh(allowance)
    return allowance


@router.put("/{allowance_id}", response_model=VacationAllowanceRead)
def update_vacation_allowance(
    allowance_id: int,
    allowance_data: VacationAllowanceUpdate,
    session: Session = Depends(get_session),
    current_user: str = Depends(get_current_user)
):
    """Update an existing vacation allowance"""
    allowance = session.get(VacationAllowance, allowance_id)
    if not allowance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vacation allowance not found"
        )
    
    # Update only provided fields
    update_data = allowance_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(allowance, field, value)
    
    session.add(allowance)
    session.commit()
    session.refresh(allowance)
    return allowance


@router.delete("/{allowance_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_vacation_allowance(
    allowance_id: int,
    session: Session = Depends(get_session),
    current_user: str = Depends(get_current_user)
):
    """Delete a vacation allowance"""
    allowance = session.get(VacationAllowance, allowance_id)
    if not allowance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vacation allowance not found"
        )
    
    session.delete(allowance)
    session.commit()
    return None


@router.get("/employee/{employee_id}/year/{year}", response_model=VacationAllowanceRead)
def get_vacation_allowance_by_employee_and_year(
    employee_id: int,
    year: int,
    session: Session = Depends(get_session),
    current_user: str = Depends(get_current_user)
):
    """Get vacation allowance for a specific employee and year"""
    # Check if employee exists
    employee = session.get(Employee, employee_id)
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found"
        )
    
    allowance = session.exec(
        select(VacationAllowance).where(
            VacationAllowance.employee_id == employee_id,
            VacationAllowance.year == year
        )
    ).first()
    
    if not allowance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No vacation allowance found for employee {employee_id} in year {year}"
        )
    
    return allowance


@router.post("/employee/{employee_id}", response_model=VacationAllowanceRead, status_code=status.HTTP_201_CREATED)
def create_vacation_allowance_for_employee(
    employee_id: int,
    allowance_data: VacationAllowanceCreate,
    session: Session = Depends(get_session),
    current_user: str = Depends(get_current_user)
):
    """Create a vacation allowance for a specific employee"""
    # Check if employee exists first
    employee = session.get(Employee, employee_id)
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found"
        )
    
    # Create a new allowance data object with the correct employee_id
    allowance_dict = allowance_data.model_dump()
    allowance_dict['employee_id'] = employee_id
    
    # Check if allowance for this employee and year already exists
    existing_allowance = session.exec(
        select(VacationAllowance).where(
            VacationAllowance.employee_id == employee_id,
            VacationAllowance.year == allowance_dict['year']
        )
    ).first()
    
    if existing_allowance:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Vacation allowance for employee {employee_id} and year {allowance_dict['year']} already exists"
        )
    
    allowance = VacationAllowance(**allowance_dict)
    session.add(allowance)
    session.commit()
    session.refresh(allowance)
    return allowance
