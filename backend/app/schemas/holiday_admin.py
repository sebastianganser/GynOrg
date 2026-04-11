"""
Pydantic schemas for Holiday Admin API endpoints

These schemas define the request and response models for the
Holiday Management Admin API (Task 22.6).
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum

from ..models.federal_state import FederalState


class ImportTriggerRequest(BaseModel):
    """Request model for triggering manual holiday import"""
    start_year: Optional[int] = Field(None, description="Start year for import (defaults to config)")
    end_year: Optional[int] = Field(None, description="End year for import (defaults to config)")
    federal_states: Optional[List[FederalState]] = Field(None, description="Federal states to import (defaults to all)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "start_year": 2024,
                "end_year": 2026,
                "federal_states": ["BADEN_WUERTTEMBERG", "BAYERN"]
            }
        }


class ImportStatusResponse(BaseModel):
    """Response model for import status"""
    is_running: bool = Field(..., description="Whether an import is currently running")
    last_import: Optional[datetime] = Field(None, description="Timestamp of last import")
    last_result: Optional[Dict[str, Any]] = Field(None, description="Result of last import")
    current_progress: Optional[Dict[str, Any]] = Field(None, description="Current import progress if running")
    
    class Config:
        json_schema_extra = {
            "example": {
                "is_running": False,
                "last_import": "2025-10-27T14:00:00",
                "last_result": {
                    "action": "imported",
                    "total_imported": 150,
                    "missing_years": [2026, 2027]
                },
                "current_progress": None
            }
        }


class SchedulerStatusResponse(BaseModel):
    """Response model for scheduler status"""
    status: str = Field(..., description="Scheduler status (RUNNING, STOPPED, ERROR)")
    running: bool = Field(..., description="Whether scheduler is running")
    jobs_count: int = Field(..., description="Number of scheduled jobs")
    next_run_time: Optional[datetime] = Field(None, description="Next scheduled run time")
    last_execution: Optional[Dict[str, Any]] = Field(None, description="Last job execution details")
    configuration: Dict[str, Any] = Field(..., description="Scheduler configuration")
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "RUNNING",
                "running": True,
                "jobs_count": 1,
                "next_run_time": "2025-11-01T02:00:00",
                "last_execution": {
                    "status": "COMPLETED",
                    "started_at": "2025-10-01T02:00:00",
                    "duration_seconds": 45.2
                },
                "configuration": {
                    "cron_expression": "0 2 1 * *",
                    "timezone": "Europe/Berlin"
                }
            }
        }


class JobInfo(BaseModel):
    """Information about a scheduled job"""
    id: str = Field(..., description="Job ID")
    name: str = Field(..., description="Job name")
    next_run_time: Optional[datetime] = Field(None, description="Next run time")
    trigger: str = Field(..., description="Trigger description")


class JobsListResponse(BaseModel):
    """Response model for jobs list"""
    jobs: List[JobInfo] = Field(..., description="List of scheduled jobs")
    total_count: int = Field(..., description="Total number of jobs")


class JobExecution(BaseModel):
    """Information about a job execution"""
    job_id: str = Field(..., description="Job ID")
    execution_id: str = Field(..., description="Execution ID")
    status: str = Field(..., description="Execution status")
    started_at: datetime = Field(..., description="Start time")
    completed_at: Optional[datetime] = Field(None, description="Completion time")
    duration_seconds: Optional[float] = Field(None, description="Execution duration")
    import_result: Optional[Dict[str, Any]] = Field(None, description="Import result details")
    error_message: Optional[str] = Field(None, description="Error message if failed")


class JobExecutionsResponse(BaseModel):
    """Response model for job executions history"""
    executions: List[JobExecution] = Field(..., description="List of job executions")
    total_count: int = Field(..., description="Total number of executions")
    limit: int = Field(..., description="Number of executions returned")


class AdminActionResponse(BaseModel):
    """Generic response for admin actions"""
    success: bool = Field(..., description="Whether the action was successful")
    message: str = Field(..., description="Action result message")
    action: str = Field(..., description="Action performed")
    performed_at: datetime = Field(..., description="When the action was performed")
    performed_by: str = Field(..., description="Who performed the action")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional details")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Scheduler started successfully",
                "action": "start_scheduler",
                "performed_at": "2025-10-27T14:30:00",
                "performed_by": "admin",
                "details": {"previous_status": "STOPPED"}
            }
        }


class TriggerJobResponse(BaseModel):
    """Response model for manual job trigger"""
    success: bool = Field(..., description="Whether the trigger was successful")
    message: str = Field(..., description="Trigger result message")
    job_id: str = Field(..., description="ID of the triggered job")
    triggered_at: datetime = Field(..., description="When the job was triggered")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Manual import job triggered successfully",
                "job_id": "manual_import_20251027_143000",
                "triggered_at": "2025-10-27T14:30:00"
            }
        }
