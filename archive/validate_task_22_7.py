"""
Validation Script for Task 22.7: Functional Tests and Documentation

This script validates:
1. E2E functional test exists and is complete
2. Admin API tests exist and are complete
3. Documentation exists and is comprehensive
4. All previous validations (22.1-22.6) still pass
5. System integration
"""
import sys
from pathlib import Path
from datetime import datetime
import subprocess

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


def validate_e2e_test():
    """Validate E2E functional test"""
    print_header("1. Validating E2E Functional Test")
    
    test_file = backend_path / "tests" / "test_holiday_management_e2e.py"
    
    if not test_file.exists():
        print_error(f"E2E test file not found: {test_file}")
        return False
    
    print_success("E2E test file exists")
    
    # Check test content
    content = test_file.read_text(encoding='utf-8')
    
    required_classes = [
        "TestStartupImport",
        "TestSchedulerOperation",
        "TestErrorHandling",
        "TestIntegration"
    ]
    
    all_present = True
    for test_class in required_classes:
        if f"class {test_class}" in content:
            print_success(f"Found test class: {test_class}")
        else:
            print_error(f"Missing test class: {test_class}")
            all_present = False
    
    # Check key test methods
    key_tests = [
        "test_startup_import_creates_holidays",
        "test_scheduler_starts_automatically",
        "test_api_failure_handling",
        "test_full_workflow"
    ]
    
    for test in key_tests:
        if f"def {test}" in content:
            print_success(f"Found test: {test}")
        else:
            print_error(f"Missing test: {test}")
            all_present = False
    
    return all_present


def validate_admin_api_tests():
    """Validate Admin API tests"""
    print_header("2. Validating Admin API Tests")
    
    test_file = backend_path / "tests" / "test_holiday_admin_api.py"
    
    if not test_file.exists():
        print_error(f"Admin API test file not found: {test_file}")
        return False
    
    print_success("Admin API test file exists")
    
    content = test_file.read_text(encoding='utf-8')
    
    # Check test classes
    required_classes = [
        "TestImportEndpoints",
        "TestSchedulerEndpoints",
        "TestAuthentication",
        "TestErrorHandling"
    ]
    
    all_present = True
    for test_class in required_classes:
        if f"class {test_class}" in content:
            print_success(f"Found test class: {test_class}")
        else:
            print_error(f"Missing test class: {test_class}")
            all_present = False
    
    # Check endpoint tests
    endpoint_tests = [
        "test_trigger_import",
        "test_get_import_status",
        "test_get_scheduler_status",
        "test_start_scheduler",
        "test_stop_scheduler",
        "test_trigger_manual_job",
        "test_get_scheduler_jobs",
        "test_get_job_executions"
    ]
    
    for test in endpoint_tests:
        if f"def {test}" in content:
            print_success(f"Found endpoint test: {test}")
        else:
            print_error(f"Missing endpoint test: {test}")
            all_present = False
    
    return all_present


def validate_documentation():
    """Validate documentation"""
    print_header("3. Validating Documentation")
    
    doc_file = Path(__file__).parent / "docs" / "HOLIDAY_MANAGEMENT.md"
    
    if not doc_file.exists():
        print_error(f"Documentation file not found: {doc_file}")
        return False
    
    print_success("Documentation file exists")
    
    content = doc_file.read_text(encoding='utf-8')
    
    # Check required sections
    required_sections = [
        "# Multi-Year Holiday Management System",
        "## Übersicht",
        "## Architektur",
        "## Konfiguration",
        "## Startup-Verhalten",
        "## Scheduler-Operation",
        "## Admin API",
        "## Troubleshooting",
        "## Migration vom alten System",
        "## Best Practices"
    ]
    
    all_present = True
    for section in required_sections:
        if section in content:
            print_success(f"Found section: {section}")
        else:
            print_error(f"Missing section: {section}")
            all_present = False
    
    # Check for all 8 endpoints documented
    endpoints = [
        "/api/v1/holidays/admin/import",
        "/api/v1/holidays/admin/import/status",
        "/api/v1/holidays/admin/scheduler/status",
        "/api/v1/holidays/admin/scheduler/start",
        "/api/v1/holidays/admin/scheduler/stop",
        "/api/v1/holidays/admin/scheduler/trigger",
        "/api/v1/holidays/admin/scheduler/jobs",
        "/api/v1/holidays/admin/scheduler/executions"
    ]
    
    for endpoint in endpoints:
        if endpoint in content:
            print_success(f"Endpoint documented: {endpoint}")
        else:
            print_error(f"Endpoint not documented: {endpoint}")
            all_present = False
    
    # Check for code examples
    if "```bash" in content and "curl" in content:
        print_success("Found curl examples")
    else:
        print_error("Missing curl examples")
        all_present = False
    
    return all_present


def validate_previous_validations():
    """Run all previous validation scripts"""
    print_header("4. Validating Previous Tasks (22.1-22.6)")
    
    validation_scripts = [
        "validate_task_22_1.py",
        "validate_task_22_2.py",
        "validate_task_22_3.py",
        "validate_task_22_4.py",
        "validate_task_22_5.py",
        "validate_task_22_6.py"
    ]
    
    all_passed = True
    for script in validation_scripts:
        script_path = Path(__file__).parent / script
        
        if not script_path.exists():
            print_error(f"Validation script not found: {script}")
            all_passed = False
            continue
        
        try:
            result = subprocess.run(
                [sys.executable, str(script_path)],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                print_success(f"Validation passed: {script}")
            else:
                print_error(f"Validation failed: {script}")
                all_passed = False
        except subprocess.TimeoutExpired:
            print_error(f"Validation timeout: {script}")
            all_passed = False
        except Exception as e:
            print_error(f"Error running {script}: {e}")
            all_passed = False
    
    return all_passed


def validate_file_structure():
    """Validate complete file structure"""
    print_header("5. Validating File Structure")
    
    required_files = [
        ("E2E Test", backend_path / "tests" / "test_holiday_management_e2e.py"),
        ("Admin API Test", backend_path / "tests" / "test_holiday_admin_api.py"),
        ("Documentation", Path(__file__).parent / "docs" / "HOLIDAY_MANAGEMENT.md"),
        ("Config Test", backend_path / "tests" / "test_config_holiday_management.py"),
        ("Startup Service Test", backend_path / "tests" / "test_holiday_startup_service.py"),
        ("Scheduler Test", backend_path / "tests" / "test_holiday_scheduler.py"),
    ]
    
    all_exist = True
    for name, file_path in required_files:
        if file_path.exists():
            print_success(f"Found: {name}")
        else:
            print_error(f"Missing: {name}")
            all_exist = False
    
    return all_exist


def main():
    """Run all validations"""
    print_header("Task 22.7 Validation: Functional Tests and Documentation")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    print_info("Validating comprehensive functional tests and documentation")
    print_info("This includes E2E tests, Admin API tests, and complete system documentation\n")
    
    results = {
        "E2E Functional Test": validate_e2e_test(),
        "Admin API Tests": validate_admin_api_tests(),
        "Documentation": validate_documentation(),
        "Previous Validations (22.1-22.6)": validate_previous_validations(),
        "File Structure": validate_file_structure(),
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
        print(f"\n{Colors.GREEN}{Colors.BOLD}✓ All validations passed! Task 22.7 is complete.{Colors.RESET}")
        print(f"\n{Colors.GREEN}Deliverables:{Colors.RESET}")
        print(f"  ✓ E2E Functional Test (test_holiday_management_e2e.py)")
        print(f"  ✓ Admin API Tests (test_holiday_admin_api.py)")
        print(f"  ✓ Comprehensive Documentation (docs/HOLIDAY_MANAGEMENT.md)")
        print(f"  ✓ All previous validations still passing")
        print(f"\n{Colors.GREEN}Next Steps:{Colors.RESET}")
        print(f"  1. Run: python stop.py")
        print(f"  2. Run: python start.py")
        print(f"  3. Perform Playwright visual tests")
        print(f"  4. Mark Task 22.7 as done\n")
        return 0
    else:
        print(f"\n{Colors.RED}{Colors.BOLD}✗ Some validations failed. Please review the errors above.{Colors.RESET}\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
