"""
Schema für Mitarbeiter-Kalenderinformationen
Vereinfachte Darstellung für Kalender-Sidebar
"""
from sqlmodel import SQLModel
from typing import Optional


class EmployeeCalendarInfo(SQLModel):
    """Vereinfachte Mitarbeiterinformationen für Kalender-Sidebar"""
    id: int
    first_name: str
    last_name: str
    full_name: str
    calendar_color: str
    active: bool
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "first_name": "Maria",
                "last_name": "Ganser",
                "full_name": "Maria Ganser",
                "calendar_color": "#3b82f6",
                "active": True
            }
        }
