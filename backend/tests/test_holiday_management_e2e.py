"""
End-to-End Functional Tests for Multi-Year Holiday Management System

This test suite validates the complete holiday management system including:
- Automatic startup import (HolidayStartupService)
- Scheduler operation (HolidayScheduler)
- Error handling and graceful degradation
- Integration of all components
"""
import pytest
from datetime import datetime, date
from sqlmodel import Session, select
from unittest.mock import Mock, patch, MagicMock

from app.core.database import get_session
from app.models.holiday import Holiday, DataSource
from app.models.federal_state import FederalState
from app.services.holiday_startup_service import HolidayStartupService
from app.services.holiday_scheduler import HolidayScheduler, SchedulerStatus
from app.core.config import get_settings


class TestStartupImport:
    """Test automatic holiday import on startup"""
    
    def test_startup_import_creates_holidays(self, db_session: Session):
        """Test that startup service imports holidays on first run"""
        # Clear existing holidays
        db_session.query(Holiday).delete()
        db_session.commit()
        
        # Run startup service
        startup_service = HolidayStartupService(db_session)
        result = startup_service.ensure_holiday_data()
        
        # Verify import occurred
        assert result['action'] in ['imported', 'up_to_date']
        
        # Verify holidays exist in database
        holidays = db_session.exec(
            select(Holiday).where(Holiday.data_source == DataSource.FEIERTAGE_API)
        ).all()
        
        assert len(holidays) > 0, "No holidays were imported"
        
        # Verify multi-year coverage
        years = set(h.date.year for h in holidays)
        settings = get_settings()
        current_year = datetime.now().year
        
        expected_years = range(
            current_year - settings.HOLIDAY_YEARS_PAST,
            current_year + settings.HOLIDAY_YEARS_FUTURE + 1
        )
        
        for year in expected_years:
            assert year in years, f"Missing holidays for year {year}"
    
    def test_startup_import_idempotent(self, db_session: Session):
        """Test that running startup service multiple times doesn't duplicate data"""
        # First run
        startup_service = HolidayStartupService(db_session)
        result1 = startup_service.ensure_holiday_data()
        
        count1 = db_session.query(Holiday).filter(
            Holiday.data_source == DataSource.FEIERTAGE_API
        ).count()
        
        # Second run
        result2 = startup_service.ensure_holiday_data()
        
        count2 = db_session.query(Holiday).filter(
            Holiday.data_source == DataSource.FEIERTAGE_API
        ).count()
        
        # Verify no duplicates
        assert count1 == count2, "Duplicate holidays created on second run"
        assert result2['action'] == 'up_to_date'
    
    def test_startup_import_handles_missing_years(self, db_session: Session):
        """Test that startup service detects and imports missing years"""
        # Clear existing holidays
        db_session.query(Holiday).delete()
        db_session.commit()
        
        # Import initial data
        startup_service = HolidayStartupService(db_session)
        startup_service.ensure_holiday_data()
        
        # Delete holidays for one year
        current_year = datetime.now().year
        db_session.query(Holiday).filter(
            Holiday.date >= date(current_year, 1, 1),
            Holiday.date < date(current_year + 1, 1, 1),
            Holiday.data_source == DataSource.FEIERTAGE_API
        ).delete()
        db_session.commit()
        
        # Run startup service again
        result = startup_service.ensure_holiday_data()
        
        # Verify missing year was detected and imported
        assert result['action'] == 'imported'
        assert current_year in result.get('missing_years', [])
        
        # Verify holidays exist for that year now
        holidays_for_year = db_session.query(Holiday).filter(
            Holiday.date >= date(current_year, 1, 1),
            Holiday.date < date(current_year + 1, 1, 1),
            Holiday.data_source == DataSource.FEIERTAGE_API
        ).count()
        
        assert holidays_for_year > 0, f"Holidays not re-imported for year {current_year}"


class TestSchedulerOperation:
    """Test scheduler functionality"""
    
    def test_scheduler_starts_automatically(self):
        """Test that scheduler starts on initialization"""
        scheduler = HolidayScheduler()
        
        # Verify scheduler is running
        assert scheduler.status == SchedulerStatus.RUNNING
        assert scheduler.scheduler is not None
        assert scheduler.scheduler.running
    
    def test_scheduler_job_is_scheduled(self):
        """Test that monthly import job is scheduled"""
        scheduler = HolidayScheduler()
        
        # Get job info
        job_info = scheduler.get_job_info(scheduler.JOB_ID)
        
        assert job_info is not None
        assert job_info['id'] == scheduler.JOB_ID
        assert job_info['name'] == 'monthly_holiday_import'
        assert job_info['next_run_time'] is not None
    
    def test_manual_trigger_creates_job(self):
        """Test manual job trigger functionality"""
        scheduler = HolidayScheduler()
        
        # Trigger manual import
        job_id = scheduler.trigger_manual_import()
        
        assert job_id is not None
        assert job_id.startswith('manual_import_')
        
        # Verify job was created
        jobs = scheduler.get_all_jobs()
        job_ids = [job['id'] for job in jobs]
        
        assert job_id in job_ids
    
    def test_scheduler_start_stop(self):
        """Test scheduler start/stop functionality"""
        scheduler = HolidayScheduler()
        
        # Stop scheduler
        scheduler.stop()
        assert scheduler.status == SchedulerStatus.STOPPED
        assert not scheduler.scheduler.running
        
        # Start scheduler
        scheduler.start()
        assert scheduler.status == SchedulerStatus.RUNNING
        assert scheduler.scheduler.running
    
    def test_job_execution_logging(self):
        """Test that job executions are logged"""
        scheduler = HolidayScheduler()
        
        # Get execution history
        executions = scheduler.get_job_executions(limit=10)
        
        # Verify structure
        assert isinstance(executions, list)
        
        if len(executions) > 0:
            execution = executions[0]
            assert 'job_id' in execution
            assert 'execution_id' in execution
            assert 'status' in execution
            assert 'started_at' in execution


class TestErrorHandling:
    """Test error scenarios and graceful degradation"""
    
    @patch('app.services.holiday_service.HolidayService.import_holidays_for_year')
    def test_api_failure_handling(self, mock_import, db_session: Session):
        """Test that API failures are handled gracefully"""
        # Mock API failure
        mock_import.side_effect = Exception("API connection failed")
        
        # Run startup service
        startup_service = HolidayStartupService(db_session)
        
        # Should not raise exception
        try:
            result = startup_service.ensure_holiday_data()
            # Service should handle error gracefully
            assert True
        except Exception as e:
            pytest.fail(f"Startup service did not handle API failure gracefully: {e}")
    
    def test_missing_config_handling(self):
        """Test handling of missing configuration"""
        # This test verifies that the system has sensible defaults
        settings = get_settings()
        
        assert settings.HOLIDAY_YEARS_PAST >= 0
        assert settings.HOLIDAY_YEARS_FUTURE >= 0
        assert settings.HOLIDAY_IMPORT_ENABLED is not None
        assert settings.HOLIDAY_SCHEDULER_ENABLED is not None
    
    def test_scheduler_error_recovery(self):
        """Test that scheduler recovers from errors"""
        scheduler = HolidayScheduler()
        
        # Verify scheduler is in healthy state
        status = scheduler.get_scheduler_status()
        
        assert status['status'] in ['RUNNING', 'STOPPED']
        assert 'error' not in status or status.get('error') is None


class TestIntegration:
    """Test integration of all components"""
    
    def test_full_workflow(self, db_session: Session):
        """Test complete workflow from startup to scheduled import"""
        # 1. Startup import
        startup_service = HolidayStartupService(db_session)
        startup_result = startup_service.ensure_holiday_data()
        
        assert startup_result['action'] in ['imported', 'up_to_date']
        
        # 2. Verify data in database
        holidays = db_session.query(Holiday).filter(
            Holiday.data_source == DataSource.FEIERTAGE_API
        ).all()
        
        assert len(holidays) > 0
        
        # 3. Scheduler is running
        scheduler = HolidayScheduler()
        assert scheduler.status == SchedulerStatus.RUNNING
        
        # 4. Job is scheduled
        job_info = scheduler.get_job_info(scheduler.JOB_ID)
        assert job_info is not None
        
        # 5. Manual trigger works
        job_id = scheduler.trigger_manual_import()
        assert job_id is not None
    
    def test_data_consistency(self, db_session: Session):
        """Test that data remains consistent across operations"""
        # Import data
        startup_service = HolidayStartupService(db_session)
        startup_service.ensure_holiday_data()
        
        # Get initial count
        initial_count = db_session.query(Holiday).filter(
            Holiday.data_source == DataSource.FEIERTAGE_API
        ).count()
        
        # Run import again
        startup_service.ensure_holiday_data()
        
        # Verify count unchanged (no duplicates)
        final_count = db_session.query(Holiday).filter(
            Holiday.data_source == DataSource.FEIERTAGE_API
        ).count()
        
        assert initial_count == final_count
    
    def test_multi_federal_state_support(self, db_session: Session):
        """Test that holidays are imported for all federal states"""
        startup_service = HolidayStartupService(db_session)
        startup_service.ensure_holiday_data()
        
        # Get holidays
        holidays = db_session.query(Holiday).filter(
            Holiday.data_source == DataSource.FEIERTAGE_API
        ).all()
        
        # Verify multiple federal states are represented
        federal_states = set(h.federal_state for h in holidays if h.federal_state)
        
        # Should have holidays for multiple states
        assert len(federal_states) > 1, "Holidays not imported for multiple federal states"
        
        # Verify some common states are present
        common_states = [FederalState.BAYERN, FederalState.NORDRHEIN_WESTFALEN]
        for state in common_states:
            state_holidays = [h for h in holidays if h.federal_state == state]
            assert len(state_holidays) > 0, f"No holidays found for {state.value}"


# Fixtures
@pytest.fixture
def db_session():
    """Provide a database session for tests"""
    session = next(get_session())
    yield session
    session.close()
