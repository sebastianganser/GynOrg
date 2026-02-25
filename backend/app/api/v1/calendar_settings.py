from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import Optional
from datetime import datetime
import traceback
import logging

from ...core.database import get_session
from ...models.calendar_settings import (
    CalendarSettings,
    CalendarSettingsCreate,
    CalendarSettingsUpdate,
    CalendarSettingsResponse
)
from ...models.federal_state import FederalState

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('calendar_settings_debug.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

router = APIRouter()


def get_or_create_default_settings(session: Session, user_id: str = "default") -> CalendarSettings:
    """Holt die Einstellungen oder erstellt Standard-Einstellungen"""
    statement = select(CalendarSettings).where(CalendarSettings.user_id == user_id)
    settings = session.exec(statement).first()
    
    if not settings:
        # Standard-Einstellungen erstellen
        settings = CalendarSettings(
            user_id=user_id,
            selected_federal_states=[FederalState.NORDRHEIN_WESTFALEN.name],  # Default: NRW
            show_nationwide_holidays=True,
            show_calendar_weeks=False,
            # Kalender-Filter (alle standardmäßig aktiviert)
            show_holidays=True,
            show_school_vacations=True,
            show_vacation_absences=True,
            show_sick_leave=True,
            show_training=True,
            show_special_leave=True,
            # Mitarbeiter-Filter (None = alle sichtbar)
            visible_employee_ids=None
        )
        session.add(settings)
        session.commit()
        session.refresh(settings)
    
    return settings


@router.get("/", response_model=CalendarSettingsResponse)
def get_calendar_settings(
    user_id: str = "default",
    session: Session = Depends(get_session)
):
    """Holt die aktuellen Kalendereinstellungen"""
    try:
        logger.info(f"GET /calendar-settings/ called for user_id: {user_id}")
        settings = get_or_create_default_settings(session, user_id)
        logger.info(f"Settings retrieved: {settings}")
        logger.info(f"Settings type: {type(settings)}")
        logger.info(f"Settings.selected_federal_states: {settings.selected_federal_states}")
        logger.info(f"Settings.selected_federal_states type: {type(settings.selected_federal_states)}")
        
        response = CalendarSettingsResponse.from_settings(settings)
        logger.info(f"Response created successfully: {response}")
        return response
    except Exception as e:
        logger.error(f"ERROR in get_calendar_settings: {str(e)}")
        logger.error(f"Full traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Fehler beim Laden der Kalendereinstellungen: {str(e)}"
        )


@router.put("/", response_model=CalendarSettingsResponse)
def update_calendar_settings(
    settings_update: CalendarSettingsUpdate,
    user_id: str = "default",
    session: Session = Depends(get_session)
):
    """Aktualisiert die Kalendereinstellungen"""
    try:
        # Bestehende Einstellungen holen oder erstellen
        settings = get_or_create_default_settings(session, user_id)
        
        # Validierung der Bundesländer
        if settings_update.selected_federal_states is not None:
            # Prüfen ob alle Bundesländer-Codes gültig sind (Kürzel wie "BW", "BY", etc.)
            valid_states = set(state.value for state in FederalState)
            invalid_states = set(settings_update.selected_federal_states) - valid_states
            
            if invalid_states:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Ungültige Bundesländer-Codes: {', '.join(invalid_states)}"
                )
            
            # Mindestens ein Bundesland muss ausgewählt sein
            if len(settings_update.selected_federal_states) == 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Mindestens ein Bundesland muss ausgewählt werden"
                )
            
            settings.selected_federal_states = settings_update.selected_federal_states
        
        # Validierung der Schulferien-Bundesländer
        if settings_update.school_holiday_federal_states is not None:
            # Prüfen ob alle Bundesländer-Codes gültig sind
            valid_states = set(state.value for state in FederalState)
            invalid_states = set(settings_update.school_holiday_federal_states) - valid_states
            
            if invalid_states:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Ungültige Bundesländer-Codes für Schulferien: {', '.join(invalid_states)}"
                )
            
            settings.school_holiday_federal_states = settings_update.school_holiday_federal_states
        
        # Andere Felder aktualisieren
        if settings_update.show_nationwide_holidays is not None:
            settings.show_nationwide_holidays = settings_update.show_nationwide_holidays
        
        if settings_update.show_calendar_weeks is not None:
            settings.show_calendar_weeks = settings_update.show_calendar_weeks
        
        # Kalender-Filter aktualisieren
        if settings_update.show_holidays is not None:
            settings.show_holidays = settings_update.show_holidays
        
        if settings_update.show_school_vacations is not None:
            settings.show_school_vacations = settings_update.show_school_vacations
        
        if settings_update.show_vacation_absences is not None:
            settings.show_vacation_absences = settings_update.show_vacation_absences
        
        if settings_update.show_sick_leave is not None:
            settings.show_sick_leave = settings_update.show_sick_leave
        
        if settings_update.show_training is not None:
            settings.show_training = settings_update.show_training
        
        if settings_update.show_special_leave is not None:
            settings.show_special_leave = settings_update.show_special_leave
        
        # Mitarbeiter-Filter aktualisieren
        if settings_update.visible_employee_ids is not None:
            settings.visible_employee_ids = settings_update.visible_employee_ids
        
        # Zeitstempel aktualisieren
        settings.updated_at = datetime.utcnow()
        
        session.add(settings)
        session.commit()
        session.refresh(settings)
        
        return CalendarSettingsResponse.from_settings(settings)
        
    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Fehler beim Speichern der Kalendereinstellungen: {str(e)}"
        )


@router.post("/reset", response_model=CalendarSettingsResponse)
def reset_calendar_settings(
    user_id: str = "default",
    session: Session = Depends(get_session)
):
    """Setzt die Kalendereinstellungen auf Standard zurück"""
    try:
        # Bestehende Einstellungen löschen
        statement = select(CalendarSettings).where(CalendarSettings.user_id == user_id)
        existing_settings = session.exec(statement).first()
        
        if existing_settings:
            session.delete(existing_settings)
            session.commit()
        
        # Neue Standard-Einstellungen erstellen
        settings = get_or_create_default_settings(session, user_id)
        return CalendarSettingsResponse.from_settings(settings)
        
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Fehler beim Zurücksetzen der Kalendereinstellungen: {str(e)}"
        )


@router.get("/federal-states")
def get_available_federal_states():
    """Gibt alle verfügbaren Bundesländer zurück"""
    federal_states = [
        {"code": "BW", "name": "Baden-Württemberg"},
        {"code": "BY", "name": "Bayern"},
        {"code": "BE", "name": "Berlin"},
        {"code": "BB", "name": "Brandenburg"},
        {"code": "HB", "name": "Bremen"},
        {"code": "HH", "name": "Hamburg"},
        {"code": "HE", "name": "Hessen"},
        {"code": "MV", "name": "Mecklenburg-Vorpommern"},
        {"code": "NI", "name": "Niedersachsen"},
        {"code": "NW", "name": "Nordrhein-Westfalen"},
        {"code": "RP", "name": "Rheinland-Pfalz"},
        {"code": "SL", "name": "Saarland"},
        {"code": "SN", "name": "Sachsen"},
        {"code": "ST", "name": "Sachsen-Anhalt"},
        {"code": "SH", "name": "Schleswig-Holstein"},
        {"code": "TH", "name": "Thüringen"}
    ]
    return {"federal_states": federal_states}
