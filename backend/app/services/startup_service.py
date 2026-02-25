"""
Startup Service für automatische Holiday-Daten-Population
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from sqlmodel import Session

from ..core.database import get_session
from ..models.federal_state import FederalState
from .holiday_service import HolidayService

logger = logging.getLogger(__name__)


class StartupService:
    """Service für Startup-Operationen, insbesondere Holiday-Daten-Management"""
    
    def __init__(self, session: Session):
        self.session = session
        self.holiday_service = HolidayService(session)
    
    async def ensure_holiday_data_complete(
        self, 
        start_year: int = 2020, 
        end_year: int = 2030,
        federal_states: Optional[List[FederalState]] = None,
        timeout_seconds: int = 30
    ) -> Dict[str, Any]:
        """
        Stellt sicher, dass alle Feiertage für den angegebenen Zeitraum vorhanden sind.
        
        Args:
            start_year: Startjahr für Holiday-Daten (Standard: 2020)
            end_year: Endjahr für Holiday-Daten (Standard: 2030)
            federal_states: Liste der Bundesländer (Standard: alle)
            timeout_seconds: Timeout für den Import-Prozess
            
        Returns:
            Dict mit Informationen über den Import-Prozess
        """
        start_time = datetime.now()
        result = {
            "success": True,
            "start_year": start_year,
            "end_year": end_year,
            "duration_seconds": 0,
            "missing_years_found": [],
            "import_result": None,
            "error": None,
            "skipped_reason": None
        }
        
        try:
            logger.info(f"🚀 Startup: Prüfe Holiday-Daten für {start_year}-{end_year}...")
            
            # Prüfe fehlende Jahre
            missing_years = self.holiday_service.get_missing_years(
                start_year, end_year, federal_states
            )
            
            result["missing_years_found"] = missing_years
            
            if not missing_years:
                logger.info("Startup: Alle Holiday-Daten bereits vollständig vorhanden")
                result["skipped_reason"] = "All holiday data already complete"
                return result
            
            logger.info(f"📅 Startup: Importiere fehlende Holiday-Daten für {len(missing_years)} Jahre: {missing_years}")
            
            # Importiere fehlende Jahre
            import_result = self.holiday_service.import_missing_years(
                missing_years, federal_states
            )
            
            result["import_result"] = import_result
            
            # Erfolg loggen
            imported = import_result.get("total_imported", 0)
            errors = import_result.get("total_errors", 0)
            
            if errors > 0:
                logger.warning(f"⚠️ Startup: Holiday-Import mit {errors} Fehlern abgeschlossen. {imported} Feiertage importiert.")
            else:
                logger.info(f"✅ Startup: Holiday-Import erfolgreich. {imported} Feiertage importiert.")
            
        except Exception as e:
            logger.error(f"❌ Startup: Fehler beim Holiday-Import: {str(e)}")
            result["success"] = False
            result["error"] = str(e)
            
            # Startup soll nicht fehlschlagen wegen Holiday-Problemen
            # Daher wird der Fehler nur geloggt, aber nicht weitergegeben
            
        finally:
            end_time = datetime.now()
            result["duration_seconds"] = (end_time - start_time).total_seconds()
            
            if result["success"]:
                logger.info(f"Startup: Holiday-Daten-Prüfung abgeschlossen in {result['duration_seconds']:.2f}s")
            else:
                logger.error(f"💥 Startup: Holiday-Daten-Prüfung fehlgeschlagen nach {result['duration_seconds']:.2f}s")
        
        return result
    
    def get_holiday_statistics(self) -> Dict[str, Any]:
        """Gibt Statistiken über vorhandene Holiday-Daten zurück"""
        try:
            from sqlmodel import select, func
            from ..models.holiday import Holiday
            
            # Gesamtanzahl Feiertage
            total_query = select(func.count(Holiday.id))
            total_holidays = self.session.exec(total_query).first()
            
            # Jahre mit Daten
            years_query = select(Holiday.year).distinct().order_by(Holiday.year)
            years = self.session.exec(years_query).all()
            
            # Bundesweite vs. bundeslandspezifische Feiertage
            nationwide_query = select(func.count(Holiday.id)).where(Holiday.is_nationwide == True)
            nationwide_count = self.session.exec(nationwide_query).first()
            
            return {
                "total_holidays": total_holidays or 0,
                "nationwide_holidays": nationwide_count or 0,
                "state_specific_holidays": (total_holidays or 0) - (nationwide_count or 0),
                "years_with_data": years,
                "year_range": {
                    "min": min(years) if years else None,
                    "max": max(years) if years else None,
                    "count": len(years)
                }
            }
            
        except Exception as e:
            logger.error(f"Fehler beim Abrufen der Holiday-Statistiken: {str(e)}")
            return {
                "error": str(e),
                "total_holidays": 0,
                "years_with_data": []
            }
    
    async def validate_holiday_data_integrity(self) -> Dict[str, Any]:
        """Validiert die Integrität der Holiday-Daten"""
        try:
            stats = self.get_holiday_statistics()
            
            validation_result = {
                "is_valid": True,
                "issues": [],
                "statistics": stats
            }
            
            # Prüfe ob grundlegende Daten vorhanden sind
            if stats["total_holidays"] == 0:
                validation_result["is_valid"] = False
                validation_result["issues"].append("No holiday data found in database")
            
            # Prüfe ob aktuelle und nächste Jahre abgedeckt sind
            current_year = datetime.now().year
            years = stats["years_with_data"]
            
            if current_year not in years:
                validation_result["issues"].append(f"Current year {current_year} not covered")
            
            if (current_year + 1) not in years:
                validation_result["issues"].append(f"Next year {current_year + 1} not covered")
            
            # Prüfe auf Lücken in den Jahren
            if years:
                year_gaps = []
                for i in range(len(years) - 1):
                    if years[i + 1] - years[i] > 1:
                        year_gaps.append(f"{years[i] + 1}-{years[i + 1] - 1}")
                
                if year_gaps:
                    validation_result["issues"].append(f"Year gaps found: {', '.join(year_gaps)}")
            
            if validation_result["issues"]:
                validation_result["is_valid"] = False
            
            return validation_result
            
        except Exception as e:
            logger.error(f"Fehler bei Holiday-Daten-Validierung: {str(e)}")
            return {
                "is_valid": False,
                "error": str(e),
                "issues": ["Validation failed due to error"]
            }


def get_startup_service() -> StartupService:
    """Dependency für StartupService"""
    session = next(get_session())
    return StartupService(session)
