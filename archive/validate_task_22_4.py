"""
Validation Script for Task 22.4: Startup and Shutdown Event Handlers Integration

This script validates:
1. Startup event handler exists and is properly configured
2. Holiday Startup Service integration in startup
3. Holiday Scheduler integration in startup
4. Shutdown event handler exists and is properly configured
5. Scheduler shutdown integration
6. Configuration flags are respected
7. Error handling (graceful degradation)
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


def validate_startup_event_handler():
    """Validate startup event handler exists and is properly configured"""
    print_header("1. Validating Startup Event Handler")
    
    main_file = backend_path / "main.py"
    
    if not main_file.exists():
        print_error(f"main.py not found: {main_file}")
        return False
    
    content = main_file.read_text(encoding='utf-8')
    
    # Check for startup event handler
    checks = [
        ("Startup event decorator", "@app.on_event(\"startup\")"),
        ("Startup function definition", "async def startup_event():"),
        ("Startup docstring", "Application startup event"),
    ]
    
    all_present = True
    for name, pattern in checks:
        if pattern in content:
            print_success(f"Found: {name}")
        else:
            print_error(f"Missing: {name}")
            all_present = False
    
    return all_present


def validate_holiday_startup_service_integration():
    """Validate Holiday Startup Service integration in startup event"""
    print_header("2. Validating Holiday Startup Service Integration")
    
    main_file = backend_path / "main.py"
    content = main_file.read_text(encoding='utf-8')
    
    checks = [
        ("Configuration check", "if settings.HOLIDAY_AUTO_IMPORT_ON_STARTUP:"),
        ("Service import", "from app.services.holiday_startup_service import ensure_holiday_data_on_startup"),
        ("Service call", "result = await ensure_holiday_data_on_startup()"),
        ("Result handling - imported", 'if result["action"] == "imported":'),
        ("Result handling - none needed", 'elif result["action"] == "none_needed":'),
        ("Result handling - error", 'elif result["action"] == "error":'),
        ("Result handling - critical", 'elif result["action"] == "critical_error":'),
        ("Success logging", "✅ Holiday import:"),
        ("Error handling", "except Exception as e:"),
        ("Graceful degradation comment", "# App startet trotzdem"),
    ]
    
    all_present = True
    for name, pattern in checks:
        if pattern in content:
            print_success(f"Found: {name}")
        else:
            print_error(f"Missing: {name}")
            all_present = False
    
    return all_present


def validate_holiday_scheduler_integration():
    """Validate Holiday Scheduler integration in startup event"""
    print_header("3. Validating Holiday Scheduler Integration")
    
    main_file = backend_path / "main.py"
    content = main_file.read_text(encoding='utf-8')
    
    checks = [
        ("Configuration check", "if settings.HOLIDAY_SCHEDULER_ENABLED:"),
        ("Scheduler import", "from app.services.holiday_scheduler import start_holiday_scheduler"),
        ("Scheduler start", "scheduler = start_holiday_scheduler()"),
        ("Job info retrieval", "job_info = scheduler.get_job_info(scheduler.JOB_ID)"),
        ("Next run time check", "if job_info and job_info.get('next_run_time'):"),
        ("Success logging with time", "✅ Holiday Scheduler started. Next run:"),
        ("Success logging without time", "✅ Holiday Scheduler started"),
        ("Error handling", "except Exception as e:"),
        ("Error logging", "Failed to start Holiday Scheduler"),
    ]
    
    all_present = True
    for name, pattern in checks:
        if pattern in content:
            print_success(f"Found: {name}")
        else:
            print_error(f"Missing: {name}")
            all_present = False
    
    return all_present


def validate_shutdown_event_handler():
    """Validate shutdown event handler exists and is properly configured"""
    print_header("4. Validating Shutdown Event Handler")
    
    main_file = backend_path / "main.py"
    content = main_file.read_text(encoding='utf-8')
    
    checks = [
        ("Shutdown event decorator", "@app.on_event(\"shutdown\")"),
        ("Shutdown function definition", "async def shutdown_event():"),
        ("Shutdown docstring", "Application shutdown event"),
        ("Shutdown logging", "Shutting down"),
    ]
    
    all_present = True
    for name, pattern in checks:
        if pattern in content:
            print_success(f"Found: {name}")
        else:
            print_error(f"Missing: {name}")
            all_present = False
    
    return all_present


def validate_scheduler_shutdown_integration():
    """Validate Scheduler shutdown integration"""
    print_header("5. Validating Scheduler Shutdown Integration")
    
    main_file = backend_path / "main.py"
    content = main_file.read_text(encoding='utf-8')
    
    # Find shutdown event handler
    if "@app.on_event(\"shutdown\")" not in content:
        print_error("Shutdown event handler not found")
        return False
    
    checks = [
        ("Configuration check", "if settings.HOLIDAY_SCHEDULER_ENABLED:"),
        ("Scheduler import", "from app.services.holiday_scheduler import stop_holiday_scheduler"),
        ("Scheduler stop", "stop_holiday_scheduler()"),
        ("Success logging", "Holiday Scheduler stopped"),
        ("Error handling", "except Exception as e:"),
        ("Error logging", "Failed to stop Holiday Scheduler"),
    ]
    
    all_present = True
    for name, pattern in checks:
        if pattern in content:
            print_success(f"Found: {name}")
        else:
            print_error(f"Missing: {name}")
            all_present = False
    
    return all_present


def validate_configuration_flags():
    """Validate that configuration flags are properly used"""
    print_header("6. Validating Configuration Flags Usage")
    
    try:
        from app.core.config import settings
        
        # Check that required settings exist
        required_settings = [
            ('HOLIDAY_AUTO_IMPORT_ON_STARTUP', 'Holiday auto-import flag'),
            ('HOLIDAY_SCHEDULER_ENABLED', 'Holiday scheduler flag'),
        ]
        
        all_present = True
        for setting_name, description in required_settings:
            if hasattr(settings, setting_name):
                value = getattr(settings, setting_name)
                print_success(f"{description}: {setting_name} = {value}")
            else:
                print_error(f"Missing setting: {setting_name}")
                all_present = False
        
        return all_present
        
    except Exception as e:
        print_error(f"Configuration validation failed: {e}")
        return False


def validate_error_handling():
    """Validate error handling and graceful degradation"""
    print_header("7. Validating Error Handling")
    
    main_file = backend_path / "main.py"
    content = main_file.read_text(encoding='utf-8')
    
    checks = [
        ("Startup try-except for holiday import", "try:\n            from app.services.holiday_startup_service"),
        ("Startup except for holiday import", "except Exception as e:\n            logger.error(f\"Failed to initialize holiday data"),
        ("Startup try-except for scheduler", "try:\n            from app.services.holiday_scheduler import start_holiday_scheduler"),
        ("Startup except for scheduler", "except Exception as e:\n            logger.error(f\"Failed to start Holiday Scheduler"),
        ("Shutdown try-except", "try:\n            from app.services.holiday_scheduler import stop_holiday_scheduler"),
        ("Shutdown except", "except Exception as e:\n            logger.error(f\"Failed to stop Holiday Scheduler"),
        ("Graceful degradation comment 1", "# App startet trotzdem (graceful degradation)"),
    ]
    
    all_present = True
    for name, pattern in checks:
        if pattern in content:
            print_success(f"Found: {name}")
        else:
            print_error(f"Missing: {name}")
            all_present = False
    
    return all_present


def validate_logging():
    """Validate proper logging throughout event handlers"""
    print_header("8. Validating Logging")
    
    main_file = backend_path / "main.py"
    content = main_file.read_text(encoding='utf-8')
    
    checks = [
        ("Startup info log", "logger.info(f\"Starting {settings.PROJECT_NAME}"),
        ("Holiday import check log", "logger.info(\"Checking holiday data...\")"),
        ("Holiday import success log", "logger.info(\n                    f\"✅ Holiday import:"),
        ("Holiday import none needed log", "logger.info(\"✅ Holiday data: All years already present\")"),
        ("Scheduler start log", "logger.info(\"Starting Holiday Scheduler...\")"),
        ("Scheduler success log", "logger.info(f\"✅ Holiday Scheduler started"),
        ("Shutdown log", "logger.info(f\"Shutting down {settings.PROJECT_NAME}\")"),
        ("Scheduler stop log", "logger.info(\"Holiday Scheduler stopped\")"),
    ]
    
    all_present = True
    for name, pattern in checks:
        if pattern in content:
            print_success(f"Found: {name}")
        else:
            print_error(f"Missing: {name}")
            all_present = False
    
    return all_present


def main():
    """Run all validations"""
    print_header("Task 22.4 Validation: Startup and Shutdown Event Handlers")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    print_info("Note: Task 22.4 functionality was implemented in Tasks 22.2 and 22.3")
    print_info("This validation confirms the integration is complete and correct\n")
    
    results = {
        "Startup Event Handler": validate_startup_event_handler(),
        "Holiday Startup Service Integration": validate_holiday_startup_service_integration(),
        "Holiday Scheduler Integration": validate_holiday_scheduler_integration(),
        "Shutdown Event Handler": validate_shutdown_event_handler(),
        "Scheduler Shutdown Integration": validate_scheduler_shutdown_integration(),
        "Configuration Flags": validate_configuration_flags(),
        "Error Handling": validate_error_handling(),
        "Logging": validate_logging(),
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
        print(f"\n{Colors.GREEN}{Colors.BOLD}✓ All validations passed! Task 22.4 is complete.{Colors.RESET}")
        print(f"{Colors.GREEN}{Colors.BOLD}  (Functionality was implemented in Tasks 22.2 and 22.3){Colors.RESET}\n")
        return 0
    else:
        print(f"\n{Colors.RED}{Colors.BOLD}✗ Some validations failed. Please review the errors above.{Colors.RESET}\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
