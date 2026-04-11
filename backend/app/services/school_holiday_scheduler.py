"""
School Holiday Scheduler Service

This service provides automated scheduling for monthly school holiday synchronization
using APScheduler with persistent job storage and monitoring capabilities.
"""
import logging
import json
import os
from typing import Optional, Dict, Any, List, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.executors.pool import ThreadPoolExecutor
from apscheduler.triggers.cron import CronTrigger
from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR, EVENT_JOB_MISSED
from apscheduler.job import Job

from ..core.config import settings
from ..core.database import get_session
from .school_holiday_sync_service import (
    SchoolHolidaySyncService, 
    get_school_holiday_sync_service,
    SyncResult,
    ConflictResolutionStrategy
)

logger = logging.getLogger(__name__)


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
    """Konfiguration für den Scheduler"""
    # Cron expression for monthly sync (1st of every month at 2:00 AM)
    cron_expression: str = "0 2 1 * *"
    timezone: str = "Europe/Berlin"
    max_instances: int = 1
    coalesce: bool = True
    misfire_grace_time: int = 3600  # 1 hour
    
    # Sync configuration
    conflict_strategy: ConflictResolutionStrategy = ConflictResolutionStrategy.API_WINS
    years_to_sync: Optional[List[int]] = None
    dry_run: bool = False
    
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
        
        if self.years_to_sync is None:
            current_year = datetime.now().year
            self.years_to_sync = list(range(current_year - 1, current_year + 8))  # Previous year to +7 years


@dataclass
class JobExecution:
    """Repräsentiert eine Job-Ausführung"""
    job_id: str
    execution_id: str
    status: JobStatus
    started_at: datetime
    completed_at: Optional[datetime] = None
    duration: Optional[timedelta] = None
    sync_result: Optional[Dict[str, Any]] = None
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
            "sync_result": self.sync_result,
            "error_message": self.error_message,
            "exception_type": self.exception_type
        }


class SchoolHolidayScheduler:
    """
    Scheduler für automatische Schulferien-Synchronisation
    
    Features:
    - Monatliche automatische Synchronisation
    - Persistente Job-Speicherung in der Datenbank
    - Überwachung und Logging von Job-Ausführungen
    - Manuelle Job-Trigger-Funktionalität
    - Konfigurierbare Retry-Mechanismen
    - Event-basierte Benachrichtigungen
    """
    
    JOB_ID = "school_holiday_monthly_sync"
    
    def __init__(self, config: Optional[SchedulerConfig] = None):
        """
        Initialize the scheduler
        
        Args:
            config: Scheduler configuration (uses defaults if None)
        """
        self.config = config or SchedulerConfig()
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
                'default': SQLAlchemyJobStore(url=settings.DATABASE_URL, tablename='scheduler_jobs')
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
            
            logger.info("Scheduler configured successfully")
            
        except Exception as e:
            logger.error(f"Failed to setup scheduler: {e}")
            self.status = SchedulerStatus.ERROR
            raise
    
    def start(self) -> None:
        """Startet den Scheduler"""
        try:
            if self.scheduler is None:
                raise RuntimeError("Scheduler not initialized")
            
            if self.status == SchedulerStatus.RUNNING:
                logger.warning("Scheduler is already running")
                return
            
            self.scheduler.start()
            self.status = SchedulerStatus.RUNNING
            
            # Schedule the monthly sync job if not already scheduled
            if not self.scheduler.get_job(self.JOB_ID):
                self.schedule_monthly_sync()
            
            logger.info("Scheduler started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start scheduler: {e}")
            self.status = SchedulerStatus.ERROR
            raise
    
    def stop(self, wait: bool = True) -> None:
        """Stoppt den Scheduler"""
        try:
            if self.scheduler is None:
                return
            
            if self.status == SchedulerStatus.STOPPED:
                logger.warning("Scheduler is already stopped")
                return
            
            self.scheduler.shutdown(wait=wait)
            self.status = SchedulerStatus.STOPPED
            
            logger.info("Scheduler stopped successfully")
            
        except Exception as e:
            logger.error(f"Failed to stop scheduler: {e}")
            raise
    
    def pause(self) -> None:
        """Pausiert den Scheduler"""
        try:
            if self.scheduler is None:
                raise RuntimeError("Scheduler not initialized")
            
            self.scheduler.pause()
            self.status = SchedulerStatus.PAUSED
            
            logger.info("Scheduler paused")
            
        except Exception as e:
            logger.error(f"Failed to pause scheduler: {e}")
            raise
    
    def resume(self) -> None:
        """Setzt den Scheduler fort"""
        try:
            if self.scheduler is None:
                raise RuntimeError("Scheduler not initialized")
            
            self.scheduler.resume()
            self.status = SchedulerStatus.RUNNING
            
            logger.info("Scheduler resumed")
            
        except Exception as e:
            logger.error(f"Failed to resume scheduler: {e}")
            raise
    
    def schedule_monthly_sync(self) -> str:
        """
        Schedulet den monatlichen Sync-Job
        
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
            
            # Add job
            job = self.scheduler.add_job(
                func=self._execute_sync_job,
                trigger=trigger,
                id=self.JOB_ID,
                name="Monthly School Holiday Sync",
                replace_existing=True,
                kwargs={
                    'conflict_strategy': self.config.conflict_strategy,
                    'years_to_sync': self.config.years_to_sync,
                    'dry_run': self.config.dry_run
                }
            )
            
            next_run = job.next_run_time
            logger.info(f"Monthly sync job scheduled. Next run: {next_run}")
            
            return self.JOB_ID
            
        except Exception as e:
            logger.error(f"Failed to schedule monthly sync: {e}")
            raise
    
    def trigger_manual_sync(
        self,
        conflict_strategy: Optional[ConflictResolutionStrategy] = None,
        years_to_sync: Optional[List[int]] = None,
        dry_run: bool = False
    ) -> str:
        """
        Triggert eine manuelle Synchronisation
        
        Args:
            conflict_strategy: Konfliktauflösungsstrategie
            years_to_sync: Jahre für die Synchronisation
            dry_run: Wenn True, werden keine Änderungen committet
            
        Returns:
            Job ID der manuellen Ausführung
        """
        try:
            if self.scheduler is None:
                raise RuntimeError("Scheduler not initialized")
            
            manual_job_id = f"manual_sync_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            job = self.scheduler.add_job(
                func=self._execute_sync_job,
                trigger='date',  # Run immediately
                id=manual_job_id,
                name="Manual School Holiday Sync",
                kwargs={
                    'conflict_strategy': conflict_strategy or self.config.conflict_strategy,
                    'years_to_sync': years_to_sync or self.config.years_to_sync,
                    'dry_run': dry_run
                }
            )
            
            logger.info(f"Manual sync job triggered: {manual_job_id}")
            return manual_job_id
            
        except Exception as e:
            logger.error(f"Failed to trigger manual sync: {e}")
            raise
    
    def _execute_sync_job(
        self,
        conflict_strategy: ConflictResolutionStrategy,
        years_to_sync: List[int],
        dry_run: bool = False
    ) -> None:
        """
        Führt den Sync-Job aus
        
        Args:
            conflict_strategy: Konfliktauflösungsstrategie
            years_to_sync: Jahre für die Synchronisation
            dry_run: Wenn True, werden keine Änderungen committet
        """
        execution_id = f"exec_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        job_execution = JobExecution(
            job_id=self.JOB_ID,
            execution_id=execution_id,
            status=JobStatus.RUNNING,
            started_at=datetime.now()
        )
        
        self.job_executions.append(job_execution)
        
        try:
            logger.info(f"Starting sync job execution: {execution_id}")
            
            # Create sync service
            sync_service = get_school_holiday_sync_service(
                conflict_strategy=conflict_strategy,
                years_to_sync=years_to_sync
            )
            
            # Execute synchronization
            sync_result = sync_service.sync_all_states(
                years=years_to_sync,
                dry_run=dry_run
            )
            
            # Update job execution
            job_execution.completed_at = datetime.now()
            job_execution.duration = job_execution.completed_at - job_execution.started_at
            job_execution.sync_result = sync_result.to_dict()
            job_execution.status = JobStatus.COMPLETED
            
            logger.info(f"Sync job completed: {execution_id}, Success rate: {sync_result.success_rate:.1%}")
            
            # Notify listeners
            self._notify_listeners('job_completed', job_execution)
            
        except Exception as e:
            logger.error(f"Sync job failed: {execution_id}, Error: {e}")
            
            job_execution.completed_at = datetime.now()
            job_execution.duration = job_execution.completed_at - job_execution.started_at
            job_execution.status = JobStatus.FAILED
            job_execution.error_message = str(e)
            job_execution.exception_type = type(e).__name__
            
            # Notify listeners
            self._notify_listeners('job_failed', job_execution)
            
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
                'trigger': str(job.trigger),
                'kwargs': job.kwargs
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
                    'trigger': str(job.trigger),
                    'kwargs': job.kwargs
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
    
    def remove_job(self, job_id: str) -> bool:
        """
        Entfernt einen Job
        
        Args:
            job_id: Job ID
            
        Returns:
            True wenn erfolgreich entfernt
        """
        try:
            if self.scheduler is None:
                return False
            
            self.scheduler.remove_job(job_id)
            logger.info(f"Job {job_id} removed")
            return True
            
        except Exception as e:
            logger.error(f"Failed to remove job {job_id}: {e}")
            return False
    
    def update_config(self, new_config: SchedulerConfig) -> None:
        """
        Aktualisiert die Scheduler-Konfiguration
        
        Args:
            new_config: Neue Konfiguration
        """
        try:
            self.config = new_config
            
            # Reschedule monthly job with new config
            if self.scheduler and self.scheduler.running:
                self.schedule_monthly_sync()
            
            logger.info("Scheduler configuration updated")
            
        except Exception as e:
            logger.error(f"Failed to update scheduler config: {e}")
            raise


# Global scheduler instance
_scheduler_instance: Optional[SchoolHolidayScheduler] = None


def get_scheduler(config: Optional[SchedulerConfig] = None) -> SchoolHolidayScheduler:
    """
    Factory function für den Scheduler (Singleton)
    
    Args:
        config: Scheduler-Konfiguration
        
    Returns:
        Scheduler-Instanz
    """
    global _scheduler_instance
    
    if _scheduler_instance is None:
        _scheduler_instance = SchoolHolidayScheduler(config)
    
    return _scheduler_instance


def start_scheduler(config: Optional[SchedulerConfig] = None) -> SchoolHolidayScheduler:
    """
    Startet den globalen Scheduler
    
    Args:
        config: Scheduler-Konfiguration
        
    Returns:
        Gestartete Scheduler-Instanz
    """
    scheduler = get_scheduler(config)
    scheduler.start()
    return scheduler


def stop_scheduler() -> None:
    """Stoppt den globalen Scheduler"""
    global _scheduler_instance
    
    if _scheduler_instance:
        _scheduler_instance.stop()
        _scheduler_instance = None
