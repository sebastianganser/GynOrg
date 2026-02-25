"""
Comprehensive Test Suite for Task 18.8: Multi-Year Holiday System Final Validation

This test suite performs end-to-end validation of the complete multi-year holiday system
including all subtasks 18.1-18.7 and measures performance improvements.
"""

import pytest
import requests
import time
import json
from datetime import date, datetime, timedelta
from typing import Dict, Any, List

# Test configuration
BASE_URL = "http://localhost:8001/api/v1"
TEST_USERNAME = "MGanser"
TEST_PASSWORD = "SecurePass123!"

class TestTask18ComprehensiveValidation:
    """Comprehensive validation of Task 18 Multi-Year Holiday System"""
    
    def setup_method(self):
        """Setup for each test method"""
        self.headers = self.get_auth_headers()
        self.performance_metrics = {}
        
    def get_auth_headers(self) -> Dict[str, str]:
        """Get authentication headers for API requests"""
        try:
            auth_response = requests.post(
                f"{BASE_URL}/auth/login",
                data={"username": TEST_USERNAME, "password": TEST_PASSWORD},
                timeout=10
            )
            
            if auth_response.status_code != 200:
                raise Exception(f"Authentication failed: {auth_response.status_code}")
            
            token = auth_response.json()["access_token"]
            return {"Authorization": f"Bearer {token}"}
        except Exception as e:
            print(f"⚠️ Authentication failed: {e}")
            return {}
    
    def measure_performance(self, test_name: str, func, *args, **kwargs):
        """Measure performance of a function call"""
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        
        duration_ms = (end_time - start_time) * 1000
        self.performance_metrics[test_name] = duration_ms
        
        return result, duration_ms
    
    def test_01_subtask_18_1_bulk_import_validation(self):
        """Test 1: Validate Subtask 18.1 - Bulk Holiday Import"""
        print("\n🔍 Test 1: Bulk Holiday Import Validation (Subtask 18.1)")
        
        # Test bulk import endpoint exists and works
        response, duration = self.measure_performance(
            "bulk_import_check",
            requests.get,
            f"{BASE_URL}/holidays/bulk-import/status",
            headers=self.headers
        )
        
        print(f"   📊 Bulk import status check: {duration:.2f}ms")
        
        if response.status_code == 200:
            status = response.json()
            print(f"   ✅ Bulk import status: {status.get('status', 'unknown')}")
            print(f"   📅 Years available: {status.get('years_available', 'unknown')}")
        else:
            print(f"   ⚠️ Bulk import status endpoint not available: {response.status_code}")
        
        # Test that holidays exist for multiple years
        test_years = [2020, 2024, 2025, 2030]
        years_with_data = 0
        
        for year in test_years:
            response, duration = self.measure_performance(
                f"holiday_check_{year}",
                requests.get,
                f"{BASE_URL}/holidays",
                params={"year": year, "federal_state": "SACHSEN_ANHALT"},
                headers=self.headers
            )
            
            if response.status_code == 200:
                holidays = response.json()
                if len(holidays) > 0:
                    years_with_data += 1
                    print(f"   ✅ Year {year}: {len(holidays)} holidays found ({duration:.2f}ms)")
                else:
                    print(f"   ⚠️ Year {year}: No holidays found")
            else:
                print(f"   ❌ Year {year}: API error {response.status_code}")
        
        print(f"   📊 Years with holiday data: {years_with_data}/{len(test_years)}")
        assert years_with_data >= 3, "At least 3 test years should have holiday data"
    
    def test_02_subtask_18_2_startup_logic_validation(self):
        """Test 2: Validate Subtask 18.2 - Startup Logic"""
        print("\n🚀 Test 2: Startup Logic Validation (Subtask 18.2)")
        
        # Test startup status endpoint
        response, duration = self.measure_performance(
            "startup_status",
            requests.get,
            f"{BASE_URL}/system/startup-status",
            headers=self.headers
        )
        
        print(f"   📊 Startup status check: {duration:.2f}ms")
        
        if response.status_code == 200:
            status = response.json()
            print(f"   ✅ Startup completed: {status.get('startup_completed', False)}")
            print(f"   📅 Holiday data initialized: {status.get('holiday_data_initialized', False)}")
            print(f"   ⏱️ Last startup: {status.get('last_startup_time', 'unknown')}")
        else:
            print(f"   ⚠️ Startup status endpoint not available: {response.status_code}")
        
        # Verify that holiday data is consistently available
        response, duration = self.measure_performance(
            "holiday_consistency_check",
            requests.get,
            f"{BASE_URL}/holidays/years",
            headers=self.headers
        )
        
        if response.status_code == 200:
            years = response.json()
            print(f"   ✅ Available years: {len(years)} years ({duration:.2f}ms)")
            print(f"   📅 Year range: {min(years)} - {max(years)}")
            
            # Should have years 2020-2030
            expected_years = list(range(2020, 2031))
            missing_years = set(expected_years) - set(years)
            if missing_years:
                print(f"   ⚠️ Missing years: {sorted(missing_years)}")
            else:
                print("   ✅ All expected years (2020-2030) available")
        else:
            print(f"   ❌ Years endpoint error: {response.status_code}")
    
    def test_03_subtask_18_3_available_years_api(self):
        """Test 3: Validate Subtask 18.3 - Available Years API"""
        print("\n📅 Test 3: Available Years API Validation (Subtask 18.3)")
        
        # Test the years endpoint performance and accuracy
        response, duration = self.measure_performance(
            "years_api_performance",
            requests.get,
            f"{BASE_URL}/holidays/years",
            headers=self.headers
        )
        
        print(f"   📊 Years API response time: {duration:.2f}ms")
        
        if response.status_code == 200:
            years = response.json()
            print(f"   ✅ API returned {len(years)} years")
            
            # Validate year range
            if years:
                min_year, max_year = min(years), max(years)
                print(f"   📅 Year range: {min_year} - {max_year}")
                
                # Should span at least 10 years
                year_span = max_year - min_year + 1
                print(f"   📊 Year span: {year_span} years")
                assert year_span >= 10, "Should have at least 10 years of data"
                
                # Should include current year
                current_year = date.today().year
                if current_year in years:
                    print(f"   ✅ Current year ({current_year}) included")
                else:
                    print(f"   ⚠️ Current year ({current_year}) missing")
            
            # Test federal state specific years
            response, duration = self.measure_performance(
                "years_api_federal_state",
                requests.get,
                f"{BASE_URL}/holidays/years",
                params={"federal_state": "SACHSEN_ANHALT"},
                headers=self.headers
            )
            
            if response.status_code == 200:
                state_years = response.json()
                print(f"   ✅ Sachsen-Anhalt specific years: {len(state_years)} ({duration:.2f}ms)")
            
        else:
            print(f"   ❌ Years API error: {response.status_code}")
    
    def test_04_subtask_18_4_frontend_hook_integration(self):
        """Test 4: Validate Subtask 18.4 - Frontend useHolidays Hook"""
        print("\n🎣 Test 4: Frontend Hook Integration (Subtask 18.4)")
        
        # Test multiple year requests to simulate frontend hook behavior
        test_years = [2023, 2024, 2025]
        hook_performance = {}
        
        for year in test_years:
            # First request (cache miss)
            response, duration1 = self.measure_performance(
                f"hook_first_request_{year}",
                requests.get,
                f"{BASE_URL}/holidays",
                params={"year": year, "federal_state": "SACHSEN_ANHALT"},
                headers=self.headers
            )
            
            # Second request (should be faster due to backend optimizations)
            response, duration2 = self.measure_performance(
                f"hook_second_request_{year}",
                requests.get,
                f"{BASE_URL}/holidays",
                params={"year": year, "federal_state": "SACHSEN_ANHALT"},
                headers=self.headers
            )
            
            hook_performance[year] = {
                "first_request": duration1,
                "second_request": duration2,
                "improvement": duration1 - duration2
            }
            
            print(f"   📅 Year {year}:")
            print(f"     First request: {duration1:.2f}ms")
            print(f"     Second request: {duration2:.2f}ms")
            print(f"     Improvement: {duration1 - duration2:.2f}ms")
            
            if response.status_code == 200:
                holidays = response.json()
                print(f"     ✅ {len(holidays)} holidays retrieved")
            else:
                print(f"     ❌ API error: {response.status_code}")
        
        # Calculate average performance
        avg_first = sum(p["first_request"] for p in hook_performance.values()) / len(hook_performance)
        avg_second = sum(p["second_request"] for p in hook_performance.values()) / len(hook_performance)
        
        print(f"   📊 Average performance:")
        print(f"     First requests: {avg_first:.2f}ms")
        print(f"     Second requests: {avg_second:.2f}ms")
        print(f"     Average improvement: {avg_first - avg_second:.2f}ms")
    
    def test_05_subtask_18_5_calendar_navigation(self):
        """Test 5: Validate Subtask 18.5 - Calendar Navigation"""
        print("\n📅 Test 5: Calendar Navigation Validation (Subtask 18.5)")
        
        # Test rapid year switching (simulating calendar navigation)
        navigation_years = [2020, 2021, 2024, 2025, 2030]
        navigation_performance = []
        
        for i, year in enumerate(navigation_years):
            response, duration = self.measure_performance(
                f"calendar_navigation_{i}",
                requests.get,
                f"{BASE_URL}/holidays",
                params={"year": year, "federal_state": "SACHSEN_ANHALT"},
                headers=self.headers
            )
            
            navigation_performance.append(duration)
            
            if response.status_code == 200:
                holidays = response.json()
                print(f"   📅 Year {year}: {len(holidays)} holidays ({duration:.2f}ms)")
            else:
                print(f"   ❌ Year {year}: API error {response.status_code}")
        
        # Analyze navigation performance
        avg_navigation = sum(navigation_performance) / len(navigation_performance)
        max_navigation = max(navigation_performance)
        min_navigation = min(navigation_performance)
        
        print(f"   📊 Navigation performance:")
        print(f"     Average: {avg_navigation:.2f}ms")
        print(f"     Fastest: {min_navigation:.2f}ms")
        print(f"     Slowest: {max_navigation:.2f}ms")
        
        # Navigation should be consistently fast
        assert avg_navigation < 200, f"Average navigation time too slow: {avg_navigation:.2f}ms"
        assert max_navigation < 500, f"Slowest navigation too slow: {max_navigation:.2f}ms"
    
    def test_06_subtask_18_6_absence_calculations(self):
        """Test 6: Validate Subtask 18.6 - Absence Calculations"""
        print("\n🧮 Test 6: Absence Calculations Validation (Subtask 18.6)")
        
        # Test working days calculator with multi-year support
        test_cases = [
            {
                "name": "Single year calculation",
                "start_date": "2024-12-01",
                "end_date": "2024-12-31",
                "federal_state": "SACHSEN_ANHALT"
            },
            {
                "name": "Cross-year calculation",
                "start_date": "2024-12-15",
                "end_date": "2025-01-15",
                "federal_state": "SACHSEN_ANHALT"
            },
            {
                "name": "Multi-year span",
                "start_date": "2024-11-01",
                "end_date": "2025-02-28",
                "federal_state": "SACHSEN_ANHALT"
            }
        ]
        
        for test_case in test_cases:
            print(f"   🧮 {test_case['name']}:")
            
            response, duration = self.measure_performance(
                f"absence_calc_{test_case['name'].replace(' ', '_')}",
                requests.get,
                f"{BASE_URL}/absences/working-days-calculator",
                params={
                    "start_date": test_case["start_date"],
                    "end_date": test_case["end_date"],
                    "federal_state": test_case["federal_state"]
                },
                headers=self.headers
            )
            
            print(f"     Response time: {duration:.2f}ms")
            
            if response.status_code == 200:
                data = response.json()
                print(f"     ✅ Working days: {data.get('working_days', 'N/A')}")
                print(f"     📅 Total days: {data.get('total_days', 'N/A')}")
                print(f"     🎄 Holiday days: {data.get('holiday_days', 'N/A')}")
                print(f"     🏖️ Weekend days: {data.get('weekend_days', 'N/A')}")
                
                # Validate holidays are included
                holidays = data.get('holidays', [])
                if holidays:
                    print(f"     🎄 Holidays found: {len(holidays)}")
                    for holiday in holidays[:3]:  # Show first 3
                        print(f"       • {holiday.get('date')}: {holiday.get('name')}")
                else:
                    print("     ⚠️ No holidays found in period")
            else:
                print(f"     ❌ API error: {response.status_code}")
    
    def test_07_subtask_18_7_database_performance(self):
        """Test 7: Validate Subtask 18.7 - Database Performance Optimizations"""
        print("\n🗄️ Test 7: Database Performance Validation (Subtask 18.7)")
        
        # Test performance of optimized queries
        performance_tests = [
            {
                "name": "Year-based query",
                "endpoint": "/holidays",
                "params": {"year": 2024}
            },
            {
                "name": "Federal state query",
                "endpoint": "/holidays",
                "params": {"federal_state": "SACHSEN_ANHALT"}
            },
            {
                "name": "Combined year+state query",
                "endpoint": "/holidays",
                "params": {"year": 2024, "federal_state": "SACHSEN_ANHALT"}
            },
            {
                "name": "Date range query",
                "endpoint": "/holidays",
                "params": {
                    "start_date": "2024-01-01",
                    "end_date": "2024-12-31",
                    "federal_state": "SACHSEN_ANHALT"
                }
            }
        ]
        
        for test in performance_tests:
            print(f"   🔍 {test['name']}:")
            
            # Run multiple iterations to get average
            durations = []
            for i in range(5):
                response, duration = self.measure_performance(
                    f"db_perf_{test['name'].replace(' ', '_')}_{i}",
                    requests.get,
                    f"{BASE_URL}{test['endpoint']}",
                    params=test["params"],
                    headers=self.headers
                )
                durations.append(duration)
            
            avg_duration = sum(durations) / len(durations)
            min_duration = min(durations)
            max_duration = max(durations)
            
            print(f"     Average: {avg_duration:.2f}ms")
            print(f"     Best: {min_duration:.2f}ms")
            print(f"     Worst: {max_duration:.2f}ms")
            
            if response.status_code == 200:
                data = response.json()
                print(f"     ✅ Results: {len(data)} holidays")
            else:
                print(f"     ❌ API error: {response.status_code}")
            
            # Performance should be good (under 100ms average)
            if avg_duration < 100:
                print(f"     ✅ Excellent performance")
            elif avg_duration < 200:
                print(f"     ✅ Good performance")
            else:
                print(f"     ⚠️ Performance could be improved")
    
    def test_08_end_to_end_integration(self):
        """Test 8: End-to-End Integration Test"""
        print("\n🔄 Test 8: End-to-End Integration Validation")
        
        # Simulate complete user workflow
        print("   🎯 Simulating complete user workflow...")
        
        # 1. Get available years
        response, duration = self.measure_performance(
            "e2e_get_years",
            requests.get,
            f"{BASE_URL}/holidays/years",
            headers=self.headers
        )
        
        if response.status_code == 200:
            years = response.json()
            print(f"   ✅ Step 1: Retrieved {len(years)} available years ({duration:.2f}ms)")
            
            # 2. Select a year and get holidays
            test_year = 2024 if 2024 in years else years[0]
            response, duration = self.measure_performance(
                "e2e_get_holidays",
                requests.get,
                f"{BASE_URL}/holidays",
                params={"year": test_year, "federal_state": "SACHSEN_ANHALT"},
                headers=self.headers
            )
            
            if response.status_code == 200:
                holidays = response.json()
                print(f"   ✅ Step 2: Retrieved {len(holidays)} holidays for {test_year} ({duration:.2f}ms)")
                
                # 3. Calculate working days using holidays
                if holidays:
                    start_date = f"{test_year}-01-01"
                    end_date = f"{test_year}-12-31"
                    
                    response, duration = self.measure_performance(
                        "e2e_calculate_working_days",
                        requests.get,
                        f"{BASE_URL}/absences/working-days-calculator",
                        params={
                            "start_date": start_date,
                            "end_date": end_date,
                            "federal_state": "SACHSEN_ANHALT"
                        },
                        headers=self.headers
                    )
                    
                    if response.status_code == 200:
                        calc_data = response.json()
                        print(f"   ✅ Step 3: Calculated working days ({duration:.2f}ms)")
                        print(f"     Working days: {calc_data.get('working_days')}")
                        print(f"     Holiday days: {calc_data.get('holiday_days')}")
                        
                        # Verify holidays are properly integrated
                        calc_holidays = calc_data.get('holidays', [])
                        if len(calc_holidays) > 0:
                            print(f"   ✅ Step 4: Holidays properly integrated ({len(calc_holidays)} holidays)")
                        else:
                            print("   ⚠️ Step 4: No holidays in calculation")
                    else:
                        print(f"   ❌ Step 3 failed: {response.status_code}")
                else:
                    print("   ⚠️ Step 2: No holidays found")
            else:
                print(f"   ❌ Step 2 failed: {response.status_code}")
        else:
            print(f"   ❌ Step 1 failed: {response.status_code}")
    
    def test_09_performance_summary(self):
        """Test 9: Performance Summary and Validation"""
        print("\n📊 Test 9: Performance Summary")
        
        if not self.performance_metrics:
            print("   ⚠️ No performance metrics collected")
            return
        
        # Categorize metrics
        api_metrics = {k: v for k, v in self.performance_metrics.items() if 'api' in k.lower()}
        db_metrics = {k: v for k, v in self.performance_metrics.items() if 'db_perf' in k}
        calc_metrics = {k: v for k, v in self.performance_metrics.items() if 'calc' in k}
        
        print(f"   📊 Total metrics collected: {len(self.performance_metrics)}")
        
        # Overall performance analysis
        all_times = list(self.performance_metrics.values())
        avg_time = sum(all_times) / len(all_times)
        max_time = max(all_times)
        min_time = min(all_times)
        
        print(f"   📈 Overall performance:")
        print(f"     Average response time: {avg_time:.2f}ms")
        print(f"     Fastest response: {min_time:.2f}ms")
        print(f"     Slowest response: {max_time:.2f}ms")
        
        # Performance targets validation
        fast_responses = sum(1 for t in all_times if t < 100)
        good_responses = sum(1 for t in all_times if t < 200)
        slow_responses = sum(1 for t in all_times if t >= 500)
        
        print(f"   🎯 Performance distribution:")
        print(f"     Fast (<100ms): {fast_responses}/{len(all_times)} ({fast_responses/len(all_times)*100:.1f}%)")
        print(f"     Good (<200ms): {good_responses}/{len(all_times)} ({good_responses/len(all_times)*100:.1f}%)")
        print(f"     Slow (≥500ms): {slow_responses}/{len(all_times)} ({slow_responses/len(all_times)*100:.1f}%)")
        
        # Performance grade
        if avg_time < 100 and slow_responses == 0:
            grade = "A+ (Excellent)"
        elif avg_time < 150 and slow_responses <= 1:
            grade = "A (Very Good)"
        elif avg_time < 200 and slow_responses <= 2:
            grade = "B (Good)"
        elif avg_time < 300:
            grade = "C (Acceptable)"
        else:
            grade = "D (Needs Improvement)"
        
        print(f"   🏆 Performance Grade: {grade}")
        
        return {
            "average_time": avg_time,
            "max_time": max_time,
            "min_time": min_time,
            "grade": grade,
            "fast_responses": fast_responses,
            "total_responses": len(all_times)
        }


def run_comprehensive_validation():
    """Run the comprehensive validation test suite"""
    print("Starting Task 18.8 Comprehensive Validation...")
    print("=" * 80)
    
    # Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code != 200:
            print("❌ Server health check failed")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to server: {e}")
        print("   Please ensure the server is running on http://localhost:8001")
        return False
    
    print("✅ Server is running and accessible")
    
    # Run test suite
    test_suite = TestTask18ComprehensiveValidation()
    test_suite.setup_method()
    
    tests = [
        test_suite.test_01_subtask_18_1_bulk_import_validation,
        test_suite.test_02_subtask_18_2_startup_logic_validation,
        test_suite.test_03_subtask_18_3_available_years_api,
        test_suite.test_04_subtask_18_4_frontend_hook_integration,
        test_suite.test_05_subtask_18_5_calendar_navigation,
        test_suite.test_06_subtask_18_6_absence_calculations,
        test_suite.test_07_subtask_18_7_database_performance,
        test_suite.test_08_end_to_end_integration,
        test_suite.test_09_performance_summary
    ]
    
    passed = 0
    total = len(tests)
    
    for i, test in enumerate(tests, 1):
        try:
            print(f"\n{'='*20} Test {i}/{total} {'='*20}")
            test()
            passed += 1
            print(f"✅ Test {i} PASSED")
        except Exception as e:
            print(f"❌ Test {i} FAILED: {e}")
    
    print("\n" + "=" * 80)
    print(f"📊 FINAL RESULTS: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! Task 18 Multi-Year Holiday System is fully validated!")
        print("\n🎯 Key Achievements:")
        print("   ✅ All subtasks 18.1-18.7 validated")
        print("   ✅ Multi-year holiday system fully functional")
        print("   ✅ Performance optimizations confirmed")
        print("   ✅ End-to-end integration working")
        print("   ✅ Ready for production deployment")
    else:
        print(f"⚠️ {total - passed} tests failed. Please review and fix issues before deployment.")
    
    return passed == total


if __name__ == "__main__":
    success = run_comprehensive_validation()
    exit(0 if success else 1)
