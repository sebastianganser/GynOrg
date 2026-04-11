from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.core.database import get_session
from app.models.absence_type import (
    AbsenceType,
    AbsenceTypeCreate,
    AbsenceTypeUpdate,
    AbsenceTypeRead
)

router = APIRouter()


@router.get("/", response_model=List[AbsenceTypeRead])
def get_absence_types(
    *,
    session: Session = Depends(get_session),
    skip: int = 0,
    limit: int = 100,
    active_only: bool = True
):
    """Get all absence types"""
    statement = select(AbsenceType)
    
    if active_only:
        statement = statement.where(AbsenceType.active == True)
    
    statement = statement.offset(skip).limit(limit)
    absence_types = session.exec(statement).all()
    return absence_types


@router.get("/{absence_type_id}", response_model=AbsenceTypeRead)
def get_absence_type(
    *,
    session: Session = Depends(get_session),
    absence_type_id: int
):
    """Get a specific absence type by ID"""
    absence_type = session.get(AbsenceType, absence_type_id)
    if not absence_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Absence type not found"
        )
    return absence_type


@router.post("/", response_model=AbsenceTypeRead, status_code=status.HTTP_201_CREATED)
def create_absence_type(
    *,
    session: Session = Depends(get_session),
    absence_type_in: AbsenceTypeCreate
):
    """Create a new absence type"""
    absence_type = AbsenceType.model_validate(absence_type_in)
    session.add(absence_type)
    session.commit()
    session.refresh(absence_type)
    return absence_type


@router.put("/{absence_type_id}", response_model=AbsenceTypeRead)
def update_absence_type(
    *,
    session: Session = Depends(get_session),
    absence_type_id: int,
    absence_type_in: AbsenceTypeUpdate
):
    """Update an absence type"""
    absence_type = session.get(AbsenceType, absence_type_id)
    if not absence_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Absence type not found"
        )
    
    absence_type_data = absence_type_in.model_dump(exclude_unset=True)
    for field, value in absence_type_data.items():
        setattr(absence_type, field, value)
    
    session.add(absence_type)
    session.commit()
    session.refresh(absence_type)
    return absence_type


@router.delete("/{absence_type_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_absence_type(
    *,
    session: Session = Depends(get_session),
    absence_type_id: int
):
    """Delete an absence type (soft delete by setting active=False)"""
    absence_type = session.get(AbsenceType, absence_type_id)
    if not absence_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Absence type not found"
        )
    
    # Soft delete by setting active to False
    absence_type.active = False
    session.add(absence_type)
    session.commit()
    return None


@router.delete("/{absence_type_id}/hard", status_code=status.HTTP_204_NO_CONTENT)
def hard_delete_absence_type(
    *,
    session: Session = Depends(get_session),
    absence_type_id: int
):
    """Hard delete an absence type (permanent deletion)"""
    absence_type = session.get(AbsenceType, absence_type_id)
    if not absence_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Absence type not found"
        )
    
    # Check if absence type is used in any absences
    from app.models.absence import Absence
    statement = select(Absence).where(Absence.absence_type_id == absence_type_id)
    existing_absences = session.exec(statement).first()
    
    if existing_absences:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete absence type that is used in existing absences"
        )
    
    session.delete(absence_type)
    session.commit()
    return None
