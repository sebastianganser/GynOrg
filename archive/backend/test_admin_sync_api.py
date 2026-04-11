"""
Test Admin Sync API Endpoints

This module tests the admin interface API endpoints for school holiday
synchronization management, including status monitoring, manual triggers,
and system health checks.
"""
import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, AsyncMock
from fastapi.testclient import TestClient
from sqlmodel import Session

from app.main import app
from app.core.database import get_session
from app.core.auth import get_current_user
from app.services.school_holiday_sync_service import SyncStatus
from app.services.school_holiday_scheduler import SchedulerStatus, JobStatus


# Test client setup
client = TestClient(app)

# Mock dependencies
def mock_get_session():
    """Mock database session"""
    return Mock(spec=Session)

def mock_get_current_user():
    """Mock authenticated admin user"""
    return {"username": "admin", "role": "admin"}

# Override dependencies for testing
app.dependency_overrides[get_session] = mock_get_session
app.dependency_overrides[get_current_user] = mock_get_current_user


class TestAdminSyncAPI:
    """Test cases for Admin Sync API endpoints"""
    
    def test_get_sync_status_no_running_sync(self):
        """Test getting sync status when no sync is running"""
        with patch('app.api.v1.endpoints.admin_sync.get_school_holiday_sync_service') as mock_service_factory:
            mock_service = Mock()
            mock_service.get_sync_status.return_value = None
            mock_service_factory.return_value = mock_service
            
            response = client.get("/api/v1/admin/sync/status")
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "PENDING"
            assert data["total_states"] == 0
            assert data["completed_states"] == 0
            assert data["failed_states"] == 0
    
    def test_get_sync_status_with_running_sync(self):
        """Test getting sync status when sync is running"""
        mock_sync_data = {
            "sync_id": "sync_test_123",
            "status": "RUNNING",
            "started_at": "2025-09-21T15:30:00",
            "total_states": 16,
            "successful_states": ["BW", "BY"],
            "failed_states": []
        }
        
        with patch('app.api.v1.endpoints.admin_sync.get_school_holiday_sync_service') as mock_service_factory:
            mock_service = Mock()
            mock_service.get_sync_status.return_value = mock_sync_data
            mock_service_factory.return_value = mock_service
            
            response = client.get("/api/v1/admin/sync/status")
            
            assert response.status_code == 200
            data = response.json()
            assert data["sync_id"] == "sync_test_123"
            assert data["status"] == "RUNNING"
            assert data["total_states"] == 16
            assert data["completed_states"] == 2
            assert data["failed_states"] == 0
            assert "progress" in data
            assert data["progress"]["percentage"] == 12.5  # 2/16 * 100
    
    def test_trigger_manual_sync_success(self):
        """Test triggering manual sync successfully"""
        with patch('app.api.v1.endpoints.admin_sync.get_school_holiday_sync_service') as mock_service_factory:
            mock_service = Mock()
            mock_service.get_sync_status.return_value = None  # No running sync
            mock_service_factory.return_value = mock_service
            
            sync_request = {
                "federal_states": ["BW", "BY"],
                "years": [2025],
                "dry_run": True,
                "conflict_strategy": "API_WINS"
            }
            
            response = client.post("/api/v1/admin/sync/trigger", json=sync_request)
            
            assert response.status_code == 200
            data = response.json()
            assert data["action"] == "trigger_sync"
            assert data["success"] is True
            assert "Manual sync started successfully" in data["message"]
            assert data["performed_by"] == "admin"
    
    def test_trigger_manual_sync_already_running(self):
        """Test triggering manual sync when sync is already running"""
        mock_sync_data = {
            "sync_id": "sync_running_123",
            "status": "RUNNING"
        }
        
        with patch('app.api.v1.endpoints.admin_sync.get_school_holiday_sync_service') as mock_service_factory:
            mock_service = Mock()
            mock_service.get_sync_status.return_value = mock_sync_data
            mock_service_factory.return_value = mock_service
            
            sync_request = {
                "federal_states": ["BW"],
                "years": [2025],
                "dry_run": False,
                "conflict_strategy": "API_WINS"
            }
            
            response = client.post("/api/v1/admin/sync/trigger", json=sync_request)
            
            assert response.status_code == 409
            assert "already running" in response.json()["detail"]
    
    def test_get_sync_history_empty(self):
        """Test getting sync history when no history exists"""
        response = client.get("/api/v1/admin/sync/history")
        
        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []
        assert data["total_count"] == 0
        assert data["page"] == 1
        assert data["page_size"] == 20
        assert data["has_next"] is False
    
    def test_get_sync_history_with_pagination(self):
        """Test getting sync history with pagination"""
        # Mock some history data in the global variable
        with patch('app.api.v1.endpoints.admin_sync._sync_history') as mock_history:
            mock_history_data = [
                {
                    "sync_id": f"sync_test_{i}",
                    "status": "COMPLETED",
                    "started_at": "2025-09-21T15:30:00",
                    "completed_at": "2025-09-21T15:35:00",
                    "duration_seconds": 300,
                    "total_states": 16,
                    "successful_states": ["BW", "BY"],
                    "failed_states": [],
                    "total_changes": 10,
                    "total_conflicts": 0,
                    "success_rate": 1.0,
                    "triggered_by": "admin",
                    "error_summary": None
                }
                for i in range(5)
            ]
            mock_history.__iter__ = Mock(return_value=iter(mock_history_data))
            mock_history.__len__ = Mock(return_value=len(mock_history_data))
            mock_history.copy.return_value = mock_history_data
            
            response = client.get("/api/v1/admin/sync/history?page=1&page_size=3")
            
            assert response.status_code == 200
            data = response.json()
            assert len(data["items"]) == 3
            assert data["total_count"] == 5
            assert data["page"] == 1
            assert data["page_size"] == 3
            assert data["has_next"] is True
    
    def test_get_sync_statistics(self):
        """Test getting sync statistics"""
        with patch('app.api.v1.endpoints.admin_sync._sync_history') as mock_history:
            mock_history_data = [
                {
                    "status": "COMPLETED",
                    "started_at": "2025-09-21T15:30:00",
                    "completed_at": "2025-09-21T15:35:00",
                    "duration_seconds": 300,
                    "total_conflicts": 2
                },
                {
                    "status": "FAILED",
                    "started_at": "2025-09-21T14:30:00",
                    "completed_at": "2025-09-21T14:31:00",
                    "duration_seconds": 60,
                    "total_conflicts": 0
                }
            ]
            mock_history.__iter__ = Mock(return_value=iter(mock_history_data))
            mock_history.__len__ = Mock(return_value=len(mock_history_data))
            
            with patch('app.api.v1.endpoints.admin_sync.get_school_holiday_scheduler') as mock_scheduler_factory:
                mock_scheduler = Mock()
                mock_scheduler.get_next_run_time.return_value = datetime.now() + timedelta(days=1)
                mock_scheduler_factory.return_value = mock_scheduler
                
                response = client.get("/api/v1/admin/sync/statistics")
                
                assert response.status_code == 200
                data = response.json()
                assert data["total_syncs"] == 2
                assert data["successful_syncs"] == 1
                assert data["failed_syncs"] == 1
                assert data["average_duration_seconds"] == 180.0  # (300 + 60) / 2
                assert data["total_conflicts_resolved"] == 2
    
    def test_get_scheduler_status(self):
        """Test getting scheduler status"""
        mock_status = {
            "status": SchedulerStatus.RUNNING,
            "running": True,
            "jobs_count": 1,
            "next_run": datetime.now() + timedelta(hours=1),
            "last_run": datetime.now() - timedelta(hours=23),
            "last_run_status": JobStatus.COMPLETED,
            "uptime_seconds": 86400,
            "configuration": {"cron": "0 2 1 * *"}
        }
        
        with patch('app.api.v1.endpoints.admin_sync.get_school_holiday_scheduler') as mock_scheduler_factory:
            mock_scheduler = Mock()
            mock_scheduler.get_status.return_value = mock_status
            mock_scheduler_factory.return_value = mock_scheduler
            
            response = client.get("/api/v1/admin/sync/scheduler/status")
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "RUNNING"
            assert data["running"] is True
            assert data["jobs_count"] == 1
            assert data["uptime_seconds"] == 86400
    
    def test_pause_scheduler(self):
        """Test pausing the scheduler"""
        with patch('app.api.v1.endpoints.admin_sync.get_school_holiday_scheduler') as mock_scheduler_factory:
            mock_scheduler = Mock()
            mock_scheduler_factory.return_value = mock_scheduler
            
            response = client.post("/api/v1/admin/sync/scheduler/pause")
            
            assert response.status_code == 200
            data = response.json()
            assert data["action"] == "pause_scheduler"
            assert data["success"] is True
            assert "paused successfully" in data["message"]
            mock_scheduler.pause.assert_called_once()
    
    def test_resume_scheduler(self):
        """Test resuming the scheduler"""
        with patch('app.api.v1.endpoints.admin_sync.get_school_holiday_scheduler') as mock_scheduler_factory:
            mock_scheduler = Mock()
            mock_scheduler_factory.return_value = mock_scheduler
            
            response = client.post("/api/v1/admin/sync/scheduler/resume")
            
            assert response.status_code == 200
            data = response.json()
            assert data["action"] == "resume_scheduler"
            assert data["success"] is True
            assert "resumed successfully" in data["message"]
            mock_scheduler.resume.assert_called_once()
    
    def test_get_system_health(self):
        """Test getting system health status"""
        with patch('app.api.v1.endpoints.admin_sync.get_school_holiday_scheduler') as mock_scheduler_factory:
            mock_scheduler = Mock()
            mock_scheduler.get_status.return_value = {"running": True}
            mock_scheduler_factory.return_value = mock_scheduler
            
            with patch('app.api.v1.endpoints.admin_sync.get_school_holiday_api_client'):
                with patch('app.api.v1.endpoints.admin_sync.psutil') as mock_psutil:
                    mock_process = Mock()
                    mock_process.memory_info.return_value.rss = 256 * 1024 * 1024  # 256 MB
                    mock_psutil.Process.return_value = mock_process
                    mock_psutil.disk_usage.return_value.percent = 45.0
                    
                    response = client.get("/api/v1/admin/sync/health")
                    
                    assert response.status_code == 200
                    data = response.json()
                    assert data["overall_status"] == "healthy"
                    assert data["database_status"] == "healthy"
                    assert data["api_client_status"] == "healthy"
                    assert data["scheduler_status"] == "healthy"
                    assert data["memory_usage_mb"] == 256.0
                    assert data["disk_usage_percentage"] == 45.0
    
    def test_get_conflicts_placeholder(self):
        """Test getting conflicts (placeholder endpoint)"""
        response = client.get("/api/v1/admin/sync/conflicts")
        
        assert response.status_code == 200
        data = response.json()
        assert data["conflicts"] == []
        assert "not yet implemented" in data["message"]
    
    def test_resolve_conflict_placeholder(self):
        """Test resolving conflict (placeholder endpoint)"""
        conflict_request = {
            "conflict_id": "test_conflict_123",
            "resolution_strategy": "API_WINS",
            "notes": "Test resolution"
        }
        
        response = client.post("/api/v1/admin/sync/conflicts/test_conflict_123/resolve", json=conflict_request)
        
        assert response.status_code == 200
        data = response.json()
        assert "not yet implemented" in data["message"]
    
    def test_unauthorized_access(self):
        """Test unauthorized access to admin endpoints"""
        # Override auth dependency to return None (unauthorized)
        app.dependency_overrides[get_current_user] = lambda: None
        
        try:
            response = client.get("/api/v1/admin/sync/status")
            assert response.status_code == 401
        finally:
            # Restore mock auth
            app.dependency_overrides[get_current_user] = mock_get_current_user
    
    def test_api_error_handling(self):
        """Test API error handling"""
        with patch('app.api.v1.endpoints.admin_sync.get_school_holiday_sync_service') as mock_service_factory:
            mock_service_factory.side_effect = Exception("Service unavailable")
            
            response = client.get("/api/v1/admin/sync/status")
            
            assert response.status_code == 500
            assert "Failed to get sync status" in response.json()["detail"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
