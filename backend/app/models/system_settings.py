from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime


class SystemSettingsBase(SQLModel):
    """Basis-Modell für Grundeinstellungen (System Settings)"""
    auto_logout_minutes: int = Field(
        default=30,
        description="Automatische Abmeldung nach X Minuten Inaktivität"
    )

class SystemSettings(SystemSettingsBase, table=True):
    """Systemeinstellungen-Tabelle"""
    __tablename__ = "system_settings"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(
        default="default",
        max_length=50,
        description="Benutzer-ID (falls später mandantenfähig)"
    )
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class SystemSettingsCreate(SystemSettingsBase):
    """Modell für das Erstellen von Grundeinstellungen"""
    pass

class SystemSettingsUpdate(SQLModel):
    """Modell für das Aktualisieren von Grundeinstellungen"""
    auto_logout_minutes: Optional[int] = None

class SystemSettingsRead(SystemSettingsBase):
    """Modell für das Lesen (Output) von Grundeinstellungen"""
    id: int
    user_id: str
    created_at: datetime
    updated_at: datetime
