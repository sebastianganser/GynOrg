from sqlmodel import SQLModel, Field, Column, JSON
from typing import Optional, List
from datetime import datetime
from .federal_state import FederalState


class CalendarSettingsBase(SQLModel):
    """Basis-Modell für Kalendereinstellungen"""
    selected_federal_states: List[str] = Field(
        default_factory=lambda: [FederalState.NORDRHEIN_WESTFALEN.name],  # Default: Nordrhein-Westfalen
        sa_column=Column(JSON),
        description="Liste der ausgewählten Bundesländer-Kürzel (für Feiertage)"
    )
    school_holiday_federal_states: List[str] = Field(
        default_factory=lambda: [],  # Default: Leer (keine Schulferien, oder NRW?)
        sa_column=Column(JSON),
        description="Liste der ausgewählten Bundesländer-Kürzel (für Schulferien)"
    )
    show_nationwide_holidays: bool = Field(
        default=True,
        description="Bundesweite Feiertage anzeigen"
    )
    show_calendar_weeks: bool = Field(
        default=False,
        description="Kalenderwochen im Kalender anzeigen"
    )
    
    # Urlaubs- und Feiertagsberechnung
    employer_federal_state: str = Field(
        default=FederalState.NORDRHEIN_WESTFALEN.name,
        description="Stammsitz des Arbeitgebers für Urlaubsberechnung"
    )
    dec_24_is_half_day: bool = Field(
        default=True,
        description="Heiligabend (24.12.) zählt als halber Urlaubstag"
    )
    dec_31_is_half_day: bool = Field(
        default=True,
        description="Silvester (31.12.) zählt als halber Urlaubstag"
    )
    
    # Kalender-Filter für verschiedene Event-Typen
    show_holidays: bool = Field(
        default=True,
        description="Feiertage im Kalender anzeigen"
    )
    show_school_vacations: bool = Field(
        default=True,
        description="Schulferien im Kalender anzeigen"
    )
    show_vacation_absences: bool = Field(
        default=True,
        description="Urlaubsabwesenheiten im Kalender anzeigen"
    )
    show_sick_leave: bool = Field(
        default=True,
        description="Krankmeldungen im Kalender anzeigen"
    )
    show_training: bool = Field(
        default=True,
        description="Fortbildungen im Kalender anzeigen"
    )
    show_special_leave: bool = Field(
        default=True,
        description="Sonderurlaub im Kalender anzeigen"
    )
    
    # Mitarbeiter-Filter
    visible_employee_ids: Optional[List[int]] = Field(
        default=None,
        sa_column=Column(JSON),
        description="Liste der sichtbaren Mitarbeiter-IDs (None = alle sichtbar)"
    )
    
    # Farbanpassungen für allgemeine Kalenderkategorien (die keinen separaten Eintrag in der DB haben)
    holiday_color: str = Field(
        default="#EF4444",  # red-500
        description="Farbe für Feiertage im Kalender"
    )
    school_vacation_color: str = Field(
        default="#3B82F6",  # blue-500
        description="Farbe für Schulferien im Kalender"
    )


class CalendarSettings(CalendarSettingsBase, table=True):
    """Kalendereinstellungen-Tabelle"""
    __tablename__ = "calendar_settings"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: Optional[str] = Field(
        default="default",  # Für Einzelnutzer-System
        max_length=50,
        description="Benutzer-ID (für zukünftige Mehrbenutzerfähigkeit)"
    )
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class CalendarSettingsCreate(CalendarSettingsBase):
    """Modell für das Erstellen von Kalendereinstellungen"""
    pass


class CalendarSettingsUpdate(SQLModel):
    """Modell für das Aktualisieren von Kalendereinstellungen"""
    selected_federal_states: Optional[List[str]] = None
    school_holiday_federal_states: Optional[List[str]] = None
    show_nationwide_holidays: Optional[bool] = None
    show_calendar_weeks: Optional[bool] = None
    
    # Urlaubsberechnung
    employer_federal_state: Optional[str] = None
    dec_24_is_half_day: Optional[bool] = None
    dec_31_is_half_day: Optional[bool] = None
    
    # Kalender-Filter
    show_holidays: Optional[bool] = None
    show_school_vacations: Optional[bool] = None
    show_vacation_absences: Optional[bool] = None
    show_sick_leave: Optional[bool] = None
    show_training: Optional[bool] = None
    show_special_leave: Optional[bool] = None
    
    # Mitarbeiter-Filter
    visible_employee_ids: Optional[List[int]] = None

    # Farbanpassungen
    holiday_color: Optional[str] = None
    school_vacation_color: Optional[str] = None


class CalendarSettingsRead(CalendarSettingsBase):
    """Modell für das Lesen von Kalendereinstellungen"""
    id: int
    user_id: str
    created_at: datetime
    updated_at: datetime


class CalendarSettingsResponse(CalendarSettingsRead):
    """Erweiterte Antwort mit zusätzlichen Informationen"""
    federal_states_display: List[dict] = Field(
        description="Bundesländer mit Anzeigenamen für Frontend"
    )
    
    @classmethod
    def from_settings(cls, settings: CalendarSettings) -> "CalendarSettingsResponse":
        """Erstellt eine Response aus CalendarSettings mit Anzeigenamen"""
        federal_states_display = []
        selected_states = settings.selected_federal_states or []
        for state_code in selected_states:
            try:
                state = FederalState[state_code]
                federal_states_display.append({
                    "code": state_code,
                    "name": state.value
                })
            except KeyError:
                # Fallback für ungültige Codes
                federal_states_display.append({
                    "code": state_code,
                    "name": state_code
                })
        
        school_holiday_federal_states_display = []
        school_states = settings.school_holiday_federal_states or []
        for state_code in school_states:
            try:
                state = FederalState[state_code]
                school_holiday_federal_states_display.append({
                    "code": state_code,
                    "name": state.value
                })
            except KeyError:
                school_holiday_federal_states_display.append({
                    "code": state_code,
                    "name": state_code
                })
        
        return cls(
            id=settings.id,
            user_id=settings.user_id,
            selected_federal_states=selected_states,
            school_holiday_federal_states=school_states,
            show_nationwide_holidays=settings.show_nationwide_holidays,
            show_calendar_weeks=settings.show_calendar_weeks,
            employer_federal_state=settings.employer_federal_state,
            dec_24_is_half_day=settings.dec_24_is_half_day,
            dec_31_is_half_day=settings.dec_31_is_half_day,
            show_holidays=settings.show_holidays,
            show_school_vacations=settings.show_school_vacations,
            show_vacation_absences=settings.show_vacation_absences,
            show_sick_leave=settings.show_sick_leave,
            show_training=settings.show_training,
            show_special_leave=settings.show_special_leave,
            visible_employee_ids=settings.visible_employee_ids,
            holiday_color=settings.holiday_color,
            school_vacation_color=settings.school_vacation_color,
            created_at=settings.created_at,
            updated_at=settings.updated_at,
            federal_states_display=federal_states_display
        )
