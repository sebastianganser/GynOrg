"""
Unit tests for Holiday Scheduler
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
from sqlmodel import Session

from app.services.holiday_scheduler import (
    HolidayScheduler,
    SchedulerConfig,
    SchedulerStatus,
    JobStatus,
    get_holiday_scheduler,
    start_holiday_scheduler,
    stop_holiday_scheduler
)


class TestSchedulerConfig:
    """Test suite for SchedulerConfig"""
    
    def test_default_config(self):
        """Test default configuration values"""
        config = SchedulerConfig()
        
        assert config.cron_expression == "0 2 1 * *"
        assert config.timezone == "Europe/Berlin"
        assert config.max_instances == 1
        assert config.coalesce is True
        assert config.misfire_grace_time == 3600
        assert config.max_workers == 2
        assert config.job_defaults is not None
    
    def test_custom_config(self):
        """Test custom configuration"""
        config = SchedulerConfig(
            cron_expression="0 3 15 * *",
            timezone="UTC",
            max_workers=4
        )
        
        assert config.cron_expression == "0 3 15 * *"
        assert config.timezone == "UTC"
        assert config.max_workers == 4


class TestHolidayScheduler:
    """Test suite for HolidayScheduler"""
    
    @pytest.fixture
    def mock_scheduler_backend(self):
        """Mock APScheduler backend"""
        with patch('app.services.holiday_scheduler.BackgroundScheduler') as mock:
            yield mock
    
    @pytest.fixture
    def scheduler(self, mock_scheduler_backend):
        """Create HolidayScheduler with mocked backend"""
        config = SchedulerConfig()
        scheduler = HolidayScheduler(config)
        return scheduler
    
    def test_scheduler_initialization(self, scheduler):
        """Test that scheduler initializes correctly"""
        assert scheduler.config is not None
        assert scheduler.status == SchedulerStatus.STOPPED
        assert scheduler.job_executions == []
        assert scheduler.event_listeners == []
    
    def test_scheduler_uses_config_cron(self):
        """Test that scheduler uses cron from settings"""
        with patch('app.services.holiday_scheduler.settings') as mock_settings, \
             patch('app.services.holiday_scheduler.BackgroundScheduler'), \
             patch('app.services.holiday_scheduler.SQLAlchemyJobStore'):
            
            mock_settings.HOLIDAY_SCHEDULER_CRON = "0 4 2 * *"
            mock_settings.DATABASE_URL = "sqlite:///test.db"
            
            scheduler = HolidayScheduler()
            
            assert scheduler.config.cron_expression == "0 4 2 * *"
    
    def test_start_scheduler(self, scheduler):
        """Test starting the scheduler"""
        scheduler.start()
        
        assert scheduler.status == SchedulerStatus.RUNNING
        scheduler.scheduler.start.assert_called_once()
    
    def test_start_already_running(self, scheduler):
        """Test starting scheduler when already running"""
        scheduler.status = SchedulerStatus.RUNNING
        
        scheduler.start()
        
        # Should not call start again
        scheduler.scheduler.start.assert_not_called()
    
    def test_stop_scheduler(self, scheduler):
        """Test stopping the scheduler"""
        scheduler.status = SchedulerStatus.RUNNING
        
        scheduler.stop()
        
        assert scheduler.status == SchedulerStatus.STOPPED
        scheduler.scheduler.shutdown.assert_called_once_with(wait=True)
    
    def test_stop_already_stopped(self, scheduler):
        """Test stopping scheduler when already stopped"""
        scheduler.status = SchedulerStatus.STOPPED
        
        scheduler.stop()
        
        # Should not call shutdown
        scheduler.scheduler.shutdown.assert_not_called()
    
    def test_schedule_monthly_import(self, scheduler):
        """Test scheduling monthly import job"""
        mock_job = Mock()
        mock_job.next_run_time = datetime.now() + timedelta(days=1)
        scheduler.scheduler.add_job.return_value = mock_job
        scheduler.scheduler.get_job.return_value = None
        
        job_id = scheduler.schedule_monthly_import()
        
        assert job_id == HolidayScheduler.JOB_ID
        scheduler.scheduler.add_job.assert_called_once()
        
        # Verify cron trigger was used
        call_args = scheduler.scheduler.add_job.call_args
        assert call_args[1]['id'] == HolidayScheduler.JOB_ID
        assert call_args[1]['name'] == "Monthly Holiday Import"
    
    def test_trigger_manual_import(self, scheduler):
        """Test triggering manual import"""
        mock_job = Mock()
        scheduler.scheduler.add_job.return_value = mock_job
        
        job_id = scheduler.trigger_manual_import()
        
        assert job_id.startswith("manual_import_")
        scheduler.scheduler.add_job.assert_called_once()
        
        # Verify date trigger was used (immediate execution)
        call_args = scheduler.scheduler.add_job.call_args
        assert call_args[1]['trigger'] == 'date'
    
    def test_get_job_info(self, scheduler):
        """Test getting job information"""
        mock_job = Mock()
        mock_job.id = "test_job"
        mock_job.name = "Test Job"
        mock_job.next_run_time = datetime(2025, 11, 1, 2, 0)
        mock_job.trigger = "cron"
        
        scheduler.scheduler.get_job.return_value = mock_job
        
        info = scheduler.get_job_info("test_job")
        
        assert info is not None
        assert info['id'] == "test_job"
        assert info['name'] == "Test Job"
        assert info['next_run_time'] is not None
    
    def test_get_job_info_not_found(self, scheduler):
        """Test getting info for non-existent job"""
        scheduler.scheduler.get_job.return_value = None
        
        info = scheduler.get_job_info("nonexistent")
        
        assert info is None
    
    def test_get_all_jobs(self, scheduler):
        """Test getting all jobs"""
        mock_job1 = Mock()
        mock_job1.id = "job1"
        mock_job1.name = "Job 1"
        mock_job1.next_run_time = datetime.now()
        mock_job1.trigger = "cron"
        
        mock_job2 = Mock()
        mock_job2.id = "job2"
        mock_job2.name = "Job 2"
        mock_job2.next_run_time = None
        mock_job2.trigger = "date"
        
        scheduler.scheduler.get_jobs.return_value = [mock_job1, mock_job2]
        
        jobs = scheduler.get_all_jobs()
        
        assert len(jobs) == 2
        assert jobs[0]['id'] == "job1"
        assert jobs[1]['id'] == "job2"
    
    def test_get_scheduler_status(self, scheduler):
        """Test getting scheduler status"""
        scheduler.status = SchedulerStatus.RUNNING
        scheduler.scheduler.running = True
        scheduler.scheduler.get_jobs.return_value = [Mock(), Mock()]
        
        status = scheduler.get_scheduler_status()
        
        assert status['status'] == "RUNNING"
        assert status['running'] is True
        assert status['jobs_count'] == 2
        assert 'config' in status


class TestHolidaySchedulerJobExecution:
    """Test suite for job execution"""
    
    @pytest.fixture
    def mock_session(self):
        """Mock database session"""
        return Mock(spec=Session)
    
    @pytest.fixture
    def mock_holiday_service(self):
        """Mock HolidayService"""
        return Mock()
    
    def test_execute_import_job_no_missing_years(self):
        """Test job execution when no years are missing"""
        with patch('app.services.holiday_scheduler.BackgroundScheduler'), \
             patch('app.services.holiday_scheduler.SQLAlchemyJobStore'), \
             patch('app.services.holiday_scheduler.get_session') as mock_get_session, \
             patch('app.services.holiday_scheduler.HolidayService') as mock_service_class, \
             patch('app.services.holiday_scheduler.settings') as mock_settings:
            
            # Setup mocks
            mock_session = Mock()
            mock_get_session.return_value = iter([mock_session])
            
            mock_service = Mock()
            mock_service.get_missing_years.return_value = []
            mock_service_class.return_value = mock_service
            
            mock_settings.get_holiday_year_range.return_value = (2023, 2028)
            
            # Create scheduler and execute job
            scheduler = HolidayScheduler()
            scheduler._execute_import_job()
            
            # Verify
            assert len(scheduler.job_executions) == 1
            execution = scheduler.job_executions[0]
            assert execution.status == JobStatus.COMPLETED
            assert execution.import_result['total_imported'] == 0
            assert execution.import_result['message'] == "All holidays already present"
            
            # Verify session was closed
            mock_session.close.assert_called_once()
    
    def test_execute_import_job_with_missing_years(self):
        """Test job execution with missing years"""
        with patch('app.services.holiday_scheduler.BackgroundScheduler'), \
             patch('app.services.holiday_scheduler.SQLAlchemyJobStore'), \
             patch('app.services.holiday_scheduler.get_session') as mock_get_session, \
             patch('app.services.holiday_scheduler.HolidayService') as mock_service_class, \
             patch('app.services.holiday_scheduler.settings') as mock_settings:
            
            # Setup mocks
            mock_session = Mock()
            mock_get_session.return_value = iter([mock_session])
            
            mock_service = Mock()
            mock_service.get_missing_years.return_value = [2023, 2024]
            mock_service.import_missing_years.return_value = {
                'total_imported': 150,
                'total_skipped': 5,
                'total_errors': 0,
                'years_processed': 2
            }
            mock_service_class.return_value = mock_service
            
            mock_settings.get_holiday_year_range.return_value = (2023, 2028)
            
            # Create scheduler and execute job
            scheduler = HolidayScheduler()
            scheduler._execute_import_job()
            
            # Verify
            assert len(scheduler.job_executions) == 1
            execution = scheduler.job_executions[0]
            assert execution.status == JobStatus.COMPLETED
            assert execution.import_result['total_imported'] == 150
            assert execution.import_result['years_processed'] == 2
            
            # Verify import was called
            mock_service.import_missing_years.assert_called_once()
    
    def test_execute_import_job_error_handling(self):
        """Test job execution error handling"""
        with patch('app.services.holiday_scheduler.BackgroundScheduler'), \
             patch('app.services.holiday_scheduler.SQLAlchemyJobStore'), \
             patch('app.services.holiday_scheduler.get_session') as mock_get_session, \
             patch('app.services.holiday_scheduler.HolidayService') as mock_service_class, \
             patch('app.services.holiday_scheduler.settings') as mock_settings:
            
            # Setup mocks
            mock_session = Mock()
            mock_get_session.return_value = iter([mock_session])
            
            mock_service = Mock()
            mock_service.get_missing_years.side_effect = Exception("Database error")
            mock_service_class.return_value = mock_service
            
            mock_settings.get_holiday_year_range.return_value = (2023, 2028)
            
            # Create scheduler and execute job
            scheduler = HolidayScheduler()
            
            with pytest.raises(Exception, match="Database error"):
                scheduler._execute_import_job()
            
            # Verify error was logged
            assert len(scheduler.job_executions) == 1
            execution = scheduler.job_executions[0]
            assert execution.status == JobStatus.FAILED
            assert execution.error_message == "Database error"
            assert execution.exception_type == "Exception"


class TestGlobalSchedulerFunctions:
    """Test suite for global scheduler functions"""
    
    def test_get_holiday_scheduler_singleton(self):
        """Test that get_holiday_scheduler returns singleton"""
        with patch('app.services.holiday_scheduler.BackgroundScheduler'):
            # Reset global instance
            import app.services.holiday_scheduler as scheduler_module
            scheduler_module._scheduler_instance = None
            
            scheduler1 = get_holiday_scheduler()
            scheduler2 = get_holiday_scheduler()
            
            assert scheduler1 is scheduler2
    
    def test_start_holiday_scheduler(self):
        """Test start_holiday_scheduler function"""
        with patch('app.services.holiday_scheduler.BackgroundScheduler'):
            # Reset global instance
            import app.services.holiday_scheduler as scheduler_module
            scheduler_module._scheduler_instance = None
            
            scheduler = start_holiday_scheduler()
            
            assert scheduler.status == SchedulerStatus.RUNNING
    
    def test_stop_holiday_scheduler(self):
        """Test stop_holiday_scheduler function"""
        with patch('app.services.holiday_scheduler.BackgroundScheduler'):
            # Reset and start
            import app.services.holiday_scheduler as scheduler_module
            scheduler_module._scheduler_instance = None
            
            start_holiday_scheduler()
            stop_holiday_scheduler()
            
            # Instance should be None after stop
            assert scheduler_module._scheduler_instance is None
