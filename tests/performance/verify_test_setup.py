#!/usr/bin/env python3
"""
Test Setup Verification Script
Überprüft die Konfiguration und Funktionalität der Performance Tests
"""

import os
import sys
import asyncio
import requests
from datetime import datetime
from test_data_generator import TestDataGenerator
from config import config, validate_config

class TestSetupVerifier:
    """Verifies test setup and configuration"""
    
    def __init__(self):
        self.issues = []
        self.warnings = []
        
    def check_environment(self) -> bool:
        """Überprüft die Test-Umgebung"""
        print("=== Environment Check ===")
        
        # Konfiguration prüfen
        if not validate_config():
            self.issues.append("Configuration validation failed")
            return False
        
        # Verzeichnisse prüfen
        required_dirs = [
            "tests/performance/reports",
            "tests/performance/logs",
            "tests/performance/screenshots"
        ]
        
        for dir_path in required_dirs:
            if not os.path.exists(dir_path):
                try:
                    os.makedirs(dir_path, exist_ok=True)
                    print(f"✅ Created directory: {dir_path}")
                except Exception as e:
                    self.issues.append(f"Cannot create directory {dir_path}: {e}")
            else:
                print(f"✅ Directory exists: {dir_path}")
        
        # API Erreichbarkeit prüfen
        try:
            response = requests.get(f"{config.base_url}/docs", timeout=10)
            if response.status_code == 200:
                print(f"✅ API is reachable at {config.base_url}")
            else:
                self.warnings.append(f"API returned status {response.status_code}")
        except Exception as e:
            self.issues.append(f"API not reachable: {e}")
        
        # Frontend Erreichbarkeit prüfen
        try:
            response = requests.get(config.frontend_url, timeout=10)
            if response.status_code == 200:
                print(f"✅ Frontend is reachable at {config.frontend_url}")
            else:
                self.warnings.append(f"Frontend returned status {response.status_code}")
        except Exception as e:
            self.warnings.append(f"Frontend not reachable: {e}")
        
        return len(self.issues) == 0
    
    def check_authentication(self) -> bool:
        """Überprüft die Authentifizierung"""
        print("\n=== Authentication Check ===")
        
        generator = TestDataGenerator()
        
        if generator.authenticate():
            print(f"✅ Authentication successful for user: {config.auth_username}")
            
            # Bundesländer laden testen
            generator.load_federal_states()
            if generator.federal_states:
                print(f"✅ Federal states loaded: {len(generator.federal_states)} states")
            else:
                self.warnings.append("No federal states loaded")
            
            return True
        else:
            self.issues.append("Authentication failed")
            return False
    
    def check_data_operations(self) -> bool:
        """Überprüft Datenoperationen"""
        print("\n=== Data Operations Check ===")
        
        generator = TestDataGenerator()
        
        if not generator.authenticate():
            self.issues.append("Cannot authenticate for data operations test")
            return False
        
        try:
            # Aktuelle Mitarbeiter abrufen
            initial_employees = generator.get_all_employees()
            print(f"✅ Current employees in system: {len(initial_employees)}")
            
            # Test-Mitarbeiter erstellen (nur 1 für Verifikation)
            print("Creating test employee...")
            test_employees = generator.create_employees(count=1)
            
            if test_employees:
                print(f"✅ Test employee created successfully")
                
                # Urlaubsanspruch erstellen
                employee_id = test_employees[0]["id"]
                vacation_allowances = generator.create_vacation_allowances([employee_id], 1)
                
                if vacation_allowances:
                    print(f"✅ Vacation allowance created successfully")
                else:
                    self.warnings.append("Vacation allowance creation failed")
                
                # Cleanup
                generator.cleanup_test_data()
                
                # Verifikation nach Cleanup
                final_employees = generator.get_all_employees()
                if len(final_employees) == len(initial_employees):
                    print(f"✅ Cleanup successful - back to {len(final_employees)} employees")
                else:
                    self.warnings.append(f"Cleanup incomplete: {len(final_employees)} vs {len(initial_employees)} employees")
                
                return True
            else:
                self.issues.append("Test employee creation failed")
                return False
                
        except Exception as e:
            self.issues.append(f"Data operations test failed: {e}")
            return False
    
    def check_dependencies(self) -> bool:
        """Überprüft Python-Dependencies"""
        print("\n=== Dependencies Check ===")
        
        required_packages = [
            'requests',
            'faker',
            'locust',
            'psutil',
            'playwright',
            'asyncio'
        ]
        
        missing_packages = []
        
        for package in required_packages:
            try:
                __import__(package)
                print(f"✅ {package} is available")
            except ImportError:
                missing_packages.append(package)
                print(f"❌ {package} is missing")
        
        if missing_packages:
            self.issues.append(f"Missing packages: {', '.join(missing_packages)}")
            print(f"\nInstall missing packages with:")
            print(f"pip install {' '.join(missing_packages)}")
            return False
        
        return True
    
    def check_test_files(self) -> bool:
        """Überprüft Test-Dateien"""
        print("\n=== Test Files Check ===")
        
        required_files = [
            'config.py',
            'locustfile.py',
            'db_performance.py',
            'frontend_performance.py',
            'memory_monitor.py',
            'test_data_generator.py',
            'run_phase1_tests.py'
        ]
        
        missing_files = []
        
        for file_name in required_files:
            file_path = f"tests/performance/{file_name}"
            if os.path.exists(file_path):
                print(f"✅ {file_name} exists")
            else:
                missing_files.append(file_name)
                print(f"❌ {file_name} is missing")
        
        if missing_files:
            self.issues.append(f"Missing test files: {', '.join(missing_files)}")
            return False
        
        return True
    
    async def run_full_verification(self) -> bool:
        """Führt vollständige Verifikation aus"""
        print("🔍 Starting Test Setup Verification")
        print("=" * 60)
        
        checks = [
            ("Environment", self.check_environment),
            ("Dependencies", self.check_dependencies),
            ("Test Files", self.check_test_files),
            ("Authentication", self.check_authentication),
            ("Data Operations", self.check_data_operations)
        ]
        
        all_passed = True
        
        for check_name, check_func in checks:
            try:
                if asyncio.iscoroutinefunction(check_func):
                    result = await check_func()
                else:
                    result = check_func()
                
                if not result:
                    all_passed = False
                    print(f"❌ {check_name} check failed")
                else:
                    print(f"✅ {check_name} check passed")
                    
            except Exception as e:
                all_passed = False
                self.issues.append(f"{check_name} check error: {e}")
                print(f"❌ {check_name} check error: {e}")
        
        # Zusammenfassung
        print("\n" + "=" * 60)
        print("VERIFICATION SUMMARY")
        print("=" * 60)
        
        if self.issues:
            print("❌ ISSUES FOUND:")
            for issue in self.issues:
                print(f"  - {issue}")
        
        if self.warnings:
            print("\n⚠️ WARNINGS:")
            for warning in self.warnings:
                print(f"  - {warning}")
        
        if all_passed and not self.issues:
            print("\n✅ ALL CHECKS PASSED!")
            print("The test environment is ready for Phase 1 performance testing.")
            print("\nNext steps:")
            print("1. Run: python run_phase1_tests.py")
            print("2. Check reports in tests/performance/reports/")
        else:
            print("\n❌ VERIFICATION FAILED!")
            print("Please fix the issues above before running performance tests.")
        
        print("=" * 60)
        
        return all_passed and not self.issues

async def main():
    """Hauptfunktion"""
    verifier = TestSetupVerifier()
    
    success = await verifier.run_full_verification()
    
    # Exit code basierend auf Ergebnis
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    asyncio.run(main())
