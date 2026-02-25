"""
Validation Script for Task 22.3: Holiday Scheduler Implementation

This script validates:
1. HolidayScheduler service file exists and has correct structure
2. Scheduler functionality (initialization, start, stop, job scheduling)
3. Integration in main.py (startup and shutdown)
4. Unit tests exist and pass
5. Configuration settings
"""
import sys
import os
from pathlib import Path
from datetime import datetime

# Add backend to path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))


class Colors:
    """ANSI color codes"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


def print_header(text: str):
    """Print formatted header"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*80}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text:^80}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*80}{Colors.RESET}\n")


def print_success(text: str):
    """Print success message"""
    print(f"{Colors.GREEN}✓ {text}{Colors.RESET}")


def print_error(text: str):
    """Print error message"""
    print(f"{Colors.RED}✗ {text}{Colors.RESET}")


def print_info(text: str):
    """Print info message"""
    print(f"{Colors.YELLOW}ℹ {text}{Colors.RESET}")


def validate_service_file():
    """Validate HolidayScheduler service file"""
    print_header("1. Validating HolidayScheduler Service File")
    
    service_file = backend_path / "app" / "services" / "holiday_scheduler.py"
    
    if not service_file.exists():
        print_error(f"Service file not found: {service_file}")
        return False
    
    print_success(f"Service file exists: {service_file}")
    
    # Check file content
    content = service_file.read_text(encoding='utf-8')
    
    required_elements = [
        ("HolidayScheduler class", "class HolidayScheduler:"),
        ("SchedulerConfig class", "class SchedulerConfig:"),
        ("JobExecution class", "class JobExecution:"),
        ("schedule_monthly_import method", "def schedule_monthly_import(self)"),
        ("trigger_manual_import method", "def trigger_manual_import(self)"),
        ("_execute_import_job method", "def _execute_import_job(self)"),
        ("get_holiday_scheduler function", "def get_holiday_scheduler("),
        ("start_holiday_scheduler function", "def start_holiday_scheduler("),
        ("stop_holiday_scheduler function", "def stop_holiday_scheduler("),
        ("HolidayService import", "from .holiday_service import HolidayService"),
        ("APScheduler imports", "from apscheduler.schedulers.background import BackgroundScheduler"),
    ]
    
    all_present = True
    for name, pattern in required_elements:
        if pattern in content:
            print_success(f"Found: {name}")
        else:
            print_error(f"Missing: {name}")
            all_present = False
    
    return all_present


def validate_scheduler_functionality():
    """Validate scheduler can be instantiated and configured"""
    print_header("2. Validating Scheduler Functionality")
    
    try:
        from unittest.mock import patch, Mock
        
        # Mock APScheduler components
        with patch('app.services.holiday_scheduler.BackgroundScheduler') as mock_scheduler, \
             patch('app.services.holiday_scheduler.SQLAlchemyJobStore'):
            
            from app.services.holiday_scheduler import (
                HolidayScheduler,
                SchedulerConfig,
                SchedulerStatus
            )
            
            # Test 1: Initialization
            config = SchedulerConfig(cron_expression="0 2 1 * *")
            scheduler = HolidayScheduler(config)
            
            if scheduler.status == SchedulerStatus.STOPPED:
                print_success("Scheduler initializes with STOPPED status")
            else:
                print_error(f"Unexpected initial status: {scheduler.status}")
                return False
            
            # Test 2: Configuration
            if scheduler.config.cron_expression == "0 2 1 * *":
                print_success("Scheduler uses correct cron expression")
            else:
                print_error(f"Wrong cron: {scheduler.config.cron_expression}")
                return False
            
            # Test 3: Start
            scheduler.start()
            if scheduler.status == SchedulerStatus.RUNNING:
                print_success("Scheduler can be started")
            else:
                print_error("Scheduler failed to start")
                return False
            
            # Test 4: Job scheduling
            mock_job = Mock()
            mock_job.next_run_time = datetime.now()
            scheduler.scheduler.add_job.return_value = mock_job
            scheduler.scheduler.get_job.return_value = None
            
            job_id = scheduler.schedule_monthly_import()
            if job_id == "holiday_monthly_import":
                print_success("Monthly import job can be scheduled")
            else:
                print_error(f"Wrong job ID: {job_id}")
                return False
            
            # Test 5: Manual trigger
            job_id = scheduler.trigger_manual_import()
            if job_id.startswith("manual_import_"):
                print_success("Manual import can be triggered")
            else:
                print_error("Manual trigger failed")
                return False
            
            # Test 6: Stop
            scheduler.stop()
            if scheduler.status == SchedulerStatus.STOPPED:
                print_success("Scheduler can be stopped")
            else:
                print_error("Scheduler failed to stop")
                return False
            
            return True
            
    except Exception as e:
        print_error(f"Scheduler functionality test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def validate_main_integration():
    """Validate integration in main.py"""
    print_header("3. Validating main.py Integration")
    
    main_file = backend_path / "main.py"
    
    if not main_file.exists():
        print_error(f"main.py not found: {main_file}")
        return False
    
    content = main_file.read_text(encoding='utf-8')
    
    checks = [
        ("Startup integration", "from app.services.holiday_scheduler import start_holiday_scheduler"),
        ("Startup check", "if settings.HOLIDAY_SCHEDULER_ENABLED:"),
        ("Scheduler start call", "scheduler = start_holiday_scheduler()"),
        ("Shutdown integration", "from app.services.holiday_scheduler import stop_holiday_scheduler"),
        ("Scheduler stop call", "stop_holiday_scheduler()"),
    ]
    
    all_present = True
    for name, pattern in checks:
        if pattern in content:
            print_success(f"Found: {name}")
        else:
            print_error(f"Missing: {name}")
            all_present = False
    
    return all_present


def validate_unit_tests():
    """Validate unit tests exist and pass"""
    print_header("4. Validating Unit Tests")
    
    test_file = backend_path / "tests" / "test_holiday_scheduler.py"
    
    if not test_file.exists():
        print_error(f"Test file not found: {test_file}")
        return False
    
    print_success(f"Test file exists: {test_file}")
    
    # Run tests
    print_info("Running unit tests...")
    import subprocess
    
    result = subprocess.run(
        ["python", "-m", "pytest", str(test_file), "-v", "--tb=short"],
        capture_output=True,
        text=True,
        cwd=backend_path
    )
    
    if result.returncode == 0:
        # Count passed tests
        output = result.stdout
        if "passed" in output:
            import re
            match = re.search(r'(\d+) passed', output)
            if match:
                count = match.group(1)
                print_success(f"All {count} unit tests passed")
                return True
        print_success("All unit tests passed")
        return True
    else:
        print_error("Some unit tests failed")
        print(result.stdout)
        return False


def validate_configuration():
    """Validate configuration settings"""
    print_header("5. Validating Configuration")
    
    try:
        from app.core.config import settings
        
        # Check scheduler settings
        if hasattr(settings, 'HOLIDAY_SCHEDULER_ENABLED'):
            print_success(f"HOLIDAY_SCHEDULER_ENABLED: {settings.HOLIDAY_SCHEDULER_ENABLED}")
        else:
            print_error("HOLIDAY_SCHEDULER_ENABLED not found in settings")
            return False
        
        if hasattr(settings, 'HOLIDAY_SCHEDULER_CRON'):
            print_success(f"HOLIDAY_SCHEDULER_CRON: {settings.HOLIDAY_SCHEDULER_CRON}")
            
            # Validate cron expression format
            cron = settings.HOLIDAY_SCHEDULER_CRON
            parts = cron.split()
            if len(parts) == 5:
                print_success("Cron expression has correct format (5 parts)")
            else:
                print_error(f"Invalid cron format: {cron}")
                return False
        else:
            print_error("HOLIDAY_SCHEDULER_CRON not found in settings")
            return False
        
        # Check year range settings (used by scheduler)
        if hasattr(settings, 'HOLIDAY_YEARS_PAST'):
            print_success(f"HOLIDAY_YEARS_PAST: {settings.HOLIDAY_YEARS_PAST}")
        else:
            print_error("HOLIDAY_YEARS_PAST not found")
            return False
        
        if hasattr(settings, 'HOLIDAY_YEARS_FUTURE'):
            print_success(f"HOLIDAY_YEARS_FUTURE: {settings.HOLIDAY_YEARS_FUTURE}")
        else:
            print_error("HOLIDAY_YEARS_FUTURE not found")
            return False
        
        return True
        
    except Exception as e:
        print_error(f"Configuration validation failed: {e}")
        return False


def main():
    """Run all validations"""
    print_header("Task 22.3 Validation: Holiday Scheduler Implementation")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    results = {
        "Service File": validate_service_file(),
        "Scheduler Functionality": validate_scheduler_functionality(),
        "main.py Integration": validate_main_integration(),
        "Unit Tests": validate_unit_tests(),
        "Configuration": validate_configuration(),
    }
    
    # Summary
    print_header("Validation Summary")
    
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    
    for test_name, result in results.items():
        status = f"{Colors.GREEN}PASS{Colors.RESET}" if result else f"{Colors.RED}FAIL{Colors.RESET}"
        print(f"{test_name:.<50} {status}")
    
    print(f"\n{Colors.BOLD}Total: {passed}/{total} validations passed{Colors.RESET}")
    
    if passed == total:
        print(f"\n{Colors.GREEN}{Colors.BOLD}✓ All validations passed! Task 22.3 is complete.{Colors.RESET}\n")
        return 0
    else:
        print(f"\n{Colors.RED}{Colors.BOLD}✗ Some validations failed. Please review the errors above.{Colors.RESET}\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
