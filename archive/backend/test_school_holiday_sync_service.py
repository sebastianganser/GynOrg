"""
Unit tests for SchoolHolidaySyncService

Tests cover:
- Sync orchestration logic
- Error handling and rollback mechanisms
- Federal state processing
- API integration with retry logic
- Conflict resolution workflows
- Performance and reliability
"""
import pytest
from unittest.mock import Mock, patch, MagicMock, call
from datetime import date, datetime, timedelta
from sqlmodel import Session
from app.services.school_holiday_sync_service import (
    SchoolHolidaySyncService,
    SyncStatus,
    SyncErrorType,
    SyncError,
    StateSyncResult,
    SyncResult,
    get_school_holiday_sync_service
)
from app.services.school_holiday_diff_service import (
    HolidayDiff,
    DiffStatistics,
    ConflictResolutionStrategy
)
from app.models.holiday import Holiday, HolidayType, SchoolVacationType, DataSource
from app.models.federal_state import FederalState


class TestSchoolHolidaySyncService:
    """Test suite for SchoolHolidaySyncService"""
    
    @pytest.fixture
    def mock_session(self):
        """Create a mock database session"""
        session = Mock(spec=Session)
        session.exec.return_value.all.return_value = []
        return session
    
    @pytest.fixture
    def mock_api_client(self):
        """Create a mock API client"""
        client = Mock()
        client.get_school_holidays.return_value = [
            {
                "name": "Osterferien",
                "start_date": date(2025, 4, 14),
                "end_date": date(2025, 4, 25),
                "school_vacation_type": SchoolVacationType.EASTER,
                "api_id": "4673",
                "notes": "Easter holidays"
            }
        ]
        return client
    
    @pytest.fixture
    def mock_diff_service(self):
        """Create a mock diff service"""
        service = Mock()
        
        # Mock diff result with no changes
        diff = HolidayDiff(
            new_holidays=[],
            updated_holidays=[],
            deleted_holidays=[],
            conflicts=[],
            statistics=DiffStatistics(
                total_api_records=1,
                total_local_records=1,
                processing_time_ms=100
            )
        )
        service.compare_holiday_data.return_value = diff
        service.apply_diff.return_value = {"applied": 0, "errors": 0, "skipped": 0}
        
        return service
    
    @pytest.fixture
    def sync_service(self, mock_session, mock_api_client, mock_diff_service):
        """Create a test sync service instance"""
        return SchoolHolidaySyncService(
            session=mock_session,
            api_client=mock_api_client,
            diff_service=mock_diff_service,
            years_to_sync=[2025]
        )
    
    def test_service_initialization(self, mock_session):
        """Test service initialization with different configurations"""
        # Default initialization
        service = SchoolHolidaySyncService(mock_session)
        assert service.session == mock_session
        assert service.conflict_strategy == ConflictResolutionStrategy.API_WINS
        assert service.years_to_sync == list(range(2023, 2031))
        assert service.max_retries == 3
        assert service.retry_delay == 1.0
        
        # Custom initialization
        custom_years = [2024, 2025]
        service = SchoolHolidaySyncService(
            mock_session,
            conflict_strategy=ConflictResolutionStrategy.LOCAL_WINS,
            years_to_sync=custom_years,
            max_retries=5,
            retry_delay=2.0
        )
        assert service.conflict_strategy == ConflictResolutionStrategy.LOCAL_WINS
        assert service.years_to_sync == custom_years
        assert service.max_retries == 5
        assert service.retry_delay == 2.0
    
    def test_validate_sync_prerequisites_success(self, sync_service):
        """Test successful prerequisite validation"""
        # Should not raise any exception
        sync_service._validate_sync_prerequisites()
        
        # Verify database query was executed
        sync_service.session.exec.assert_called_once()
    
    def test_validate_sync_prerequisites_failure(self, sync_service):
        """Test prerequisite validation failure"""
        # Mock database error
        sync_service.session.exec.side_effect = Exception("Database connection failed")
        
        with pytest.raises(Exception, match="Database connection failed"):
            sync_service._validate_sync_prerequisites()
    
    def test_create_rollback_point(self, sync_service):
        """Test rollback point creation"""
        # Mock existing holidays
        mock_holidays = [
            Mock(id=1, federal_state_code="BW"),
            Mock(id=2, federal_state_code="BW")
        ]
        sync_service.session.exec.return_value.all.return_value = mock_holidays
        
        rollback_point = sync_service._create_rollback_point(FederalState.BW)
        
        assert rollback_point["federal_state"] == "BW"
        assert rollback_point["holiday_count"] == 2
        assert rollback_point["holiday_ids"] == [1, 2]
        assert "timestamp" in rollback_point
        
        # Verify rollback point is stored
        assert "BW" in sync_service._rollback_points
    
    def test_rollback_to_point(self, sync_service):
        """Test rollback execution"""
        # Setup rollback point
        rollback_point = {
            "federal_state": "BW",
            "timestamp": datetime.now(),
            "holiday_count": 1,
            "holiday_ids": [1]
        }
        
        # Mock current holidays (including new ones)
        mock_holidays = [
            Mock(id=1, federal_state_code="BW"),  # Original
            Mock(id=2, federal_state_code="BW"),  # New (should be deleted)
            Mock(id=3, federal_state_code="BW")   # New (should be deleted)
        ]
        sync_service.session.exec.return_value.all.return_value = mock_holidays
        
        sync_service._rollback_to_point(FederalState.BW, rollback_point)
        
        # Verify new holidays were deleted
        assert sync_service.session.delete.call_count == 2
        sync_service.session.delete.assert_any_call(mock_holidays[1])
        sync_service.session.delete.assert_any_call(mock_holidays[2])
        
        # Verify commit was called
        sync_service.session.commit.assert_called_once()
    
    def test_fetch_api_data_with_retry_success(self, sync_service):
        """Test successful API data fetching"""
        expected_data = [{"name": "Test Holiday"}]
        sync_service.api_client.get_school_holidays.return_value = expected_data
        
        result = sync_service._fetch_api_data_with_retry(FederalState.BW, 2025)
        
        assert result == expected_data
        sync_service.api_client.get_school_holidays.assert_called_once_with(FederalState.BW, 2025)
    
    @patch('time.sleep')
    def test_fetch_api_data_with_retry_failure_then_success(self, mock_sleep, sync_service):
        """Test API data fetching with retry logic"""
        # First call fails, second succeeds
        sync_service.api_client.get_school_holidays.side_effect = [
            Exception("API Error"),
            [{"name": "Test Holiday"}]
        ]
        
        result = sync_service._fetch_api_data_with_retry(FederalState.BW, 2025)
        
        assert result == [{"name": "Test Holiday"}]
        assert sync_service.api_client.get_school_holidays.call_count == 2
        mock_sleep.assert_called_once_with(1.0)  # First retry delay
    
    @patch('time.sleep')
    def test_fetch_api_data_with_retry_max_retries_exceeded(self, mock_sleep, sync_service):
        """Test API data fetching when max retries are exceeded"""
        # All calls fail
        sync_service.api_client.get_school_holidays.side_effect = Exception("Persistent API Error")
        
        with pytest.raises(Exception, match="Persistent API Error"):
            sync_service._fetch_api_data_with_retry(FederalState.BW, 2025)
        
        # Should try max_retries + 1 times
        assert sync_service.api_client.get_school_holidays.call_count == sync_service.max_retries + 1
        assert mock_sleep.call_count == sync_service.max_retries
    
    def test_sync_federal_state_success(self, sync_service):
        """Test successful federal state synchronization"""
        # Mock diff with changes
        diff = HolidayDiff(
            new_holidays=[{"name": "New Holiday"}],
            updated_holidays=[],
            deleted_holidays=[],
            conflicts=[],
            statistics=DiffStatistics()
        )
        sync_service.diff_service.compare_holiday_data.return_value = diff
        sync_service.diff_service.apply_diff.return_value = {"applied": 1, "errors": 0, "skipped": 0}
        
        result = sync_service._sync_federal_state(FederalState.BW, [2025])
        
        assert result.federal_state == FederalState.BW
        assert result.status == SyncStatus.COMPLETED
        assert result.years_processed == [2025]
        assert result.total_changes == 1
        assert result.new_holidays == 1
        assert len(result.errors) == 0
    
    def test_sync_federal_state_with_api_error(self, sync_service):
        """Test federal state sync with API error"""
        # Mock API error
        sync_service.api_client.get_school_holidays.side_effect = Exception("API Error")
        
        result = sync_service._sync_federal_state(FederalState.BW, [2025])
        
        assert result.federal_state == FederalState.BW
        assert result.status == SyncStatus.FAILED
        assert len(result.errors) == 1
        assert result.errors[0].error_type == SyncErrorType.API_ERROR
        assert "API Error" in result.errors[0].message
    
    def test_sync_federal_state_partial_success(self, sync_service):
        """Test federal state sync with partial success"""
        # First year succeeds, second fails
        def api_side_effect(state, year):
            if year == 2025:
                return [{"name": "Holiday 2025"}]
            else:
                raise Exception("API Error for 2026")
        
        sync_service.api_client.get_school_holidays.side_effect = api_side_effect
        
        result = sync_service._sync_federal_state(FederalState.BW, [2025, 2026])
        
        assert result.status == SyncStatus.COMPLETED  # Partial success
        assert result.years_processed == [2025]
        assert len(result.errors) == 1
        assert result.errors[0].year == 2026
    
    def test_sync_all_states_success(self, sync_service):
        """Test successful synchronization of all states"""
        # Mock successful state sync
        with patch.object(sync_service, '_sync_federal_state') as mock_sync_state:
            mock_sync_state.return_value = StateSyncResult(
                federal_state=FederalState.BW,
                status=SyncStatus.COMPLETED,
                years_processed=[2025],
                total_changes=5
            )
            
            with patch.object(sync_service, '_create_rollback_point') as mock_rollback:
                mock_rollback.return_value = {"test": "rollback"}
                
                result = sync_service.sync_all_states(
                    federal_states=[FederalState.BW, FederalState.BY],
                    years=[2025]
                )
        
        assert result.status == SyncStatus.COMPLETED
        assert result.total_states == 2
        assert len(result.successful_states) == 2
        assert len(result.failed_states) == 0
        assert result.total_changes == 10  # 5 changes per state
        assert result.success_rate == 1.0
    
    def test_sync_all_states_with_failures(self, sync_service):
        """Test synchronization with some state failures"""
        def mock_sync_state(state, years, dry_run):
            if state == FederalState.BW:
                return StateSyncResult(
                    federal_state=state,
                    status=SyncStatus.COMPLETED,
                    total_changes=3
                )
            else:
                return StateSyncResult(
                    federal_state=state,
                    status=SyncStatus.FAILED,
                    errors=[SyncError(SyncErrorType.API_ERROR, state, message="API failed")]
                )
        
        with patch.object(sync_service, '_sync_federal_state', side_effect=mock_sync_state):
            with patch.object(sync_service, '_create_rollback_point') as mock_rollback:
                mock_rollback.return_value = {"test": "rollback"}
                
                with patch.object(sync_service, '_rollback_to_point') as mock_rollback_exec:
                    result = sync_service.sync_all_states(
                        federal_states=[FederalState.BW, FederalState.BY]
                    )
        
        assert result.status == SyncStatus.COMPLETED  # Partial success
        assert len(result.successful_states) == 1
        assert len(result.failed_states) == 1
        assert result.success_rate == 0.5
        assert len(result.errors) == 1
        
        # Verify rollback was called for failed state
        mock_rollback_exec.assert_called_once()
    
    def test_sync_all_states_critical_error(self, sync_service):
        """Test synchronization with critical system error"""
        # Mock critical error during state processing
        with patch.object(sync_service, '_validate_sync_prerequisites'):
            with patch.object(sync_service, '_sync_federal_state', side_effect=Exception("Critical Error")):
                with patch.object(sync_service, '_create_rollback_point') as mock_rollback:
                    mock_rollback.return_value = {"test": "rollback"}
                    
                    result = sync_service.sync_all_states(federal_states=[FederalState.BW])
        
        assert result.status == SyncStatus.FAILED
        assert len(result.failed_states) == 1
        assert len(result.successful_states) == 0
        assert len(result.errors) >= 1
        assert any("Critical Error" in error.message for error in result.errors)
    
    def test_sync_all_states_dry_run(self, sync_service):
        """Test dry run synchronization"""
        with patch.object(sync_service, '_sync_federal_state') as mock_sync_state:
            mock_sync_state.return_value = StateSyncResult(
                federal_state=FederalState.BW,
                status=SyncStatus.COMPLETED,
                total_changes=3
            )
            
            with patch.object(sync_service, '_create_rollback_point') as mock_rollback:
                mock_rollback.return_value = {"test": "rollback"}
                
                result = sync_service.sync_all_states(
                    federal_states=[FederalState.BW],
                    dry_run=True
                )
        
        # Verify dry_run was passed to state sync
        mock_sync_state.assert_called_once_with(FederalState.BW, sync_service.years_to_sync, True)
        assert result.status == SyncStatus.COMPLETED
    
    def test_get_sync_status_running(self, sync_service):
        """Test getting sync status while sync is running"""
        # Simulate running sync
        sync_service._current_sync = SyncResult(
            sync_id="test_sync",
            status=SyncStatus.RUNNING,
            started_at=datetime.now(),
            total_states=2
        )
        
        status = sync_service.get_sync_status()
        
        assert status is not None
        assert status["sync_id"] == "test_sync"
        assert status["status"] == "RUNNING"
        assert status["total_states"] == 2
    
    def test_get_sync_status_not_running(self, sync_service):
        """Test getting sync status when no sync is running"""
        status = sync_service.get_sync_status()
        assert status is None
    
    def test_factory_function(self):
        """Test the factory function"""
        with patch('app.services.school_holiday_sync_service.get_session') as mock_get_session:
            mock_session = Mock()
            # Fix: Return a generator that yields the session
            mock_get_session.return_value = (session for session in [mock_session])
            
            with patch('app.services.school_holiday_sync_service.get_school_holiday_api_client') as mock_api:
                with patch('app.services.school_holiday_sync_service.get_school_holiday_diff_service') as mock_diff:
                    service = get_school_holiday_sync_service()
                    
                    assert isinstance(service, SchoolHolidaySyncService)
                    assert service.conflict_strategy == ConflictResolutionStrategy.API_WINS
                    
                    # Test with custom parameters - create new mock for second call
                    mock_get_session.return_value = (session for session in [mock_session])
                    custom_years = [2024, 2025]
                    service = get_school_holiday_sync_service(
                        ConflictResolutionStrategy.LOCAL_WINS,
                        custom_years
                    )
                    assert service.conflict_strategy == ConflictResolutionStrategy.LOCAL_WINS
                    assert service.years_to_sync == custom_years


class TestSyncDataClasses:
    """Test the data classes used by the sync service"""
    
    def test_sync_error_to_dict(self):
        """Test SyncError serialization"""
        error = SyncError(
            error_type=SyncErrorType.API_ERROR,
            federal_state=FederalState.BW,
            year=2025,
            message="Test error",
            exception=ValueError("Test exception")
        )
        
        result = error.to_dict()
        
        assert result["error_type"] == "API_ERROR"
        assert result["federal_state"] == "Baden-Württemberg"
        assert result["year"] == 2025
        assert result["message"] == "Test error"
        assert result["exception_type"] == "ValueError"
        assert "timestamp" in result
    
    def test_state_sync_result_to_dict(self):
        """Test StateSyncResult serialization"""
        result = StateSyncResult(
            federal_state=FederalState.BW,
            status=SyncStatus.COMPLETED,
            years_processed=[2024, 2025],
            total_changes=10,
            new_holidays=5,
            updated_holidays=3,
            deleted_holidays=2,
            conflicts=1,
            execution_time=timedelta(seconds=30)
        )
        
        data = result.to_dict()
        
        assert data["federal_state"] == "Baden-Württemberg"
        assert data["status"] == "COMPLETED"
        assert data["years_processed"] == [2024, 2025]
        assert data["total_changes"] == 10
        assert data["new_holidays"] == 5
        assert data["updated_holidays"] == 3
        assert data["deleted_holidays"] == 2
        assert data["conflicts"] == 1
        assert data["execution_time_seconds"] == 30.0
    
    def test_sync_result_success_rate(self):
        """Test SyncResult success rate calculation"""
        # 100% success
        result = SyncResult(
            sync_id="test",
            status=SyncStatus.COMPLETED,
            started_at=datetime.now(),
            total_states=3,
            successful_states=["BW", "BY", "BE"]
        )
        assert result.success_rate == 1.0
        
        # 50% success
        result.successful_states = ["BW"]
        result.failed_states = ["BY", "BE"]
        assert result.success_rate == 1/3
        
        # 0% success
        result.successful_states = []
        result.failed_states = ["BW", "BY", "BE"]
        assert result.success_rate == 0.0
        
        # No states
        result.total_states = 0
        assert result.success_rate == 0.0
    
    def test_sync_result_to_dict(self):
        """Test SyncResult serialization"""
        started = datetime.now()
        completed = started + timedelta(minutes=5)
        
        result = SyncResult(
            sync_id="test_sync_123",
            status=SyncStatus.COMPLETED,
            started_at=started,
            completed_at=completed,
            total_states=2,
            successful_states=["Baden-Württemberg"],
            failed_states=["Bayern"],
            total_changes=15,
            total_conflicts=2,
            execution_time=timedelta(minutes=5)
        )
        
        data = result.to_dict()
        
        assert data["sync_id"] == "test_sync_123"
        assert data["status"] == "COMPLETED"
        assert data["started_at"] == started.isoformat()
        assert data["completed_at"] == completed.isoformat()
        assert data["total_states"] == 2
        assert data["successful_states"] == ["Baden-Württemberg"]
        assert data["failed_states"] == ["Bayern"]
        assert data["total_changes"] == 15
        assert data["total_conflicts"] == 2
        assert data["execution_time_seconds"] == 300.0
        assert data["success_rate"] == 0.5


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
