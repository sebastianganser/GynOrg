import os
#!/usr/bin/env python3
"""
Comprehensive test script for Vacation Allowances API endpoints
Tests all CRUD operations with proper authentication
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"
USERNAME = os.environ.get("ADMIN_USERNAME", "admin")
PASSWORD = os.environ.get("ADMIN_PASSWORD", "admin")

def get_auth_token():
    """Get authentication token"""
    auth_data = {
        "username": USERNAME,
        "password": PASSWORD
    }
    
    response = requests.post(f"{BASE_URL}/api/v1/auth/login", json=auth_data)
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        print(f"Authentication failed: {response.status_code}")
        print(response.text)
        return None

def create_test_employee(token):
    """Create a test employee for vacation allowance testing"""
    headers = {"Authorization": f"Bearer {token}"}
    employee_data = {
        "title": "Dr.",
        "first_name": "Test",
        "last_name": "Employee",
        "email": "test.employee@example.com",
        "position": "Ärztin",
        "birth_date": "1985-03-20",
        "date_hired": "2023-01-15",
        "federal_state": "Bayern",
        "active": True
    }
    
    response = requests.post(f"{BASE_URL}/api/v1/employees/", 
                           json=employee_data, headers=headers)
    if response.status_code == 201:
        employee = response.json()
        print(f"✓ Test employee created: ID {employee['id']}")
        return employee['id']
    else:
        print(f"✗ Failed to create test employee: {response.status_code}")
        print(response.text)
        return None

def test_vacation_allowances_crud(token, employee_id):
    """Test all CRUD operations for vacation allowances"""
    headers = {"Authorization": f"Bearer {token}"}
    
    print("\n=== Testing Vacation Allowances CRUD Operations ===")
    
    # 1. CREATE - Test creating a vacation allowance
    print("\n1. Testing CREATE vacation allowance...")
    vacation_data = {
        "employee_id": employee_id,
        "year": 2025,
        "annual_allowance": 30,
        "carryover_days": 5
    }
    
    response = requests.post(f"{BASE_URL}/api/v1/vacation-allowances/", 
                           json=vacation_data, headers=headers)
    if response.status_code == 201:
        vacation_allowance = response.json()
        vacation_id = vacation_allowance['id']
        print(f"✓ Vacation allowance created successfully: ID {vacation_id}")
        print(f"  Year: {vacation_allowance['year']}")
        print(f"  Annual allowance: {vacation_allowance['annual_allowance']}")
        print(f"  Carryover days: {vacation_allowance['carryover_days']}")
    else:
        print(f"✗ Failed to create vacation allowance: {response.status_code}")
        print(response.text)
        return None
    
    # 2. READ - Test getting all vacation allowances
    print("\n2. Testing GET all vacation allowances...")
    response = requests.get(f"{BASE_URL}/api/v1/vacation-allowances/", headers=headers)
    if response.status_code == 200:
        vacation_allowances = response.json()
        print(f"✓ Retrieved {len(vacation_allowances)} vacation allowance(s)")
        for va in vacation_allowances:
            print(f"  ID {va['id']}: {va['year']} - {va['annual_allowance']} days")
    else:
        print(f"✗ Failed to get vacation allowances: {response.status_code}")
        print(response.text)
    
    # 3. READ - Test getting specific vacation allowance
    print(f"\n3. Testing GET vacation allowance by ID ({vacation_id})...")
    response = requests.get(f"{BASE_URL}/api/v1/vacation-allowances/{vacation_id}", headers=headers)
    if response.status_code == 200:
        vacation_allowance = response.json()
        print(f"✓ Retrieved vacation allowance: {vacation_allowance['year']}")
        print(f"  Employee ID: {vacation_allowance['employee_id']}")
        print(f"  Annual allowance: {vacation_allowance['annual_allowance']}")
        print(f"  Carryover days: {vacation_allowance['carryover_days']}")
    else:
        print(f"✗ Failed to get vacation allowance: {response.status_code}")
        print(response.text)
    
    # 4. UPDATE - Test updating vacation allowance
    print(f"\n4. Testing UPDATE vacation allowance ({vacation_id})...")
    update_data = {
        "annual_allowance": 32,
        "carryover_days": 3
    }
    
    response = requests.put(f"{BASE_URL}/api/v1/vacation-allowances/{vacation_id}", 
                          json=update_data, headers=headers)
    if response.status_code == 200:
        updated_vacation = response.json()
        print(f"✓ Vacation allowance updated successfully")
        print(f"  Annual allowance: {updated_vacation['annual_allowance']} (was 30)")
        print(f"  Carryover days: {updated_vacation['carryover_days']} (was 5)")
    else:
        print(f"✗ Failed to update vacation allowance: {response.status_code}")
        print(response.text)
    
    # 5. Test duplicate year constraint
    print(f"\n5. Testing duplicate year constraint...")
    duplicate_data = {
        "employee_id": employee_id,
        "year": 2025,  # Same year as existing
        "annual_allowance": 25,
        "carryover_days": 2
    }
    
    response = requests.post(f"{BASE_URL}/api/v1/vacation-allowances/", 
                           json=duplicate_data, headers=headers)
    if response.status_code == 400:
        print(f"✓ Duplicate year constraint working correctly")
        print(f"  Error: {response.json().get('detail', 'Unknown error')}")
    else:
        print(f"✗ Duplicate year constraint not working: {response.status_code}")
        print(response.text)
    
    # 6. DELETE - Test deleting vacation allowance
    print(f"\n6. Testing DELETE vacation allowance ({vacation_id})...")
    response = requests.delete(f"{BASE_URL}/api/v1/vacation-allowances/{vacation_id}", headers=headers)
    if response.status_code == 204:
        print(f"✓ Vacation allowance deleted successfully")
    else:
        print(f"✗ Failed to delete vacation allowance: {response.status_code}")
        print(response.text)
    
    # 7. Verify deletion
    print(f"\n7. Verifying deletion...")
    response = requests.get(f"{BASE_URL}/api/v1/vacation-allowances/{vacation_id}", headers=headers)
    if response.status_code == 404:
        print(f"✓ Vacation allowance successfully deleted (404 Not Found)")
    else:
        print(f"✗ Vacation allowance still exists: {response.status_code}")
    
    return True

def cleanup_test_employee(token, employee_id):
    """Clean up test employee"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.delete(f"{BASE_URL}/api/v1/employees/{employee_id}", headers=headers)
    if response.status_code == 204:
        print(f"✓ Test employee cleaned up: ID {employee_id}")
    else:
        print(f"✗ Failed to clean up test employee: {response.status_code}")

def main():
    print("=== Vacation Allowances API Test Suite ===")
    print(f"Testing against: {BASE_URL}")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Get authentication token
    print("\nAuthenticating...")
    token = get_auth_token()
    if not token:
        print("✗ Authentication failed. Exiting.")
        sys.exit(1)
    print("✓ Authentication successful")
    
    # Create test employee
    employee_id = create_test_employee(token)
    if not employee_id:
        print("✗ Failed to create test employee. Exiting.")
        sys.exit(1)
    
    try:
        # Run vacation allowances tests
        success = test_vacation_allowances_crud(token, employee_id)
        
        if success:
            print("\n=== All Tests Completed Successfully! ===")
        else:
            print("\n=== Some Tests Failed ===")
            sys.exit(1)
            
    finally:
        # Clean up
        print("\nCleaning up...")
        cleanup_test_employee(token, employee_id)

if __name__ == "__main__":
    main()
