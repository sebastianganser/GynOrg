"""
Complete Employee Lifecycle Test for GynOrg Application
Tests the entire employee lifecycle from creation to deletion with all integrations.

This test covers:
- Employee CRUD operations
- VacationAllowance integration
- Data integrity and relationships
- Validation and error handling
- Performance metrics
- Complete cleanup verification

Author: AI Assistant
Date: 2025-01-22
Task: 17.9 - Complete Employee Lifecycle Test
"""

import requests
import json
import time
from datetime import datetime, date, timedelta
from typing import Dict, List, Optional, Any
import uuid

class EmployeeLifecycleTest:
    """Complete Employee Lifecycle Test Suite"""
    
    def __init__(self, base_url: str = "http://localhost:8000/api/v1"):
        self.base_url = base_url
        self.headers = None
        self.test_data = {
            'employees': [],
            'vacation_allowances': [],
            'created_ids': {'employees': [], 'vacation_allowances': []}
        }
        self.metrics = {
            'start_time': None,
            'phase_times': {},
            'operations_count': 0,
            'api_calls': 0
        }
        
    def log(self, message: str, level: str = "INFO"):
        """Enhanced logging with timestamps"""
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        print(f"[{timestamp}] {level}: {message}")
        
    def start_metrics(self):
        """Start performance metrics tracking"""
        self.metrics['start_time'] = time.time()
        
    def record_phase_time(self, phase_name: str):
        """Record time for a test phase"""
        if self.metrics['start_time']:
            elapsed = time.time() - self.metrics['start_time']
            self.metrics['phase_times'][phase_name] = elapsed
            self.log(f"Phase '{phase_name}' completed in {elapsed:.2f}s")
            
    def api_call(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """Wrapper for API calls with metrics tracking"""
        self.metrics['api_calls'] += 1
        url = f"{self.base_url}{endpoint}"
        
        if self.headers and 'headers' not in kwargs:
            kwargs['headers'] = self.headers
            
        response = requests.request(method, url, **kwargs)
        self.log(f"API: {method} {endpoint} -> {response.status_code}")
        return response

    def setup_authentication(self) -> bool:
        """Setup authentication and get token"""
        self.log("=== PHASE 1: Authentication Setup ===")
        
        auth_data = {
            "username": "MGanser",
            "password": "M4rvelf4n"
        }
        
        try:
            response = self.api_call("POST", "/auth/login", json=auth_data)
            
            if response.status_code == 200:
                token_data = response.json()
                self.headers = {"Authorization": f"Bearer {token_data['access_token']}"}
                self.log("✅ Authentication successful")
                
                # Verify token works
                test_response = self.api_call("GET", "/employees")
                if test_response.status_code == 200:
                    self.log("✅ Token verification successful")
                    self.record_phase_time("authentication")
                    return True
                else:
                    self.log(f"❌ Token verification failed: {test_response.status_code}")
                    return False
            else:
                self.log(f"❌ Authentication failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.log(f"❌ Authentication error: {e}", "ERROR")
            return False

    def test_employee_creation(self) -> Optional[Dict]:
        """Test comprehensive employee creation"""
        self.log("=== PHASE 2: Employee Creation & Validation ===")
        
        # Generate unique data
        timestamp = int(time.time())
        unique_id = str(uuid.uuid4())[:8]
        
        # Test data with all fields
        employee_data = {
            "title": "Dr. med.",
            "first_name": "Lifecycle",
            "last_name": f"Test-{unique_id}",
            "email": f"lifecycle.test.{timestamp}@gynorg-test.de",
            "position": "Oberärztin Gynäkologie",
            "birth_date": "1985-03-15",
            "date_hired": "2024-01-15",
            "federal_state": "Baden-Württemberg",
            "active": True
        }
        
        try:
            # Create employee
            response = self.api_call("POST", "/employees", json=employee_data)
            
            if response.status_code == 201:
                employee = response.json()
                employee_id = employee["id"]
                self.test_data['employees'].append(employee)
                self.test_data['created_ids']['employees'].append(employee_id)
                self.metrics['operations_count'] += 1
                
                self.log(f"✅ Employee created: {employee['first_name']} {employee['last_name']} (ID: {employee_id})")
                
                # Validate all fields were saved correctly
                self.validate_employee_data(employee, employee_data)
                
                # Test immediate retrieval
                get_response = self.api_call("GET", f"/employees/{employee_id}")
                if get_response.status_code == 200:
                    retrieved_employee = get_response.json()
                    self.log("✅ Employee immediately retrievable after creation")
                    
                    # Validate retrieved data matches created data
                    if self.validate_employee_data(retrieved_employee, employee_data):
                        self.record_phase_time("employee_creation")
                        return employee
                    else:
                        self.log("❌ Retrieved employee data doesn't match created data")
                        return None
                else:
                    self.log(f"❌ Failed to retrieve created employee: {get_response.status_code}")
                    return None
            else:
                self.log(f"❌ Employee creation failed: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            self.log(f"❌ Employee creation error: {e}", "ERROR")
            return None

    def validate_employee_data(self, employee: Dict, expected_data: Dict) -> bool:
        """Validate employee data matches expectations"""
        validation_passed = True
        
        for key, expected_value in expected_data.items():
            if key in employee:
                actual_value = employee[key]
                if actual_value != expected_value:
                    self.log(f"❌ Field '{key}': expected '{expected_value}', got '{actual_value}'")
                    validation_passed = False
            else:
                self.log(f"❌ Missing field: '{key}'")
                validation_passed = False
                
        if validation_passed:
            self.log("✅ Employee data validation passed")
            
        return validation_passed

    def test_employee_crud_operations(self, employee: Dict) -> bool:
        """Test complete CRUD operations on employee"""
        self.log("=== PHASE 3: Employee CRUD Operations ===")
        
        employee_id = employee["id"]
        
        try:
            # Test READ operation
            read_response = self.api_call("GET", f"/employees/{employee_id}")
            if read_response.status_code != 200:
                self.log(f"❌ Employee READ failed: {read_response.status_code}")
                return False
            self.log("✅ Employee READ operation successful")
            
            # Test UPDATE operation - partial update
            update_data = {
                "position": "Chefärztin Gynäkologie",
                "title": "Prof. Dr. med."
            }
            
            update_response = self.api_call("PUT", f"/employees/{employee_id}", json=update_data)
            if update_response.status_code == 200:
                updated_employee = update_response.json()
                self.log(f"✅ Employee UPDATE successful: {updated_employee['title']} {updated_employee['position']}")
                
                # Verify update was applied
                verify_response = self.api_call("GET", f"/employees/{employee_id}")
                if verify_response.status_code == 200:
                    verified_employee = verify_response.json()
                    if (verified_employee['position'] == update_data['position'] and 
                        verified_employee['title'] == update_data['title']):
                        self.log("✅ Employee UPDATE verification successful")
                        self.metrics['operations_count'] += 2
                    else:
                        self.log("❌ Employee UPDATE verification failed")
                        return False
                else:
                    self.log(f"❌ Employee UPDATE verification request failed: {verify_response.status_code}")
                    return False
            else:
                self.log(f"❌ Employee UPDATE failed: {update_response.status_code}")
                return False
                
            # Test LIST operation with filters
            list_response = self.api_call("GET", "/employees")
            if list_response.status_code == 200:
                employees_list = list_response.json()
                if any(emp['id'] == employee_id for emp in employees_list):
                    self.log("✅ Employee appears in LIST operation")
                else:
                    self.log("❌ Employee missing from LIST operation")
                    return False
            else:
                self.log(f"❌ Employee LIST operation failed: {list_response.status_code}")
                return False
                
            # Test search functionality
            search_response = self.api_call("GET", f"/employees?search=Lifecycle")
            if search_response.status_code == 200:
                search_results = search_response.json()
                if any(emp['id'] == employee_id for emp in search_results):
                    self.log("✅ Employee found in SEARCH operation")
                else:
                    self.log("❌ Employee not found in SEARCH operation")
                    return False
            else:
                self.log(f"❌ Employee SEARCH operation failed: {search_response.status_code}")
                return False
                
            self.record_phase_time("employee_crud")
            return True
            
        except Exception as e:
            self.log(f"❌ Employee CRUD operations error: {e}", "ERROR")
            return False

    def test_vacation_allowance_integration(self, employee: Dict) -> Optional[Dict]:
        """Test VacationAllowance integration with employee"""
        self.log("=== PHASE 4: VacationAllowance Integration ===")
        
        employee_id = employee["id"]
        current_year = datetime.now().year
        
        allowance_data = {
            "employee_id": employee_id,
            "year": current_year,
            "annual_allowance": 30,
            "carryover_days": 5
        }
        
        try:
            # Create vacation allowance
            response = self.api_call("POST", "/vacation-allowances", json=allowance_data)
            
            if response.status_code == 201:
                allowance = response.json()
                allowance_id = allowance["id"]
                self.test_data['vacation_allowances'].append(allowance)
                self.test_data['created_ids']['vacation_allowances'].append(allowance_id)
                
                self.log(f"✅ VacationAllowance created: {allowance['total_allowance']} days (ID: {allowance_id})")
                
                # Validate business logic (total_allowance = annual_allowance + carryover_days)
                expected_total = allowance_data['annual_allowance'] + allowance_data['carryover_days']
                if allowance['total_allowance'] == expected_total:
                    self.log("✅ VacationAllowance business logic validation passed")
                else:
                    self.log(f"❌ VacationAllowance business logic failed: expected {expected_total}, got {allowance['total_allowance']}")
                    return None
                
                # Test relationship - get employee's vacation allowances
                emp_allowances_response = self.api_call("GET", f"/employees/{employee_id}/vacation-allowances")
                if emp_allowances_response.status_code == 200:
                    emp_allowances = emp_allowances_response.json()
                    if any(va['id'] == allowance_id for va in emp_allowances):
                        self.log("✅ VacationAllowance relationship validation passed")
                        self.metrics['operations_count'] += 2
                        self.record_phase_time("vacation_allowance_integration")
                        return allowance
                    else:
                        self.log("❌ VacationAllowance not found in employee's allowances")
                        return None
                else:
                    self.log(f"❌ Failed to get employee's vacation allowances: {emp_allowances_response.status_code}")
                    return None
            else:
                self.log(f"❌ VacationAllowance creation failed: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            self.log(f"❌ VacationAllowance integration error: {e}", "ERROR")
            return None

    def test_data_relationships_integrity(self, employee: Dict, vacation_allowance: Dict) -> bool:
        """Test data relationships and referential integrity"""
        self.log("=== PHASE 5: Data Relationships & Integrity ===")
        
        employee_id = employee["id"]
        allowance_id = vacation_allowance["id"]
        
        try:
            # Test 1: Employee-VacationAllowance relationship
            emp_response = self.api_call("GET", f"/employees/{employee_id}")
            if emp_response.status_code != 200:
                self.log(f"❌ Failed to retrieve employee for relationship test: {emp_response.status_code}")
                return False
                
            # Test 2: VacationAllowance-Employee relationship
            allowance_response = self.api_call("GET", f"/vacation-allowances/{allowance_id}")
            if allowance_response.status_code == 200:
                allowance_data = allowance_response.json()
                if allowance_data['employee_id'] == employee_id:
                    self.log("✅ VacationAllowance->Employee relationship intact")
                else:
                    self.log(f"❌ VacationAllowance employee_id mismatch: expected {employee_id}, got {allowance_data['employee_id']}")
                    return False
            else:
                self.log(f"❌ Failed to retrieve vacation allowance: {allowance_response.status_code}")
                return False
                
            # Test 3: Federal state relationship
            emp_data = emp_response.json()
            federal_states_response = self.api_call("GET", "/federal-states")
            if federal_states_response.status_code == 200:
                federal_states = federal_states_response.json()
                if emp_data['federal_state'] in federal_states:
                    self.log("✅ Employee federal state relationship valid")
                else:
                    self.log(f"❌ Employee federal state '{emp_data['federal_state']}' not in valid states")
                    return False
            else:
                self.log(f"❌ Failed to retrieve federal states: {federal_states_response.status_code}")
                return False
                
            # Test 4: Data consistency across operations
            list_employees_response = self.api_call("GET", "/employees")
            if list_employees_response.status_code == 200:
                employees_list = list_employees_response.json()
                found_employee = next((emp for emp in employees_list if emp['id'] == employee_id), None)
                if found_employee:
                    # Compare key fields
                    if (found_employee['email'] == emp_data['email'] and 
                        found_employee['first_name'] == emp_data['first_name'] and
                        found_employee['last_name'] == emp_data['last_name']):
                        self.log("✅ Data consistency across list and detail views")
                    else:
                        self.log("❌ Data inconsistency between list and detail views")
                        return False
                else:
                    self.log("❌ Employee not found in list view")
                    return False
            else:
                self.log(f"❌ Failed to retrieve employees list: {list_employees_response.status_code}")
                return False
                
            self.metrics['operations_count'] += 4
            self.record_phase_time("data_relationships")
            return True
            
        except Exception as e:
            self.log(f"❌ Data relationships test error: {e}", "ERROR")
            return False

    def test_edge_cases_validation(self, employee: Dict) -> bool:
        """Test edge cases and validation scenarios"""
        self.log("=== PHASE 6: Edge Cases & Validation ===")
        
        employee_id = employee["id"]
        
        try:
            # Test 1: Invalid email update
            invalid_email_data = {"email": "invalid-email-format"}
            invalid_response = self.api_call("PUT", f"/employees/{employee_id}", json=invalid_email_data)
            if invalid_response.status_code == 422:
                self.log("✅ Email validation working correctly")
            else:
                self.log(f"❌ Email validation failed: expected 422, got {invalid_response.status_code}")
                return False
                
            # Test 2: Future birth date
            future_birth_data = {"birth_date": "2030-01-01"}
            future_response = self.api_call("PUT", f"/employees/{employee_id}", json=future_birth_data)
            if future_response.status_code == 422:
                self.log("✅ Future birth date validation working correctly")
            else:
                self.log(f"❌ Future birth date validation failed: expected 422, got {future_response.status_code}")
                return False
                
            # Test 3: Non-existent employee
            nonexistent_response = self.api_call("GET", "/employees/99999")
            if nonexistent_response.status_code == 404:
                self.log("✅ Non-existent employee handling working correctly")
            else:
                self.log(f"❌ Non-existent employee handling failed: expected 404, got {nonexistent_response.status_code}")
                return False
                
            # Test 4: Duplicate email (create another employee with same email)
            duplicate_data = {
                "first_name": "Duplicate",
                "last_name": "Test",
                "email": employee["email"],  # Same email as existing employee
                "federal_state": "Bayern"
            }
            duplicate_response = self.api_call("POST", "/employees", json=duplicate_data)
            if duplicate_response.status_code in [400, 422]:  # Accept both 400 and 422 for validation errors
                self.log("✅ Duplicate email validation working correctly")
            else:
                self.log(f"❌ Duplicate email validation failed: expected 400 or 422, got {duplicate_response.status_code}")
                return False
                
            # Test 5: Invalid vacation allowance year
            invalid_va_data = {
                "employee_id": employee_id,
                "year": 1900,  # Invalid year
                "annual_allowance": 30,
                "carryover_days": 0
            }
            invalid_va_response = self.api_call("POST", "/vacation-allowances", json=invalid_va_data)
            if invalid_va_response.status_code == 422:
                self.log("✅ Invalid vacation allowance year validation working correctly")
            else:
                self.log(f"❌ Invalid vacation allowance year validation failed: expected 422, got {invalid_va_response.status_code}")
                return False
                
            self.metrics['operations_count'] += 5
            self.record_phase_time("edge_cases_validation")
            return True
            
        except Exception as e:
            self.log(f"❌ Edge cases validation error: {e}", "ERROR")
            return False

    def test_cleanup_and_verification(self) -> bool:
        """Test cleanup operations and verify data integrity"""
        self.log("=== PHASE 7: Cleanup & Final Verification ===")
        
        try:
            # Delete vacation allowances first (due to foreign key constraints)
            for allowance_id in self.test_data['created_ids']['vacation_allowances']:
                delete_response = self.api_call("DELETE", f"/vacation-allowances/{allowance_id}")
                if delete_response.status_code == 204:
                    self.log(f"✅ VacationAllowance {allowance_id} deleted successfully")
                else:
                    self.log(f"❌ Failed to delete VacationAllowance {allowance_id}: {delete_response.status_code}")
                    return False
                    
                # Verify deletion
                verify_response = self.api_call("GET", f"/vacation-allowances/{allowance_id}")
                if verify_response.status_code == 404:
                    self.log(f"✅ VacationAllowance {allowance_id} deletion verified")
                else:
                    self.log(f"❌ VacationAllowance {allowance_id} still exists after deletion")
                    return False
                    
            # Delete employees (using hard delete for complete removal)
            for employee_id in self.test_data['created_ids']['employees']:
                delete_response = self.api_call("DELETE", f"/employees/{employee_id}/hard")
                if delete_response.status_code == 204:
                    self.log(f"✅ Employee {employee_id} hard deleted successfully")
                else:
                    self.log(f"❌ Failed to hard delete Employee {employee_id}: {delete_response.status_code}")
                    return False
                    
                # Verify deletion
                verify_response = self.api_call("GET", f"/employees/{employee_id}")
                if verify_response.status_code == 404:
                    self.log(f"✅ Employee {employee_id} deletion verified")
                else:
                    self.log(f"❌ Employee {employee_id} still exists after deletion")
                    return False
                    
            # Final verification - ensure no test data remains
            final_employees_response = self.api_call("GET", "/employees?search=Lifecycle")
            if final_employees_response.status_code == 200:
                remaining_test_employees = final_employees_response.json()
                if len(remaining_test_employees) == 0:
                    self.log("✅ No test employees remain in system")
                else:
                    self.log(f"❌ {len(remaining_test_employees)} test employees still in system")
                    return False
            else:
                self.log(f"❌ Final verification failed: {final_employees_response.status_code}")
                return False
                
            self.metrics['operations_count'] += len(self.test_data['created_ids']['employees']) * 2
            self.metrics['operations_count'] += len(self.test_data['created_ids']['vacation_allowances']) * 2
            self.record_phase_time("cleanup_verification")
            return True
            
        except Exception as e:
            self.log(f"❌ Cleanup and verification error: {e}", "ERROR")
            return False

    def print_final_report(self, success: bool):
        """Print comprehensive test report"""
        total_time = time.time() - self.metrics['start_time']
        
        print("\n" + "=" * 80)
        print("🎯 COMPLETE EMPLOYEE LIFECYCLE TEST REPORT")
        print("=" * 80)
        
        print(f"📊 OVERALL RESULT: {'✅ SUCCESS' if success else '❌ FAILURE'}")
        print(f"⏱️  TOTAL DURATION: {total_time:.2f} seconds")
        print(f"🔄 TOTAL OPERATIONS: {self.metrics['operations_count']}")
        print(f"📡 API CALLS MADE: {self.metrics['api_calls']}")
        
        print(f"\n📈 PHASE BREAKDOWN:")
        for phase, duration in self.metrics['phase_times'].items():
            print(f"   {phase.replace('_', ' ').title()}: {duration:.2f}s")
            
        print(f"\n📋 TEST COVERAGE:")
        print(f"   ✅ Authentication & Authorization")
        print(f"   ✅ Employee CRUD Operations")
        print(f"   ✅ VacationAllowance Integration")
        print(f"   ✅ Data Relationships & Integrity")
        print(f"   ✅ Validation & Error Handling")
        print(f"   ✅ Edge Cases & Boundary Conditions")
        print(f"   ✅ Cleanup & Data Verification")
        
        print(f"\n🧪 CREATED & CLEANED UP:")
        print(f"   Employees: {len(self.test_data['created_ids']['employees'])}")
        print(f"   VacationAllowances: {len(self.test_data['created_ids']['vacation_allowances'])}")
        
        if success:
            print(f"\n🎉 ALL EMPLOYEE LIFECYCLE TESTS PASSED!")
            print(f"   The complete employee management system is working correctly.")
            print(f"   All data integrity checks passed.")
            print(f"   All cleanup operations completed successfully.")
        else:
            print(f"\n❌ SOME TESTS FAILED!")
            print(f"   Please check the detailed log above for specific failures.")
            
        print("=" * 80)

    def run_complete_lifecycle_test(self) -> bool:
        """Run the complete employee lifecycle test suite"""
        self.log("🚀 Starting Complete Employee Lifecycle Test")
        self.start_metrics()
        
        try:
            # Phase 1: Authentication
            if not self.setup_authentication():
                self.print_final_report(False)
                return False
                
            # Phase 2: Employee Creation
            employee = self.test_employee_creation()
            if not employee:
                self.print_final_report(False)
                return False
                
            # Phase 3: CRUD Operations
            if not self.test_employee_crud_operations(employee):
                self.print_final_report(False)
                return False
                
            # Phase 4: VacationAllowance Integration
            vacation_allowance = self.test_vacation_allowance_integration(employee)
            if not vacation_allowance:
                self.print_final_report(False)
                return False
                
            # Phase 5: Data Relationships
            if not self.test_data_relationships_integrity(employee, vacation_allowance):
                self.print_final_report(False)
                return False
                
            # Phase 6: Edge Cases & Validation
            if not self.test_edge_cases_validation(employee):
                self.print_final_report(False)
                return False
                
            # Phase 7: Cleanup & Verification
            if not self.test_cleanup_and_verification():
                self.print_final_report(False)
                return False
                
            # All tests passed
            self.print_final_report(True)
            return True
            
        except Exception as e:
            self.log(f"❌ Test suite failed with unexpected error: {e}", "ERROR")
            self.print_final_report(False)
            return False

def main():
    """Main test execution function"""
    print("🔬 GynOrg Complete Employee Lifecycle Test")
    print("Testing comprehensive employee management functionality...")
    print()
    
    test_suite = EmployeeLifecycleTest()
    success = test_suite.run_complete_lifecycle_test()
    
    # Exit with appropriate code
    exit(0 if success else 1)

if __name__ == "__main__":
    main()
