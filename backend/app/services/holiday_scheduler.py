"""
Holiday Scheduler Service

This service provides automated scheduling for monthly holiday data import
using APScheduler with persistent job storage and monitoring capabilities.
"""
import logging
from typing import Optional, Dict, Any, List, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.executors.pool import ThreadPoolExecutor
from apscheduler.triggers.cron import CronTrigger
from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR, EVENT_JOB_MISSED

from ..core.config import settings
from ..core.database import get_session
from .holiday_service import HolidayService
from ..models.federal_state import FederalState

logger = logging.getLogger(__name__)


# Global job execution storage
_job_executions: List['JobExecution'] = []
_event_listeners: List[Callable] = []


def execute_holiday_import_job() -> Dict[str, Any]:
    """
    Standalone function to execute holiday import job.
    This is separate from the class to avoid serialization issues with APScheduler.
    
    Returns:
        Import result dictionary
    """
    execution_id = f"exec_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
    
    try:
        logger.info(f"Starting holiday import job execution: {execution_id}")
        
        # Get database session
        session = next(get_session())
        
        try:
            # Create HolidayService
            holiday_service = HolidayService(session)
            
            # Get year range from configuration
            start_year, end_year = settings.get_holiday_year_range()
            
            logger.info(f"Checking for missing years in range {start_year}-{end_year}")
            
            # Get missing years
            missing_years = holiday_service.get_missing_years(
                start_year,
                end_year,
                list(FederalState)
            )
            
            if not missing_years:
                logger.info("No missing years found, all holidays up to date")
                import_result = {
                    "total_imported": 0,
                    "total_skipped": 0,
                    "total_errors": 0,
                    "years_processed": 0,
                    "message": "All holidays already present"
                }
            else:
                logger.info(f"Found {len(missing_years)} missing years: {missing_years}")
                
                # Import missing years
                import_result = holiday_service.import_missing_years(
                    missing_years,
                    list(FederalState)
                )
                
                logger.info(
                    f"Import completed: {import_result['total_imported']} imported, "
                    f"{import_result['total_skipped']} skipped, "
                    f"{import_result['total_errors']} errors"
                )
            
            logger.info(f"Holiday import job completed: {execution_id}")
            return import_result
            
        finally:
            session.close()
        
    except Exception as e:
        logger.error(f"Holiday import job failed: {execution_id}, Error: {e}")
        raise


class SchedulerStatus(str, Enum):
    """Status des Schedulers"""
    STOPPED = "STOPPED"
    RUNNING = "RUNNING"
    PAUSED = "PAUSED"
    ERROR = "ERROR"


class JobStatus(str, Enum):
    """Status eines Jobs"""
    SCHEDULED = "SCHEDULED"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    MISSED = "MISSED"


@dataclass
class SchedulerConfig:
    """Konfiguration für den Holiday Scheduler"""
    # Cron expression for monthly import (1st of every month at 2:00 AM)
    cron_expression: str = "0 2 1 * *"
    timezone: str = "Europe/Berlin"
    max_instances: int = 1
    coalesce: bool = True
    misfire_grace_time: int = 3600  # 1 hour
    
    # Scheduler settings
    max_workers: int = 2
    job_defaults: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.job_defaults is None:
            self.job_defaults = {
                'coalesce': self.coalesce,
                'max_instances': self.max_instances,
                'misfire_grace_time': self.misfire_grace_time
            }


@dataclass
class JobExecution:
    """Repräsentiert eine Job-Ausführung"""
    job_id: str
    execution_id: str
    status: JobStatus
    started_at: datetime
    completed_at: Optional[datetime] = None
    duration: Optional[timedelta] = None
    import_result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    exception_type: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Konvertiert zu Dictionary für Serialisierung"""
        return {
            "job_id": self.job_id,
            "execution_id": self.execution_id,
            "status": self.status.value,
            "started_at": self.started_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "duration_seconds": self.duration.total_seconds() if self.duration else None,
            "import_result": self.import_result,
            "error_message": self.error_message,
            "exception_type": self.exception_type
        }


class HolidayScheduler:
    """
    Scheduler für automatischen Holiday-Import
    
    Features:
    - Monatliche automatische Prüfung und Import fehlender Jahre
    - Persistente Job-Speicherung in der Datenbank
    - Überwachung und Logging von Job-Ausführungen
    - Manuelle Job-Trigger-Funktionalität
    - Event-basierte Benachrichtigungen
    """
    
    JOB_ID = "holiday_monthly_import"
    
    def __init__(self, config: Optional[SchedulerConfig] = None):
        """
        Initialize the scheduler
        
        Args:
            config: Scheduler configuration (uses defaults if None)
        """
        self.config = config or SchedulerConfig(
            cron_expression=settings.HOLIDAY_SCHEDULER_CRON
        )
        self.scheduler: Optional[BackgroundScheduler] = None
        self.status = SchedulerStatus.STOPPED
        self.job_executions: List[JobExecution] = []
        self.event_listeners: List[Callable] = []
        
        # Initialize scheduler
        self._setup_scheduler()
    
    def _setup_scheduler(self) -> None:
        """Konfiguriert den APScheduler"""
        try:
            # Configure job store (SQLAlchemy)
            jobstores = {
                'default': SQLAlchemyJobStore(
                    url=settings.DATABASE_URL, 
                    tablename='holiday_scheduler_jobs'
                )
            }
            
            # Configure executors
            executors = {
                'default': ThreadPoolExecutor(max_workers=self.config.max_workers)
            }
            
            # Create scheduler
            self.scheduler = BackgroundScheduler(
                jobstores=jobstores,
                executors=executors,
                job_defaults=self.config.job_defaults,
                timezone=self.config.timezone
            )
            
            # Add event listeners
            self.scheduler.add_listener(
                self._job_executed_listener, 
                EVENT_JOB_EXECUTED | EVENT_JOB_ERROR | EVENT_JOB_MISSED
            )
            
            logger.info("Holiday Scheduler configured successfully")
            
        except Exception as e:
            logger.error(f"Failed to setup holiday scheduler: {e}")
            self.status = SchedulerStatus.ERROR
            raise
    
    def start(self) -> None:
        """Startet den Scheduler"""
        try:
            if self.scheduler is None:
                raise RuntimeError("Scheduler not initialized")
            
            if self.status == SchedulerStatus.RUNNING:
                logger.warning("Holiday Scheduler is already running")
                return
            
            self.scheduler.start()
            self.status = SchedulerStatus.RUNNING
            
            # Schedule the monthly import job if not already scheduled
            if not self.scheduler.get_job(self.JOB_ID):
                self.schedule_monthly_import()
            
            logger.info("Holiday Scheduler started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start holiday scheduler: {e}")
            self.status = SchedulerStatus.ERROR
            raise
    
    def stop(self, wait: bool = True) -> None:
        """Stoppt den Scheduler"""
        try:
            if self.scheduler is None:
                return
            
            if self.status == SchedulerStatus.STOPPED:
                logger.warning("Holiday Scheduler is already stopped")
                return
            
            self.scheduler.shutdown(wait=wait)
            self.status = SchedulerStatus.STOPPED
            
            logger.info("Holiday Scheduler stopped successfully")
            
        except Exception as e:
            logger.error(f"Failed to stop holiday scheduler: {e}")
            raise
    
    def schedule_monthly_import(self) -> str:
        """
        Schedulet den monatlichen Import-Job
        
        Returns:
            Job ID
        """
        try:
            if self.scheduler is None:
                raise RuntimeError("Scheduler not initialized")
            
            # Remove existing job if present
            if self.scheduler.get_job(self.JOB_ID):
                self.scheduler.remove_job(self.JOB_ID)
            
            # Create cron trigger
            trigger = CronTrigger.from_crontab(
                self.config.cron_expression,
                timezone=self.config.timezone
            )
            
            # Add job - use standalone function to avoid serialization issues
            job = self.scheduler.add_job(
                func=execute_holiday_import_job,
                trigger=trigger,
                id=self.JOB_ID,
                name="Monthly Holiday Import",
                replace_existing=True
            )
            
            next_run = job.next_run_time
            logger.info(f"Monthly holiday import job scheduled. Next run: {next_run}")
            
            return self.JOB_ID
            
        except Exception as e:
            logger.error(f"Failed to schedule monthly import: {e}")
            raise
    
    def trigger_manual_import(self) -> str:
        """
        Triggert einen manuellen Import
        
        Returns:
            Job ID der manuellen Ausführung
        """
        try:
            if self.scheduler is None:
                raise RuntimeError("Scheduler not initialized")
            
            manual_job_id = f"manual_import_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Use standalone function to avoid serialization issues
            job = self.scheduler.add_job(
                func=execute_holiday_import_job,
                trigger='date',  # Run immediately
                id=manual_job_id,
                name="Manual Holiday Import"
            )
            
            logger.info(f"Manual holiday import job triggered: {manual_job_id}")
            return manual_job_id
            
        except Exception as e:
            logger.error(f"Failed to trigger manual import: {e}")
            raise
    
    
    def _job_executed_listener(self, event) -> None:
        """Event-Listener für Job-Ausführungen"""
        try:
            job_id = event.job_id
            
            if event.exception:
                logger.error(f"Job {job_id} failed: {event.exception}")
            else:
                logger.info(f"Job {job_id} executed successfully")
            
        except Exception as e:
            logger.error(f"Error in job event listener: {e}")
    
    def add_event_listener(self, listener: Callable) -> None:
        """
        Fügt einen Event-Listener hinzu
        
        Args:
            listener: Callable das bei Events aufgerufen wird
        """
        self.event_listeners.append(listener)
    
    def _notify_listeners(self, event_type: str, data: Any) -> None:
        """
        Benachrichtigt alle Event-Listener
        
        Args:
            event_type: Art des Events
            data: Event-Daten
        """
        for listener in self.event_listeners:
            try:
                listener(event_type, data)
            except Exception as e:
                logger.error(f"Error in event listener: {e}")
    
    def get_job_info(self, job_id: str) -> Optional[Dict[str, Any]]:
        """
        Gibt Informationen über einen Job zurück
        
        Args:
            job_id: Job ID
            
        Returns:
            Job-Informationen oder None
        """
        try:
            if self.scheduler is None:
                return None
            
            job = self.scheduler.get_job(job_id)
            if not job:
                return None
            
            return {
                'id': job.id,
                'name': job.name,
                'next_run_time': job.next_run_time.isoformat() if job.next_run_time else None,
                'trigger': str(job.trigger)
            }
            
        except Exception as e:
            logger.error(f"Failed to get job info for {job_id}: {e}")
            return None
    
    def get_all_jobs(self) -> List[Dict[str, Any]]:
        """
        Gibt alle geplanten Jobs zurück
        
        Returns:
            Liste aller Jobs
        """
        try:
            if self.scheduler is None:
                return []
            
            jobs = []
            for job in self.scheduler.get_jobs():
                jobs.append({
                    'id': job.id,
                    'name': job.name,
                    'next_run_time': job.next_run_time.isoformat() if job.next_run_time else None,
                    'trigger': str(job.trigger)
                })
            
            return jobs
            
        except Exception as e:
            logger.error(f"Failed to get all jobs: {e}")
            return []
    
    def get_job_executions(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Gibt die letzten Job-Ausführungen zurück
        
        Args:
            limit: Maximale Anzahl der Ergebnisse
            
        Returns:
            Liste der Job-Ausführungen
        """
        executions = sorted(
            self.job_executions, 
            key=lambda x: x.started_at, 
            reverse=True
        )
        return [exec.to_dict() for exec in executions[:limit]]
    
    def get_scheduler_status(self) -> Dict[str, Any]:
        """
        Gibt den aktuellen Scheduler-Status zurück
        
        Returns:
            Scheduler-Status-Informationen
        """
        return {
            'status': self.status.value,
            'running': self.scheduler.running if self.scheduler else False,
            'jobs_count': len(self.scheduler.get_jobs()) if self.scheduler else 0,
            'config': asdict(self.config),
            'last_execution': self.job_executions[-1].to_dict() if self.job_executions else None
        }


# Global scheduler instance
_scheduler_instance: Optional[HolidayScheduler] = None


def get_holiday_scheduler(config: Optional[SchedulerConfig] = None) -> HolidayScheduler:
    """
    Factory function für den Scheduler (Singleton)
    
    Args:
        config: Scheduler-Konfiguration
        
    Returns:
        Scheduler-Instanz
    """
    global _scheduler_instance
    
    if _scheduler_instance is None:
        _scheduler_instance = HolidayScheduler(config)
    
    return _scheduler_instance


def start_holiday_scheduler(config: Optional[SchedulerConfig] = None) -> HolidayScheduler:
    """
    Startet den globalen Holiday Scheduler
    
    Args:
        config: Scheduler-Konfiguration
        
    Returns:
        Gestartete Scheduler-Instanz
    """
    scheduler = get_holiday_scheduler(config)
    scheduler.start()
    return scheduler


def stop_holiday_scheduler() -> None:
    """Stoppt den globalen Holiday Scheduler"""
    global _scheduler_instance
    
    if _scheduler_instance:
        _scheduler_instance.stop()
        _scheduler_instance = None
