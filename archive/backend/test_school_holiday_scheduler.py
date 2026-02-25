"""
Unit tests for SchoolHolidayScheduler

Tests cover:
- Scheduler initialization and configuration
- Job scheduling and management
- Sync execution coordination
- Error handling and recovery
- Status monitoring and reporting
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.job import Job

from app.services.school_holiday_scheduler import (
    SchoolHolidayScheduler,
    SchedulerStatus,
    JobStatus,
    SchedulerConfig,
    get_scheduler
)
from app.services.school_holiday_sync_service import (
    SyncResult,
    SyncStatus,
    ConflictResolutionStrategy
)
from app.models.federal_state import FederalState


class TestSchoolHolidayScheduler:
    """Test suite for SchoolHolidayScheduler"""
    
    @pytest.fixture
    def mock_scheduler_backend(self):
        """Create a mock APScheduler backend"""
        scheduler = Mock(spec=BackgroundScheduler)
        scheduler.running = False
        scheduler.get_jobs.return_value = []
        return scheduler
    
    @pytest.fixture
    def scheduler_config(self):
        """Create a test scheduler config"""
        return SchedulerConfig(
            cron_expression="0 2 1 * *",
            timezone="Europe/Berlin",
            conflict_strategy=ConflictResolutionStrategy.API_WINS,
            years_to_sync=[2025],
            dry_run=False
        )
    
    @pytest.fixture
    def scheduler_service(self, scheduler_config, mock_scheduler_backend):
        """Create a test scheduler service instance"""
        with patch('app.services.school_holiday_scheduler.BackgroundScheduler', return_value=mock_scheduler_backend):
            return SchoolHolidayScheduler(config=scheduler_config)
    
    def test_scheduler_initialization_default(self):
        """Test scheduler initialization with default settings"""
        with patch('app.services.school_holiday_scheduler.BackgroundScheduler') as mock_scheduler_class:
            mock_scheduler = Mock()
            mock_scheduler_class.return_value = mock_scheduler
            
            scheduler = SchoolHolidayScheduler()
            
            assert scheduler.config.conflict_strategy == ConflictResolutionStrategy.API_WINS
            assert scheduler.config.cron_expression == "0 2 1 * *"
            assert scheduler.config.timezone == "Europe/Berlin"
            assert scheduler.status == SchedulerStatus.STOPPED
            
            # Verify scheduler was configured
            mock_scheduler_class.assert_called_once()
    
    def test_scheduler_initialization_custom(self, scheduler_config):
        """Test scheduler initialization with custom settings"""
        with patch('app.services.school_holiday_scheduler.BackgroundScheduler') as mock_scheduler_class:
            mock_scheduler = Mock()
            mock_scheduler_class.return_value = mock_scheduler
            
            custom_config = SchedulerConfig(
                conflict_strategy=ConflictResolutionStrategy.LOCAL_WINS,
                cron_expression="0 6 15 * *",
                timezone="UTC",
                years_to_sync=[2024, 2025]
            )
            
            scheduler = SchoolHolidayScheduler(config=custom_config)
            
            assert scheduler.config.conflict_strategy == ConflictResolutionStrategy.LOCAL_WINS
            assert scheduler.config.cron_expression == "0 6 15 * *"
            assert scheduler.config.timezone == "UTC"
            assert scheduler.config.years_to_sync == [2024, 2025]
    
    def test_start_scheduler(self, scheduler_service):
        """Test starting the scheduler"""
        # Mock that no job exists initially
        scheduler_service.scheduler.get_job.return_value = None
        
        scheduler_service.start()
        
        # Verify scheduler was started
        scheduler_service.scheduler.start.assert_called_once()
        assert scheduler_service.status == SchedulerStatus.RUNNING
        
        # Verify monthly job was scheduled
        scheduler_service.scheduler.add_job.assert_called()
    
    def test_stop_scheduler(self, scheduler_service):
        """Test stopping the scheduler"""
        # Start first
        scheduler_service.start()
        
        # Then stop
        scheduler_service.stop()
        
        scheduler_service.scheduler.shutdown.assert_called_once_with(wait=True)
        assert scheduler_service.status == SchedulerStatus.STOPPED
    
    def test_trigger_manual_sync(self, scheduler_service):
        """Test triggering a manual sync"""
        # Mock job creation
        mock_job = Mock(spec=Job)
        mock_job.id = "manual_sync_123"
        scheduler_service.scheduler.add_job.return_value = mock_job
        
        job_id = scheduler_service.trigger_manual_sync()
        
        assert job_id.startswith("manual_sync_")
        
        # Verify job was scheduled
        scheduler_service.scheduler.add_job.assert_called()
        call_args = scheduler_service.scheduler.add_job.call_args
        assert call_args[1]['trigger'] == 'date'
    
    def test_trigger_manual_sync_with_custom_params(self, scheduler_service):
        """Test triggering manual sync with custom parameters"""
        custom_years = [2024, 2025]
        
        mock_job = Mock(spec=Job)
        mock_job.id = "manual_sync_custom"
        scheduler_service.scheduler.add_job.return_value = mock_job
        
        job_id = scheduler_service.trigger_manual_sync(
            years_to_sync=custom_years,
            dry_run=True
        )
        
        assert job_id.startswith("manual_sync_")
        
        # Verify job was scheduled with custom parameters
        call_args = scheduler_service.scheduler.add_job.call_args
        assert call_args[1]['kwargs']['years_to_sync'] == custom_years
        assert call_args[1]['kwargs']['dry_run'] is True
    
    def test_remove_job(self, scheduler_service):
        """Test removing a scheduled job"""
        job_id = "test_job_123"
        
        # Test successful removal
        result = scheduler_service.remove_job(job_id)
        
        assert result is True
        scheduler_service.scheduler.remove_job.assert_called_once_with(job_id)
    
    def test_remove_job_not_found(self, scheduler_service):
        """Test removing a non-existent job"""
        from apscheduler.jobstores.base import JobLookupError
        
        job_id = "nonexistent_job"
        scheduler_service.scheduler.remove_job.side_effect = JobLookupError(job_id)
        
        result = scheduler_service.remove_job(job_id)
        
        assert result is False
    
    def test_get_all_jobs(self, scheduler_service):
        """Test getting list of all jobs"""
        # Mock jobs
        mock_job1 = Mock(spec=Job)
        mock_job1.id = "monthly_sync"
        mock_job1.name = "Monthly School Holiday Sync"
        mock_job1.next_run_time = datetime.now() + timedelta(days=1)
        mock_job1.trigger = "cron"
        mock_job1.kwargs = {}
        
        mock_job2 = Mock(spec=Job)
        mock_job2.id = "manual_sync_123"
        mock_job2.name = "Manual School Holiday Sync"
        mock_job2.next_run_time = datetime.now() + timedelta(minutes=1)
        mock_job2.trigger = "date"
        mock_job2.kwargs = {}
        
        scheduler_service.scheduler.get_jobs.return_value = [mock_job1, mock_job2]
        
        jobs = scheduler_service.get_all_jobs()
        
        assert len(jobs) == 2
        assert jobs[0]['id'] == "monthly_sync"
        assert jobs[0]['name'] == "Monthly School Holiday Sync"
        assert jobs[1]['id'] == "manual_sync_123"
        assert jobs[1]['name'] == "Manual School Holiday Sync"
    
    def test_get_job_info(self, scheduler_service):
        """Test getting info for a specific job"""
        job_id = "test_job"
        
        # Mock job exists
        mock_job = Mock(spec=Job)
        mock_job.id = job_id
        mock_job.name = "Test Job"
        mock_job.next_run_time = datetime.now() + timedelta(hours=1)
        mock_job.trigger = "cron"
        mock_job.kwargs = {"test": "value"}
        scheduler_service.scheduler.get_job.return_value = mock_job
        
        info = scheduler_service.get_job_info(job_id)
        
        assert info is not None
        assert info['id'] == job_id
        assert info['name'] == "Test Job"
        assert info['kwargs'] == {"test": "value"}
        
        # Test job not found
        scheduler_service.scheduler.get_job.return_value = None
        info = scheduler_service.get_job_info("nonexistent")
        
        assert info is None
    
    def test_execute_sync_job_success(self, scheduler_service):
        """Test successful sync job execution"""
        # Mock successful sync
        with patch('app.services.school_holiday_scheduler.get_school_holiday_sync_service') as mock_sync_factory:
            mock_sync_service = Mock()
            sync_result = SyncResult(
                sync_id="test_sync",
                status=SyncStatus.COMPLETED,
                started_at=datetime.now(),
                total_states=2,
                successful_states=["BW", "BY"],
                failed_states=[]
            )
            mock_sync_service.sync_all_states.return_value = sync_result
            mock_sync_factory.return_value = mock_sync_service
            
            # Execute sync job
            scheduler_service._execute_sync_job(
                conflict_strategy=ConflictResolutionStrategy.API_WINS,
                years_to_sync=[2025],
                dry_run=False
            )
            
            # Verify sync service was called
            mock_sync_service.sync_all_states.assert_called_once_with(
                years=[2025],
                dry_run=False
            )
            
            # Verify execution was tracked
            assert len(scheduler_service.job_executions) == 1
            assert scheduler_service.job_executions[0].status == JobStatus.COMPLETED
    
    def test_execute_sync_job_failure(self, scheduler_service):
        """Test sync job execution with failure"""
        # Mock sync failure
        with patch('app.services.school_holiday_scheduler.get_school_holiday_sync_service') as mock_sync_factory:
            mock_sync_service = Mock()
            mock_sync_service.sync_all_states.side_effect = Exception("Sync failed")
            mock_sync_factory.return_value = mock_sync_service
            
            with pytest.raises(Exception, match="Sync failed"):
                scheduler_service._execute_sync_job(
                    conflict_strategy=ConflictResolutionStrategy.API_WINS,
                    years_to_sync=[2025],
                    dry_run=False
                )
            
            # Verify failure was tracked
            assert len(scheduler_service.job_executions) == 1
            assert scheduler_service.job_executions[0].status == JobStatus.FAILED
            assert "Sync failed" in scheduler_service.job_executions[0].error_message
    
    def test_get_job_executions(self, scheduler_service):
        """Test getting job execution history"""
        # Add some mock executions
        from app.services.school_holiday_scheduler import JobExecution
        
        execution1 = JobExecution(
            job_id="job1",
            execution_id="exec1",
            status=JobStatus.COMPLETED,
            started_at=datetime.now() - timedelta(hours=2)
        )
        execution2 = JobExecution(
            job_id="job2",
            execution_id="exec2",
            status=JobStatus.FAILED,
            started_at=datetime.now() - timedelta(hours=1)
        )
        
        scheduler_service.job_executions = [execution1, execution2]
        
        # Test default limit
        executions = scheduler_service.get_job_executions()
        assert len(executions) == 2
        
        # Test custom limit
        executions = scheduler_service.get_job_executions(limit=1)
        assert len(executions) == 1
        assert executions[0]["execution_id"] == "exec2"  # Most recent first
    
    def test_get_scheduler_status(self, scheduler_service):
        """Test getting scheduler status"""
        # Mock running scheduler
        scheduler_service.scheduler.running = True
        scheduler_service.status = SchedulerStatus.RUNNING
        
        # Mock some jobs
        mock_job = Mock(spec=Job)
        scheduler_service.scheduler.get_jobs.return_value = [mock_job]
        
        status = scheduler_service.get_scheduler_status()
        
        assert status["status"] == "RUNNING"
        assert status["running"] is True
        assert status["jobs_count"] == 1
        assert "config" in status
    
    def test_pause_resume_scheduler(self, scheduler_service):
        """Test pausing and resuming the scheduler"""
        # Start scheduler first
        scheduler_service.start()
        
        # Pause
        scheduler_service.pause()
        scheduler_service.scheduler.pause.assert_called_once()
        assert scheduler_service.status == SchedulerStatus.PAUSED
        
        # Resume
        scheduler_service.resume()
        scheduler_service.scheduler.resume.assert_called_once()
        assert scheduler_service.status == SchedulerStatus.RUNNING
    
    def test_update_config(self, scheduler_service):
        """Test updating scheduler configuration"""
        new_config = SchedulerConfig(
            conflict_strategy=ConflictResolutionStrategy.LOCAL_WINS,
            cron_expression="0 6 15 * *",
            years_to_sync=[2024, 2025]
        )
        
        scheduler_service.update_config(new_config)
        
        assert scheduler_service.config == new_config
    
    def test_factory_function(self):
        """Test the factory function"""
        with patch('app.services.school_holiday_scheduler.BackgroundScheduler'):
            # Reset the global instance for testing
            import app.services.school_holiday_scheduler as scheduler_module
            scheduler_module._scheduler_instance = None
            
            scheduler = get_scheduler()
            
            assert isinstance(scheduler, SchoolHolidayScheduler)
            assert scheduler.config.conflict_strategy == ConflictResolutionStrategy.API_WINS
            
            # Reset again for second test
            scheduler_module._scheduler_instance = None
            
            # Test with custom config
            custom_config = SchedulerConfig(
                conflict_strategy=ConflictResolutionStrategy.LOCAL_WINS
            )
            scheduler = get_scheduler(config=custom_config)
            assert scheduler.config.conflict_strategy == ConflictResolutionStrategy.LOCAL_WINS
            
            # Clean up
            scheduler_module._scheduler_instance = None


class TestSchedulerConfig:
    """Test the SchedulerConfig data class"""
    
    def test_config_creation_default(self):
        """Test creating config with defaults"""
        config = SchedulerConfig()
        
        assert config.cron_expression == "0 2 1 * *"
        assert config.timezone == "Europe/Berlin"
        assert config.conflict_strategy == ConflictResolutionStrategy.API_WINS
        assert config.dry_run is False
        assert config.max_workers == 2
        assert config.years_to_sync is not None
        assert len(config.years_to_sync) > 0
    
    def test_config_creation_custom(self):
        """Test creating config with custom values"""
        custom_years = [2024, 2025]
        config = SchedulerConfig(
            cron_expression="0 6 15 * *",
            timezone="UTC",
            conflict_strategy=ConflictResolutionStrategy.LOCAL_WINS,
            years_to_sync=custom_years,
            dry_run=True,
            max_workers=4
        )
        
        assert config.cron_expression == "0 6 15 * *"
        assert config.timezone == "UTC"
        assert config.conflict_strategy == ConflictResolutionStrategy.LOCAL_WINS
        assert config.years_to_sync == custom_years
        assert config.dry_run is True
        assert config.max_workers == 4


class TestSchedulerIntegration:
    """Integration tests for scheduler components"""
    
    def test_full_scheduler_lifecycle(self):
        """Test complete scheduler lifecycle"""
        with patch('app.services.school_holiday_scheduler.BackgroundScheduler') as mock_scheduler_class:
            mock_scheduler = Mock()
            mock_scheduler.running = False
            mock_scheduler.get_jobs.return_value = []  # Mock get_jobs to return empty list
            mock_scheduler_class.return_value = mock_scheduler
            
            # Reset global instance
            import app.services.school_holiday_scheduler as scheduler_module
            scheduler_module._scheduler_instance = None
            
            # Create scheduler
            scheduler = get_scheduler()
            
            # Start scheduler
            scheduler.start()
            assert scheduler.status == SchedulerStatus.RUNNING
            
            # Trigger manual sync
            mock_job = Mock()
            mock_job.id = "manual_123"
            mock_scheduler.add_job.return_value = mock_job
            
            job_id = scheduler.trigger_manual_sync()
            assert job_id.startswith("manual_sync_")
            
            # Get status
            status = scheduler.get_scheduler_status()
            assert status["status"] == "RUNNING"
            
            # Stop scheduler
            scheduler.stop()
            assert scheduler.status == SchedulerStatus.STOPPED
            
            # Clean up
            scheduler_module._scheduler_instance = None
    
    def test_error_handling_during_sync(self):
        """Test error handling during sync execution"""
        with patch('app.services.school_holiday_scheduler.BackgroundScheduler'):
            with patch('app.services.school_holiday_scheduler.get_school_holiday_sync_service') as mock_sync_factory:
                mock_sync_service = Mock()
                mock_sync_service.sync_all_states.side_effect = Exception("Database error")
                mock_sync_factory.return_value = mock_sync_service
                
                scheduler = get_scheduler()
                
                # Execute sync should handle error gracefully
                with pytest.raises(Exception, match="Database error"):
                    scheduler._execute_sync_job(
                        conflict_strategy=ConflictResolutionStrategy.API_WINS,
                        years_to_sync=[2025],
                        dry_run=False
                    )
                
                # Error should be recorded in executions
                executions = scheduler.get_job_executions()
                assert len(executions) == 1
                assert executions[0]["status"] == "FAILED"
                assert "Database error" in executions[0]["error_message"]


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
