import requests
import json
from datetime import date

# Test Employee API endpoints with new data model
BASE_URL = "http://localhost:8000/api/v1"
headers = {"Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJNR2Fuc2VyIiwiZXhwIjoxNzUxOTg5OTg2fQ.rCoKp_343ein1melRX_30rpXNf_6uiHeCytW04T-PWU"}

def test_get_employees():
    """Test getting all employees"""
    response = requests.get(f"{BASE_URL}/employees", headers=headers)
    print(f"GET /employees: {response.status_code}")
    if response.status_code == 200:
        employees = response.json()
        print(f"Found {len(employees)} employees")
        for emp in employees:
            print(f"  - {emp.get('full_name', 'N/A')} ({emp.get('email', 'N/A')})")
    else:
        print(f"Error: {response.text}")
    return response

def test_create_employee():
    """Test creating a new employee with extended data model"""
    employee_data = {
        "title": "Dr.",
        "first_name": "Maria",
        "last_name": "Ganser",
        "email": "maria.ganser@gynorg.de",
        "position": "Gynäkologin",
        "birth_date": "1985-03-15",
        "date_hired": "2024-01-15",
        "federal_state": "BW",
        "active": True
    }
    
    response = requests.post(
        f"{BASE_URL}/employees", 
        headers=headers,
        json=employee_data
    )
    print(f"POST /employees: {response.status_code}")
    if response.status_code == 201:
        employee = response.json()
        print(f"Created employee: {employee.get('full_name')} (ID: {employee.get('id')})")
        print(f"  Email: {employee.get('email')}")
        print(f"  Federal State: {employee.get('federal_state')}")
        print(f"  Display Name: {employee.get('display_name')}")
    else:
        print(f"Error: {response.text}")
    return response

def test_create_employee_validation_errors():
    """Test validation errors for employee creation"""
    print("\n--- Testing Validation Errors ---")
    
    # Test 1: Invalid email
    invalid_email_data = {
        "first_name": "Test",
        "last_name": "User",
        "email": "invalid-email",
        "federal_state": "BW"
    }
    response = requests.post(f"{BASE_URL}/employees", headers=headers, json=invalid_email_data)
    print(f"Invalid email test: {response.status_code} (expected 422)")
    
    # Test 2: Birth date in future
    future_birth_data = {
        "first_name": "Test",
        "last_name": "User",
        "email": "test@example.com",
        "birth_date": "2030-01-01",
        "federal_state": "BW"
    }
    response = requests.post(f"{BASE_URL}/employees", headers=headers, json=future_birth_data)
    print(f"Future birth date test: {response.status_code} (expected 422)")
    
    # Test 3: Hire date before birth date
    invalid_dates_data = {
        "first_name": "Test",
        "last_name": "User",
        "email": "test2@example.com",
        "birth_date": "1990-01-01",
        "date_hired": "1985-01-01",
        "federal_state": "BW"
    }
    response = requests.post(f"{BASE_URL}/employees", headers=headers, json=invalid_dates_data)
    print(f"Hire date before birth date test: {response.status_code} (expected 422)")
    
    # Test 4: Missing required fields
    missing_fields_data = {
        "first_name": "Test"
        # Missing last_name, email, federal_state
    }
    response = requests.post(f"{BASE_URL}/employees", headers=headers, json=missing_fields_data)
    print(f"Missing required fields test: {response.status_code} (expected 422)")

def test_get_employee_by_id(employee_id):
    """Test getting employee by ID"""
    response = requests.get(f"{BASE_URL}/employees/{employee_id}", headers=headers)
    print(f"GET /employees/{employee_id}: {response.status_code}")
    if response.status_code == 200:
        employee = response.json()
        print(f"Employee details:")
        print(f"  Full Name: {employee.get('full_name')}")
        print(f"  Display Name: {employee.get('display_name')}")
        print(f"  Email: {employee.get('email')}")
        print(f"  Position: {employee.get('position')}")
        print(f"  Federal State: {employee.get('federal_state')}")
        print(f"  Active: {employee.get('active')}")
    else:
        print(f"Error: {response.text}")
    return response

def test_update_employee(employee_id):
    """Test updating an employee with new fields"""
    update_data = {
        "title": "Prof. Dr.",
        "position": "Chefärztin",
        "federal_state": "BY"
    }
    
    response = requests.put(
        f"{BASE_URL}/employees/{employee_id}", 
        headers=headers,
        json=update_data
    )
    print(f"PUT /employees/{employee_id}: {response.status_code}")
    if response.status_code == 200:
        employee = response.json()
        print(f"Updated employee: {employee.get('full_name')}")
        print(f"  New title: {employee.get('title')}")
        print(f"  New position: {employee.get('position')}")
        print(f"  New federal state: {employee.get('federal_state')}")
    else:
        print(f"Error: {response.text}")
    return response

def test_federal_states_endpoint():
    """Test the federal states utility endpoint"""
    response = requests.get(f"{BASE_URL}/federal-states", headers=headers)
    print(f"GET /federal-states: {response.status_code}")
    if response.status_code == 200:
        states = response.json()
        print(f"Available federal states: {len(states)}")
        for state in states[:3]:  # Show first 3
            print(f"  - {state.get('code')}: {state.get('name')}")
        print("  ...")
    else:
        print(f"Error: {response.text}")
    return response

def test_employee_search():
    """Test employee search functionality"""
    # Test search by name
    response = requests.get(f"{BASE_URL}/employees?search=Maria", headers=headers)
    print(f"GET /employees?search=Maria: {response.status_code}")
    if response.status_code == 200:
        employees = response.json()
        print(f"Search results: {len(employees)} employees")
    
    # Test filter by federal state
    response = requests.get(f"{BASE_URL}/employees?federal_state=BW", headers=headers)
    print(f"GET /employees?federal_state=BW: {response.status_code}")
    if response.status_code == 200:
        employees = response.json()
        print(f"BW employees: {len(employees)} employees")
    
    # Test filter by active status
    response = requests.get(f"{BASE_URL}/employees?active=true", headers=headers)
    print(f"GET /employees?active=true: {response.status_code}")
    if response.status_code == 200:
        employees = response.json()
        print(f"Active employees: {len(employees)} employees")

if __name__ == "__main__":
    print("Testing Employee API endpoints with extended data model...")
    print("=" * 60)
    
    # Test utility endpoints first
    print("\n1. Testing utility endpoints...")
    test_federal_states_endpoint()
    
    # Test getting empty/existing list
    print("\n2. Getting current employees...")
    test_get_employees()
    
    # Test validation errors
    test_create_employee_validation_errors()
    
    # Test creating employee with new model
    print("\n3. Creating new employee...")
    create_response = test_create_employee()
    
    if create_response.status_code == 201:
        employee_id = create_response.json()["id"]
        
        # Test getting specific employee
        print(f"\n4. Getting employee by ID...")
        test_get_employee_by_id(employee_id)
        
        # Test updating employee
        print(f"\n5. Updating employee...")
        test_update_employee(employee_id)
        
        # Test getting updated employee
        print(f"\n6. Getting updated employee...")
        test_get_employee_by_id(employee_id)
        
        # Test search functionality
        print(f"\n7. Testing search functionality...")
        test_employee_search()
        
        # Test getting all employees again
        print(f"\n8. Final employee list...")
        test_get_employees()
    
    print("\n" + "=" * 60)
    print("Employee API testing completed!")
