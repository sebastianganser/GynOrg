"""
Admin Sync Schemas for School Holiday Synchronization Management

This module defines Pydantic schemas for the admin interface API endpoints,
including sync status, conflict resolution, and monitoring data structures.
"""
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from pydantic import BaseModel, Field
from enum import Enum

from ..services.school_holiday_sync_service import SyncStatus
from ..services.school_holiday_diff_service import ConflictResolutionStrategy
from ..services.school_holiday_scheduler import SchedulerStatus, JobStatus
from ..models.federal_state import FederalState


class SyncTriggerRequest(BaseModel):
    """Request schema for triggering manual sync"""
    federal_states: Optional[List[FederalState]] = Field(
        None, 
        description="Specific federal states to sync (all if None)"
    )
    years: Optional[List[int]] = Field(
        None,
        description="Years to sync (default range if None)"
    )
    dry_run: bool = Field(
        False,
        description="Whether to perform a dry run without committing changes"
    )
    conflict_strategy: ConflictResolutionStrategy = Field(
        ConflictResolutionStrategy.API_WINS,
        description="Strategy for resolving conflicts"
    )


class SyncStatusResponse(BaseModel):
    """Response schema for sync status"""
    sync_id: Optional[str] = Field(None, description="Current sync ID if running")
    status: SyncStatus = Field(description="Current sync status")
    started_at: Optional[datetime] = Field(None, description="Sync start time")
    progress: Optional[Dict[str, Any]] = Field(None, description="Progress information")
    estimated_completion: Optional[datetime] = Field(None, description="Estimated completion time")
    current_state: Optional[str] = Field(None, description="Currently processing state")
    total_states: int = Field(0, description="Total states to process")
    completed_states: int = Field(0, description="Completed states")
    failed_states: int = Field(0, description="Failed states")


class SyncHistoryItem(BaseModel):
    """Schema for sync history items"""
    sync_id: str = Field(description="Unique sync identifier")
    status: SyncStatus = Field(description="Final sync status")
    started_at: datetime = Field(description="Sync start time")
    completed_at: Optional[datetime] = Field(None, description="Sync completion time")
    duration_seconds: float = Field(description="Sync duration in seconds")
    total_states: int = Field(description="Total states processed")
    successful_states: List[str] = Field(description="Successfully synced states")
    failed_states: List[str] = Field(description="Failed states")
    total_changes: int = Field(description="Total changes applied")
    total_conflicts: int = Field(description="Total conflicts encountered")
    success_rate: float = Field(description="Success rate (0.0 to 1.0)")
    triggered_by: str = Field(description="Who/what triggered the sync")
    error_summary: Optional[str] = Field(None, description="Error summary if failed")


class SyncHistoryResponse(BaseModel):
    """Response schema for sync history"""
    items: List[SyncHistoryItem] = Field(description="History items")
    total_count: int = Field(description="Total number of history items")
    page: int = Field(description="Current page number")
    page_size: int = Field(description="Items per page")
    has_next: bool = Field(description="Whether there are more pages")


class SyncStatistics(BaseModel):
    """Schema for sync statistics"""
    total_syncs: int = Field(description="Total number of syncs performed")
    successful_syncs: int = Field(description="Number of successful syncs")
    failed_syncs: int = Field(description="Number of failed syncs")
    average_duration_seconds: float = Field(description="Average sync duration")
    last_successful_sync: Optional[datetime] = Field(None, description="Last successful sync time")
    last_failed_sync: Optional[datetime] = Field(None, description="Last failed sync time")
    total_holidays_synced: int = Field(description="Total holidays synchronized")
    total_conflicts_resolved: int = Field(description="Total conflicts resolved")
    uptime_percentage: float = Field(description="Sync system uptime percentage")
    next_scheduled_sync: Optional[datetime] = Field(None, description="Next scheduled sync time")


class ConflictItem(BaseModel):
    """Schema for conflict items"""
    conflict_id: str = Field(description="Unique conflict identifier")
    federal_state: FederalState = Field(description="Federal state with conflict")
    holiday_name: str = Field(description="Name of the conflicting holiday")
    conflict_type: str = Field(description="Type of conflict")
    api_data: Dict[str, Any] = Field(description="Data from API")
    local_data: Dict[str, Any] = Field(description="Local database data")
    conflicting_fields: List[str] = Field(description="Fields that are in conflict")
    created_at: datetime = Field(description="When conflict was detected")
    priority: str = Field(description="Conflict priority (high/medium/low)")
    auto_resolvable: bool = Field(description="Whether conflict can be auto-resolved")


class ConflictResolutionRequest(BaseModel):
    """Request schema for resolving conflicts"""
    conflict_id: str = Field(description="ID of conflict to resolve")
    resolution_strategy: ConflictResolutionStrategy = Field(description="Resolution strategy")
    manual_data: Optional[Dict[str, Any]] = Field(
        None,
        description="Manual data override (for manual resolution)"
    )
    notes: Optional[str] = Field(None, description="Resolution notes")


class ConflictResolutionResponse(BaseModel):
    """Response schema for conflict resolution"""
    conflict_id: str = Field(description="Resolved conflict ID")
    resolution_strategy: ConflictResolutionStrategy = Field(description="Strategy used")
    resolved_at: datetime = Field(description="Resolution timestamp")
    resolved_by: str = Field(description="Who resolved the conflict")
    changes_applied: Dict[str, Any] = Field(description="Changes that were applied")
    success: bool = Field(description="Whether resolution was successful")
    error_message: Optional[str] = Field(None, description="Error message if failed")


class SchedulerStatusResponse(BaseModel):
    """Response schema for scheduler status"""
    status: SchedulerStatus = Field(description="Current scheduler status")
    running: bool = Field(description="Whether scheduler is running")
    jobs_count: int = Field(description="Number of scheduled jobs")
    next_run: Optional[datetime] = Field(None, description="Next scheduled run time")
    last_run: Optional[datetime] = Field(None, description="Last run time")
    last_run_status: Optional[JobStatus] = Field(None, description="Last run status")
    uptime_seconds: float = Field(description="Scheduler uptime in seconds")
    configuration: Dict[str, Any] = Field(description="Scheduler configuration")


class JobExecutionItem(BaseModel):
    """Schema for job execution history items"""
    execution_id: str = Field(description="Unique execution identifier")
    job_id: str = Field(description="Job identifier")
    status: JobStatus = Field(description="Execution status")
    started_at: datetime = Field(description="Execution start time")
    completed_at: Optional[datetime] = Field(None, description="Execution completion time")
    duration_seconds: Optional[float] = Field(None, description="Execution duration")
    result_summary: Optional[str] = Field(None, description="Execution result summary")
    error_message: Optional[str] = Field(None, description="Error message if failed")


class JobExecutionHistoryResponse(BaseModel):
    """Response schema for job execution history"""
    executions: List[JobExecutionItem] = Field(description="Execution history items")
    total_count: int = Field(description="Total number of executions")
    page: int = Field(description="Current page number")
    page_size: int = Field(description="Items per page")


class AlertConfiguration(BaseModel):
    """Schema for alert configuration"""
    email_alerts_enabled: bool = Field(description="Whether email alerts are enabled")
    email_recipients: List[str] = Field(description="Email recipients for alerts")
    browser_notifications_enabled: bool = Field(description="Whether browser notifications are enabled")
    alert_on_sync_failure: bool = Field(description="Alert on sync failures")
    alert_on_conflicts: bool = Field(description="Alert on conflicts")
    alert_on_scheduler_down: bool = Field(description="Alert when scheduler is down")
    quiet_hours_start: Optional[str] = Field(None, description="Quiet hours start time (HH:MM)")
    quiet_hours_end: Optional[str] = Field(None, description="Quiet hours end time (HH:MM)")


class SystemHealthResponse(BaseModel):
    """Response schema for system health check"""
    overall_status: str = Field(description="Overall system status (healthy/degraded/unhealthy)")
    database_status: str = Field(description="Database connection status")
    api_client_status: str = Field(description="External API client status")
    scheduler_status: str = Field(description="Scheduler status")
    last_successful_sync: Optional[datetime] = Field(None, description="Last successful sync")
    pending_conflicts: int = Field(description="Number of pending conflicts")
    system_uptime_seconds: float = Field(description="System uptime in seconds")
    memory_usage_mb: float = Field(description="Memory usage in MB")
    disk_usage_percentage: float = Field(description="Disk usage percentage")
    checks_performed_at: datetime = Field(description="When health checks were performed")


class AdminActionRequest(BaseModel):
    """Base schema for admin actions"""
    action: str = Field(description="Action to perform")
    parameters: Optional[Dict[str, Any]] = Field(None, description="Action parameters")
    reason: Optional[str] = Field(None, description="Reason for the action")


class AdminActionResponse(BaseModel):
    """Response schema for admin actions"""
    action: str = Field(description="Action that was performed")
    success: bool = Field(description="Whether action was successful")
    message: str = Field(description="Result message")
    performed_at: datetime = Field(description="When action was performed")
    performed_by: str = Field(description="Who performed the action")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional details")


# Utility schemas for common patterns
class PaginationParams(BaseModel):
    """Schema for pagination parameters"""
    page: int = Field(1, ge=1, description="Page number (1-based)")
    page_size: int = Field(20, ge=1, le=100, description="Items per page")


class DateRangeFilter(BaseModel):
    """Schema for date range filtering"""
    start_date: Optional[datetime] = Field(None, description="Start date for filtering")
    end_date: Optional[datetime] = Field(None, description="End date for filtering")


class SyncHistoryFilter(BaseModel):
    """Schema for sync history filtering"""
    status: Optional[SyncStatus] = Field(None, description="Filter by sync status")
    federal_state: Optional[FederalState] = Field(None, description="Filter by federal state")
    date_range: Optional[DateRangeFilter] = Field(None, description="Date range filter")
    triggered_by: Optional[str] = Field(None, description="Filter by who triggered sync")
