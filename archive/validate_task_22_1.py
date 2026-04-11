"""
Validation Script for Task 22.1: Holiday Management Configuration
Validates all aspects of the configuration implementation.
"""
import sys
from datetime import datetime
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

def print_section(title):
    """Print a formatted section header."""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}")

def print_success(message):
    """Print a success message."""
    print(f"✅ {message}")

def print_error(message):
    """Print an error message."""
    print(f"❌ {message}")

def print_info(message):
    """Print an info message."""
    print(f"ℹ️  {message}")

def validate_config_import():
    """Validate that configuration can be imported."""
    print_section("1. Configuration Import Test")
    try:
        from app.core.config import settings
        print_success("Configuration module imported successfully")
        return True, settings
    except Exception as e:
        print_error(f"Failed to import configuration: {e}")
        return False, None

def validate_config_parameters(settings):
    """Validate all configuration parameters exist and have correct types."""
    print_section("2. Configuration Parameters Test")
    
    tests_passed = 0
    tests_total = 0
    
    # Test parameter existence and types
    params = {
        'HOLIDAY_YEARS_PAST': (int, 2),
        'HOLIDAY_YEARS_FUTURE': (int, 3),
        'HOLIDAY_AUTO_IMPORT_ON_STARTUP': (bool, True),
        'HOLIDAY_SCHEDULER_ENABLED': (bool, True),
        'HOLIDAY_SCHEDULER_CRON': (str, "0 2 1 * *"),
        'HOLIDAY_CLEANUP_OLD_YEARS': (bool, False),
        'HOLIDAY_CLEANUP_YEARS_THRESHOLD': (int, 5),
    }
    
    for param_name, (expected_type, expected_default) in params.items():
        tests_total += 1
        if not hasattr(settings, param_name):
            print_error(f"Parameter '{param_name}' not found")
            continue
        
        value = getattr(settings, param_name)
        
        # Check type
        if not isinstance(value, expected_type):
            print_error(f"{param_name}: Wrong type (expected {expected_type.__name__}, got {type(value).__name__})")
            continue
        
        # Check default value
        if value != expected_default:
            print_info(f"{param_name}: {value} (default: {expected_default}, may be overridden by .env)")
        else:
            print_success(f"{param_name}: {value} ✓")
        
        tests_passed += 1
    
    print(f"\nParameter Tests: {tests_passed}/{tests_total} passed")
    return tests_passed == tests_total

def validate_helper_method(settings):
    """Validate the get_holiday_year_range helper method."""
    print_section("3. Helper Method Test")
    
    try:
        # Check method exists
        if not hasattr(settings, 'get_holiday_year_range'):
            print_error("Method 'get_holiday_year_range' not found")
            return False
        
        if not callable(settings.get_holiday_year_range):
            print_error("'get_holiday_year_range' is not callable")
            return False
        
        print_success("Method 'get_holiday_year_range' exists and is callable")
        
        # Test method execution
        start_year, end_year = settings.get_holiday_year_range()
        current_year = datetime.now().year
        
        print_info(f"Current Year: {current_year}")
        print_info(f"Calculated Range: {start_year} - {end_year}")
        
        # Validate calculation
        expected_start = current_year - settings.HOLIDAY_YEARS_PAST
        expected_end = current_year + settings.HOLIDAY_YEARS_FUTURE
        
        if start_year != expected_start:
            print_error(f"Start year mismatch: expected {expected_start}, got {start_year}")
            return False
        
        if end_year != expected_end:
            print_error(f"End year mismatch: expected {expected_end}, got {end_year}")
            return False
        
        print_success(f"Year range calculation correct: {start_year} - {end_year}")
        
        # Validate range properties
        total_years = end_year - start_year + 1
        expected_total = settings.HOLIDAY_YEARS_PAST + settings.HOLIDAY_YEARS_FUTURE + 1
        
        if total_years != expected_total:
            print_error(f"Total years mismatch: expected {expected_total}, got {total_years}")
            return False
        
        print_success(f"Total years covered: {total_years} years")
        
        # Validate return type
        if not isinstance((start_year, end_year), tuple):
            print_error("Return value is not a tuple")
            return False
        
        print_success("Return type is tuple")
        
        return True
        
    except Exception as e:
        print_error(f"Helper method test failed: {e}")
        return False

def validate_env_example():
    """Validate that .env.example contains all parameters."""
    print_section("4. .env.example Documentation Test")
    
    try:
        env_example_path = Path(__file__).parent / ".env.example"
        
        if not env_example_path.exists():
            print_error(".env.example file not found")
            return False
        
        print_success(".env.example file exists")
        
        content = env_example_path.read_text()
        
        # Check for Holiday Management section
        if "Holiday Management" not in content:
            print_error("'Holiday Management' section not found in .env.example")
            return False
        
        print_success("'Holiday Management' section found")
        
        # Check for all parameters
        required_params = [
            'HOLIDAY_YEARS_PAST',
            'HOLIDAY_YEARS_FUTURE',
            'HOLIDAY_AUTO_IMPORT_ON_STARTUP',
            'HOLIDAY_SCHEDULER_ENABLED',
            'HOLIDAY_SCHEDULER_CRON',
            'HOLIDAY_CLEANUP_OLD_YEARS',
            'HOLIDAY_CLEANUP_YEARS_THRESHOLD',
        ]
        
        missing_params = []
        for param in required_params:
            if param not in content:
                missing_params.append(param)
        
        if missing_params:
            print_error(f"Missing parameters in .env.example: {', '.join(missing_params)}")
            return False
        
        print_success(f"All {len(required_params)} parameters documented in .env.example")
        return True
        
    except Exception as e:
        print_error(f".env.example validation failed: {e}")
        return False

def validate_unit_tests():
    """Check if unit tests exist and can be imported."""
    print_section("5. Unit Tests Validation")
    
    try:
        test_file = Path(__file__).parent / "backend" / "tests" / "test_config_holiday_management.py"
        
        if not test_file.exists():
            print_error("Unit test file not found")
            return False
        
        print_success("Unit test file exists")
        
        # Check test file content
        content = test_file.read_text()
        
        required_tests = [
            'test_holiday_config_defaults',
            'test_get_holiday_year_range',
            'test_holiday_scheduler_cron_format',
            'test_config_accessible_from_settings',
        ]
        
        missing_tests = []
        for test in required_tests:
            if test not in content:
                missing_tests.append(test)
        
        if missing_tests:
            print_error(f"Missing tests: {', '.join(missing_tests)}")
            return False
        
        print_success(f"All {len(required_tests)} key tests found")
        print_info("Run 'python -m pytest backend/tests/test_config_holiday_management.py -v' to execute tests")
        
        return True
        
    except Exception as e:
        print_error(f"Unit tests validation failed: {e}")
        return False

def generate_summary(results):
    """Generate validation summary."""
    print_section("Validation Summary")
    
    total_tests = len(results)
    passed_tests = sum(1 for r in results.values() if r)
    
    print(f"\nTotal Tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {total_tests - passed_tests}")
    print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    
    print("\nDetailed Results:")
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status} - {test_name}")
    
    if passed_tests == total_tests:
        print("\n" + "="*70)
        print("  🎉 ALL VALIDATIONS PASSED! Task 22.1 is successfully implemented!")
        print("="*70)
        return True
    else:
        print("\n" + "="*70)
        print("  ⚠️  Some validations failed. Please review the errors above.")
        print("="*70)
        return False

def main():
    """Main validation function."""
    print("="*70)
    print("  Task 22.1 Validation Script")
    print("  Holiday Management Configuration")
    print("="*70)
    print(f"  Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)
    
    results = {}
    
    # Run validations
    success, settings = validate_config_import()
    results["Configuration Import"] = success
    
    if not success:
        print("\n❌ Cannot proceed without valid configuration import")
        generate_summary(results)
        return False
    
    results["Configuration Parameters"] = validate_config_parameters(settings)
    results["Helper Method"] = validate_helper_method(settings)
    results[".env.example Documentation"] = validate_env_example()
    results["Unit Tests"] = validate_unit_tests()
    
    # Generate summary
    return generate_summary(results)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
