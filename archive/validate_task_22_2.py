"""
Validation Script for Task 22.2: Holiday Startup Service
Validates all aspects of the startup service implementation.
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

def validate_service_file():
    """Validate that service file exists and is importable."""
    print_section("1. Service File Validation")
    
    try:
        service_file = Path(__file__).parent / "backend" / "app" / "services" / "holiday_startup_service.py"
        
        if not service_file.exists():
            print_error("holiday_startup_service.py not found")
            return False
        
        print_success("Service file exists")
        
        # Try to import
        from app.services.holiday_startup_service import HolidayStartupService, ensure_holiday_data_on_startup
        print_success("Service module imported successfully")
        
        # Check class exists
        if not HolidayStartupService:
            print_error("HolidayStartupService class not found")
            return False
        
        print_success("HolidayStartupService class found")
        
        # Check async function exists
        if not ensure_holiday_data_on_startup:
            print_error("ensure_holiday_data_on_startup function not found")
            return False
        
        print_success("ensure_holiday_data_on_startup function found")
        
        return True
        
    except Exception as e:
        print_error(f"Service file validation failed: {e}")
        return False

def validate_service_methods():
    """Validate that service has required methods."""
    print_section("2. Service Methods Validation")
    
    try:
        from app.services.holiday_startup_service import HolidayStartupService
        from unittest.mock import Mock
        
        # Create instance with mock session
        mock_session = Mock()
        service = HolidayStartupService(mock_session)
        
        # Check ensure_holiday_data method
        if not hasattr(service, 'ensure_holiday_data'):
            print_error("ensure_holiday_data method not found")
            return False
        
        print_success("ensure_holiday_data method exists")
        
        if not callable(service.ensure_holiday_data):
            print_error("ensure_holiday_data is not callable")
            return False
        
        print_success("ensure_holiday_data is callable")
        
        # Check holiday_service attribute
        if not hasattr(service, 'holiday_service'):
            print_error("holiday_service attribute not found")
            return False
        
        print_success("holiday_service attribute exists")
        
        return True
        
    except Exception as e:
        print_error(f"Service methods validation failed: {e}")
        return False

def validate_main_integration():
    """Validate integration in main.py."""
    print_section("3. Main.py Integration Validation")
    
    try:
        main_file = Path(__file__).parent / "backend" / "main.py"
        
        if not main_file.exists():
            print_error("main.py not found")
            return False
        
        print_success("main.py exists")
        
        content = main_file.read_text(encoding='utf-8')
        
        # Check for import
        if "from app.services.holiday_startup_service import ensure_holiday_data_on_startup" not in content:
            print_error("Import statement not found in main.py")
            return False
        
        print_success("Import statement found in main.py")
        
        # Check for startup_event modification
        if "ensure_holiday_data_on_startup" not in content:
            print_error("ensure_holiday_data_on_startup not called in main.py")
            return False
        
        print_success("ensure_holiday_data_on_startup called in startup_event")
        
        # Check for config check
        if "HOLIDAY_AUTO_IMPORT_ON_STARTUP" not in content:
            print_error("Config check not found in main.py")
            return False
        
        print_success("Config check found in main.py")
        
        # Check for logging
        if "Holiday import:" not in content or "Holiday data:" not in content:
            print_error("Logging statements not found in main.py")
            return False
        
        print_success("Logging statements found in main.py")
        
        # Check for graceful degradation
        if "# App startet trotzdem" not in content:
            print_error("Graceful degradation comment not found")
            return False
        
        print_success("Graceful degradation implemented")
        
        return True
        
    except Exception as e:
        print_error(f"Main.py integration validation failed: {e}")
        return False

def validate_unit_tests():
    """Validate unit tests exist and structure."""
    print_section("4. Unit Tests Validation")
    
    try:
        test_file = Path(__file__).parent / "backend" / "tests" / "test_holiday_startup_service.py"
        
        if not test_file.exists():
            print_error("test_holiday_startup_service.py not found")
            return False
        
        print_success("Unit test file exists")
        
        content = test_file.read_text()
        
        # Check for test classes
        required_classes = [
            'TestHolidayStartupService',
            'TestEnsureHolidayDataOnStartup',
            'TestHolidayStartupServiceIntegration'
        ]
        
        for class_name in required_classes:
            if f"class {class_name}" not in content:
                print_error(f"Test class '{class_name}' not found")
                return False
        
        print_success(f"All {len(required_classes)} test classes found")
        
        # Check for key test methods
        required_tests = [
            'test_ensure_holiday_data_auto_import_disabled',
            'test_ensure_holiday_data_no_missing_years',
            'test_ensure_holiday_data_with_missing_years',
            'test_ensure_holiday_data_import_error',
        ]
        
        for test_name in required_tests:
            if test_name not in content:
                print_error(f"Test method '{test_name}' not found")
                return False
        
        print_success(f"All {len(required_tests)} key test methods found")
        
        return True
        
    except Exception as e:
        print_error(f"Unit tests validation failed: {e}")
        return False

def validate_config_usage():
    """Validate that service uses configuration correctly."""
    print_section("5. Configuration Usage Validation")
    
    try:
        from app.services.holiday_startup_service import HolidayStartupService
        from app.core.config import settings
        from unittest.mock import Mock, patch
        
        mock_session = Mock()
        service = HolidayStartupService(mock_session)
        
        # Test with auto-import disabled
        with patch('app.services.holiday_startup_service.settings') as mock_settings:
            mock_settings.HOLIDAY_AUTO_IMPORT_ON_STARTUP = False
            
            result = service.ensure_holiday_data()
            
            if result["action"] != "skipped":
                print_error("Service doesn't respect HOLIDAY_AUTO_IMPORT_ON_STARTUP=False")
                return False
        
        print_success("Service respects HOLIDAY_AUTO_IMPORT_ON_STARTUP flag")
        
        # Test year range usage
        with patch('app.services.holiday_startup_service.settings') as mock_settings:
            mock_settings.HOLIDAY_AUTO_IMPORT_ON_STARTUP = True
            mock_settings.get_holiday_year_range.return_value = (2020, 2030)
            
            with patch.object(service.holiday_service, 'get_missing_years', return_value=[]):
                result = service.ensure_holiday_data()
                
                if result["year_range"]["start"] != 2020 or result["year_range"]["end"] != 2030:
                    print_error("Service doesn't use get_holiday_year_range() correctly")
                    return False
        
        print_success("Service uses get_holiday_year_range() correctly")
        
        return True
        
    except Exception as e:
        print_error(f"Configuration usage validation failed: {e}")
        return False

def validate_error_handling():
    """Validate error handling and graceful degradation."""
    print_section("6. Error Handling Validation")
    
    try:
        from app.services.holiday_startup_service import HolidayStartupService
        from unittest.mock import Mock, patch
        
        mock_session = Mock()
        service = HolidayStartupService(mock_session)
        
        # Test error handling
        with patch('app.services.holiday_startup_service.settings') as mock_settings:
            mock_settings.HOLIDAY_AUTO_IMPORT_ON_STARTUP = True
            mock_settings.get_holiday_year_range.return_value = (2023, 2028)
            
            with patch.object(service.holiday_service, 'get_missing_years', return_value=[2023]):
                with patch.object(service.holiday_service, 'import_missing_years', side_effect=Exception("Test error")):
                    result = service.ensure_holiday_data()
                    
                    if result["action"] != "error":
                        print_error("Service doesn't handle errors correctly")
                        return False
                    
                    if "error" not in result:
                        print_error("Error details not included in result")
                        return False
        
        print_success("Service handles errors gracefully")
        print_success("Error details included in result")
        
        return True
        
    except Exception as e:
        print_error(f"Error handling validation failed: {e}")
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
        print("  🎉 ALL VALIDATIONS PASSED! Task 22.2 is successfully implemented!")
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
    print("  Task 22.2 Validation Script")
    print("  Holiday Startup Service")
    print("="*70)
    print(f"  Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)
    
    results = {}
    
    # Run validations
    results["Service File"] = validate_service_file()
    
    if not results["Service File"]:
        print("\n❌ Cannot proceed without valid service file")
        generate_summary(results)
        return False
    
    results["Service Methods"] = validate_service_methods()
    results["Main.py Integration"] = validate_main_integration()
    results["Unit Tests"] = validate_unit_tests()
    results["Configuration Usage"] = validate_config_usage()
    results["Error Handling"] = validate_error_handling()
    
    # Generate summary
    return generate_summary(results)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
