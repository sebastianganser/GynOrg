"""
Unit tests for SchoolHolidayDiffService

Tests cover:
- Data comparison logic
- Change detection (new, updated, deleted)
- Conflict resolution strategies
- Diff application
- Report generation
- Edge cases and error handling
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import date, datetime, timedelta
from sqlmodel import Session
from app.services.school_holiday_diff_service import (
    SchoolHolidayDiffService,
    ConflictResolutionStrategy,
    ChangeType,
    HolidayConflict,
    DiffStatistics,
    HolidayDiff,
    get_school_holiday_diff_service
)
from app.models.holiday import (
    Holiday, HolidayType, SchoolVacationType, DataSource
)
from app.models.federal_state import FederalState


class TestSchoolHolidayDiffService:
    """Test suite for SchoolHolidayDiffService"""
    
    @pytest.fixture
    def mock_session(self):
        """Create a mock database session"""
        session = Mock(spec=Session)
        session.exec.return_value.all.return_value = []
        return session
    
    @pytest.fixture
    def diff_service(self, mock_session):
        """Create a test diff service instance"""
        return SchoolHolidayDiffService(mock_session)
    
    @pytest.fixture
    def sample_local_holiday(self):
        """Create a sample local holiday"""
        return Holiday(
            id=1,
            name="Osterferien",
            date=date(2025, 4, 14),
            federal_state=FederalState.BW,
            federal_state_code="BW",
            holiday_type=HolidayType.SCHOOL_VACATION,
            school_vacation_type=SchoolVacationType.EASTER,
            data_source=DataSource.MEHR_SCHULFERIEN_API,
            api_id="4673",
            year=2025,
            notes="Easter holidays",
            is_nationwide=False,
            last_updated=datetime(2025, 1, 1, 12, 0, 0),
            created_at=datetime(2025, 1, 1, 12, 0, 0)
        )
    
    @pytest.fixture
    def sample_api_data(self):
        """Create sample API data"""
        return [
            {
                "name": "Osterferien",
                "start_date": date(2025, 4, 14),
                "end_date": date(2025, 4, 25),
                "school_vacation_type": SchoolVacationType.EASTER,
                "api_id": "4673",
                "notes": "Easter holidays"
            },
            {
                "name": "Sommerferien",
                "start_date": date(2025, 7, 31),
                "end_date": date(2025, 9, 13),
                "school_vacation_type": SchoolVacationType.SUMMER,
                "api_id": "4674",
                "notes": "Summer holidays"
            }
        ]
    
    def test_service_initialization(self, mock_session):
        """Test service initialization with different strategies"""
        # Default strategy
        service = SchoolHolidayDiffService(mock_session)
        assert service.default_conflict_strategy == ConflictResolutionStrategy.API_WINS
        assert service.session == mock_session
        
        # Custom strategy
        service = SchoolHolidayDiffService(mock_session, ConflictResolutionStrategy.LOCAL_WINS)
        assert service.default_conflict_strategy == ConflictResolutionStrategy.LOCAL_WINS
    
    def test_generate_holiday_key(self, diff_service):
        """Test holiday key generation"""
        # With date object
        key1 = diff_service._generate_holiday_key("4673", "BW", date(2025, 4, 14))
        assert key1 == "4673_BW_2025-04-14"
        
        # With string date
        key2 = diff_service._generate_holiday_key("4674", "BY", "2025-07-31")
        assert key2 == "4674_BY_2025-07-31"
        
        # With other type
        key3 = diff_service._generate_holiday_key("4675", "BE", 12345)
        assert key3 == "4675_BE_12345"
    
    def test_build_api_index(self, diff_service, sample_api_data):
        """Test API data indexing"""
        index = diff_service._build_api_index(sample_api_data, FederalState.BW)
        
        assert len(index) == 2
        assert "4673_BW_2025-04-14" in index
        assert "4674_BW_2025-07-31" in index
        assert index["4673_BW_2025-04-14"]["name"] == "Osterferien"
    
    def test_build_local_index(self, diff_service, sample_local_holiday):
        """Test local data indexing"""
        holidays = [sample_local_holiday]
        index = diff_service._build_local_index(holidays)
        
        assert len(index) == 1
        assert "4673_BW_2025-04-14" in index
        assert index["4673_BW_2025-04-14"].name == "Osterferien"
    
    def test_detect_new_holidays(self, diff_service, sample_api_data):
        """Test detection of new holidays"""
        api_index = diff_service._build_api_index(sample_api_data, FederalState.BW)
        local_index = {}  # Empty local index
        
        new_holidays = diff_service._detect_new_holidays(api_index, local_index, FederalState.BW, 2025)
        
        assert len(new_holidays) == 2
        assert new_holidays[0]["name"] == "Osterferien"
        assert new_holidays[0]["federal_state"] == FederalState.BW
        assert new_holidays[0]["holiday_type"] == HolidayType.SCHOOL_VACATION
        assert new_holidays[0]["data_source"] == DataSource.MEHR_SCHULFERIEN_API
    
    def test_detect_field_changes(self, diff_service, sample_local_holiday):
        """Test field change detection"""
        # No changes
        api_data = {
            "name": "Osterferien",
            "start_date": date(2025, 4, 14),
            "school_vacation_type": SchoolVacationType.EASTER,
            "notes": "Easter holidays"
        }
        changes = diff_service._detect_field_changes(sample_local_holiday, api_data)
        assert len(changes) == 0
        
        # Name change
        api_data["name"] = "Osterferien 2025"
        changes = diff_service._detect_field_changes(sample_local_holiday, api_data)
        assert "name" in changes
        assert changes["name"] == "Osterferien 2025"
        
        # Date change
        api_data["start_date"] = date(2025, 4, 15)
        changes = diff_service._detect_field_changes(sample_local_holiday, api_data)
        assert "date" in changes
        assert changes["date"] == date(2025, 4, 15)
        
        # Vacation type change
        api_data["school_vacation_type"] = SchoolVacationType.SUMMER
        changes = diff_service._detect_field_changes(sample_local_holiday, api_data)
        assert "school_vacation_type" in changes
        assert changes["school_vacation_type"] == SchoolVacationType.SUMMER
    
    def test_has_manual_changes(self, diff_service, sample_local_holiday):
        """Test manual change detection"""
        # API source, no manual changes
        assert not diff_service._has_manual_changes(sample_local_holiday)
        
        # Manual source
        sample_local_holiday.data_source = DataSource.MANUAL
        assert diff_service._has_manual_changes(sample_local_holiday)
        
        # Recent update (within 24h)
        sample_local_holiday.data_source = DataSource.MEHR_SCHULFERIEN_API
        sample_local_holiday.updated_at = datetime.now() - timedelta(hours=12)
        assert diff_service._has_manual_changes(sample_local_holiday)
        
        # Old update (more than 24h)
        sample_local_holiday.updated_at = datetime.now() - timedelta(days=2)
        assert not diff_service._has_manual_changes(sample_local_holiday)
    
    def test_detect_updated_holidays_no_conflicts(self, diff_service, sample_local_holiday):
        """Test update detection without conflicts"""
        # Setup indices
        api_data = {
            "name": "Osterferien 2025",  # Changed name
            "start_date": date(2025, 4, 14),
            "school_vacation_type": SchoolVacationType.EASTER,
            "api_id": "4673",
            "notes": "Easter holidays"
        }
        api_index = {"4673_BW_2025-04-14": api_data}
        local_index = {"4673_BW_2025-04-14": sample_local_holiday}
        
        updated_holidays, conflicts = diff_service._detect_updated_holidays(
            api_index, local_index, ConflictResolutionStrategy.API_WINS
        )
        
        assert len(updated_holidays) == 1
        assert len(conflicts) == 0
        assert updated_holidays[0][0] == sample_local_holiday
        assert "name" in updated_holidays[0][1]
        assert updated_holidays[0][1]["name"] == "Osterferien 2025"
    
    def test_detect_updated_holidays_with_conflicts(self, diff_service, sample_local_holiday):
        """Test update detection with conflicts"""
        # Make holiday appear manually changed
        sample_local_holiday.data_source = DataSource.MANUAL
        
        api_data = {
            "name": "Osterferien 2025",  # Changed name
            "start_date": date(2025, 4, 14),
            "school_vacation_type": SchoolVacationType.EASTER,
            "api_id": "4673",
            "notes": "Easter holidays"
        }
        api_index = {"4673_BW_2025-04-14": api_data}
        local_index = {"4673_BW_2025-04-14": sample_local_holiday}
        
        updated_holidays, conflicts = diff_service._detect_updated_holidays(
            api_index, local_index, ConflictResolutionStrategy.API_WINS
        )
        
        assert len(updated_holidays) == 0
        assert len(conflicts) == 1
        assert conflicts[0].local_holiday == sample_local_holiday
        assert conflicts[0].conflict_type == "MANUAL_VS_API"
        assert "name" in conflicts[0].conflict_fields
    
    def test_detect_deleted_holidays(self, diff_service, sample_local_holiday):
        """Test deletion detection"""
        api_index = {}  # Empty API index
        local_index = {"4673_BW_2025-04-14": sample_local_holiday}
        
        deleted_holidays = diff_service._detect_deleted_holidays(api_index, local_index)
        
        assert len(deleted_holidays) == 1
        assert deleted_holidays[0] == sample_local_holiday
        
        # Test with manual holiday (should not be deleted)
        sample_local_holiday.data_source = DataSource.MANUAL
        deleted_holidays = diff_service._detect_deleted_holidays(api_index, local_index)
        assert len(deleted_holidays) == 0
    
    def test_transform_api_to_create_schema(self, diff_service):
        """Test API data transformation"""
        api_data = {
            "name": "Sommerferien",
            "start_date": "2025-07-31",
            "school_vacation_type": SchoolVacationType.SUMMER,
            "api_id": "4674",
            "notes": "Summer holidays"
        }
        
        result = diff_service._transform_api_to_create_schema(api_data, FederalState.BW, 2025)
        
        assert result is not None
        assert result["name"] == "Sommerferien"
        assert result["date"] == date(2025, 7, 31)
        assert result["federal_state"] == FederalState.BW
        assert result["federal_state_code"] == "BW"
        assert result["holiday_type"] == HolidayType.SCHOOL_VACATION
        assert result["school_vacation_type"] == SchoolVacationType.SUMMER
        assert result["data_source"] == DataSource.MEHR_SCHULFERIEN_API
        assert result["api_id"] == "4674"
        assert result["year"] == 2025
        assert result["is_nationwide"] is False
    
    def test_transform_api_invalid_data(self, diff_service):
        """Test transformation with invalid data"""
        # Missing required fields
        api_data = {"name": "Test"}
        result = diff_service._transform_api_to_create_schema(api_data, FederalState.BW, 2025)
        assert result is None
        
        # Invalid date format
        api_data = {
            "name": "Test",
            "start_date": "invalid-date",
            "school_vacation_type": SchoolVacationType.SUMMER,
            "api_id": "123"
        }
        result = diff_service._transform_api_to_create_schema(api_data, FederalState.BW, 2025)
        assert result is None
    
    @patch('app.services.school_holiday_diff_service.logger')
    def test_compare_holiday_data_full_workflow(self, mock_logger, diff_service, sample_api_data):
        """Test complete comparison workflow"""
        # Mock local holidays query
        diff_service.session.exec.return_value.all.return_value = []
        
        result = diff_service.compare_holiday_data(sample_api_data, FederalState.BW, 2025)
        
        assert isinstance(result, HolidayDiff)
        assert len(result.new_holidays) == 2
        assert len(result.updated_holidays) == 0
        assert len(result.deleted_holidays) == 0
        assert len(result.conflicts) == 0
        assert result.has_changes()
        assert not result.has_conflicts()
        
        # Check statistics
        assert result.statistics.total_api_records == 2
        assert result.statistics.total_local_records == 0
        assert result.statistics.new_records == 2
        assert result.statistics.federal_state == FederalState.BW
        assert result.statistics.year == 2025
        assert result.statistics.processing_time_ms >= 0
    
    def test_apply_diff_new_holidays(self, diff_service):
        """Test applying diff with new holidays"""
        # Create diff with new holidays
        new_holiday_data = {
            "name": "Sommerferien",
            "date": date(2025, 7, 31),
            "federal_state": FederalState.BW,
            "federal_state_code": "BW",
            "holiday_type": HolidayType.SCHOOL_VACATION,
            "school_vacation_type": SchoolVacationType.SUMMER,
            "data_source": DataSource.MEHR_SCHULFERIEN_API,
            "api_id": "4674",
            "year": 2025,
            "notes": "Summer holidays",
            "is_nationwide": False,
            "last_updated": datetime.now()
        }
        
        diff = HolidayDiff(
            new_holidays=[new_holiday_data],
            updated_holidays=[],
            deleted_holidays=[],
            conflicts=[],
            statistics=DiffStatistics()
        )
        
        result = diff_service.apply_diff(diff, dry_run=True)
        
        assert result["applied"] == 1
        assert result["errors"] == 0
        assert result["skipped"] == 0
        assert "Added: Sommerferien" in result["details"]
        
        # Verify session operations
        diff_service.session.add.assert_called_once()
        diff_service.session.rollback.assert_called_once()  # dry_run=True
    
    def test_apply_diff_updated_holidays(self, diff_service, sample_local_holiday):
        """Test applying diff with updated holidays"""
        changes = {"name": "Osterferien 2025", "notes": "Updated notes"}
        
        diff = HolidayDiff(
            new_holidays=[],
            updated_holidays=[(sample_local_holiday, changes)],
            deleted_holidays=[],
            conflicts=[],
            statistics=DiffStatistics()
        )
        
        result = diff_service.apply_diff(diff, dry_run=False)
        
        assert result["applied"] == 1
        assert result["errors"] == 0
        assert sample_local_holiday.name == "Osterferien 2025"
        assert sample_local_holiday.notes == "Updated notes"
        assert sample_local_holiday.updated_at is not None
        
        diff_service.session.commit.assert_called_once()
    
    def test_apply_diff_deleted_holidays(self, diff_service, sample_local_holiday):
        """Test applying diff with deleted holidays"""
        diff = HolidayDiff(
            new_holidays=[],
            updated_holidays=[],
            deleted_holidays=[sample_local_holiday],
            conflicts=[],
            statistics=DiffStatistics()
        )
        
        result = diff_service.apply_diff(diff, dry_run=False)
        
        assert result["applied"] == 1
        assert result["errors"] == 0
        assert "Deleted: Osterferien" in result["details"]
        
        diff_service.session.delete.assert_called_once_with(sample_local_holiday)
        diff_service.session.commit.assert_called_once()
    
    def test_apply_diff_no_changes(self, diff_service):
        """Test applying diff with no changes"""
        diff = HolidayDiff(
            new_holidays=[],
            updated_holidays=[],
            deleted_holidays=[],
            conflicts=[],
            statistics=DiffStatistics()
        )
        
        result = diff_service.apply_diff(diff)
        
        assert result["applied"] == 0
        assert result["errors"] == 0
        assert result["skipped"] == 0
    
    def test_resolve_conflicts_api_wins(self, diff_service, sample_local_holiday):
        """Test conflict resolution with API_WINS strategy"""
        api_data = {
            "name": "Osterferien 2025",
            "start_date": date(2025, 4, 14),
            "school_vacation_type": SchoolVacationType.EASTER,
            "notes": "Updated from API"
        }
        
        conflict = HolidayConflict(
            local_holiday=sample_local_holiday,
            api_data=api_data,
            conflict_fields=["name", "notes"],
            conflict_type="MANUAL_VS_API",
            resolution_strategy=ConflictResolutionStrategy.API_WINS,
            created_at=datetime.now()
        )
        
        resolved = diff_service.resolve_conflicts([conflict], ConflictResolutionStrategy.API_WINS)
        
        assert len(resolved) == 1
        assert resolved[0][0] == sample_local_holiday
        assert "name" in resolved[0][1]
        assert resolved[0][1]["name"] == "Osterferien 2025"
    
    def test_resolve_conflicts_local_wins(self, diff_service, sample_local_holiday):
        """Test conflict resolution with LOCAL_WINS strategy"""
        api_data = {"name": "Osterferien 2025"}
        
        conflict = HolidayConflict(
            local_holiday=sample_local_holiday,
            api_data=api_data,
            conflict_fields=["name"],
            conflict_type="MANUAL_VS_API",
            resolution_strategy=ConflictResolutionStrategy.LOCAL_WINS,
            created_at=datetime.now()
        )
        
        resolved = diff_service.resolve_conflicts([conflict], ConflictResolutionStrategy.LOCAL_WINS)
        
        assert len(resolved) == 0  # No changes applied
    
    def test_resolve_conflicts_timestamp_based(self, diff_service, sample_local_holiday):
        """Test conflict resolution with TIMESTAMP_BASED strategy"""
        # Set old timestamp on local holiday
        sample_local_holiday.last_updated = datetime.now() - timedelta(days=1)
        
        api_data = {"name": "Osterferien 2025"}
        
        conflict = HolidayConflict(
            local_holiday=sample_local_holiday,
            api_data=api_data,
            conflict_fields=["name"],
            conflict_type="MANUAL_VS_API",
            resolution_strategy=ConflictResolutionStrategy.TIMESTAMP_BASED,
            created_at=datetime.now()
        )
        
        resolved = diff_service.resolve_conflicts([conflict], ConflictResolutionStrategy.TIMESTAMP_BASED)
        
        assert len(resolved) == 1  # API is newer, so changes applied
    
    def test_generate_diff_report(self, diff_service, sample_local_holiday):
        """Test diff report generation"""
        new_holiday_data = {
            "name": "Sommerferien",
            "date": date(2025, 7, 31),
            "school_vacation_type": SchoolVacationType.SUMMER,
            "api_id": "4674"
        }
        
        changes = {"name": "Updated name"}
        
        conflict = HolidayConflict(
            local_holiday=sample_local_holiday,
            api_data={"name": "Conflict name"},
            conflict_fields=["name"],
            conflict_type="MANUAL_VS_API",
            resolution_strategy=ConflictResolutionStrategy.API_WINS,
            created_at=datetime.now()
        )
        
        statistics = DiffStatistics(
            total_api_records=3,
            total_local_records=2,
            new_records=1,
            updated_records=1,
            deleted_records=0,
            conflicts=1,
            processing_time_ms=150,
            federal_state=FederalState.BW,
            year=2025
        )
        
        diff = HolidayDiff(
            new_holidays=[new_holiday_data],
            updated_holidays=[(sample_local_holiday, changes)],
            deleted_holidays=[],
            conflicts=[conflict],
            statistics=statistics
        )
        
        report = diff_service.generate_diff_report(diff)
        
        # Check summary
        assert report["summary"]["total_changes"] == 2
        assert report["summary"]["new_holidays"] == 1
        assert report["summary"]["updated_holidays"] == 1
        assert report["summary"]["deleted_holidays"] == 0
        assert report["summary"]["conflicts"] == 1
        assert report["summary"]["has_changes"] is True
        assert report["summary"]["has_conflicts"] is True
        
        # Check statistics
        assert report["statistics"]["total_api_records"] == 3
        assert report["statistics"]["total_local_records"] == 2
        assert report["statistics"]["processing_time_ms"] == 150
        assert report["statistics"]["federal_state"] == "Baden-Württemberg"
        assert report["statistics"]["year"] == 2025
        
        # Check details
        assert len(report["details"]["new_holidays"]) == 1
        assert report["details"]["new_holidays"][0]["name"] == "Sommerferien"
        
        assert len(report["details"]["updated_holidays"]) == 1
        assert report["details"]["updated_holidays"][0]["name"] == "Osterferien"
        
        assert len(report["details"]["conflicts"]) == 1
        assert report["details"]["conflicts"][0]["holiday_name"] == "Osterferien"
        
        assert "generated_at" in report
    
    def test_factory_function(self):
        """Test the factory function"""
        with patch('app.services.school_holiday_diff_service.get_session') as mock_get_session:
            mock_session = Mock()
            mock_get_session.return_value = iter([mock_session])  # Make it an iterator
            
            service = get_school_holiday_diff_service()
            
            assert isinstance(service, SchoolHolidayDiffService)
            assert service.default_conflict_strategy == ConflictResolutionStrategy.API_WINS
            
            # Test with custom strategy
            mock_get_session.return_value = iter([mock_session])  # Reset iterator
            service = get_school_holiday_diff_service(ConflictResolutionStrategy.LOCAL_WINS)
            assert service.default_conflict_strategy == ConflictResolutionStrategy.LOCAL_WINS


class TestHolidayDiffDataClasses:
    """Test the data classes used by the diff service"""
    
    def test_holiday_diff_has_changes(self):
        """Test HolidayDiff.has_changes() method"""
        # No changes
        diff = HolidayDiff([], [], [], [], DiffStatistics())
        assert not diff.has_changes()
        
        # With new holidays
        diff = HolidayDiff([{"name": "test"}], [], [], [], DiffStatistics())
        assert diff.has_changes()
        
        # With updated holidays
        diff = HolidayDiff([], [("holiday", {"name": "test"})], [], [], DiffStatistics())
        assert diff.has_changes()
        
        # With deleted holidays
        mock_holiday = Mock()
        diff = HolidayDiff([], [], [mock_holiday], [], DiffStatistics())
        assert diff.has_changes()
    
    def test_holiday_diff_has_conflicts(self):
        """Test HolidayDiff.has_conflicts() method"""
        # No conflicts
        diff = HolidayDiff([], [], [], [], DiffStatistics())
        assert not diff.has_conflicts()
        
        # With conflicts
        mock_conflict = Mock()
        diff = HolidayDiff([], [], [], [mock_conflict], DiffStatistics())
        assert diff.has_conflicts()


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
