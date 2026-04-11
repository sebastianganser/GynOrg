"""
School Holiday Sync Service - Central Orchestrator

This service coordinates the complete synchronization workflow for German school holidays,
integrating the API client and diff service to provide automated monthly updates.
"""
import logging
import time
from typing import List, Dict, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
from sqlmodel import Session, select
from contextlib import contextmanager

from ..core.database import get_session
from ..models.federal_state import FederalState
from ..models.holiday import Holiday, DataSource, HolidayType
from .school_holiday_api_client import SchoolHolidayApiClient, get_school_holiday_api_client
from .school_holiday_diff_service import (
    SchoolHolidayDiffService, 
    get_school_holiday_diff_service,
    ConflictResolutionStrategy,
    HolidayDiff
)

logger = logging.getLogger(__name__)


class SyncStatus(str, Enum):
    """Status des Synchronisationsprozesses"""
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    ROLLED_BACK = "ROLLED_BACK"


class SyncErrorType(str, Enum):
    """Arten von Synchronisationsfehlern"""
    API_ERROR = "API_ERROR"
    DATABASE_ERROR = "DATABASE_ERROR"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    SYSTEM_ERROR = "SYSTEM_ERROR"
    ROLLBACK_ERROR = "ROLLBACK_ERROR"


@dataclass
class SyncError:
    """Repräsentiert einen Synchronisationsfehler"""
    error_type: SyncErrorType
    federal_state: Optional[FederalState] = None
    year: Optional[int] = None
    message: str = ""
    exception: Optional[Exception] = None
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Konvertiert zu Dictionary für Serialisierung"""
        return {
            "error_type": self.error_type.value,
            "federal_state": self.federal_state.value if self.federal_state else None,
            "year": self.year,
            "message": self.message,
            "exception_type": type(self.exception).__name__ if self.exception else None,
            "timestamp": self.timestamp.isoformat()
        }


@dataclass
class StateSyncResult:
    """Ergebnis der Synchronisation für ein Bundesland"""
    federal_state: FederalState
    status: SyncStatus
    years_processed: List[int] = field(default_factory=list)
    total_changes: int = 0
    new_holidays: int = 0
    updated_holidays: int = 0
    deleted_holidays: int = 0
    conflicts: int = 0
    execution_time: timedelta = field(default_factory=lambda: timedelta(0))
    errors: List[SyncError] = field(default_factory=list)
    rollback_performed: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Konvertiert zu Dictionary für Serialisierung"""
        return {
            "federal_state": self.federal_state.value,
            "status": self.status.value,
            "years_processed": self.years_processed,
            "total_changes": self.total_changes,
            "new_holidays": self.new_holidays,
            "updated_holidays": self.updated_holidays,
            "deleted_holidays": self.deleted_holidays,
            "conflicts": self.conflicts,
            "execution_time_seconds": self.execution_time.total_seconds(),
            "errors": [error.to_dict() for error in self.errors],
            "rollback_performed": self.rollback_performed
        }


@dataclass
class SyncResult:
    """Gesamtergebnis der Synchronisation"""
    sync_id: str
    status: SyncStatus
    started_at: datetime
    completed_at: Optional[datetime] = None
    total_states: int = 0
    successful_states: List[str] = field(default_factory=list)
    failed_states: List[str] = field(default_factory=list)
    state_results: Dict[str, StateSyncResult] = field(default_factory=dict)
    total_changes: int = 0
    total_conflicts: int = 0
    execution_time: timedelta = field(default_factory=lambda: timedelta(0))
    errors: List[SyncError] = field(default_factory=list)
    rollback_performed: bool = False
    
    @property
    def success_rate(self) -> float:
        """Berechnet die Erfolgsrate"""
        if self.total_states == 0:
            return 0.0
        return len(self.successful_states) / self.total_states
    
    def to_dict(self) -> Dict[str, Any]:
        """Konvertiert zu Dictionary für Serialisierung"""
        return {
            "sync_id": self.sync_id,
            "status": self.status.value,
            "started_at": self.started_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "total_states": self.total_states,
            "successful_states": self.successful_states,
            "failed_states": self.failed_states,
            "state_results": {k: v.to_dict() for k, v in self.state_results.items()},
            "total_changes": self.total_changes,
            "total_conflicts": self.total_conflicts,
            "execution_time_seconds": self.execution_time.total_seconds(),
            "success_rate": self.success_rate,
            "errors": [error.to_dict() for error in self.errors],
            "rollback_performed": self.rollback_performed
        }


class SchoolHolidaySyncService:
    """
    Zentraler Service für die Orchestrierung der Schulferien-Synchronisation
    
    Features:
    - Koordination von API Client und Diff Service
    - Batch-Verarbeitung aller deutschen Bundesländer
    - Transaktionale Sicherheit mit Rollback-Mechanismen
    - Umfassende Fehlerbehandlung und Retry-Logic
    - Detaillierte Metriken und Logging
    - Konfliktauflösung und manuelle Overrides
    """
    
    def __init__(
        self,
        session: Session,
        api_client: Optional[SchoolHolidayApiClient] = None,
        diff_service: Optional[SchoolHolidayDiffService] = None,
        conflict_strategy: ConflictResolutionStrategy = ConflictResolutionStrategy.API_WINS,
        years_to_sync: Optional[List[int]] = None,
        max_retries: int = 3,
        retry_delay: float = 1.0
    ):
        """
        Initialize the sync service
        
        Args:
            session: Database session
            api_client: Optional API client (will create if None)
            diff_service: Optional diff service (will create if None)
            conflict_strategy: Default conflict resolution strategy
            years_to_sync: Years to synchronize (defaults to 2023-2030)
            max_retries: Maximum retry attempts for failed operations
            retry_delay: Delay between retries in seconds
        """
        self.session = session
        self.api_client = api_client or get_school_holiday_api_client()
        self.diff_service = diff_service or get_school_holiday_diff_service(conflict_strategy)
        self.conflict_strategy = conflict_strategy
        self.years_to_sync = years_to_sync or list(range(2023, 2031))  # 2023-2030
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        
        # Sync state tracking
        self._current_sync: Optional[SyncResult] = None
        self._rollback_points: Dict[str, Any] = {}
    
    async def sync_all_states(
        self,
        federal_states: Optional[List[FederalState]] = None,
        years: Optional[List[int]] = None,
        dry_run: bool = False
    ) -> SyncResult:
        """
        Synchronisiert alle deutschen Bundesländer
        
        Args:
            federal_states: Liste der zu synchronisierenden Bundesländer (alle wenn None)
            years: Jahre für die Synchronisation (Standard: 2023-2030)
            dry_run: Wenn True, werden keine Änderungen committet
            
        Returns:
            SyncResult mit detaillierten Ergebnissen
        """
        sync_id = f"sync_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        states_to_sync = federal_states or list(FederalState)
        years_to_process = years or self.years_to_sync
        
        logger.info(f"Starting sync {sync_id} for {len(states_to_sync)} states, years {years_to_process}")
        
        # Initialize sync result
        sync_result = SyncResult(
            sync_id=sync_id,
            status=SyncStatus.RUNNING,
            started_at=datetime.now(),
            total_states=len(states_to_sync)
        )
        self._current_sync = sync_result
        
        try:
            # Pre-sync validation
            self._validate_sync_prerequisites()
            
            # Process each federal state
            for federal_state in states_to_sync:
                try:
                    logger.info(f"Processing {federal_state.value}")
                    
                    # Create rollback point
                    rollback_point = self._create_rollback_point(federal_state)
                    
                    # Sync the state
                    state_result = await self._sync_federal_state(
                        federal_state, 
                        years_to_process, 
                        dry_run
                    )
                    
                    # Update overall results
                    sync_result.state_results[federal_state.name] = state_result
                    
                    if state_result.status == SyncStatus.COMPLETED:
                        sync_result.successful_states.append(federal_state.value)
                        sync_result.total_changes += state_result.total_changes
                        sync_result.total_conflicts += state_result.conflicts
                        
                        # Commit rollback point on success
                        self._commit_rollback_point(federal_state)
                        
                    else:
                        sync_result.failed_states.append(federal_state.value)
                        sync_result.errors.extend(state_result.errors)
                        
                        # Rollback on failure
                        if not dry_run:
                            self._rollback_to_point(federal_state, rollback_point)
                            state_result.rollback_performed = True
                    
                except Exception as e:
                    logger.error(f"Critical error processing {federal_state.value}: {e}")
                    
                    error = SyncError(
                        error_type=SyncErrorType.SYSTEM_ERROR,
                        federal_state=federal_state,
                        message=f"Critical error: {str(e)}",
                        exception=e
                    )
                    
                    # Create failed state result
                    state_result = StateSyncResult(
                        federal_state=federal_state,
                        status=SyncStatus.FAILED,
                        errors=[error]
                    )
                    
                    sync_result.state_results[federal_state.name] = state_result
                    sync_result.failed_states.append(federal_state.value)
                    sync_result.errors.append(error)
                    
                    # Attempt rollback
                    if not dry_run:
                        try:
                            rollback_point = self._rollback_points.get(federal_state.name)
                            if rollback_point:
                                self._rollback_to_point(federal_state, rollback_point)
                                state_result.rollback_performed = True
                        except Exception as rollback_error:
                            logger.error(f"Rollback failed for {federal_state.value}: {rollback_error}")
                            sync_result.errors.append(SyncError(
                                error_type=SyncErrorType.ROLLBACK_ERROR,
                                federal_state=federal_state,
                                message=f"Rollback failed: {str(rollback_error)}",
                                exception=rollback_error
                            ))
            
            # Finalize sync result
            sync_result.completed_at = datetime.now()
            sync_result.execution_time = sync_result.completed_at - sync_result.started_at
            
            # Determine overall status
            if len(sync_result.failed_states) == 0:
                sync_result.status = SyncStatus.COMPLETED
            elif len(sync_result.successful_states) > 0:
                sync_result.status = SyncStatus.COMPLETED  # Partial success
            else:
                sync_result.status = SyncStatus.FAILED
            
            logger.info(f"Sync {sync_id} completed: {sync_result.success_rate:.1%} success rate")
            
        except Exception as e:
            logger.error(f"Critical sync failure: {e}")
            sync_result.status = SyncStatus.FAILED
            sync_result.completed_at = datetime.now()
            sync_result.execution_time = sync_result.completed_at - sync_result.started_at
            sync_result.errors.append(SyncError(
                error_type=SyncErrorType.SYSTEM_ERROR,
                message=f"Critical sync failure: {str(e)}",
                exception=e
            ))
            
            # Attempt global rollback
            if not dry_run:
                try:
                    self._perform_global_rollback(sync_result)
                    sync_result.rollback_performed = True
                except Exception as rollback_error:
                    logger.error(f"Global rollback failed: {rollback_error}")
        
        finally:
            self._current_sync = None
            self._rollback_points.clear()
        
        return sync_result
    
    async def _sync_federal_state(
        self, 
        federal_state: FederalState, 
        years: List[int], 
        dry_run: bool = False
    ) -> StateSyncResult:
        """
        Synchronisiert ein einzelnes Bundesland
        
        Args:
            federal_state: Das zu synchronisierende Bundesland
            years: Jahre für die Synchronisation
            dry_run: Wenn True, werden keine Änderungen committet
            
        Returns:
            StateSyncResult mit Ergebnissen für das Bundesland
        """
        start_time = datetime.now()
        result = StateSyncResult(
            federal_state=federal_state,
            status=SyncStatus.RUNNING
        )
        
        try:
            total_changes = 0
            total_conflicts = 0
            
            for year in years:
                try:
                    logger.debug(f"Processing {federal_state.value} for year {year}")
                    
                    # Fetch API data with retries
                    api_data = await self._fetch_api_data_with_retry(federal_state, year)
                    
                    if not api_data:
                        logger.warning(f"No data received for {federal_state.value} {year}")
                        continue
                    
                    # Perform diff analysis
                    diff = self.diff_service.compare_holiday_data(
                        api_data, federal_state, year, self.conflict_strategy
                    )
                    
                    # Apply changes if any
                    if diff.has_changes():
                        apply_result = self.diff_service.apply_diff(diff, dry_run)
                        
                        total_changes += apply_result["applied"]
                        result.new_holidays += len(diff.new_holidays)
                        result.updated_holidays += len(diff.updated_holidays)
                        result.deleted_holidays += len(diff.deleted_holidays)
                        
                        logger.info(f"{federal_state.value} {year}: {apply_result['applied']} changes applied")
                    
                    if diff.has_conflicts():
                        total_conflicts += len(diff.conflicts)
                        logger.warning(f"{federal_state.value} {year}: {len(diff.conflicts)} conflicts detected")
                    
                    result.years_processed.append(year)
                    
                except Exception as e:
                    logger.error(f"Error processing {federal_state.value} {year}: {e}")
                    error = SyncError(
                        error_type=SyncErrorType.API_ERROR if "api" in str(e).lower() else SyncErrorType.SYSTEM_ERROR,
                        federal_state=federal_state,
                        year=year,
                        message=str(e),
                        exception=e
                    )
                    result.errors.append(error)
            
            # Update result statistics
            result.total_changes = total_changes
            result.conflicts = total_conflicts
            result.execution_time = datetime.now() - start_time
            
            # Determine status
            if len(result.errors) == 0:
                result.status = SyncStatus.COMPLETED
            elif len(result.years_processed) > 0:
                result.status = SyncStatus.COMPLETED  # Partial success
            else:
                result.status = SyncStatus.FAILED
            
        except Exception as e:
            logger.error(f"Critical error in state sync for {federal_state.value}: {e}")
            result.status = SyncStatus.FAILED
            result.execution_time = datetime.now() - start_time
            result.errors.append(SyncError(
                error_type=SyncErrorType.SYSTEM_ERROR,
                federal_state=federal_state,
                message=f"Critical state sync error: {str(e)}",
                exception=e
            ))
        
        return result
    
    async def _fetch_api_data_with_retry(
        self, 
        federal_state: FederalState, 
        year: int
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Holt API-Daten mit Retry-Mechanismus
        
        Args:
            federal_state: Bundesland
            year: Jahr
            
        Returns:
            API-Daten oder None bei Fehler
        """
        for attempt in range(self.max_retries + 1):
            try:
                return await self.api_client.fetch_school_holidays(federal_state, year)
            
            except Exception as e:
                if attempt < self.max_retries:
                    wait_time = self.retry_delay * (2 ** attempt)  # Exponential backoff
                    logger.warning(f"API call failed (attempt {attempt + 1}), retrying in {wait_time}s: {e}")
                    time.sleep(wait_time)
                else:
                    logger.error(f"API call failed after {self.max_retries + 1} attempts: {e}")
                    raise
        
        return None
    
    def _validate_sync_prerequisites(self) -> None:
        """Validiert die Voraussetzungen für die Synchronisation"""
        try:
            # Test database connection
            self.session.exec(select(Holiday).limit(1))
            
            # Test API client
            if not self.api_client:
                raise ValueError("API client not available")
            
            # Test diff service
            if not self.diff_service:
                raise ValueError("Diff service not available")
            
            logger.debug("Sync prerequisites validated successfully")
            
        except Exception as e:
            logger.error(f"Sync prerequisites validation failed: {e}")
            raise
    
    def _create_rollback_point(self, federal_state: FederalState) -> Dict[str, Any]:
        """
        Erstellt einen Rollback-Punkt für ein Bundesland
        
        Args:
            federal_state: Bundesland
            
        Returns:
            Rollback-Point-Daten
        """
        try:
            # Get current holiday count for the state
            query = select(Holiday).where(
                Holiday.federal_state_code == federal_state.name,
                Holiday.data_source == DataSource.MEHR_SCHULFERIEN_API
            )
            current_holidays = self.session.exec(query).all()
            
            rollback_point = {
                "federal_state": federal_state.name,
                "timestamp": datetime.now(),
                "holiday_count": len(current_holidays),
                "holiday_ids": [h.id for h in current_holidays if h.id]
            }
            
            self._rollback_points[federal_state.name] = rollback_point
            logger.debug(f"Created rollback point for {federal_state.value}: {rollback_point['holiday_count']} holidays")
            
            return rollback_point
            
        except Exception as e:
            logger.error(f"Failed to create rollback point for {federal_state.value}: {e}")
            raise
    
    def _commit_rollback_point(self, federal_state: FederalState) -> None:
        """
        Committet einen Rollback-Punkt (entfernt ihn)
        
        Args:
            federal_state: Bundesland
        """
        if federal_state.name in self._rollback_points:
            del self._rollback_points[federal_state.name]
            logger.debug(f"Committed rollback point for {federal_state.value}")
    
    def _rollback_to_point(self, federal_state: FederalState, rollback_point: Dict[str, Any]) -> None:
        """
        Führt einen Rollback zu einem bestimmten Punkt durch
        
        Args:
            federal_state: Bundesland
            rollback_point: Rollback-Point-Daten
        """
        try:
            logger.warning(f"Performing rollback for {federal_state.value}")
            
            # Delete all holidays added after rollback point
            query = select(Holiday).where(
                Holiday.federal_state_code == federal_state.name,
                Holiday.data_source == DataSource.MEHR_SCHULFERIEN_API
            )
            current_holidays = self.session.exec(query).all()
            
            rollback_holiday_ids = set(rollback_point.get("holiday_ids", []))
            
            for holiday in current_holidays:
                if holiday.id and holiday.id not in rollback_holiday_ids:
                    self.session.delete(holiday)
            
            self.session.commit()
            logger.info(f"Rollback completed for {federal_state.value}")
            
        except Exception as e:
            logger.error(f"Rollback failed for {federal_state.value}: {e}")
            self.session.rollback()
            raise
    
    def _perform_global_rollback(self, sync_result: SyncResult) -> None:
        """
        Führt einen globalen Rollback für alle Bundesländer durch
        
        Args:
            sync_result: Sync-Ergebnis mit Rollback-Informationen
        """
        logger.warning("Performing global rollback")
        
        for federal_state_name, rollback_point in self._rollback_points.items():
            try:
                federal_state = FederalState[federal_state_name]
                self._rollback_to_point(federal_state, rollback_point)
            except Exception as e:
                logger.error(f"Global rollback failed for {federal_state_name}: {e}")
    
    def get_sync_status(self) -> Optional[Dict[str, Any]]:
        """
        Gibt den aktuellen Sync-Status zurück
        
        Returns:
            Sync-Status oder None wenn kein Sync läuft
        """
        if self._current_sync:
            return self._current_sync.to_dict()
        return None
    
    def get_last_sync_results(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Gibt die letzten Sync-Ergebnisse zurück
        
        Args:
            limit: Maximale Anzahl der Ergebnisse
            
        Returns:
            Liste der letzten Sync-Ergebnisse
        """
        # TODO: Implement persistent storage of sync results
        # For now, return empty list
        return []


# Factory function for dependency injection
def get_school_holiday_sync_service(
    conflict_strategy: ConflictResolutionStrategy = ConflictResolutionStrategy.API_WINS,
    years_to_sync: Optional[List[int]] = None
) -> SchoolHolidaySyncService:
    """
    Factory function for SchoolHolidaySyncService
    
    Args:
        conflict_strategy: Default conflict resolution strategy
        years_to_sync: Years to synchronize
        
    Returns:
        Configured SchoolHolidaySyncService instance
    """
    session = next(get_session())
    return SchoolHolidaySyncService(
        session=session,
        conflict_strategy=conflict_strategy,
        years_to_sync=years_to_sync
    )
