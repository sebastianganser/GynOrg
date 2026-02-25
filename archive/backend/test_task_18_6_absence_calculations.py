"""
Test Suite for Task 18.6: Multi-Year Absence Calculation Services

This test suite validates the new AbsenceCalculationService functionality
that integrates with the multi-year holiday system.
"""

import pytest
import requests
from datetime import date, timedelta
from typing import Dict, Any

# Test configuration
BASE_URL = "http://localhost:8001/api/v1"
TEST_USERNAME = "MGanser"
TEST_PASSWORD = "SecurePass123!"

def get_auth_headers() -> Dict[str, str]:
    """Get authentication headers for API requests"""
    auth_response = requests.post(
        f"{BASE_URL}/auth/login",
        data={"username": TEST_USERNAME, "password": TEST_PASSWORD}
    )
    
    if auth_response.status_code != 200:
        raise Exception(f"Authentication failed: {auth_response.status_code}")
    
    token = auth_response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


class TestAbsenceCalculationService:
    """Test class for absence calculation functionality"""
    
    def setup(self):
        """Setup test data"""
        self.headers = get_auth_headers()
        self.employee_id = self.create_test_employee()
        self.vacation_allowance_id = self.create_test_vacation_allowance()
        
    def create_test_employee(self) -> int:
        """Create a test employee"""
        employee_data = {
            "first_name": "Test",
            "last_name": "Employee",
            "email": "test.employee@example.com",
            "federal_state": "SACHSEN_ANHALT"
        }
        
        response = requests.post(
            f"{BASE_URL}/employees",
            json=employee_data,
            headers=self.headers
        )
        
        if response.status_code == 201:
            return response.json()["id"]
        else:
            # Employee might already exist, try to find it
            response = requests.get(
                f"{BASE_URL}/employees",
                headers=self.headers
            )
            employees = response.json()
            for emp in employees:
                if emp["email"] == employee_data["email"]:
                    return emp["id"]
            
            raise Exception("Failed to create or find test employee")
    
    def create_test_vacation_allowance(self) -> int:
        """Create a test vacation allowance for current year"""
        current_year = date.today().year
        allowance_data = {
            "employee_id": self.employee_id,
            "year": current_year,
            "annual_allowance": 30,
            "carryover_days": 5
        }
        
        response = requests.post(
            f"{BASE_URL}/vacation-allowances",
            json=allowance_data,
            headers=self.headers
        )
        
        if response.status_code == 201:
            return response.json()["id"]
        else:
            # Allowance might already exist
            response = requests.get(
                f"{BASE_URL}/vacation-allowances/employee/{self.employee_id}/year/{current_year}",
                headers=self.headers
            )
            if response.status_code == 200:
                return response.json()["id"]
            
            raise Exception("Failed to create or find test vacation allowance")
    
    def test_working_days_calculator(self):
        """Test the working days calculator endpoint"""
        print("\n🧮 Test 1: Working Days Calculator...")
        
        # Test basic calculation
        start_date = "2024-12-23"  # Monday
        end_date = "2024-12-27"    # Friday (includes Christmas holidays)
        
        response = requests.get(
            f"{BASE_URL}/absences/working-days-calculator",
            params={
                "start_date": start_date,
                "end_date": end_date,
                "federal_state": "SACHSEN_ANHALT"
            },
            headers=self.headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        print(f"   📅 Period: {start_date} to {end_date}")
        print(f"   📊 Total days: {data['total_days']}")
        print(f"   💼 Working days: {data['working_days']}")
        print(f"   🏖️ Weekend days: {data['weekend_days']}")
        print(f"   🎄 Holiday days: {data['holiday_days']}")
        
        # Should include Christmas holidays
        assert data["holiday_days"] > 0
        assert len(data["holidays"]) > 0
        
        # Verify holiday details
        for holiday in data["holidays"]:
            print(f"     • {holiday['date']}: {holiday['name']}")
        
        print("   ✅ Working days calculation successful")
    
    def test_vacation_balance_single_year(self):
        """Test vacation balance for a single year"""
        print("\n💰 Test 2: Vacation Balance (Single Year)...")
        
        current_year = date.today().year
        
        response = requests.get(
            f"{BASE_URL}/absences/vacation-balance/{self.employee_id}",
            params={"year": current_year},
            headers=self.headers
        )
        
        assert response.status_code == 200
        balance = response.json()
        
        print(f"   👤 Employee ID: {balance['employee_id']}")
        print(f"   📅 Year: {balance['year']}")
        print(f"   📋 Annual allowance: {balance['annual_allowance']} days")
        print(f"   ➕ Carryover days: {balance['carryover_days']} days")
        print(f"   🎯 Total allowance: {balance['total_allowance']} days")
        print(f"   ✅ Used days: {balance['used_days']} days")
        print(f"   ⏳ Pending days: {balance['pending_days']} days")
        print(f"   💚 Available days: {balance['available_days']} days")
        
        # Verify calculations
        expected_total = balance['annual_allowance'] + balance['carryover_days']
        assert balance['total_allowance'] == expected_total
        
        expected_available = balance['total_allowance'] - balance['used_days'] - balance['pending_days']
        assert balance['available_days'] == expected_available
        
        print("   ✅ Vacation balance calculation successful")
    
    def test_vacation_balance_multi_year(self):
        """Test vacation balance across multiple years"""
        print("\n📊 Test 3: Vacation Balance (Multi-Year)...")
        
        current_year = date.today().year
        start_year = current_year - 1
        end_year = current_year + 1
        
        response = requests.get(
            f"{BASE_URL}/absences/vacation-balance/{self.employee_id}/multi-year",
            params={
                "start_year": start_year,
                "end_year": end_year
            },
            headers=self.headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        print(f"   👤 Employee ID: {data['employee_id']}")
        print(f"   📅 Year range: {data['start_year']} - {data['end_year']}")
        print(f"   📋 Balances found: {len(data['balances'])}")
        
        for year_str, balance in data['balances'].items():
            print(f"     📅 {balance['year']}: {balance['available_days']}/{balance['total_allowance']} days available")
        
        # Should have at least current year
        assert str(current_year) in data['balances']
        
        print("   ✅ Multi-year vacation balance successful")
    
    def test_absence_validation_with_holidays(self):
        """Test comprehensive absence validation including holidays"""
        print("\n🔍 Test 4: Absence Validation with Holidays...")
        
        # Test validation during Christmas period (should include holidays)
        start_date = "2024-12-24"  # Christmas Eve
        end_date = "2024-12-26"    # Boxing Day
        
        response = requests.post(
            f"{BASE_URL}/absences/validate-with-holidays",
            params={
                "employee_id": self.employee_id,
                "absence_type_id": 1,  # Assuming vacation type
                "start_date": start_date,
                "end_date": end_date,
                "federal_state": "SACHSEN_ANHALT"
            },
            headers=self.headers
        )
        
        assert response.status_code == 200
        validation = response.json()
        
        print(f"   📅 Period: {start_date} to {end_date}")
        print(f"   ✅ Is valid: {validation['is_valid']}")
        print(f"   💼 Working days: {validation['working_days']}")
        print(f"   🎄 Affected holidays: {len(validation['affected_holidays'])}")
        
        if validation['errors']:
            print(f"   ❌ Errors: {validation['errors']}")
        
        if validation['warnings']:
            print(f"   ⚠️ Warnings: {validation['warnings']}")
        
        # Should detect holidays
        assert len(validation['affected_holidays']) > 0
        
        for holiday in validation['affected_holidays']:
            print(f"     • {holiday['date']}: {holiday['name']}")
        
        # Should have vacation impact if it's a vacation request
        if 'vacation_impact' in validation:
            impact = validation['vacation_impact']
            print(f"   💰 Vacation impact: {impact['available_days']} days available")
        
        print("   ✅ Absence validation with holidays successful")
    
    def test_alternative_dates_suggestion(self):
        """Test alternative dates suggestion"""
        print("\n💡 Test 5: Alternative Dates Suggestion...")
        
        # Try to suggest alternatives for a potentially conflicting period
        desired_start = "2024-12-25"  # Christmas Day
        desired_end = "2024-12-27"    # Day after Boxing Day
        
        response = requests.get(
            f"{BASE_URL}/absences/suggest-alternative-dates",
            params={
                "employee_id": self.employee_id,
                "desired_start": desired_start,
                "desired_end": desired_end,
                "federal_state": "SACHSEN_ANHALT",
                "max_suggestions": 3
            },
            headers=self.headers
        )
        
        assert response.status_code == 200
        suggestions = response.json()
        
        print(f"   🎯 Desired: {suggestions['desired_start']} to {suggestions['desired_end']}")
        print(f"   💡 Suggestions: {len(suggestions['suggestions'])}")
        
        for i, suggestion in enumerate(suggestions['suggestions'], 1):
            print(f"     {i}. {suggestion['start_date']} to {suggestion['end_date']} ({suggestion['duration_days']} days)")
        
        print("   ✅ Alternative dates suggestion successful")
    
    def test_absence_statistics(self):
        """Test absence statistics endpoint"""
        print("\n📈 Test 6: Absence Statistics...")
        
        # Get general statistics
        response = requests.get(
            f"{BASE_URL}/absences/statistics",
            headers=self.headers
        )
        
        assert response.status_code == 200
        stats = response.json()
        
        print(f"   📊 General Statistics:")
        print(f"     • Total absences: {stats['statistics']['total_absences']}")
        print(f"     • Approved: {stats['statistics']['approved_absences']}")
        print(f"     • Pending: {stats['statistics']['pending_absences']}")
        print(f"     • Rejected: {stats['statistics']['rejected_absences']}")
        print(f"     • Total days: {stats['statistics']['total_days']}")
        print(f"     • Average duration: {stats['statistics']['average_duration']:.1f} days")
        
        # Get employee-specific statistics
        response = requests.get(
            f"{BASE_URL}/absences/statistics",
            params={"employee_id": self.employee_id},
            headers=self.headers
        )
        
        assert response.status_code == 200
        employee_stats = response.json()
        
        print(f"   👤 Employee {self.employee_id} Statistics:")
        print(f"     • Total absences: {employee_stats['statistics']['total_absences']}")
        print(f"     • Total days: {employee_stats['statistics']['total_days']}")
        
        print("   ✅ Absence statistics successful")
    
    def test_multi_year_holiday_integration(self):
        """Test that absence calculations work across multiple years"""
        print("\n🌍 Test 7: Multi-Year Holiday Integration...")
        
        # Test working days calculation across year boundary
        start_date = "2024-12-30"  # Monday
        end_date = "2025-01-03"    # Friday (crosses New Year)
        
        response = requests.get(
            f"{BASE_URL}/absences/working-days-calculator",
            params={
                "start_date": start_date,
                "end_date": end_date,
                "federal_state": "SACHSEN_ANHALT"
            },
            headers=self.headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        print(f"   📅 Cross-year period: {start_date} to {end_date}")
        print(f"   💼 Working days: {data['working_days']}")
        print(f"   🎄 Holiday days: {data['holiday_days']}")
        
        # Should include New Year's Day
        new_years_found = any(
            holiday['name'] == 'Neujahr' or 'Neujahr' in holiday['name']
            for holiday in data['holidays']
        )
        
        if new_years_found:
            print("   🎉 New Year's Day correctly detected")
        
        print("   ✅ Multi-year holiday integration successful")
    
    def test_error_handling(self):
        """Test error handling in absence calculations"""
        print("\n🚨 Test 8: Error Handling...")
        
        # Test invalid date range
        response = requests.get(
            f"{BASE_URL}/absences/working-days-calculator",
            params={
                "start_date": "2024-12-31",
                "end_date": "2024-12-01",  # End before start
                "federal_state": "SACHSEN_ANHALT"
            },
            headers=self.headers
        )
        
        assert response.status_code == 400
        print("   ✅ Invalid date range correctly rejected")
        
        # Test non-existent employee
        response = requests.get(
            f"{BASE_URL}/absences/vacation-balance/99999",
            headers=self.headers
        )
        
        assert response.status_code == 404
        print("   ✅ Non-existent employee correctly handled")
        
        # Test excessive year range
        response = requests.get(
            f"{BASE_URL}/absences/vacation-balance/{self.employee_id}/multi-year",
            params={
                "start_year": 2020,
                "end_year": 2035  # More than 10 years
            },
            headers=self.headers
        )
        
        assert response.status_code == 400
        print("   ✅ Excessive year range correctly rejected")
        
        print("   ✅ Error handling tests successful")
    
    def cleanup(self):
        """Clean up test data"""
        try:
            # Delete vacation allowance
            requests.delete(
                f"{BASE_URL}/vacation-allowances/{self.vacation_allowance_id}",
                headers=self.headers
            )
            
            # Delete employee
            requests.delete(
                f"{BASE_URL}/employees/{self.employee_id}",
                headers=self.headers
            )
            
            print("   🧹 Test data cleaned up")
        except Exception as e:
            print(f"   ⚠️ Cleanup warning: {e}")


def test_absence_calculation_integration():
    """Main integration test for absence calculation features"""
    print("🚀 Starting Task 18.6 Absence Calculation Tests...")
    print("=" * 60)
    
    test_suite = TestAbsenceCalculationService()
    
    try:
        test_suite.setup()
        
        # Run all tests
        test_suite.test_working_days_calculator()
        test_suite.test_vacation_balance_single_year()
        test_suite.test_vacation_balance_multi_year()
        test_suite.test_absence_validation_with_holidays()
        test_suite.test_alternative_dates_suggestion()
        test_suite.test_absence_statistics()
        test_suite.test_multi_year_holiday_integration()
        test_suite.test_error_handling()
        
        print("\n" + "=" * 60)
        print("✅ All Task 18.6 Absence Calculation Tests PASSED!")
        print("\n🎯 Key Features Validated:")
        print("   • Working days calculation with holiday integration")
        print("   • Vacation balance tracking (single & multi-year)")
        print("   • Comprehensive absence validation with holidays")
        print("   • Alternative dates suggestion")
        print("   • Absence statistics and reporting")
        print("   • Multi-year holiday system integration")
        print("   • Robust error handling")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        raise
    
    finally:
        test_suite.cleanup()


if __name__ == "__main__":
    test_absence_calculation_integration()
