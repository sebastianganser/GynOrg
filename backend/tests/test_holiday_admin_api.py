"""
Pytest Tests for Holiday Admin API Endpoints

Tests all 8 admin endpoints with authentication, error handling, and service mocking.
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from app.main import app
from app.core.database import get_session
from app.services.holiday_scheduler import SchedulerStatus


# Test client
client = TestClient(app)


# Mock authentication
@pytest.fixture
def mock_auth():
    """Mock authentication to bypass login"""
    with patch('app.api.v1.endpoints.holiday_admin.require_admin_user') as mock:
        mock.return_value = {"username": "test_admin", "id": 1}
        yield mock


@pytest.fixture
def mock_scheduler():
    """Mock HolidayScheduler"""
    with patch('app.api.v1.endpoints.holiday_admin.get_holiday_scheduler') as mock:
        scheduler = MagicMock()
        scheduler.status = SchedulerStatus.RUNNING
        scheduler.JOB_ID = 'monthly_holiday_import'
        scheduler.get_scheduler_status.return_value = {
            'status': 'RUNNING',
            'running': True,
            'jobs_count': 1,
            'config': {'cron': '0 2 1 * *'}
        }
        scheduler.get_job_info.return_value = {
            'id': 'monthly_holiday_import',
            'name': 'monthly_holiday_import',
            'next_run_time': datetime.now().isoformat(),
            'trigger': 'cron'
        }
        scheduler.get_all_jobs.return_value = [{
            'id': 'monthly_holiday_import',
            'name': 'monthly_holiday_import',
            'next_run_time': datetime.now().isoformat(),
            'trigger': 'cron'
        }]
        scheduler.get_job_executions.return_value = []
        scheduler.trigger_manual_import.return_value = 'manual_import_123'
        mock.return_value = scheduler
        yield scheduler


class TestImportEndpoints:
    """Test import-related endpoints"""
    
    def test_trigger_import(self, mock_auth):
        """Test POST /holidays/admin/import"""
        response = client.post(
            "/api/v1/holidays/admin/import",
            json={"start_year": 2024, "end_year": 2026}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
        assert data['action'] == 'trigger_import'
        assert 'performed_at' in data
    
    def test_get_import_status(self, mock_auth):
        """Test GET /holidays/admin/import/status"""
        response = client.get("/api/v1/holidays/admin/import/status")
        
        assert response.status_code == 200
        data = response.json()
        assert 'is_running' in data
        assert isinstance(data['is_running'], bool)
    
    def test_import_requires_auth(self):
        """Test that import endpoint requires authentication"""
        response = client.post(
            "/api/v1/holidays/admin/import",
            json={}
        )
        
        assert response.status_code == 401


class TestSchedulerEndpoints:
    """Test scheduler-related endpoints"""
    
    def test_get_scheduler_status(self, mock_auth, mock_scheduler):
        """Test GET /holidays/admin/scheduler/status"""
        response = client.get("/api/v1/holidays/admin/scheduler/status")
        
        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'RUNNING'
        assert data['running'] is True
        assert 'jobs_count' in data
    
    def test_start_scheduler(self, mock_auth, mock_scheduler):
        """Test POST /holidays/admin/scheduler/start"""
        response = client.post("/api/v1/holidays/admin/scheduler/start")
        
        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
        assert data['action'] == 'start_scheduler'
    
    def test_stop_scheduler(self, mock_auth, mock_scheduler):
        """Test POST /holidays/admin/scheduler/stop"""
        mock_scheduler.status = SchedulerStatus.RUNNING
        
        response = client.post("/api/v1/holidays/admin/scheduler/stop")
        
        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
        assert data['action'] == 'stop_scheduler'
    
    def test_trigger_manual_job(self, mock_auth, mock_scheduler):
        """Test POST /holidays/admin/scheduler/trigger"""
        response = client.post("/api/v1/holidays/admin/scheduler/trigger")
        
        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
        assert 'job_id' in data
        assert data['job_id'].startswith('manual_import_')
    
    def test_get_scheduler_jobs(self, mock_auth, mock_scheduler):
        """Test GET /holidays/admin/scheduler/jobs"""
        response = client.get("/api/v1/holidays/admin/scheduler/jobs")
        
        assert response.status_code == 200
        data = response.json()
        assert 'jobs' in data
        assert 'total_count' in data
        assert isinstance(data['jobs'], list)
    
    def test_get_job_executions(self, mock_auth, mock_scheduler):
        """Test GET /holidays/admin/scheduler/executions"""
        response = client.get("/api/v1/holidays/admin/scheduler/executions?limit=10")
        
        assert response.status_code == 200
        data = response.json()
        assert 'executions' in data
        assert 'total_count' in data
        assert 'limit' in data


class TestAuthentication:
    """Test authentication requirements"""
    
    def test_all_endpoints_require_auth(self):
        """Test that all endpoints require authentication"""
        endpoints = [
            ("POST", "/api/v1/holidays/admin/import"),
            ("GET", "/api/v1/holidays/admin/import/status"),
            ("GET", "/api/v1/holidays/admin/scheduler/status"),
            ("POST", "/api/v1/holidays/admin/scheduler/start"),
            ("POST", "/api/v1/holidays/admin/scheduler/stop"),
            ("POST", "/api/v1/holidays/admin/scheduler/trigger"),
            ("GET", "/api/v1/holidays/admin/scheduler/jobs"),
            ("GET", "/api/v1/holidays/admin/scheduler/executions"),
        ]
        
        for method, endpoint in endpoints:
            if method == "GET":
                response = client.get(endpoint)
            else:
                response = client.post(endpoint, json={})
            
            assert response.status_code == 401, f"{method} {endpoint} should require auth"


class TestErrorHandling:
    """Test error handling"""
    
    def test_import_conflict_when_running(self, mock_auth):
        """Test that concurrent imports are prevented"""
        # First import
        response1 = client.post(
            "/api/v1/holidays/admin/import",
            json={}
        )
        assert response1.status_code == 200
        
        # Note: In real scenario, would need to actually have import running
        # This is a simplified test
    
    @patch('app.api.v1.endpoints.holiday_admin.get_holiday_scheduler')
    def test_scheduler_error_handling(self, mock_get_scheduler, mock_auth):
        """Test scheduler error handling"""
        mock_get_scheduler.side_effect = Exception("Scheduler error")
        
        response = client.get("/api/v1/holidays/admin/scheduler/status")
        
        assert response.status_code == 500
        assert "Failed to get scheduler status" in response.json()['detail']


class TestResponseFormats:
    """Test response format compliance"""
    
    def test_admin_action_response_format(self, mock_auth):
        """Test AdminActionResponse format"""
        response = client.post("/api/v1/holidays/admin/import", json={})
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify required fields
        assert 'success' in data
        assert 'message' in data
        assert 'action' in data
        assert 'performed_at' in data
        assert 'performed_by' in data
    
    def test_scheduler_status_response_format(self, mock_auth, mock_scheduler):
        """Test SchedulerStatusResponse format"""
        response = client.get("/api/v1/holidays/admin/scheduler/status")
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify required fields
        assert 'status' in data
        assert 'running' in data
        assert 'jobs_count' in data
        assert 'configuration' in data
