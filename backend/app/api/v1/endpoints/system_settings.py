from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import Any

from app.core.database import get_session
from app.models.system_settings import SystemSettings, SystemSettingsRead, SystemSettingsUpdate

router = APIRouter()

@router.get("/", response_model=SystemSettingsRead)
def get_system_settings(
    db: Session = Depends(get_session)
) -> Any:
    """
    Get system settings. If none exist, create default settings.
    """
    settings = db.exec(select(SystemSettings).where(SystemSettings.user_id == "default")).first()
    if not settings:
        settings = SystemSettings(user_id="default", auto_logout_minutes=30)
        db.add(settings)
        db.commit()
        db.refresh(settings)
    return settings

@router.put("/", response_model=SystemSettingsRead)
def update_system_settings(
    *,
    db: Session = Depends(get_session),
    settings_in: SystemSettingsUpdate
) -> Any:
    """
    Update system settings.
    """
    settings = db.exec(select(SystemSettings).where(SystemSettings.user_id == "default")).first()
    if not settings:
        settings = SystemSettings(user_id="default")
        db.add(settings)
        db.commit()
        db.refresh(settings)
        
    update_data = settings_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(settings, field, value)
        
    db.add(settings)
    db.commit()
    db.refresh(settings)
    return settings
