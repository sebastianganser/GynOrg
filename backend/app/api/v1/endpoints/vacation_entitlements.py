from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session, select
from app.core.database import get_session
from app.core.auth import get_current_user_optional, get_current_user
from app.models.employee import Employee
from app.models.vacation_entitlement import VacationEntitlement
from app.models.vacation_entitlement import (
    VacationEntitlementCreate,
    VacationEntitlementUpdate,
    VacationEntitlementRead
)

router = APIRouter()


@router.get("/", response_model=List[VacationEntitlementRead])
def get_vacation_entitlements(
    employee_id: Optional[int] = Query(None, description="Filter by employee ID"),
    session: Session = Depends(get_session),
    current_user: Optional[str] = Depends(get_current_user_optional)
):
    """Get vacation entitlements with optional filtering"""
    statement = select(VacationEntitlement)
    
    if employee_id:
        statement = statement.where(VacationEntitlement.employee_id == employee_id)
    
    # Sort by from_date descending
    statement = statement.order_by(VacationEntitlement.from_date.desc())
    
    entitlements = session.exec(statement).all()
    return entitlements


@router.post("/", response_model=VacationEntitlementRead, status_code=status.HTTP_201_CREATED)
def create_vacation_entitlement(
    entitlement_data: VacationEntitlementCreate,
    session: Session = Depends(get_session),
    current_user: str = Depends(get_current_user)
):
    """Create a new vacation entitlement"""
    # Check if employee exists
    employee = session.get(Employee, entitlement_data.employee_id)
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found"
        )
    
    # Check if entitlement for this employee and date already exists
    existing_entitlement = session.exec(
        select(VacationEntitlement).where(
            VacationEntitlement.employee_id == entitlement_data.employee_id,
            VacationEntitlement.from_date == entitlement_data.from_date
        )
    ).first()
    
    if existing_entitlement:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Vacation entitlement for employee {entitlement_data.employee_id} and date {entitlement_data.from_date} already exists"
        )
    
    entitlement = VacationEntitlement(**entitlement_data.model_dump())
    session.add(entitlement)
    session.commit()
    session.refresh(entitlement)
    return entitlement


@router.delete("/{entitlement_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_vacation_entitlement(
    entitlement_id: int,
    session: Session = Depends(get_session),
    current_user: str = Depends(get_current_user)
):
    """Delete a vacation entitlement"""
    entitlement = session.get(VacationEntitlement, entitlement_id)
    if not entitlement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vacation entitlement not found"
        )
    
    session.delete(entitlement)
    session.commit()
    return None
