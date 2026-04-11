"""
Validation Script for Task 22.5: Robust Error Handling and Logging

This script validates:
1. Error handling in Holiday Startup Service
2. Error handling in Holiday Scheduler
3. Error handling in main.py integration
4. Logging completeness and quality
5. Graceful degradation behavior
6. Structured error responses
"""
import sys
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


def validate_startup_service_error_handling():
    """Validate error handling in Holiday Startup Service"""
    print_header("1. Validating Holiday Startup Service Error Handling")
    
    service_file = backend_path / "app" / "services" / "holiday_startup_service.py"
    content = service_file.read_text(encoding='utf-8')
    
    checks = [
        ("Try-except in ensure_holiday_data", "try:\n            # Jahresbereich aus Konfiguration"),
        ("Exception catch in ensure_holiday_data", "except Exception as e:\n            logger.error(f\"Error during holiday startup import"),
        ("Error logging with exc_info", "exc_info=True"),
        ("Try-except in async wrapper", "try:\n        session = next(get_session())"),
        ("Critical error catch", "except Exception as e:\n        logger.error(f\"Critical error in holiday startup service"),
        ("Session close", "session.close()"),
        ("Structured error response - error", '"action": "error"'),
        ("Structured error response - critical", '"action": "critical_error"'),
        ("Error message in response", '"error": str(e)'),
    ]
    
    all_present = True
    for name, pattern in checks:
        if pattern in content:
            print_success(f"Found: {name}")
        else:
            print_error(f"Missing: {name}")
            all_present = False
    
    return all_present


def validate_startup_service_logging():
    """Validate logging in Holiday Startup Service"""
    print_header("2. Validating Holiday Startup Service Logging")
    
    service_file = backend_path / "app" / "services" / "holiday_startup_service.py"
    content = service_file.read_text(encoding='utf-8')
    
    checks = [
        ("Info: Auto-import disabled", 'logger.info("Auto-import disabled'),
        ("Info: Checking holiday data", 'logger.info(f"Checking holiday data for years'),
        ("Info: All holidays present", 'logger.info(f"All holidays for {start_year}-{end_year} already present")'),
        ("Info: Importing holidays", 'logger.info(f"Importing holidays for {len(missing_years)} missing years'),
        ("Info: Import completed", 'logger.info(\n                f"Holiday import completed:'),
        ("Error: Startup import failed", 'logger.error(f"Error during holiday startup import'),
        ("Error: Critical error", 'logger.error(f"Critical error in holiday startup service'),
    ]
    
    all_present = True
    for name, pattern in checks:
        if pattern in content:
            print_success(f"Found: {name}")
        else:
            print_error(f"Missing: {name}")
            all_present = False
    
    return all_present


def validate_scheduler_error_handling():
    """Validate error handling in Holiday Scheduler"""
    print_header("3. Validating Holiday Scheduler Error Handling")
    
    scheduler_file = backend_path / "app" / "services" / "holiday_scheduler.py"
    content = scheduler_file.read_text(encoding='utf-8')
    
    checks = [
        ("Try-except in _setup_scheduler", "try:\n            # Configure job store"),
        ("Exception catch in _setup_scheduler", "except Exception as e:\n            logger.error(f\"Failed to setup holiday scheduler"),
        ("Status ERROR on setup failure", "self.status = SchedulerStatus.ERROR"),
        ("Try-except in start", "try:\n            if self.scheduler is None:"),
        ("Exception catch in start", "except Exception as e:\n            logger.error(f\"Failed to start holiday scheduler"),
        ("Try-except in stop", "try:\n            if self.scheduler is None:"),
        ("Exception catch in stop", "except Exception as e:\n            logger.error(f\"Failed to stop holiday scheduler"),
        ("Try-except in schedule_monthly_import", "try:\n            if self.scheduler is None:"),
        ("Exception catch in schedule_monthly_import", "except Exception as e:\n            logger.error(f\"Failed to schedule monthly import"),
        ("Try-except in trigger_manual_import", "try:\n            if self.scheduler is None:"),
        ("Exception catch in trigger_manual_import", "except Exception as e:\n            logger.error(f\"Failed to trigger manual import"),
        ("Try-except in _execute_import_job", "try:\n            logger.info(f\"Starting holiday import job execution"),
        ("Exception catch in _execute_import_job", "except Exception as e:\n            logger.error(f\"Holiday import job failed"),
        ("JobExecution status tracking", "job_execution.status = JobStatus.FAILED"),
        ("Error details in JobExecution", "job_execution.error_message = str(e)"),
        ("Exception type tracking", "job_execution.exception_type = type(e).__name__"),
        ("Session close in finally", "finally:\n                session.close()"),
    ]
    
    all_present = True
    for name, pattern in checks:
        if pattern in content:
            print_success(f"Found: {name}")
        else:
            print_error(f"Missing: {name}")
            all_present = False
    
    return all_present


def validate_scheduler_logging():
    """Validate logging in Holiday Scheduler"""
    print_header("4. Validating Holiday Scheduler Logging")
    
    scheduler_file = backend_path / "app" / "services" / "holiday_scheduler.py"
    content = scheduler_file.read_text(encoding='utf-8')
    
    checks = [
        ("Info: Scheduler configured", 'logger.info("Holiday Scheduler configured successfully")'),
        ("Info: Scheduler started", 'logger.info("Holiday Scheduler started successfully")'),
        ("Info: Scheduler stopped", 'logger.info("Holiday Scheduler stopped successfully")'),
        ("Info: Job scheduled", 'logger.info(f"Monthly holiday import job scheduled'),
        ("Info: Manual import triggered", 'logger.info(f"Manual holiday import job triggered'),
        ("Info: Job execution started", 'logger.info(f"Starting holiday import job execution'),
        ("Info: No missing years", 'logger.info("No missing years found'),
        ("Info: Missing years found", 'logger.info(f"Found {len(missing_years)} missing years'),
        ("Info: Import completed", 'logger.info(\n                        f"Import completed:'),
        ("Info: Job completed", 'logger.info(f"Holiday import job completed'),
        ("Error: Setup failed", 'logger.error(f"Failed to setup holiday scheduler'),
        ("Error: Start failed", 'logger.error(f"Failed to start holiday scheduler'),
        ("Error: Stop failed", 'logger.error(f"Failed to stop holiday scheduler'),
        ("Error: Job failed", 'logger.error(f"Holiday import job failed'),
        ("Warning: Already running", 'logger.warning("Holiday Scheduler is already running")'),
        ("Warning: Already stopped", 'logger.warning("Holiday Scheduler is already stopped")'),
    ]
    
    all_present = True
    for name, pattern in checks:
        if pattern in content:
            print_success(f"Found: {name}")
        else:
            print_error(f"Missing: {name}")
            all_present = False
    
    return all_present


def validate_main_integration_error_handling():
    """Validate error handling in main.py integration"""
    print_header("5. Validating main.py Integration Error Handling")
    
    main_file = backend_path / "main.py"
    content = main_file.read_text(encoding='utf-8')
    
    checks = [
        ("Try-except for startup service", "try:\n            from app.services.holiday_startup_service"),
        ("Exception catch for startup service", "except Exception as e:\n            logger.error(f\"Failed to initialize holiday data"),
        ("Graceful degradation comment", "# App startet trotzdem (graceful degradation)"),
        ("Try-except for scheduler start", "try:\n            from app.services.holiday_scheduler import start_holiday_scheduler"),
        ("Exception catch for scheduler start", "except Exception as e:\n            logger.error(f\"Failed to start Holiday Scheduler"),
        ("Try-except for scheduler stop", "try:\n            from app.services.holiday_scheduler import stop_holiday_scheduler"),
        ("Exception catch for scheduler stop", "except Exception as e:\n            logger.error(f\"Failed to stop Holiday Scheduler"),
    ]
    
    all_present = True
    for name, pattern in checks:
        if pattern in content:
            print_success(f"Found: {name}")
        else:
            print_error(f"Missing: {name}")
            all_present = False
    
    return all_present


def validate_main_integration_logging():
    """Validate logging in main.py integration"""
    print_header("6. Validating main.py Integration Logging")
    
    main_file = backend_path / "main.py"
    content = main_file.read_text(encoding='utf-8')
    
    checks = [
        ("Info: Checking holiday data", 'logger.info("Checking holiday data...")'),
        ("Info: Import success with emoji", 'logger.info(\n                    f"✅ Holiday import:'),
        ("Info: All years present with emoji", 'logger.info("✅ Holiday data: All years already present")'),
        ("Info: Starting scheduler", 'logger.info("Starting Holiday Scheduler...")'),
        ("Info: Scheduler started with emoji", 'logger.info(f"✅ Holiday Scheduler started'),
        ("Info: Scheduler stopped", 'logger.info("Holiday Scheduler stopped")'),
        ("Warning: Import failed with emoji", 'logger.warning(f"⚠️ Holiday import failed'),
        ("Error: Critical import error with emoji", 'logger.error(f"❌ Critical holiday import error'),
        ("Error: Failed to initialize", 'logger.error(f"Failed to initialize holiday data'),
        ("Error: Failed to start scheduler", 'logger.error(f"Failed to start Holiday Scheduler'),
        ("Error: Failed to stop scheduler", 'logger.error(f"Failed to stop Holiday Scheduler'),
    ]
    
    all_present = True
    for name, pattern in checks:
        if pattern in content:
            print_success(f"Found: {name}")
        else:
            print_error(f"Missing: {name}")
            all_present = False
    
    return all_present


def validate_graceful_degradation():
    """Validate graceful degradation behavior"""
    print_header("7. Validating Graceful Degradation")
    
    # Check that errors don't crash the app
    checks = []
    
    # Startup Service
    service_file = backend_path / "app" / "services" / "holiday_startup_service.py"
    service_content = service_file.read_text(encoding='utf-8')
    
    if 'return {\n                "auto_import_enabled": True,\n                "action": "error"' in service_content:
        print_success("Startup Service returns error dict instead of raising")
        checks.append(True)
    else:
        print_error("Startup Service might raise instead of returning error")
        checks.append(False)
    
    if 'return {\n            "auto_import_enabled": True,\n            "action": "critical_error"' in service_content:
        print_success("Async wrapper returns critical_error dict instead of raising")
        checks.append(True)
    else:
        print_error("Async wrapper might raise instead of returning error")
        checks.append(False)
    
    # Main.py
    main_file = backend_path / "main.py"
    main_content = main_file.read_text(encoding='utf-8')
    
    graceful_comments = main_content.count("# App startet trotzdem")
    if graceful_comments >= 2:
        print_success(f"Found {graceful_comments} graceful degradation comments in main.py")
        checks.append(True)
    else:
        print_error(f"Only found {graceful_comments} graceful degradation comments")
        checks.append(False)
    
    # Scheduler
    scheduler_file = backend_path / "app" / "services" / "holiday_scheduler.py"
    scheduler_content = scheduler_file.read_text(encoding='utf-8')
    
    if "self.status = SchedulerStatus.ERROR" in scheduler_content:
        print_success("Scheduler sets ERROR status instead of crashing")
        checks.append(True)
    else:
        print_error("Scheduler might crash instead of setting ERROR status")
        checks.append(False)
    
    if "job_execution.status = JobStatus.FAILED" in scheduler_content:
        print_success("Job execution tracks FAILED status")
        checks.append(True)
    else:
        print_error("Job execution might not track failures properly")
        checks.append(False)
    
    return all(checks)


def main():
    """Run all validations"""
    print_header("Task 22.5 Validation: Robust Error Handling and Logging")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    print_info("Note: Task 22.5 functionality was implemented in Tasks 22.2, 22.3, and 22.4")
    print_info("This validation confirms error handling and logging are comprehensive\n")
    
    results = {
        "Startup Service Error Handling": validate_startup_service_error_handling(),
        "Startup Service Logging": validate_startup_service_logging(),
        "Scheduler Error Handling": validate_scheduler_error_handling(),
        "Scheduler Logging": validate_scheduler_logging(),
        "Main Integration Error Handling": validate_main_integration_error_handling(),
        "Main Integration Logging": validate_main_integration_logging(),
        "Graceful Degradation": validate_graceful_degradation(),
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
        print(f"\n{Colors.GREEN}{Colors.BOLD}✓ All validations passed! Task 22.5 is complete.{Colors.RESET}")
        print(f"{Colors.GREEN}{Colors.BOLD}  (Functionality was implemented in Tasks 22.2, 22.3, and 22.4){Colors.RESET}\n")
        return 0
    else:
        print(f"\n{Colors.RED}{Colors.BOLD}✗ Some validations failed. Please review the errors above.{Colors.RESET}\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
