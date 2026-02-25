"""
Holiday Admin API Endpoints

This module provides REST API endpoints for administrative management
of the Multi-Year Holiday Management System (Task 22).

These endpoints allow manual control of:
- Holiday import operations (using HolidayStartupService from Task 22.2)
- Scheduler operations (using HolidayScheduler from Task 22.3)
- Job monitoring and execution history

This is separate from admin_sync.py which handles School Holiday synchronization.
"""
import logging
from typing import Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlmodel import Session

from ....core.database import get_session
from ....core.auth import get_current_user
from ....models.federal_state import FederalState
from ....services.holiday_startup_service import HolidayStartupService
from ....services.holiday_scheduler import (
    get_holiday_scheduler,
    start_holiday_scheduler,
    stop_holiday_scheduler
)
from ....schemas.holiday_admin import (
    ImportTriggerRequest,
    ImportStatusResponse,
    SchedulerStatusResponse,
    JobsListResponse,
    JobInfo,
    JobExecutionsResponse,
    JobExecution,
    AdminActionResponse,
    TriggerJobResponse
)

logger = logging.getLogger(__name__)
router = APIRouter()

# In-memory storage for import status (in production, this could be in database or cache)
_last_import_result = None
_last_import_time = None
_import_running = False


async def require_admin_user(current_user: dict = Depends(get_current_user)):
    """Dependency to ensure user has admin privileges"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    # TODO: Add actual admin role check when user roles are implemented
    return current_user


@router.post("/import", response_model=AdminActionResponse)
async def trigger_manual_import(
    request: ImportTriggerRequest,
    background_tasks: BackgroundTasks,
    session: Session = Depends(get_session),
    current_user: dict = Depends(require_admin_user)
):
    """
    Trigger manual holiday import
    
    Starts a background import operation using HolidayStartupService.
    Returns immediately with confirmation. Use /import/status to monitor progress.
    
    Parameters:
    - start_year: Optional start year (defaults to config)
    - end_year: Optional end year (defaults to config)
    - federal_states: Optional list of federal states (defaults to all)
    """
    global _import_running, _last_import_result, _last_import_time
    
    try:
        # Check if import is already running
        if _import_running:
            raise HTTPException(
                status_code=409,
                detail="Import is already running. Please wait for completion."
            )
        
        # Prepare import parameters
        federal_states = request.federal_states if request.federal_states else list(FederalState)
        
        # Define background task
        def run_import():
            global _import_running, _last_import_result, _last_import_time
            
            try:
                _import_running = True
                logger.info(f"Starting manual holiday import for years {request.start_year}-{request.end_year}")
                
                # Create service instance
                startup_service = HolidayStartupService(session)
                
                # Run import
                result = startup_service.ensure_holiday_data()
                
                # Store result
                _last_import_result = result
                _last_import_time = datetime.now()
                _import_running = False
                
                logger.info(f"Manual holiday import completed: {result.get('action')}")
                
            except Exception as e:
                logger.error(f"Manual holiday import failed: {e}", exc_info=True)
                _last_import_result = {
                    "action": "error",
                    "error": str(e),
                    "message": f"Import failed: {str(e)}"
                }
                _last_import_time = datetime.now()
                _import_running = False
        
        # Start background task
        background_tasks.add_task(run_import)
        
        return AdminActionResponse(
            success=True,
            message="Manual holiday import started successfully",
            action="trigger_import",
            performed_at=datetime.now(),
            performed_by=current_user.get("username", "admin"),
            details={
                "start_year": request.start_year or "config_default",
                "end_year": request.end_year or "config_default",
                "federal_states": [state.value for state in federal_states] if request.federal_states else "all"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error triggering manual import: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to trigger import: {str(e)}")


@router.get("/import/status", response_model=ImportStatusResponse)
async def get_import_status(
    current_user: dict = Depends(require_admin_user)
):
    """
    Get current import status
    
    Returns information about any running import operation and the last import result.
    """
    try:
        return ImportStatusResponse(
            is_running=_import_running,
            last_import=_last_import_time,
            last_result=_last_import_result,
            current_progress={"status": "running"} if _import_running else None
        )
        
    except Exception as e:
        logger.error(f"Error getting import status: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to get import status: {str(e)}")


@router.get("/scheduler/status", response_model=SchedulerStatusResponse)
async def get_scheduler_status(
    current_user: dict = Depends(require_admin_user)
):
    """
    Get scheduler status
    
    Returns comprehensive information about the Holiday Scheduler including:
    - Current status (RUNNING, STOPPED, ERROR)
    - Number of scheduled jobs
    - Next run time
    - Last execution details
    - Configuration
    """
    try:
        scheduler = get_holiday_scheduler()
        status_info = scheduler.get_scheduler_status()
        
        # Get job info for next run time
        job_info = scheduler.get_job_info(scheduler.JOB_ID)
        next_run = None
        if job_info and job_info.get('next_run_time'):
            next_run = datetime.fromisoformat(job_info['next_run_time'])
        
        # Get last execution
        executions = scheduler.get_job_executions(limit=1)
        last_execution = executions[0] if executions else None
        
        return SchedulerStatusResponse(
            status=status_info['status'],
            running=status_info['running'],
            jobs_count=status_info['jobs_count'],
            next_run_time=next_run,
            last_execution=last_execution,
            configuration=status_info['config']
        )
        
    except Exception as e:
        logger.error(f"Error getting scheduler status: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to get scheduler status: {str(e)}")


@router.post("/scheduler/start", response_model=AdminActionResponse)
async def start_scheduler(
    current_user: dict = Depends(require_admin_user)
):
    """
    Start the Holiday Scheduler
    
    Starts the automated monthly holiday import scheduler.
    The scheduler will run on the configured schedule (default: 1st of each month at 2:00 AM).
    """
    try:
        scheduler = get_holiday_scheduler()
        
        # Check if already running
        if scheduler.status.value == "RUNNING":
            return AdminActionResponse(
                success=True,
                message="Scheduler is already running",
                action="start_scheduler",
                performed_at=datetime.now(),
                performed_by=current_user.get("username", "admin"),
                details={"previous_status": "RUNNING"}
            )
        
        # Start scheduler
        scheduler.start()
        
        logger.info(f"Holiday Scheduler started by {current_user.get('username', 'admin')}")
        
        return AdminActionResponse(
            success=True,
            message="Holiday Scheduler started successfully",
            action="start_scheduler",
            performed_at=datetime.now(),
            performed_by=current_user.get("username", "admin"),
            details={"new_status": "RUNNING"}
        )
        
    except Exception as e:
        logger.error(f"Error starting scheduler: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to start scheduler: {str(e)}")


@router.post("/scheduler/stop", response_model=AdminActionResponse)
async def stop_scheduler(
    current_user: dict = Depends(require_admin_user)
):
    """
    Stop the Holiday Scheduler
    
    Stops the automated monthly holiday import scheduler.
    Any currently running jobs will complete, but no new jobs will be scheduled.
    """
    try:
        scheduler = get_holiday_scheduler()
        
        # Check if already stopped
        if scheduler.status.value == "STOPPED":
            return AdminActionResponse(
                success=True,
                message="Scheduler is already stopped",
                action="stop_scheduler",
                performed_at=datetime.now(),
                performed_by=current_user.get("username", "admin"),
                details={"previous_status": "STOPPED"}
            )
        
        # Stop scheduler
        scheduler.stop()
        
        logger.info(f"Holiday Scheduler stopped by {current_user.get('username', 'admin')}")
        
        return AdminActionResponse(
            success=True,
            message="Holiday Scheduler stopped successfully",
            action="stop_scheduler",
            performed_at=datetime.now(),
            performed_by=current_user.get("username", "admin"),
            details={"new_status": "STOPPED"}
        )
        
    except Exception as e:
        logger.error(f"Error stopping scheduler: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to stop scheduler: {str(e)}")


@router.post("/scheduler/trigger", response_model=TriggerJobResponse)
async def trigger_manual_job(
    current_user: dict = Depends(require_admin_user)
):
    """
    Trigger manual scheduler job
    
    Manually triggers a holiday import job outside of the regular schedule.
    The job will run immediately in the background.
    """
    try:
        scheduler = get_holiday_scheduler()
        
        # Trigger manual import
        job_id = scheduler.trigger_manual_import()
        
        logger.info(f"Manual job triggered by {current_user.get('username', 'admin')}: {job_id}")
        
        return TriggerJobResponse(
            success=True,
            message="Manual import job triggered successfully",
            job_id=job_id,
            triggered_at=datetime.now()
        )
        
    except Exception as e:
        logger.error(f"Error triggering manual job: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to trigger manual job: {str(e)}")


@router.get("/scheduler/jobs", response_model=JobsListResponse)
async def get_scheduler_jobs(
    current_user: dict = Depends(require_admin_user)
):
    """
    Get all scheduled jobs
    
    Returns a list of all jobs currently scheduled in the Holiday Scheduler.
    """
    try:
        scheduler = get_holiday_scheduler()
        jobs_data = scheduler.get_all_jobs()
        
        jobs = []
        for job_data in jobs_data:
            jobs.append(JobInfo(
                id=job_data['id'],
                name=job_data['name'],
                next_run_time=datetime.fromisoformat(job_data['next_run_time']) if job_data.get('next_run_time') else None,
                trigger=job_data['trigger']
            ))
        
        return JobsListResponse(
            jobs=jobs,
            total_count=len(jobs)
        )
        
    except Exception as e:
        logger.error(f"Error getting scheduler jobs: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to get scheduler jobs: {str(e)}")


@router.get("/scheduler/executions", response_model=JobExecutionsResponse)
async def get_job_executions(
    limit: int = 50,
    current_user: dict = Depends(require_admin_user)
):
    """
    Get job execution history
    
    Returns the history of job executions with details about success/failure,
    duration, and import results.
    
    Parameters:
    - limit: Maximum number of executions to return (default: 50)
    """
    try:
        scheduler = get_holiday_scheduler()
        executions_data = scheduler.get_job_executions(limit=limit)
        
        executions = []
        for exec_data in executions_data:
            executions.append(JobExecution(
                job_id=exec_data['job_id'],
                execution_id=exec_data['execution_id'],
                status=exec_data['status'],
                started_at=datetime.fromisoformat(exec_data['started_at']),
                completed_at=datetime.fromisoformat(exec_data['completed_at']) if exec_data.get('completed_at') else None,
                duration_seconds=exec_data.get('duration_seconds'),
                import_result=exec_data.get('import_result'),
                error_message=exec_data.get('error_message')
            ))
        
        return JobExecutionsResponse(
            executions=executions,
            total_count=len(executions),
            limit=limit
        )
        
    except Exception as e:
        logger.error(f"Error getting job executions: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to get job executions: {str(e)}")
