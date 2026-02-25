"""
Unit tests for Holiday Startup Service
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from sqlmodel import Session

from app.services.holiday_startup_service import HolidayStartupService, ensure_holiday_data_on_startup
from app.models.federal_state import FederalState


class TestHolidayStartupService:
    """Test suite for HolidayStartupService"""
    
    @pytest.fixture
    def mock_session(self):
        """Create a mock database session"""
        return Mock(spec=Session)
    
    @pytest.fixture
    def mock_holiday_service(self):
        """Create a mock HolidayService"""
        return Mock()
    
    @pytest.fixture
    def startup_service(self, mock_session, mock_holiday_service):
        """Create HolidayStartupService with mocked dependencies"""
        service = HolidayStartupService(mock_session)
        service.holiday_service = mock_holiday_service
        return service
    
    def test_ensure_holiday_data_auto_import_disabled(self, startup_service):
        """Test that auto-import is skipped when disabled in config"""
        with patch('app.services.holiday_startup_service.settings') as mock_settings:
            mock_settings.HOLIDAY_AUTO_IMPORT_ON_STARTUP = False
            
            result = startup_service.ensure_holiday_data()
            
            assert result["auto_import_enabled"] is False
            assert result["action"] == "skipped"
            assert "disabled" in result["message"].lower()
    
    def test_ensure_holiday_data_no_missing_years(self, startup_service, mock_holiday_service):
        """Test when all years are already present"""
        with patch('app.services.holiday_startup_service.settings') as mock_settings:
            mock_settings.HOLIDAY_AUTO_IMPORT_ON_STARTUP = True
            mock_settings.get_holiday_year_range.return_value = (2023, 2028)
            
            # Mock: No missing years
            mock_holiday_service.get_missing_years.return_value = []
            
            result = startup_service.ensure_holiday_data()
            
            assert result["auto_import_enabled"] is True
            assert result["action"] == "none_needed"
            assert result["missing_years"] == []
            assert result["year_range"] == {"start": 2023, "end": 2028}
            assert "already present" in result["message"].lower()
            
            # Verify get_missing_years was called correctly
            mock_holiday_service.get_missing_years.assert_called_once_with(
                2023, 2028, list(FederalState)
            )
            
            # Verify import was NOT called
            mock_holiday_service.import_missing_years.assert_not_called()
    
    def test_ensure_holiday_data_with_missing_years(self, startup_service, mock_holiday_service):
        """Test successful import of missing years"""
        with patch('app.services.holiday_startup_service.settings') as mock_settings:
            mock_settings.HOLIDAY_AUTO_IMPORT_ON_STARTUP = True
            mock_settings.get_holiday_year_range.return_value = (2023, 2028)
            
            # Mock: Missing years 2023, 2024
            mock_holiday_service.get_missing_years.return_value = [2023, 2024]
            
            # Mock: Successful import
            mock_holiday_service.import_missing_years.return_value = {
                "total_imported": 150,
                "total_skipped": 5,
                "total_errors": 0,
                "years_processed": 2
            }
            
            result = startup_service.ensure_holiday_data()
            
            assert result["auto_import_enabled"] is True
            assert result["action"] == "imported"
            assert result["missing_years"] == [2023, 2024]
            assert result["year_range"] == {"start": 2023, "end": 2028}
            assert result["import_result"]["total_imported"] == 150
            assert "successfully" in result["message"].lower()
            
            # Verify import was called correctly
            mock_holiday_service.import_missing_years.assert_called_once_with(
                [2023, 2024], list(FederalState)
            )
    
    def test_ensure_holiday_data_import_error(self, startup_service, mock_holiday_service):
        """Test error handling during import"""
        with patch('app.services.holiday_startup_service.settings') as mock_settings:
            mock_settings.HOLIDAY_AUTO_IMPORT_ON_STARTUP = True
            mock_settings.get_holiday_year_range.return_value = (2023, 2028)
            
            # Mock: Missing years
            mock_holiday_service.get_missing_years.return_value = [2023]
            
            # Mock: Import raises exception
            mock_holiday_service.import_missing_years.side_effect = Exception("Database error")
            
            result = startup_service.ensure_holiday_data()
            
            assert result["auto_import_enabled"] is True
            assert result["action"] == "error"
            assert "error" in result
            assert "Database error" in result["error"]
            assert "failed" in result["message"].lower()
    
    def test_ensure_holiday_data_year_range_calculation(self, startup_service, mock_holiday_service):
        """Test that year range is correctly calculated from config"""
        with patch('app.services.holiday_startup_service.settings') as mock_settings:
            mock_settings.HOLIDAY_AUTO_IMPORT_ON_STARTUP = True
            # Simulate current year 2025, PAST=2, FUTURE=3 -> 2023-2028
            mock_settings.get_holiday_year_range.return_value = (2023, 2028)
            mock_holiday_service.get_missing_years.return_value = []
            
            result = startup_service.ensure_holiday_data()
            
            # Verify correct year range was used
            mock_settings.get_holiday_year_range.assert_called_once()
            mock_holiday_service.get_missing_years.assert_called_once_with(
                2023, 2028, list(FederalState)
            )
    
    def test_ensure_holiday_data_all_federal_states(self, startup_service, mock_holiday_service):
        """Test that all federal states are included in import"""
        with patch('app.services.holiday_startup_service.settings') as mock_settings:
            mock_settings.HOLIDAY_AUTO_IMPORT_ON_STARTUP = True
            mock_settings.get_holiday_year_range.return_value = (2023, 2028)
            mock_holiday_service.get_missing_years.return_value = [2023]
            mock_holiday_service.import_missing_years.return_value = {
                "total_imported": 50,
                "total_skipped": 0,
                "total_errors": 0,
                "years_processed": 1
            }
            
            startup_service.ensure_holiday_data()
            
            # Verify all 16 federal states are included
            call_args = mock_holiday_service.import_missing_years.call_args
            federal_states_arg = call_args[0][1]
            assert len(federal_states_arg) == 16
            assert all(isinstance(state, FederalState) for state in federal_states_arg)


class TestEnsureHolidayDataOnStartup:
    """Test suite for async wrapper function"""
    
    @pytest.mark.asyncio
    async def test_ensure_holiday_data_on_startup_success(self):
        """Test successful async wrapper execution"""
        with patch('app.services.holiday_startup_service.get_session') as mock_get_session, \
             patch('app.services.holiday_startup_service.HolidayStartupService') as mock_service_class:
            
            # Mock session
            mock_session = Mock()
            mock_get_session.return_value = iter([mock_session])
            
            # Mock service
            mock_service = Mock()
            mock_service.ensure_holiday_data.return_value = {
                "auto_import_enabled": True,
                "action": "imported",
                "message": "Success"
            }
            mock_service_class.return_value = mock_service
            
            result = await ensure_holiday_data_on_startup()
            
            assert result["action"] == "imported"
            assert result["message"] == "Success"
            
            # Verify session was closed
            mock_session.close.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_ensure_holiday_data_on_startup_critical_error(self):
        """Test critical error handling in async wrapper"""
        with patch('app.services.holiday_startup_service.get_session') as mock_get_session:
            # Mock session that raises exception
            mock_get_session.side_effect = Exception("Critical database error")
            
            result = await ensure_holiday_data_on_startup()
            
            assert result["action"] == "critical_error"
            assert "error" in result
            assert "Critical database error" in result["error"]


class TestHolidayStartupServiceIntegration:
    """Integration tests for HolidayStartupService"""
    
    @pytest.fixture
    def mock_session(self):
        """Create a mock database session"""
        return Mock(spec=Session)
    
    def test_service_initialization(self, mock_session):
        """Test that service initializes correctly"""
        service = HolidayStartupService(mock_session)
        
        assert service.session == mock_session
        assert service.holiday_service is not None
        assert hasattr(service, 'ensure_holiday_data')
    
    def test_ensure_holiday_data_returns_dict(self, mock_session):
        """Test that ensure_holiday_data always returns a dict"""
        service = HolidayStartupService(mock_session)
        
        with patch('app.services.holiday_startup_service.settings') as mock_settings:
            mock_settings.HOLIDAY_AUTO_IMPORT_ON_STARTUP = False
            
            result = service.ensure_holiday_data()
            
            assert isinstance(result, dict)
            assert "auto_import_enabled" in result
            assert "action" in result
            assert "message" in result
    
    def test_ensure_holiday_data_required_keys(self, mock_session):
        """Test that result contains all required keys"""
        service = HolidayStartupService(mock_session)
        
        with patch('app.services.holiday_startup_service.settings') as mock_settings:
            mock_settings.HOLIDAY_AUTO_IMPORT_ON_STARTUP = True
            mock_settings.get_holiday_year_range.return_value = (2023, 2028)
            
            with patch.object(service.holiday_service, 'get_missing_years', return_value=[]):
                result = service.ensure_holiday_data()
                
                # Required keys for all responses
                assert "auto_import_enabled" in result
                assert "action" in result
                assert "message" in result
                
                # Additional keys for successful check
                assert "year_range" in result
                assert "missing_years" in result
