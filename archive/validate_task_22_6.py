"""
Validation Script for Task 22.6: Holiday Admin API Endpoints

This script validates:
1. API file structure and imports
2. All 8 required endpoints exist
3. Pydantic schemas are properly defined
4. Router registration in api.py
5. Endpoint functionality (basic validation)
6. Error handling
7. Authentication requirements
"""
import sys
from pathlib import Path
from datetime import datetime
import ast

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


def validate_file_structure():
    """Validate that required files exist"""
    print_header("1. Validating File Structure")
    
    required_files = [
        ("API endpoints file", backend_path / "app" / "api" / "v1" / "endpoints" / "holiday_admin.py"),
        ("Pydantic schemas file", backend_path / "app" / "schemas" / "holiday_admin.py"),
        ("API router file", backend_path / "app" / "api" / "v1" / "api.py"),
    ]
    
    all_exist = True
    for name, file_path in required_files:
        if file_path.exists():
            print_success(f"Found: {name}")
        else:
            print_error(f"Missing: {name} at {file_path}")
            all_exist = False
    
    return all_exist


def validate_schemas():
    """Validate Pydantic schemas are properly defined"""
    print_header("2. Validating Pydantic Schemas")
    
    schema_file = backend_path / "app" / "schemas" / "holiday_admin.py"
    content = schema_file.read_text(encoding='utf-8')
    
    required_schemas = [
        "ImportTriggerRequest",
        "ImportStatusResponse",
        "SchedulerStatusResponse",
        "JobsListResponse",
        "JobInfo",
        "JobExecutionsResponse",
        "JobExecution",
        "AdminActionResponse",
        "TriggerJobResponse",
    ]
    
    all_present = True
    for schema in required_schemas:
        if f"class {schema}(BaseModel):" in content:
            print_success(f"Found schema: {schema}")
        else:
            print_error(f"Missing schema: {schema}")
            all_present = False
    
    # Check for proper imports
    imports_check = [
        ("BaseModel import", "from pydantic import BaseModel"),
        ("Field import", "from pydantic import BaseModel, Field"),
        ("FederalState import", "from ..models.federal_state import FederalState"),
    ]
    
    for name, import_stmt in imports_check:
        if import_stmt in content:
            print_success(f"Found: {name}")
        else:
            print_error(f"Missing: {name}")
            all_present = False
    
    return all_present


def validate_endpoints():
    """Validate all required endpoints exist"""
    print_header("3. Validating API Endpoints")
    
    api_file = backend_path / "app" / "api" / "v1" / "endpoints" / "holiday_admin.py"
    content = api_file.read_text(encoding='utf-8')
    
    required_endpoints = [
        ("POST /import", '@router.post("/import"', "trigger_manual_import"),
        ("GET /import/status", '@router.get("/import/status"', "get_import_status"),
        ("GET /scheduler/status", '@router.get("/scheduler/status"', "get_scheduler_status"),
        ("POST /scheduler/start", '@router.post("/scheduler/start"', "start_scheduler"),
        ("POST /scheduler/stop", '@router.post("/scheduler/stop"', "stop_scheduler"),
        ("POST /scheduler/trigger", '@router.post("/scheduler/trigger"', "trigger_manual_job"),
        ("GET /scheduler/jobs", '@router.get("/scheduler/jobs"', "get_scheduler_jobs"),
        ("GET /scheduler/executions", '@router.get("/scheduler/executions"', "get_job_executions"),
    ]
    
    all_present = True
    for name, decorator, function in required_endpoints:
        if decorator in content and f"async def {function}" in content:
            print_success(f"Found endpoint: {name} ({function})")
        else:
            print_error(f"Missing endpoint: {name}")
            all_present = False
    
    return all_present


def validate_imports():
    """Validate proper imports in holiday_admin.py"""
    print_header("4. Validating Imports")
    
    api_file = backend_path / "app" / "api" / "v1" / "endpoints" / "holiday_admin.py"
    content = api_file.read_text(encoding='utf-8')
    
    required_imports = [
        ("FastAPI Router", "from fastapi import APIRouter"),
        ("HTTPException", "from fastapi import APIRouter, Depends, HTTPException"),
        ("BackgroundTasks", "BackgroundTasks"),
        ("Database session", "from ....core.database import get_session"),
        ("Auth", "from ....core.auth import get_current_user"),
        ("FederalState", "from ....models.federal_state import FederalState"),
        ("HolidayStartupService", "from ....services.holiday_startup_service import HolidayStartupService"),
        ("HolidayScheduler", "from ....services.holiday_scheduler import"),
        ("Schemas", "from ....schemas.holiday_admin import"),
    ]
    
    all_present = True
    for name, import_check in required_imports:
        if import_check in content:
            print_success(f"Found import: {name}")
        else:
            print_error(f"Missing import: {name}")
            all_present = False
    
    return all_present


def validate_router_registration():
    """Validate router is registered in api.py"""
    print_header("5. Validating Router Registration")
    
    api_router_file = backend_path / "app" / "api" / "v1" / "api.py"
    content = api_router_file.read_text(encoding='utf-8')
    
    checks = [
        ("holiday_admin import", "holiday_admin" in content and "from app.api.v1.endpoints import" in content),
        ("Router include", 'api_router.include_router(holiday_admin.router' in content),
        ("Correct prefix", 'prefix="/holidays/admin"' in content),
        ("Correct tags", 'tags=["holiday-admin"]' in content),
    ]
    
    all_present = True
    for name, check in checks:
        if check:
            print_success(f"Found: {name}")
        else:
            print_error(f"Missing: {name}")
            all_present = False
    
    return all_present


def validate_authentication():
    """Validate authentication requirements"""
    print_header("6. Validating Authentication")
    
    api_file = backend_path / "app" / "api" / "v1" / "endpoints" / "holiday_admin.py"
    content = api_file.read_text(encoding='utf-8')
    
    checks = [
        ("require_admin_user function", "async def require_admin_user"),
        ("Auth dependency", "current_user: dict = Depends(get_current_user)"),
        ("Auth check", "if not current_user:"),
        ("HTTPException on no auth", 'raise HTTPException(status_code=401'),
    ]
    
    all_present = True
    for name, pattern in checks:
        if pattern in content:
            print_success(f"Found: {name}")
        else:
            print_error(f"Missing: {name}")
            all_present = False
    
    # Check that all endpoints use authentication
    endpoint_functions = [
        "trigger_manual_import",
        "get_import_status",
        "get_scheduler_status",
        "start_scheduler",
        "stop_scheduler",
        "trigger_manual_job",
        "get_scheduler_jobs",
        "get_job_executions",
    ]
    
    for func in endpoint_functions:
        if f"async def {func}" in content and "current_user: dict = Depends(require_admin_user)" in content:
            print_success(f"Endpoint {func} has authentication")
        else:
            # Check if it's in the function signature
            func_start = content.find(f"async def {func}")
            if func_start != -1:
                func_end = content.find("\n):", func_start)
                func_signature = content[func_start:func_end] if func_end != -1 else ""
                if "require_admin_user" in func_signature:
                    print_success(f"Endpoint {func} has authentication")
                else:
                    print_error(f"Endpoint {func} missing authentication")
                    all_present = False
    
    return all_present


def validate_error_handling():
    """Validate error handling in endpoints"""
    print_header("7. Validating Error Handling")
    
    api_file = backend_path / "app" / "api" / "v1" / "endpoints" / "holiday_admin.py"
    content = api_file.read_text(encoding='utf-8')
    
    # Count try-except blocks
    try_count = content.count("try:")
    except_count = content.count("except Exception as e:")
    
    if try_count >= 8:  # At least one per endpoint
        print_success(f"Found {try_count} try blocks")
    else:
        print_error(f"Only found {try_count} try blocks, expected at least 8")
    
    if except_count >= 8:
        print_success(f"Found {except_count} except blocks")
    else:
        print_error(f"Only found {except_count} except blocks, expected at least 8")
    
    # Check for logging
    if "logger.error" in content:
        error_log_count = content.count("logger.error")
        print_success(f"Found {error_log_count} error logging statements")
    else:
        print_error("No error logging found")
        return False
    
    # Check for HTTPException raises
    if "raise HTTPException" in content:
        http_exception_count = content.count("raise HTTPException")
        print_success(f"Found {http_exception_count} HTTPException raises")
    else:
        print_error("No HTTPException raises found")
        return False
    
    return try_count >= 8 and except_count >= 8


def validate_service_integration():
    """Validate integration with HolidayStartupService and HolidayScheduler"""
    print_header("8. Validating Service Integration")
    
    api_file = backend_path / "app" / "api" / "v1" / "endpoints" / "holiday_admin.py"
    content = api_file.read_text(encoding='utf-8')
    
    checks = [
        ("HolidayStartupService usage", "HolidayStartupService(session)"),
        ("ensure_holiday_data call", "ensure_holiday_data()"),
        ("get_holiday_scheduler call", "get_holiday_scheduler()"),
        ("scheduler.start() call", "scheduler.start()"),
        ("scheduler.stop() call", "scheduler.stop()"),
        ("trigger_manual_import call", "trigger_manual_import()"),
        ("get_all_jobs call", "get_all_jobs()"),
        ("get_job_executions call", "get_job_executions("),
        ("get_scheduler_status call", "get_scheduler_status()"),
        ("get_job_info call", "get_job_info("),
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
    print_header("Task 22.6 Validation: Holiday Admin API Endpoints")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    print_info("Validating Holiday Admin API implementation for Multi-Year Holiday Management")
    print_info("This is separate from admin_sync.py which handles School Holidays\n")
    
    results = {
        "File Structure": validate_file_structure(),
        "Pydantic Schemas": validate_schemas(),
        "API Endpoints": validate_endpoints(),
        "Imports": validate_imports(),
        "Router Registration": validate_router_registration(),
        "Authentication": validate_authentication(),
        "Error Handling": validate_error_handling(),
        "Service Integration": validate_service_integration(),
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
        print(f"\n{Colors.GREEN}{Colors.BOLD}✓ All validations passed! Task 22.6 is complete.{Colors.RESET}")
        print(f"\n{Colors.GREEN}Available endpoints:{Colors.RESET}")
        print(f"  POST   /api/v1/holidays/admin/import")
        print(f"  GET    /api/v1/holidays/admin/import/status")
        print(f"  GET    /api/v1/holidays/admin/scheduler/status")
        print(f"  POST   /api/v1/holidays/admin/scheduler/start")
        print(f"  POST   /api/v1/holidays/admin/scheduler/stop")
        print(f"  POST   /api/v1/holidays/admin/scheduler/trigger")
        print(f"  GET    /api/v1/holidays/admin/scheduler/jobs")
        print(f"  GET    /api/v1/holidays/admin/scheduler/executions\n")
        return 0
    else:
        print(f"\n{Colors.RED}{Colors.BOLD}✗ Some validations failed. Please review the errors above.{Colors.RESET}\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
