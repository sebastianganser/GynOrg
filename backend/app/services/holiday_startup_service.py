"""
Holiday Startup Service
Handles automatic holiday import on application startup.
"""
import logging
from typing import Dict, Any
from sqlmodel import Session

from ..core.config import settings
from ..core.database import get_session
from .holiday_service import HolidayService
from ..models.federal_state import FederalState

logger = logging.getLogger(__name__)


class HolidayStartupService:
    """Service für automatischen Feiertage-Import beim App-Start"""
    
    def __init__(self, session: Session):
        self.session = session
        self.holiday_service = HolidayService(session)
    
    def ensure_holiday_data(self) -> Dict[str, Any]:
        """
        Stellt sicher, dass Feiertage für den konfigurierten Jahresbereich vorhanden sind.
        
        Returns:
            Dict mit Import-Statistiken und Status-Informationen
        """
        if not settings.HOLIDAY_AUTO_IMPORT_ON_STARTUP:
            logger.info("Auto-import disabled, skipping holiday data check")
            return {
                "auto_import_enabled": False,
                "action": "skipped",
                "message": "Auto-import is disabled in configuration"
            }
        
        try:
            # Jahresbereich aus Konfiguration abrufen
            start_year, end_year = settings.get_holiday_year_range()
            
            logger.info(f"Checking holiday data for years {start_year}-{end_year}")
            
            # Fehlende Jahre ermitteln
            missing_years = self.holiday_service.get_missing_years(
                start_year, 
                end_year,
                list(FederalState)  # Alle Bundesländer
            )
            
            if not missing_years:
                logger.info(f"All holidays for {start_year}-{end_year} already present")
                return {
                    "auto_import_enabled": True,
                    "action": "none_needed",
                    "year_range": {"start": start_year, "end": end_year},
                    "missing_years": [],
                    "message": f"All holidays for {start_year}-{end_year} already present"
                }
            
            # Fehlende Jahre importieren
            logger.info(f"Importing holidays for {len(missing_years)} missing years: {missing_years}")
            
            import_result = self.holiday_service.import_missing_years(
                missing_years,
                list(FederalState)
            )
            
            logger.info(
                f"Holiday import completed: {import_result['total_imported']} imported, "
                f"{import_result['total_skipped']} skipped, "
                f"{import_result['total_errors']} errors"
            )
            
            return {
                "auto_import_enabled": True,
                "action": "imported",
                "year_range": {"start": start_year, "end": end_year},
                "missing_years": missing_years,
                "import_result": import_result,
                "message": f"Successfully imported holidays for {len(missing_years)} years"
            }
            
        except Exception as e:
            logger.error(f"Error during holiday startup import: {e}", exc_info=True)
            return {
                "auto_import_enabled": True,
                "action": "error",
                "error": str(e),
                "message": f"Failed to import holidays: {str(e)}"
            }


async def ensure_holiday_data_on_startup() -> Dict[str, Any]:
    """
    Async wrapper für Startup-Import.
    Wird von main.py beim startup_event aufgerufen.
    
    Returns:
        Dict mit Import-Statistiken und Status
    """
    try:
        session = next(get_session())
        startup_service = HolidayStartupService(session)
        result = startup_service.ensure_holiday_data()
        session.close()
        return result
    except Exception as e:
        logger.error(f"Critical error in holiday startup service: {e}", exc_info=True)
        return {
            "auto_import_enabled": True,
            "action": "critical_error",
            "error": str(e),
            "message": "Critical error during holiday import"
        }
