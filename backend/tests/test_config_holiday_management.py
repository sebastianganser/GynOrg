"""
Unit tests for Holiday Management configuration settings.
"""
import pytest
from datetime import datetime
from app.core.config import settings


class TestHolidayManagementConfig:
    """Test suite for Holiday Management configuration."""
    
    def test_holiday_config_defaults(self):
        """Test that default holiday configuration values are set correctly."""
        assert settings.HOLIDAY_YEARS_PAST == 2
        assert settings.HOLIDAY_YEARS_FUTURE == 3
        assert settings.HOLIDAY_AUTO_IMPORT_ON_STARTUP is True
        assert settings.HOLIDAY_SCHEDULER_ENABLED is True
        assert settings.HOLIDAY_SCHEDULER_CRON == "0 2 1 * *"
        assert settings.HOLIDAY_CLEANUP_OLD_YEARS is False
        assert settings.HOLIDAY_CLEANUP_YEARS_THRESHOLD == 5
    
    def test_get_holiday_year_range(self):
        """Test holiday year range calculation."""
        start_year, end_year = settings.get_holiday_year_range()
        current_year = datetime.now().year
        
        # Verify correct calculation
        assert start_year == current_year - settings.HOLIDAY_YEARS_PAST
        assert end_year == current_year + settings.HOLIDAY_YEARS_FUTURE
        
        # Verify range span
        expected_span = settings.HOLIDAY_YEARS_PAST + settings.HOLIDAY_YEARS_FUTURE
        assert end_year - start_year == expected_span
    
    def test_get_holiday_year_range_with_defaults(self):
        """Test year range with default configuration (2 past, 3 future)."""
        start_year, end_year = settings.get_holiday_year_range()
        current_year = datetime.now().year
        
        # With defaults: 2 years past, 3 years future = 6 years total
        assert start_year == current_year - 2
        assert end_year == current_year + 3
        assert end_year - start_year == 5  # 6 years total (inclusive)
    
    def test_holiday_year_range_returns_tuple(self):
        """Test that get_holiday_year_range returns a tuple."""
        result = settings.get_holiday_year_range()
        assert isinstance(result, tuple)
        assert len(result) == 2
        assert isinstance(result[0], int)
        assert isinstance(result[1], int)
    
    def test_holiday_year_range_start_before_end(self):
        """Test that start year is always before end year."""
        start_year, end_year = settings.get_holiday_year_range()
        assert start_year < end_year
    
    def test_holiday_scheduler_cron_format(self):
        """Test that scheduler cron expression is in valid format."""
        cron = settings.HOLIDAY_SCHEDULER_CRON
        
        # Basic validation: should have 5 parts (minute hour day month weekday)
        parts = cron.split()
        assert len(parts) == 5
        
        # Default should be "0 2 1 * *" (1st day of month at 2:00 AM)
        assert parts[0] == "0"  # minute
        assert parts[1] == "2"  # hour
        assert parts[2] == "1"  # day of month
        assert parts[3] == "*"  # month
        assert parts[4] == "*"  # day of week
    
    def test_holiday_config_types(self):
        """Test that configuration values have correct types."""
        assert isinstance(settings.HOLIDAY_YEARS_PAST, int)
        assert isinstance(settings.HOLIDAY_YEARS_FUTURE, int)
        assert isinstance(settings.HOLIDAY_AUTO_IMPORT_ON_STARTUP, bool)
        assert isinstance(settings.HOLIDAY_SCHEDULER_ENABLED, bool)
        assert isinstance(settings.HOLIDAY_SCHEDULER_CRON, str)
        assert isinstance(settings.HOLIDAY_CLEANUP_OLD_YEARS, bool)
        assert isinstance(settings.HOLIDAY_CLEANUP_YEARS_THRESHOLD, int)
    
    def test_holiday_years_positive_values(self):
        """Test that year configuration values are positive."""
        assert settings.HOLIDAY_YEARS_PAST >= 0
        assert settings.HOLIDAY_YEARS_FUTURE >= 0
        assert settings.HOLIDAY_CLEANUP_YEARS_THRESHOLD >= 0
    
    def test_holiday_year_range_example_2025(self):
        """Test year range calculation for year 2025 scenario."""
        # This test documents the expected behavior
        # If current year is 2025, with defaults (2 past, 3 future):
        # Expected range: 2023-2028 (6 years total)
        
        current_year = datetime.now().year
        start_year, end_year = settings.get_holiday_year_range()
        
        # Calculate expected values
        expected_start = current_year - 2
        expected_end = current_year + 3
        
        assert start_year == expected_start
        assert end_year == expected_end
        
        # Verify we get 6 years of coverage
        years_covered = end_year - start_year + 1
        assert years_covered == 6


class TestHolidayConfigIntegration:
    """Integration tests for Holiday Management configuration."""
    
    def test_config_accessible_from_settings(self):
        """Test that holiday config is accessible from global settings."""
        from app.core.config import settings as global_settings
        
        # Verify all holiday settings are accessible
        assert hasattr(global_settings, 'HOLIDAY_YEARS_PAST')
        assert hasattr(global_settings, 'HOLIDAY_YEARS_FUTURE')
        assert hasattr(global_settings, 'HOLIDAY_AUTO_IMPORT_ON_STARTUP')
        assert hasattr(global_settings, 'HOLIDAY_SCHEDULER_ENABLED')
        assert hasattr(global_settings, 'HOLIDAY_SCHEDULER_CRON')
        assert hasattr(global_settings, 'get_holiday_year_range')
    
    def test_config_method_callable(self):
        """Test that get_holiday_year_range method is callable."""
        assert callable(settings.get_holiday_year_range)
        
        # Should not raise exception
        result = settings.get_holiday_year_range()
        assert result is not None
