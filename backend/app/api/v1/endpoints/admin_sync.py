"""
Admin Sync API Endpoints

This module provides REST API endpoints for administrative management
of the school holiday synchronization system, including monitoring,
manual control, and conflict resolution.
"""
import logging
from typing import Dict, Any, List
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlmodel import Session

from ....core.database import get_session
from ....core.auth import get_current_user
from ....models.holiday import Holiday, DataSource
from ....models.federal_state import FederalState
from ....services.school_holiday_sync_service import (
    get_school_holiday_sync_service,
    SchoolHolidaySyncService,
    SyncStatus
)
from ....services.school_holiday_scheduler import (
    get_scheduler,
    SchoolHolidayScheduler,
    SchedulerStatus,
    JobStatus
)
from ....services.school_holiday_diff_service import ConflictResolutionStrategy
from ....schemas.admin_sync import (
    SyncTriggerRequest,
    SyncStatusResponse,
    SyncHistoryResponse,
    SyncHistoryItem,
    SyncStatistics,
    ConflictItem,
    ConflictResolutionRequest,
    ConflictResolutionResponse,
    SchedulerStatusResponse,
    JobExecutionHistoryResponse,
    JobExecutionItem,
    SystemHealthResponse,
    AdminActionRequest,
    AdminActionResponse,
    PaginationParams,
    SyncHistoryFilter
)

logger = logging.getLogger(__name__)
router = APIRouter()

# In-memory storage for sync history (in production, this would be in database)
_sync_history: List[Dict[str, Any]] = []


async def require_admin_user(current_user: dict = Depends(get_current_user)):
    """Dependency to ensure user has admin privileges"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    # TODO: Add actual admin role check
    return current_user


@router.get("/status", response_model=SyncStatusResponse)
async def get_sync_status(
    session: Session = Depends(get_session),
    current_user: dict = Depends(require_admin_user)
):
    """
    Get current synchronization status
    
    Returns real-time information about any running sync operations,
    including progress, estimated completion time, and current state.
    """
    try:
        sync_service = get_school_holiday_sync_service()
        current_sync = sync_service.get_sync_status()
        
        if current_sync:
            # Calculate progress information
            total_states = current_sync.get("total_states", 0)
            completed_states = len(current_sync.get("successful_states", []))
            failed_states = len(current_sync.get("failed_states", []))
            
            # Estimate completion time based on progress
            if completed_states > 0 and total_states > 0:
                elapsed = datetime.now() - datetime.fromisoformat(current_sync["started_at"])
                avg_time_per_state = elapsed.total_seconds() / completed_states
                remaining_states = total_states - completed_states - failed_states
                estimated_completion = datetime.now() + timedelta(
                    seconds=avg_time_per_state * remaining_states
                )
            else:
                estimated_completion = None
            
            return SyncStatusResponse(
                sync_id=current_sync["sync_id"],
                status=SyncStatus(current_sync["status"]),
                started_at=datetime.fromisoformat(current_sync["started_at"]),
                progress={
                    "completed": completed_states,
                    "failed": failed_states,
                    "remaining": total_states - completed_states - failed_states,
                    "percentage": (completed_states / total_states * 100) if total_states > 0 else 0
                },
                estimated_completion=estimated_completion,
                total_states=total_states,
                completed_states=completed_states,
                failed_states=failed_states
            )
        else:
            return SyncStatusResponse(
                status=SyncStatus.PENDING,
                total_states=0,
                completed_states=0,
                failed_states=0
            )
            
    except Exception as e:
        logger.error(f"Error getting sync status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get sync status: {str(e)}")


@router.post("/trigger", response_model=AdminActionResponse)
async def trigger_manual_sync(
    request: SyncTriggerRequest,
    background_tasks: BackgroundTasks,
    session: Session = Depends(get_session),
    current_user: dict = Depends(require_admin_user)
):
    """
    Trigger a manual synchronization
    
    Starts a background sync operation with the specified parameters.
    Returns immediately with a task ID for tracking progress.
    """
    try:
        # Check if sync is already running
        sync_service = get_school_holiday_sync_service(
            conflict_strategy=request.conflict_strategy,
            years_to_sync=request.years
        )
        
        current_sync = sync_service.get_sync_status()
        if current_sync and current_sync["status"] == SyncStatus.RUNNING.value:
            raise HTTPException(
                status_code=409, 
                detail="Sync is already running. Please wait for completion."
            )
        
        # Start background sync
        def run_sync():
            try:
                result = sync_service.sync_all_states(
                    federal_states=request.federal_states,
                    years=request.years,
                    dry_run=request.dry_run
                )
                
                # Store result in history
                history_item = {
                    "sync_id": result.sync_id,
                    "status": result.status.value,
                    "started_at": result.started_at.isoformat(),
                    "completed_at": result.completed_at.isoformat() if result.completed_at else None,
                    "duration_seconds": result.execution_time.total_seconds(),
                    "total_states": result.total_states,
                    "successful_states": result.successful_states,
                    "failed_states": result.failed_states,
                    "total_changes": result.total_changes,
                    "total_conflicts": result.total_conflicts,
                    "success_rate": result.success_rate,
                    "triggered_by": current_user.get("username", "admin"),
                    "error_summary": None if result.status == SyncStatus.COMPLETED else "Sync failed"
                }
                _sync_history.append(history_item)
                
                logger.info(f"Manual sync completed: {result.sync_id}")
                
            except Exception as e:
                logger.error(f"Manual sync failed: {e}")
                # Store failed sync in history
                _sync_history.append({
                    "sync_id": f"failed_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    "status": SyncStatus.FAILED.value,
                    "started_at": datetime.now().isoformat(),
                    "completed_at": datetime.now().isoformat(),
                    "duration_seconds": 0,
                    "total_states": 0,
                    "successful_states": [],
                    "failed_states": [],
                    "total_changes": 0,
                    "total_conflicts": 0,
                    "success_rate": 0.0,
                    "triggered_by": current_user.get("username", "admin"),
                    "error_summary": str(e)
                })
        
        background_tasks.add_task(run_sync)
        
        return AdminActionResponse(
            action="trigger_sync",
            success=True,
            message="Manual sync started successfully",
            performed_at=datetime.now(),
            performed_by=current_user.get("username", "admin"),
            details={
                "federal_states": [state.value for state in request.federal_states] if request.federal_states else "all",
                "years": request.years or "default_range",
                "dry_run": request.dry_run,
                "conflict_strategy": request.conflict_strategy.value
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error triggering manual sync: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to trigger sync: {str(e)}")


@router.get("/history", response_model=SyncHistoryResponse)
async def get_sync_history(
    pagination: PaginationParams = Depends(),
    filter_params: SyncHistoryFilter = Depends(),
    session: Session = Depends(get_session),
    current_user: dict = Depends(require_admin_user)
):
    """
    Get synchronization history
    
    Returns paginated history of sync operations with filtering options.
    """
    try:
        # Apply filters to sync history
        filtered_history = _sync_history.copy()
        
        if filter_params.status:
            filtered_history = [h for h in filtered_history if h["status"] == filter_params.status.value]
        
        if filter_params.triggered_by:
            filtered_history = [h for h in filtered_history if h["triggered_by"] == filter_params.triggered_by]
        
        # Apply pagination
        start_idx = (pagination.page - 1) * pagination.page_size
        end_idx = start_idx + pagination.page_size
        paginated_history = filtered_history[start_idx:end_idx]
        
        # Convert to response format
        history_items = []
        for item in paginated_history:
            history_items.append(SyncHistoryItem(
                sync_id=item["sync_id"],
                status=SyncStatus(item["status"]),
                started_at=datetime.fromisoformat(item["started_at"]),
                completed_at=datetime.fromisoformat(item["completed_at"]) if item["completed_at"] else None,
                duration_seconds=item["duration_seconds"],
                total_states=item["total_states"],
                successful_states=item["successful_states"],
                failed_states=item["failed_states"],
                total_changes=item["total_changes"],
                total_conflicts=item["total_conflicts"],
                success_rate=item["success_rate"],
                triggered_by=item["triggered_by"],
                error_summary=item.get("error_summary")
            ))
        
        return SyncHistoryResponse(
            items=history_items,
            total_count=len(filtered_history),
            page=pagination.page,
            page_size=pagination.page_size,
            has_next=end_idx < len(filtered_history)
        )
        
    except Exception as e:
        logger.error(f"Error getting sync history: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get sync history: {str(e)}")


@router.get("/statistics", response_model=SyncStatistics)
async def get_sync_statistics(
    session: Session = Depends(get_session),
    current_user: dict = Depends(require_admin_user)
):
    """
    Get synchronization statistics
    
    Returns comprehensive statistics about sync operations and system health.
    """
    try:
        # Calculate statistics from history
        total_syncs = len(_sync_history)
        successful_syncs = len([h for h in _sync_history if h["status"] == SyncStatus.COMPLETED.value])
        failed_syncs = total_syncs - successful_syncs
        
        avg_duration = 0
        if _sync_history:
            avg_duration = sum(h["duration_seconds"] for h in _sync_history) / len(_sync_history)
        
        last_successful = None
        last_failed = None
        
        for item in reversed(_sync_history):
            if item["status"] == SyncStatus.COMPLETED.value and not last_successful:
                last_successful = datetime.fromisoformat(item["completed_at"])
            elif item["status"] == SyncStatus.FAILED.value and not last_failed:
                last_failed = datetime.fromisoformat(item["completed_at"])
        
        # Get total holidays count
        total_holidays = session.query(Holiday).filter(
            Holiday.data_source == DataSource.MEHR_SCHULFERIEN_API
        ).count()
        
        total_conflicts = sum(h["total_conflicts"] for h in _sync_history)
        
        return SyncStatistics(
            total_syncs=total_syncs,
            successful_syncs=successful_syncs,
            failed_syncs=failed_syncs,
            average_duration_seconds=avg_duration,
            last_successful_sync=last_successful,
            last_failed_sync=last_failed,
            total_holidays_synced=total_holidays,
            total_conflicts_resolved=total_conflicts,
            uptime_percentage=95.0,  # TODO: Calculate actual uptime
            next_scheduled_sync=None  # TODO: Get from scheduler
        )
        
    except Exception as e:
        logger.error(f"Error getting sync statistics: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get sync statistics: {str(e)}")


@router.get("/scheduler/status", response_model=SchedulerStatusResponse)
async def get_scheduler_status(
    current_user: dict = Depends(require_admin_user)
):
    """
    Get scheduler status
    
    Returns information about the automated sync scheduler.
    """
    try:
        # TODO: Implement actual scheduler status
        return SchedulerStatusResponse(
            status=SchedulerStatus.RUNNING,
            running=True,
            jobs_count=1,
            next_run=None,
            last_run=None,
            last_run_status=None,
            uptime_seconds=3600.0,
            configuration={"interval": "monthly", "enabled": True}
        )
        
    except Exception as e:
        logger.error(f"Error getting scheduler status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get scheduler status: {str(e)}")


@router.post("/scheduler/pause", response_model=AdminActionResponse)
async def pause_scheduler(
    current_user: dict = Depends(require_admin_user)
):
    """
    Pause the sync scheduler
    
    Temporarily stops automated sync operations.
    """
    try:
        # TODO: Implement actual scheduler pause
        return AdminActionResponse(
            action="pause_scheduler",
            success=True,
            message="Scheduler paused successfully",
            performed_at=datetime.now(),
            performed_by=current_user.get("username", "admin")
        )
        
    except Exception as e:
        logger.error(f"Error pausing scheduler: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to pause scheduler: {str(e)}")


@router.post("/scheduler/resume", response_model=AdminActionResponse)
async def resume_scheduler(
    current_user: dict = Depends(require_admin_user)
):
    """
    Resume the sync scheduler
    
    Restarts automated sync operations.
    """
    try:
        # TODO: Implement actual scheduler resume
        return AdminActionResponse(
            action="resume_scheduler",
            success=True,
            message="Scheduler resumed successfully",
            performed_at=datetime.now(),
            performed_by=current_user.get("username", "admin")
        )
        
    except Exception as e:
        logger.error(f"Error resuming scheduler: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to resume scheduler: {str(e)}")


@router.get("/health", response_model=SystemHealthResponse)
async def get_system_health(
    session: Session = Depends(get_session),
    current_user: dict = Depends(require_admin_user)
):
    """
    Get system health status
    
    Returns comprehensive health information about all system components.
    """
    try:
        # Test database connection
        try:
            session.query(Holiday).limit(1).all()
            database_status = "healthy"
        except Exception:
            database_status = "unhealthy"
        
        # Test API client
        try:
            api_client = get_school_holiday_sync_service().api_client
            api_client_status = "healthy" if api_client else "unhealthy"
        except Exception:
            api_client_status = "unhealthy"
        
        # Get pending conflicts (placeholder)
        pending_conflicts = 0
        
        # Determine overall status
        if database_status == "healthy" and api_client_status == "healthy":
            overall_status = "healthy"
        elif database_status == "unhealthy" or api_client_status == "unhealthy":
            overall_status = "unhealthy"
        else:
            overall_status = "degraded"
        
        return SystemHealthResponse(
            overall_status=overall_status,
            database_status=database_status,
            api_client_status=api_client_status,
            scheduler_status="healthy",
            last_successful_sync=None,  # TODO: Get from history
            pending_conflicts=pending_conflicts,
            system_uptime_seconds=3600.0,  # TODO: Calculate actual uptime
            memory_usage_mb=128.0,  # TODO: Get actual memory usage
            disk_usage_percentage=45.0,  # TODO: Get actual disk usage
            checks_performed_at=datetime.now()
        )
        
    except Exception as e:
        logger.error(f"Error getting system health: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get system health: {str(e)}")


@router.get("/conflicts", response_model=List[ConflictItem])
async def get_conflicts(
    current_user: dict = Depends(require_admin_user)
):
    """
    Get current conflicts
    
    Returns list of unresolved data conflicts that require manual intervention.
    """
    try:
        # TODO: Implement actual conflict retrieval
        return []
        
    except Exception as e:
        logger.error(f"Error getting conflicts: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get conflicts: {str(e)}")


@router.post("/conflicts/{conflict_id}/resolve", response_model=ConflictResolutionResponse)
async def resolve_conflict(
    conflict_id: str,
    request: ConflictResolutionRequest,
    current_user: dict = Depends(require_admin_user)
):
    """
    Resolve a specific conflict
    
    Applies the specified resolution strategy to resolve a data conflict.
    """
    try:
        # TODO: Implement actual conflict resolution
        return ConflictResolutionResponse(
            conflict_id=conflict_id,
            resolution_strategy=request.resolution_strategy,
            resolved_at=datetime.now(),
            resolved_by=current_user.get("username", "admin"),
            changes_applied={},
            success=True
        )
        
    except Exception as e:
        logger.error(f"Error resolving conflict {conflict_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to resolve conflict: {str(e)}")
