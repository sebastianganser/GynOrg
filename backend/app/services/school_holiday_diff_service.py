"""
School Holiday Diff Service for intelligent data change detection

This service compares API data with local database records to detect differences
and enable incremental updates, minimizing unnecessary database writes.
"""
import logging
from typing import List, Dict, Optional, Any, Tuple, Set
from datetime import datetime, date
from dataclasses import dataclass
from enum import Enum
from sqlmodel import Session, select
from ..models.holiday import (
    Holiday, HolidayCreate, HolidayUpdate, HolidayType, 
    SchoolVacationType, DataSource, SchoolHolidayCreate
)
from ..models.federal_state import FederalState
from ..core.database import get_session

logger = logging.getLogger(__name__)


class ConflictResolutionStrategy(str, Enum):
    """Strategien für die Konfliktauflösung"""
    API_WINS = "API_WINS"                    # API-Daten haben Vorrang
    LOCAL_WINS = "LOCAL_WINS"                # Lokale Änderungen behalten
    MANUAL_REVIEW = "MANUAL_REVIEW"          # Manuelle Entscheidung erforderlich
    TIMESTAMP_BASED = "TIMESTAMP_BASED"      # Neueste Änderung gewinnt


class ChangeType(str, Enum):
    """Arten von Änderungen"""
    NEW = "NEW"                              # Neue Einträge
    UPDATED = "UPDATED"                      # Geänderte Einträge
    DELETED = "DELETED"                      # Gelöschte Einträge
    CONFLICT = "CONFLICT"                    # Konflikte


@dataclass
class HolidayConflict:
    """Repräsentiert einen Datenkonflikt zwischen API und lokaler DB"""
    local_holiday: Holiday
    api_data: Dict[str, Any]
    conflict_fields: List[str]
    conflict_type: str
    resolution_strategy: ConflictResolutionStrategy
    created_at: datetime


@dataclass
class DiffStatistics:
    """Statistiken über den Diff-Prozess"""
    total_api_records: int = 0
    total_local_records: int = 0
    new_records: int = 0
    updated_records: int = 0
    deleted_records: int = 0
    conflicts: int = 0
    processing_time_ms: int = 0
    federal_state: Optional[FederalState] = None
    year: Optional[int] = None


@dataclass
class HolidayDiff:
    """Ergebnis des Datenvergleichs"""
    new_holidays: List[Dict[str, Any]]
    updated_holidays: List[Tuple[Holiday, Dict[str, Any]]]
    deleted_holidays: List[Holiday]
    conflicts: List[HolidayConflict]
    statistics: DiffStatistics
    
    def has_changes(self) -> bool:
        """Prüft ob Änderungen vorhanden sind"""
        return (len(self.new_holidays) > 0 or 
                len(self.updated_holidays) > 0 or 
                len(self.deleted_holidays) > 0)
    
    def has_conflicts(self) -> bool:
        """Prüft ob Konflikte vorhanden sind"""
        return len(self.conflicts) > 0


class SchoolHolidayDiffService:
    """
    Service für intelligente Erkennung von Datenänderungen zwischen API und DB
    
    Features:
    - Vergleich von API-Daten mit lokalen Datenbankeinträgen
    - Erkennung von neuen, geänderten und gelöschten Einträgen
    - Konfliktauflösung mit verschiedenen Strategien
    - Batch-Update-Unterstützung
    - Detaillierte Diff-Berichte und Statistiken
    """
    
    def __init__(self, session: Session, conflict_strategy: ConflictResolutionStrategy = ConflictResolutionStrategy.API_WINS):
        """
        Initialize the diff service
        
        Args:
            session: Database session
            conflict_strategy: Default strategy for conflict resolution
        """
        self.session = session
        self.default_conflict_strategy = conflict_strategy
        self.diff_stats = DiffStatistics()
    
    def compare_holiday_data(
        self, 
        api_data: List[Dict[str, Any]], 
        federal_state: FederalState, 
        year: int,
        conflict_strategy: Optional[ConflictResolutionStrategy] = None
    ) -> HolidayDiff:
        """
        Hauptmethode für den Vergleich von API-Daten mit lokalen Daten
        
        Args:
            api_data: Liste der API-Daten
            federal_state: Bundesland für den Vergleich
            year: Jahr für den Vergleich
            conflict_strategy: Strategie für Konfliktauflösung
            
        Returns:
            HolidayDiff mit allen erkannten Änderungen
        """
        start_time = datetime.now()
        strategy = conflict_strategy or self.default_conflict_strategy
        
        logger.info(f"Starting diff comparison for {federal_state.value} ({year}) with {len(api_data)} API records")
        
        # Lokale Daten abrufen
        local_holidays = self._get_local_school_holidays(federal_state, year)
        
        # Statistiken initialisieren
        self.diff_stats = DiffStatistics(
            total_api_records=len(api_data),
            total_local_records=len(local_holidays),
            federal_state=federal_state,
            year=year
        )
        
        # API-Daten indexieren für effizienten Zugriff
        api_index = self._build_api_index(api_data, federal_state)
        local_index = self._build_local_index(local_holidays)
        
        # Änderungen erkennen
        new_holidays = self._detect_new_holidays(api_index, local_index, federal_state, year)
        updated_holidays, conflicts = self._detect_updated_holidays(api_index, local_index, strategy)
        deleted_holidays = self._detect_deleted_holidays(api_index, local_index)
        
        # Statistiken aktualisieren
        self.diff_stats.new_records = len(new_holidays)
        self.diff_stats.updated_records = len(updated_holidays)
        self.diff_stats.deleted_records = len(deleted_holidays)
        self.diff_stats.conflicts = len(conflicts)
        self.diff_stats.processing_time_ms = int((datetime.now() - start_time).total_seconds() * 1000)
        
        logger.info(f"Diff completed: {self.diff_stats.new_records} new, {self.diff_stats.updated_records} updated, "
                   f"{self.diff_stats.deleted_records} deleted, {self.diff_stats.conflicts} conflicts")
        
        return HolidayDiff(
            new_holidays=new_holidays,
            updated_holidays=updated_holidays,
            deleted_holidays=deleted_holidays,
            conflicts=conflicts,
            statistics=self.diff_stats
        )
    
    def _get_local_school_holidays(self, federal_state: FederalState, year: int) -> List[Holiday]:
        """Abrufen der lokalen Schulferien aus der Datenbank"""
        query = select(Holiday).where(
            Holiday.federal_state_code == federal_state.name,
            Holiday.year == year,
            Holiday.holiday_type == HolidayType.SCHOOL_VACATION,
            Holiday.data_source == DataSource.MEHR_SCHULFERIEN_API
        )
        return self.session.exec(query).all()
    
    def _build_api_index(self, api_data: List[Dict[str, Any]], federal_state: FederalState) -> Dict[str, Dict[str, Any]]:
        """Erstellt einen Index für API-Daten basierend auf eindeutigen Schlüsseln"""
        index = {}
        for item in api_data:
            # Eindeutiger Schlüssel: api_id + federal_state + start_date
            key = self._generate_holiday_key(
                api_id=item.get("api_id", ""),
                federal_state_code=federal_state.name,
                start_date=item.get("start_date")
            )
            index[key] = item
        return index
    
    def _build_local_index(self, local_holidays: List[Holiday]) -> Dict[str, Holiday]:
        """Erstellt einen Index für lokale Daten basierend auf eindeutigen Schlüsseln"""
        index = {}
        for holiday in local_holidays:
            key = self._generate_holiday_key(
                api_id=holiday.api_id or "",
                federal_state_code=holiday.federal_state_code or "",
                start_date=holiday.date
            )
            index[key] = holiday
        return index
    
    def _generate_holiday_key(self, api_id: str, federal_state_code: str, start_date: Any) -> str:
        """Generiert einen eindeutigen Schlüssel für einen Ferieneintrag"""
        if isinstance(start_date, date):
            date_str = start_date.isoformat()
        elif isinstance(start_date, str):
            date_str = start_date
        else:
            date_str = str(start_date)
        
        return f"{api_id}_{federal_state_code}_{date_str}"
    
    def _detect_new_holidays(
        self, 
        api_index: Dict[str, Dict[str, Any]], 
        local_index: Dict[str, Holiday],
        federal_state: FederalState,
        year: int
    ) -> List[Dict[str, Any]]:
        """Erkennt neue Feiertage, die in der API aber nicht lokal vorhanden sind"""
        new_holidays = []
        
        for key, api_data in api_index.items():
            if key not in local_index:
                # Neuer Eintrag gefunden
                transformed_data = self._transform_api_to_create_schema(api_data, federal_state, year)
                if transformed_data:
                    new_holidays.append(transformed_data)
                    logger.debug(f"New holiday detected: {api_data.get('name', 'Unknown')}")
        
        return new_holidays
    
    def _detect_updated_holidays(
        self, 
        api_index: Dict[str, Dict[str, Any]], 
        local_index: Dict[str, Holiday],
        strategy: ConflictResolutionStrategy
    ) -> Tuple[List[Tuple[Holiday, Dict[str, Any]]], List[HolidayConflict]]:
        """Erkennt geänderte Feiertage und Konflikte"""
        updated_holidays = []
        conflicts = []
        
        for key, api_data in api_index.items():
            if key in local_index:
                local_holiday = local_index[key]
                
                # Prüfe auf Änderungen
                changes = self._detect_field_changes(local_holiday, api_data)
                
                if changes:
                    # Prüfe auf Konflikte (manuelle Änderungen)
                    if self._has_manual_changes(local_holiday):
                        conflict = HolidayConflict(
                            local_holiday=local_holiday,
                            api_data=api_data,
                            conflict_fields=list(changes.keys()),
                            conflict_type="MANUAL_VS_API",
                            resolution_strategy=strategy,
                            created_at=datetime.now()
                        )
                        conflicts.append(conflict)
                        logger.warning(f"Conflict detected for holiday: {local_holiday.name}")
                    else:
                        # Keine Konflikte, Update möglich
                        updated_holidays.append((local_holiday, changes))
                        logger.debug(f"Update detected for holiday: {local_holiday.name}")
        
        return updated_holidays, conflicts
    
    def _detect_deleted_holidays(
        self, 
        api_index: Dict[str, Dict[str, Any]], 
        local_index: Dict[str, Holiday]
    ) -> List[Holiday]:
        """Erkennt gelöschte Feiertage (lokal vorhanden, aber nicht in API)"""
        deleted_holidays = []
        
        for key, local_holiday in local_index.items():
            if key not in api_index:
                # Nur löschen wenn es sich um API-importierte Daten handelt
                if local_holiday.data_source == DataSource.MEHR_SCHULFERIEN_API:
                    deleted_holidays.append(local_holiday)
                    logger.debug(f"Deleted holiday detected: {local_holiday.name}")
        
        return deleted_holidays
    
    def _detect_field_changes(self, local_holiday: Holiday, api_data: Dict[str, Any]) -> Dict[str, Any]:
        """Erkennt Änderungen in einzelnen Feldern"""
        changes = {}
        
        # Name-Vergleich
        api_name = api_data.get("name", "").strip()
        if local_holiday.name != api_name and api_name:
            changes["name"] = api_name
        
        # Datum-Vergleich (Start)
        api_start_date = api_data.get("start_date")
        if isinstance(api_start_date, str):
            try:
                api_start_date = datetime.strptime(api_start_date, "%Y-%m-%d").date()
            except ValueError:
                logger.warning(f"Invalid date format in API data: {api_start_date}")
                api_start_date = None
        
        if api_start_date and local_holiday.date != api_start_date:
            changes["date"] = api_start_date
        
        # Ferientyp-Vergleich
        api_vacation_type = api_data.get("school_vacation_type")
        if api_vacation_type and local_holiday.school_vacation_type != api_vacation_type:
            changes["school_vacation_type"] = api_vacation_type
        
        # Notes-Vergleich
        api_notes = api_data.get("notes", "").strip()
        if api_notes and local_holiday.notes != api_notes:
            changes["notes"] = api_notes
        
        return changes
    
    def _has_manual_changes(self, holiday: Holiday) -> bool:
        """Prüft ob ein Feiertag manuelle Änderungen hat"""
        # Einfache Heuristik: Wenn data_source MANUAL ist oder last_updated sehr recent
        if holiday.data_source == DataSource.MANUAL:
            return True
        
        # Prüfe ob kürzlich manuell geändert (innerhalb der letzten 24h)
        if holiday.updated_at:
            time_diff = datetime.now() - holiday.updated_at
            if time_diff.total_seconds() < 86400:  # 24 Stunden
                return True
        
        return False
    
    def _transform_api_to_create_schema(
        self, 
        api_data: Dict[str, Any], 
        federal_state: FederalState, 
        year: int
    ) -> Optional[Dict[str, Any]]:
        """Transformiert API-Daten zu einem Create-Schema"""
        try:
            # Basis-Transformation
            transformed = {
                "name": api_data.get("name", "").strip(),
                "date": api_data.get("start_date"),
                "end_date": api_data.get("end_date") or api_data.get("ends_on"), # Fallback for different key names
                "federal_state": federal_state,
                "federal_state_code": federal_state.value,
                "holiday_type": HolidayType.SCHOOL_VACATION,
                "school_vacation_type": api_data.get("school_vacation_type"),
                "data_source": DataSource.MEHR_SCHULFERIEN_API,
                "api_id": str(api_data.get("api_id", "")),
                "year": year,
                "notes": api_data.get("notes", ""),
                "is_nationwide": False,
                "last_updated": datetime.now()
            }
            
            # Datum-Validierung
            if isinstance(transformed["date"], str):
                try:
                    transformed["date"] = datetime.strptime(transformed["date"], "%Y-%m-%d").date()
                except ValueError:
                    logger.warning(f"Invalid date format: {transformed['date']}")
                    return None

            if isinstance(transformed["end_date"], str):
                try:
                    transformed["end_date"] = datetime.strptime(transformed["end_date"], "%Y-%m-%d").date()
                except ValueError:
                    logger.warning(f"Invalid end date format: {transformed['end_date']}")
                    transformed["end_date"] = None
            
            # Validierung der Pflichtfelder
            if not all([transformed["name"], transformed["date"], transformed["school_vacation_type"]]):
                logger.warning(f"Missing required fields in API data: {api_data}")
                return None
            
            return transformed
            
        except Exception as e:
            logger.error(f"Failed to transform API data: {e}")
            return None
    
    def apply_diff(self, diff: HolidayDiff, dry_run: bool = False) -> Dict[str, Any]:
        """
        Wendet die erkannten Änderungen auf die Datenbank an
        
        Args:
            diff: HolidayDiff mit den Änderungen
            dry_run: Wenn True, werden keine Änderungen committet
            
        Returns:
            Ergebnis-Dictionary mit Statistiken
        """
        if not diff.has_changes():
            logger.info("No changes to apply")
            return {"applied": 0, "errors": 0, "skipped": 0}
        
        result = {"applied": 0, "errors": 0, "skipped": 0, "details": []}
        
        try:
            # Neue Feiertage hinzufügen
            for new_holiday_data in diff.new_holidays:
                try:
                    holiday = Holiday(**new_holiday_data)
                    self.session.add(holiday)
                    result["applied"] += 1
                    result["details"].append(f"Added: {holiday.name}")
                    logger.debug(f"Added new holiday: {holiday.name}")
                except Exception as e:
                    result["errors"] += 1
                    logger.error(f"Failed to add holiday: {e}")
            
            # Bestehende Feiertage aktualisieren
            for local_holiday, changes in diff.updated_holidays:
                try:
                    for field, value in changes.items():
                        setattr(local_holiday, field, value)
                    local_holiday.updated_at = datetime.now()
                    local_holiday.last_updated = datetime.now()
                    result["applied"] += 1
                    result["details"].append(f"Updated: {local_holiday.name}")
                    logger.debug(f"Updated holiday: {local_holiday.name}")
                except Exception as e:
                    result["errors"] += 1
                    logger.error(f"Failed to update holiday: {e}")
            
            # Gelöschte Feiertage entfernen
            for deleted_holiday in diff.deleted_holidays:
                try:
                    self.session.delete(deleted_holiday)
                    result["applied"] += 1
                    result["details"].append(f"Deleted: {deleted_holiday.name}")
                    logger.debug(f"Deleted holiday: {deleted_holiday.name}")
                except Exception as e:
                    result["errors"] += 1
                    logger.error(f"Failed to delete holiday: {e}")
            
            # Konflikte überspringen (manuelle Behandlung erforderlich)
            result["skipped"] = len(diff.conflicts)
            for conflict in diff.conflicts:
                result["details"].append(f"Conflict skipped: {conflict.local_holiday.name}")
            
            if not dry_run:
                self.session.commit()
                logger.info(f"Applied {result['applied']} changes, {result['errors']} errors, {result['skipped']} skipped")
            else:
                self.session.rollback()
                logger.info(f"Dry run completed: {result['applied']} changes would be applied")
            
        except Exception as e:
            self.session.rollback()
            logger.error(f"Failed to apply diff: {e}")
            raise
        
        return result
    
    def resolve_conflicts(
        self, 
        conflicts: List[HolidayConflict], 
        strategy: ConflictResolutionStrategy = ConflictResolutionStrategy.API_WINS
    ) -> List[Tuple[Holiday, Dict[str, Any]]]:
        """
        Löst Konflikte basierend auf der gewählten Strategie
        
        Args:
            conflicts: Liste der Konflikte
            strategy: Auflösungsstrategie
            
        Returns:
            Liste der aufgelösten Updates
        """
        resolved_updates = []
        
        for conflict in conflicts:
            if strategy == ConflictResolutionStrategy.API_WINS:
                # API-Daten übernehmen
                changes = self._detect_field_changes(conflict.local_holiday, conflict.api_data)
                if changes:
                    resolved_updates.append((conflict.local_holiday, changes))
                    logger.info(f"Conflict resolved (API wins): {conflict.local_holiday.name}")
            
            elif strategy == ConflictResolutionStrategy.LOCAL_WINS:
                # Lokale Daten behalten - keine Änderung
                logger.info(f"Conflict resolved (local wins): {conflict.local_holiday.name}")
            
            elif strategy == ConflictResolutionStrategy.TIMESTAMP_BASED:
                # Neueste Änderung gewinnt
                if conflict.local_holiday.last_updated:
                    api_timestamp = datetime.now()  # API-Daten sind "aktuell"
                    if api_timestamp > conflict.local_holiday.last_updated:
                        changes = self._detect_field_changes(conflict.local_holiday, conflict.api_data)
                        if changes:
                            resolved_updates.append((conflict.local_holiday, changes))
                            logger.info(f"Conflict resolved (timestamp - API newer): {conflict.local_holiday.name}")
                    else:
                        logger.info(f"Conflict resolved (timestamp - local newer): {conflict.local_holiday.name}")
            
            # MANUAL_REVIEW wird nicht automatisch aufgelöst
        
        return resolved_updates
    
    def generate_diff_report(self, diff: HolidayDiff) -> Dict[str, Any]:
        """
        Generiert einen detaillierten Bericht über die erkannten Änderungen
        
        Args:
            diff: HolidayDiff-Objekt
            
        Returns:
            Detaillierter Bericht als Dictionary
        """
        report = {
            "summary": {
                "total_changes": len(diff.new_holidays) + len(diff.updated_holidays) + len(diff.deleted_holidays),
                "new_holidays": len(diff.new_holidays),
                "updated_holidays": len(diff.updated_holidays),
                "deleted_holidays": len(diff.deleted_holidays),
                "conflicts": len(diff.conflicts),
                "has_changes": diff.has_changes(),
                "has_conflicts": diff.has_conflicts()
            },
            "statistics": {
                "total_api_records": diff.statistics.total_api_records,
                "total_local_records": diff.statistics.total_local_records,
                "processing_time_ms": diff.statistics.processing_time_ms,
                "federal_state": diff.statistics.federal_state.value if diff.statistics.federal_state else None,
                "year": diff.statistics.year
            },
            "details": {
                "new_holidays": [
                    {
                        "name": h.get("name"),
                        "date": h.get("date").isoformat() if isinstance(h.get("date"), date) else str(h.get("date")),
                        "vacation_type": h.get("school_vacation_type").value if h.get("school_vacation_type") else None,
                        "api_id": h.get("api_id")
                    }
                    for h in diff.new_holidays
                ],
                "updated_holidays": [
                    {
                        "name": holiday.name,
                        "current_date": holiday.date.isoformat(),
                        "changes": {k: str(v) for k, v in changes.items()}
                    }
                    for holiday, changes in diff.updated_holidays
                ],
                "deleted_holidays": [
                    {
                        "name": h.name,
                        "date": h.date.isoformat(),
                        "api_id": h.api_id
                    }
                    for h in diff.deleted_holidays
                ],
                "conflicts": [
                    {
                        "holiday_name": c.local_holiday.name,
                        "conflict_fields": c.conflict_fields,
                        "conflict_type": c.conflict_type,
                        "resolution_strategy": c.resolution_strategy.value
                    }
                    for c in diff.conflicts
                ]
            },
            "generated_at": datetime.now().isoformat()
        }
        
        return report


# Convenience function for dependency injection
def get_school_holiday_diff_service(
    conflict_strategy: ConflictResolutionStrategy = ConflictResolutionStrategy.API_WINS
) -> SchoolHolidayDiffService:
    """
    Factory function for SchoolHolidayDiffService
    
    Args:
        conflict_strategy: Default conflict resolution strategy
        
    Returns:
        Configured SchoolHolidayDiffService instance
    """
    session = next(get_session())
    return SchoolHolidayDiffService(session, conflict_strategy)
