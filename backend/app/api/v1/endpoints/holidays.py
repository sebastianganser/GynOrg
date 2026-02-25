from typing import List, Optional
from datetime import date, datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session
from app.core.database import get_session
from app.models.holiday import Holiday, HolidayCreate, HolidayUpdate, HolidayRead, HolidayFilter, HolidayType, SchoolVacationType
from app.models.federal_state import FederalState
from app.services.holiday_service import HolidayService

router = APIRouter()


def get_holiday_service(session: Session = Depends(get_session)) -> HolidayService:
    """Dependency für HolidayService"""
    return HolidayService(session)


def validate_federal_state(state_str: Optional[str]) -> Optional[FederalState]:
    """
    Konvertiert String zu FederalState Enum mit robuster Validierung.
    
    Args:
        state_str: Bundesland als String (Kürzel oder Vollname)
        
    Returns:
        FederalState Enum oder None
        
    Raises:
        HTTPException: Bei ungültigem Bundesland
    """
    if not state_str:
        return None
    
    # Suche nach Enum-Member mit diesem Value (Kürzel wie "ST", "BW", etc.)
    for state in FederalState:
        if state.value == state_str:
            return state
    
    # Fallback: Versuche Enum-Name (z.B. "SACHSEN_ANHALT")
    try:
        return FederalState[state_str.upper()]
    except KeyError:
        # Letzter Fallback: Case-insensitive Suche
        for state in FederalState:
            if state.value.lower() == state_str.lower():
                return state
        
        # Wenn nichts gefunden, 422 Error mit hilfreichen Informationen
        valid_codes = [state.value for state in FederalState]
        raise HTTPException(
            status_code=422,
            detail=f"Ungültiges Bundesland: '{state_str}'. Gültige Kürzel: {valid_codes}"
        )


@router.get("/", response_model=List[HolidayRead])
def get_holidays(
    year: Optional[int] = Query(None, description="Jahr filtern"),
    month: Optional[int] = Query(None, ge=1, le=12, description="Monat filtern (1-12)"),
    federal_state: Optional[str] = Query(None, description="Bundesland filtern (z.B. ST, BW, BY, etc.)"),
    include_nationwide: bool = Query(True, description="Bundesweite Feiertage einschließen"),
    holiday_type: Optional[HolidayType] = Query(None, description="Typ des Feiertags (PUBLIC_HOLIDAY, SCHOOL_VACATION)"),
    school_vacation_type: Optional[SchoolVacationType] = Query(None, description="Art der Schulferien (WINTER, EASTER, etc.)"),
    holiday_service: HolidayService = Depends(get_holiday_service)
):
    """
    Gibt Feiertage basierend auf Filterparametern zurück.
    
    - **year**: Jahr filtern (z.B. 2025)
    - **month**: Monat filtern (1-12)
    - **federal_state**: Bundesland filtern (z.B. ST, BW, BY, etc.)
    - **include_nationwide**: Bundesweite Feiertage einschließen (Standard: true)
    - **holiday_type**: Typ des Feiertags (PUBLIC_HOLIDAY, SCHOOL_VACATION)
    - **school_vacation_type**: Art der Schulferien
    """
    # Validiere und konvertiere federal_state String zu Enum
    validated_federal_state = validate_federal_state(federal_state)
    
    filter_params = HolidayFilter(
        year=year,
        month=month,
        federal_state=validated_federal_state,
        include_nationwide=include_nationwide,
        holiday_type=holiday_type,
        school_vacation_type=school_vacation_type
    )
    
    holidays = holiday_service.get_holidays(filter_params)
    return holidays


@router.get("/upcoming", response_model=List[HolidayRead])
def get_upcoming_holidays(
    federal_state: Optional[str] = Query(None, description="Bundesland filtern (z.B. ST, BW, BY, etc.)"),
    days: int = Query(30, ge=1, le=365, description="Anzahl Tage in die Zukunft"),
    holiday_service: HolidayService = Depends(get_holiday_service)
):
    """
    Gibt kommende Feiertage zurück.
    
    - **federal_state**: Bundesland filtern (z.B. ST, BW, BY, etc.)
    - **days**: Anzahl Tage in die Zukunft (Standard: 30)
    """
    # Validiere und konvertiere federal_state String zu Enum
    validated_federal_state = validate_federal_state(federal_state)
    
    holidays = holiday_service.get_upcoming_holidays(validated_federal_state, days)
    return holidays


@router.get("/check/{check_date}")
def check_holiday(
    check_date: date,
    federal_state: Optional[str] = Query(None, description="Bundesland für Prüfung (z.B. ST, BW, BY, etc.)"),
    holiday_service: HolidayService = Depends(get_holiday_service)
):
    """
    Prüft ob ein bestimmtes Datum ein Feiertag ist.
    
    - **check_date**: Zu prüfendes Datum (YYYY-MM-DD)
    - **federal_state**: Bundesland für bundeslandspezifische Prüfung (z.B. ST, BW, BY, etc.)
    """
    # Validiere und konvertiere federal_state String zu Enum
    validated_federal_state = validate_federal_state(federal_state)
    
    holiday = holiday_service.is_holiday(check_date, validated_federal_state)
    
    if holiday:
        return {
            "is_holiday": True,
            "holiday": holiday,
            "message": f"{check_date} ist ein Feiertag: {holiday.name}"
        }
    else:
        return {
            "is_holiday": False,
            "holiday": None,
            "message": f"{check_date} ist kein Feiertag"
        }


@router.post("/import/current-year")
def import_current_year_holidays(
    holiday_service: HolidayService = Depends(get_holiday_service)
):
    """
    Importiert Feiertage für das aktuelle Jahr.
    """
    current_year = datetime.now().year
    
    try:
        result = holiday_service.import_holidays_for_year(current_year)
        return {
            "year": current_year,
            "result": result,
            "message": f"Import für {current_year} abgeschlossen: {result['imported']} importiert, {result['skipped']} übersprungen"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Fehler beim Import: {str(e)}"
        )


@router.post("/import/next-year")
def import_next_year_holidays(
    holiday_service: HolidayService = Depends(get_holiday_service)
):
    """
    Importiert Feiertage für das nächste Jahr.
    """
    next_year = datetime.now().year + 1
    
    try:
        result = holiday_service.import_holidays_for_year(next_year)
        return {
            "year": next_year,
            "result": result,
            "message": f"Import für {next_year} abgeschlossen: {result['imported']} importiert, {result['skipped']} übersprungen"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Fehler beim Import: {str(e)}"
        )


@router.post("/import/{year}")
def import_holidays_for_year(
    year: int,
    federal_states: Optional[List[FederalState]] = None,
    holiday_service: HolidayService = Depends(get_holiday_service)
):
    """
    Importiert Feiertage für ein bestimmtes Jahr.
    
    - **year**: Jahr für den Import (z.B. 2025)
    - **federal_states**: Liste der Bundesländer (optional, Standard: alle)
    """
    if year < 1900 or year > 2100:
        raise HTTPException(
            status_code=400,
            detail="Jahr muss zwischen 1900 und 2100 liegen"
        )
    
    try:
        result = holiday_service.import_holidays_for_year(year, federal_states)
        return {
            "year": year,
            "federal_states": [state.value for state in (federal_states or list(FederalState))],
            "result": result,
            "message": f"Import für {year} abgeschlossen: {result['imported']} importiert, {result['skipped']} übersprungen"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Fehler beim Import: {str(e)}"
        )


@router.post("/bulk-import/{start_year}/{end_year}")
def bulk_import_holidays(
    start_year: int,
    end_year: int,
    federal_states: Optional[List[FederalState]] = None,
    holiday_service: HolidayService = Depends(get_holiday_service)
):
    """
    Importiert Feiertage für einen Jahresbereich (Bulk-Import).
    
    - **start_year**: Startjahr für den Import (z.B. 2020)
    - **end_year**: Endjahr für den Import (z.B. 2030)
    - **federal_states**: Liste der Bundesländer (optional, Standard: alle)
    """
    # Validierung der Jahre
    if start_year < 1900 or end_year > 2100:
        raise HTTPException(
            status_code=400,
            detail="Jahre müssen zwischen 1900 und 2100 liegen"
        )
    
    if start_year > end_year:
        raise HTTPException(
            status_code=400,
            detail="Startjahr muss kleiner oder gleich Endjahr sein"
        )
    
    if end_year - start_year > 50:
        raise HTTPException(
            status_code=400,
            detail="Maximaler Jahresbereich ist 50 Jahre"
        )
    
    try:
        result = holiday_service.bulk_import_holidays_range(start_year, end_year, federal_states)
        return {
            "start_year": start_year,
            "end_year": end_year,
            "years_processed": end_year - start_year + 1,
            "federal_states": [state.value for state in (federal_states or list(FederalState))],
            "result": result,
            "message": f"Bulk-Import für {start_year}-{end_year} abgeschlossen: {result['total_imported']} importiert, {result['total_skipped']} übersprungen"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Fehler beim Bulk-Import: {str(e)}"
        )


@router.post("/ensure-range/{start_year}/{end_year}")
def ensure_holiday_range(
    start_year: int,
    end_year: int,
    federal_states: Optional[List[FederalState]] = None,
    holiday_service: HolidayService = Depends(get_holiday_service)
):
    """
    Stellt sicher, dass Feiertage für einen Jahresbereich verfügbar sind.
    Importiert nur fehlende Jahre.
    
    - **start_year**: Startjahr für die Prüfung (z.B. 2020)
    - **end_year**: Endjahr für die Prüfung (z.B. 2030)
    - **federal_states**: Liste der Bundesländer (optional, Standard: alle)
    """
    # Validierung der Jahre
    if start_year < 1900 or end_year > 2100:
        raise HTTPException(
            status_code=400,
            detail="Jahre müssen zwischen 1900 und 2100 liegen"
        )
    
    if start_year > end_year:
        raise HTTPException(
            status_code=400,
            detail="Startjahr muss kleiner oder gleich Endjahr sein"
        )
    
    try:
        # Ermittle fehlende Jahre
        missing_years = holiday_service.get_missing_years(start_year, end_year, federal_states)
        
        if not missing_years:
            return {
                "start_year": start_year,
                "end_year": end_year,
                "missing_years": [],
                "result": {"total_imported": 0, "total_skipped": 0},
                "message": f"Alle Feiertage für {start_year}-{end_year} bereits vorhanden"
            }
        
        # Importiere nur fehlende Jahre
        result = holiday_service.import_missing_years(missing_years, federal_states)
        
        return {
            "start_year": start_year,
            "end_year": end_year,
            "missing_years": missing_years,
            "years_imported": len(missing_years),
            "federal_states": [state.value for state in (federal_states or list(FederalState))],
            "result": result,
            "message": f"Fehlende Feiertage für {len(missing_years)} Jahre importiert: {result['total_imported']} importiert"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Fehler beim Ensure-Range: {str(e)}"
        )


@router.delete("/year/{year}")
def delete_holidays_for_year(
    year: int,
    holiday_service: HolidayService = Depends(get_holiday_service)
):
    """
    Löscht alle Feiertage für ein bestimmtes Jahr.
    
    - **year**: Jahr dessen Feiertage gelöscht werden sollen
    """
    if year < 1900 or year > 2100:
        raise HTTPException(
            status_code=400,
            detail="Jahr muss zwischen 1900 und 2100 liegen"
        )
    
    try:
        deleted_count = holiday_service.delete_holidays_for_year(year)
        return {
            "year": year,
            "deleted_count": deleted_count,
            "message": f"{deleted_count} Feiertage für {year} gelöscht"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Fehler beim Löschen: {str(e)}"
        )


@router.get("/federal-states", response_model=List[dict])
def get_federal_states():
    """
    Gibt alle verfügbaren Bundesländer zurück.
    """
    return FederalState.get_all_states()


@router.get("/years")
def get_available_years(
    holiday_service: HolidayService = Depends(get_holiday_service)
):
    """
    Gibt alle Jahre zurück, für die Feiertage in der Datenbank vorhanden sind.
    (Einfache Version für Backward-Kompatibilität)
    """
    from sqlmodel import select, func
    from app.models.holiday import Holiday
    
    query = select(Holiday.year).distinct().order_by(Holiday.year)
    years = holiday_service.session.exec(query).all()
    
    return {
        "years": years,
        "count": len(years),
        "current_year": datetime.now().year
    }


@router.get("/years/detailed")
def get_detailed_available_years(
    include_incomplete: bool = Query(True, description="Unvollständige Jahre einschließen"),
    federal_state: Optional[str] = Query(None, description="Nach Bundesland filtern (z.B. ST, BW, BY, etc.)"),
    holiday_service: HolidayService = Depends(get_holiday_service)
):
    """
    Gibt detaillierte Informationen über verfügbare Jahre mit Holiday-Daten zurück.
    
    - **include_incomplete**: Unvollständige Jahre einschließen (Standard: true)
    - **federal_state**: Nach Bundesland filtern (z.B. ST, BW, BY, etc.)
    
    Liefert umfassende Informationen über:
    - Vollständigkeitsstatus pro Jahr
    - Anzahl Feiertage (bundesweit vs. bundeslandspezifisch)
    - Abgedeckte Bundesländer
    - Fehlende Daten
    - Zusammenfassende Statistiken
    """
    # Validiere und konvertiere federal_state String zu Enum
    validated_federal_state = validate_federal_state(federal_state)
    
    try:
        detailed_coverage = holiday_service.get_detailed_year_coverage(
            include_incomplete=include_incomplete,
            federal_state_filter=validated_federal_state
        )
        
        return detailed_coverage
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Fehler beim Abrufen der detaillierten Jahr-Informationen: {str(e)}"
        )


@router.get("/years/{year}/status")
def get_year_completeness_status(
    year: int,
    holiday_service: HolidayService = Depends(get_holiday_service)
):
    """
    Gibt detaillierte Vollständigkeits-Informationen für ein spezifisches Jahr zurück.
    
    - **year**: Jahr für die Statusprüfung (z.B. 2025)
    """
    if year < 1900 or year > 2100:
        raise HTTPException(
            status_code=400,
            detail="Jahr muss zwischen 1900 und 2100 liegen"
        )
    
    try:
        year_status = holiday_service.get_year_completeness_status(year)
        
        if year_status["holiday_count"] == 0:
            raise HTTPException(
                status_code=404,
                detail=f"Keine Feiertage für das Jahr {year} gefunden"
            )
        
        return year_status
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Fehler beim Abrufen des Jahr-Status: {str(e)}"
        )


@router.get("/statistics")
def get_holiday_statistics(
    year: Optional[int] = Query(None, description="Jahr für Statistiken"),
    holiday_service: HolidayService = Depends(get_holiday_service)
):
    """
    Gibt Statistiken über Feiertage zurück.
    """
    from sqlmodel import select, func
    from app.models.holiday import Holiday
    
    target_year = year or datetime.now().year
    
    # Gesamtanzahl Feiertage für das Jahr
    total_query = select(func.count(Holiday.id)).where(Holiday.year == target_year)
    total_holidays = holiday_service.session.exec(total_query).first()
    
    # Bundesweite Feiertage
    nationwide_query = select(func.count(Holiday.id)).where(
        Holiday.year == target_year,
        Holiday.is_nationwide == True
    )
    nationwide_holidays = holiday_service.session.exec(nationwide_query).first()
    
    # Bundeslandspezifische Feiertage pro Bundesland
    state_query = select(
        Holiday.federal_state,
        func.count(Holiday.id).label('count')
    ).where(
        Holiday.year == target_year,
        Holiday.is_nationwide == False
    ).group_by(Holiday.federal_state)
    
    state_results = holiday_service.session.exec(state_query).all()
    state_statistics = {
        state.value if state else "Unbekannt": count 
        for state, count in state_results
    }
    
    return {
        "year": target_year,
        "total_holidays": total_holidays or 0,
        "nationwide_holidays": nationwide_holidays or 0,
        "state_specific_holidays": (total_holidays or 0) - (nationwide_holidays or 0),
        "holidays_by_state": state_statistics
    }
