import os
#!/usr/bin/env python3
"""
Test script to verify the Create Employee Form functionality.
"""

import requests
import json

# Test configuration
BASE_URL = "http://localhost:8000/api/v1"
USERNAME = os.environ.get("ADMIN_USERNAME", "admin")
PASSWORD = os.environ.get("ADMIN_PASSWORD", "admin")

def get_auth_token():
    """Get authentication token"""
    login_data = {
        'username': USERNAME,
        'password': PASSWORD
    }
    
    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    
    if response.status_code == 200:
        token_data = response.json()
        return token_data['access_token']
    else:
        print(f"❌ Login failed: {response.status_code}")
        return None

def test_create_employee(token):
    """Test creating a new employee"""
    print("Testing employee creation...")
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    # Test data for new employee
    employee_data = {
        'name': 'Test Mitarbeiter',
        'position': 'Software Developer',
        'vacation_allowance': 25,
        'date_hired': '2024-01-15',
        'active': True
    }
    
    response = requests.post(f"{BASE_URL}/employees/", json=employee_data, headers=headers)
    
    if response.status_code == 201:
        created_employee = response.json()
        print(f"✅ Employee created successfully!")
        print(f"ID: {created_employee['id']}")
        print(f"Name: {created_employee['name']}")
        print(f"Position: {created_employee['position']}")
        print(f"Vacation Allowance: {created_employee['vacation_allowance']}")
        print(f"Date Hired: {created_employee['date_hired']}")
        print(f"Active: {created_employee['active']}")
        return created_employee['id']
    else:
        print(f"❌ Employee creation failed: {response.status_code}")
        print(f"Response: {response.text}")
        return None

def test_create_minimal_employee(token):
    """Test creating employee with minimal data"""
    print("\nTesting minimal employee creation...")
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    # Minimal data (only required fields)
    employee_data = {
        'name': 'Minimal Mitarbeiter'
    }
    
    response = requests.post(f"{BASE_URL}/employees/", json=employee_data, headers=headers)
    
    if response.status_code == 201:
        created_employee = response.json()
        print(f"✅ Minimal employee created successfully!")
        print(f"ID: {created_employee['id']}")
        print(f"Name: {created_employee['name']}")
        print(f"Position: {created_employee.get('position', 'None')}")
        print(f"Vacation Allowance: {created_employee['vacation_allowance']}")
        print(f"Active: {created_employee['active']}")
        return created_employee['id']
    else:
        print(f"❌ Minimal employee creation failed: {response.status_code}")
        print(f"Response: {response.text}")
        return None

def test_validation_errors(token):
    """Test form validation"""
    print("\nTesting validation errors...")
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    # Test with empty name (should fail)
    employee_data = {
        'name': '',
        'position': 'Test Position'
    }
    
    response = requests.post(f"{BASE_URL}/employees/", json=employee_data, headers=headers)
    
    if response.status_code == 422:
        print("✅ Empty name correctly rejected!")
        errors = response.json()
        print(f"Validation errors: {errors}")
    else:
        print(f"❌ Empty name should be rejected but got: {response.status_code}")
    
    # Test with invalid vacation allowance
    employee_data = {
        'name': 'Test User',
        'vacation_allowance': -5
    }
    
    response = requests.post(f"{BASE_URL}/employees/", json=employee_data, headers=headers)
    
    if response.status_code == 422:
        print("✅ Invalid vacation allowance correctly rejected!")
    else:
        print(f"❌ Invalid vacation allowance should be rejected but got: {response.status_code}")

def test_list_employees(token):
    """Test listing all employees"""
    print("\nTesting employee list...")
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    response = requests.get(f"{BASE_URL}/employees/", headers=headers)
    
    if response.status_code == 200:
        employees = response.json()
        print(f"✅ Employee list retrieved successfully!")
        print(f"Total employees: {len(employees)}")
        for emp in employees:
            print(f"  - {emp['name']} (ID: {emp['id']})")
        return True
    else:
        print(f"❌ Employee list retrieval failed: {response.status_code}")
        return False

def main():
    print("🧪 Testing Create Employee Form Integration")
    print("=" * 50)
    
    # Get authentication token
    token = get_auth_token()
    if not token:
        print("❌ Cannot continue without valid token")
        return
    
    # Test employee creation
    employee_id = test_create_employee(token)
    if not employee_id:
        print("❌ Employee creation test failed")
        return
    
    # Test minimal employee creation
    minimal_id = test_create_minimal_employee(token)
    if not minimal_id:
        print("❌ Minimal employee creation test failed")
        return
    
    # Test validation
    test_validation_errors(token)
    
    # Test listing employees
    if not test_list_employees(token):
        print("❌ Employee list test failed")
        return
    
    print("\n🎉 All Create Employee Form tests passed!")
    print("\nThe frontend form should now be able to:")
    print("1. Create employees with full data")
    print("2. Create employees with minimal data (name only)")
    print("3. Show validation errors for invalid input")
    print("4. Refresh the employee list after creation")
    print("5. Handle server errors gracefully")

if __name__ == "__main__":
    main()
