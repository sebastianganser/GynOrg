from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from sqlalchemy.exc import IntegrityError

from app.core.database import get_session
from app.models.job_position import JobPosition, JobPositionCreate, JobPositionRead, JobPositionUpdate

router = APIRouter()

@router.get("/", response_model=List[JobPositionRead])
def read_job_positions(
    session: Session = Depends(get_session),
    skip: int = 0,
    limit: int = 100,
    active_only: bool = False
) -> Any:
    """
    Retrieve job positions.
    """
    query = select(JobPosition)
    if active_only:
        query = query.where(JobPosition.active == True)
        
    query = query.offset(skip).limit(limit)
    positions = session.exec(query).all()
    return positions

@router.post("/", response_model=JobPositionRead)
def create_job_position(
    *,
    session: Session = Depends(get_session),
    position_in: JobPositionCreate,
) -> Any:
    """
    Create new job position.
    """
    # Check if a position with the same name already exists
    statement = select(JobPosition).where(JobPosition.name == position_in.name)
    existing_position = session.exec(statement).first()
    if existing_position:
        raise HTTPException(
            status_code=400,
            detail="The job position with this name already exists in the system.",
        )
    
    position = JobPosition.model_validate(position_in)
    session.add(position)
    session.commit()
    session.refresh(position)
    return position

@router.put("/{position_id}", response_model=JobPositionRead)
def update_job_position(
    *,
    session: Session = Depends(get_session),
    position_id: int,
    position_in: JobPositionUpdate,
) -> Any:
    """
    Update a job position.
    """
    position = session.get(JobPosition, position_id)
    if not position:
        raise HTTPException(status_code=404, detail="Job position not found")
        
    # Check for name collision
    if position_in.name is not None and position_in.name != position.name:
        statement = select(JobPosition).where(JobPosition.name == position_in.name)
        existing_position = session.exec(statement).first()
        if existing_position and existing_position.id != position_id:
            raise HTTPException(
                status_code=400,
                detail="The job position with this name already exists in the system.",
            )
            
    update_data = position_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(position, field, value)
        
    session.add(position)
    session.commit()
    session.refresh(position)
    return position

@router.delete("/{position_id}")
def delete_job_position(
    *,
    session: Session = Depends(get_session),
    position_id: int,
) -> Any:
    """
    Delete a job position (Hard delete). The frontend should probably prefer soft-delete by setting active=False.
    """
    position = session.get(JobPosition, position_id)
    if not position:
        raise HTTPException(status_code=404, detail="Job position not found")
        
    session.delete(position)
    session.commit()
    return {"ok": True}
