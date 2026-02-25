import requests
import json
from datetime import datetime

# Test VacationAllowance API endpoints
BASE_URL = "http://localhost:8000/api/v1"
headers = {"Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJNR2Fuc2VyIiwiZXhwIjoxNzUxOTg5OTg2fQ.rCoKp_343ein1melRX_30rpXNf_6uiHeCytW04T-PWU"}

def create_test_employee():
    """Create a test employee for vacation allowance tests"""
    employee_data = {
        "first_name": "Test",
        "last_name": "Employee",
        "email": "test.employee@gynorg.de",
        "federal_state": "BW",
        "active": True
    }
    
    response = requests.post(f"{BASE_URL}/employees", headers=headers, json=employee_data)
    if response.status_code == 201:
        return response.json()["id"]
    else:
        print(f"Failed to create test employee: {response.text}")
        return None

def test_get_vacation_allowances():
    """Test getting all vacation allowances"""
    response = requests.get(f"{BASE_URL}/vacation-allowances", headers=headers)
    print(f"GET /vacation-allowances: {response.status_code}")
    if response.status_code == 200:
        allowances = response.json()
        print(f"Found {len(allowances)} vacation allowances")
        for allowance in allowances:
            print(f"  - Employee {allowance.get('employee_id')}: {allowance.get('year')} - {allowance.get('total_allowance')} days")
    else:
        print(f"Error: {response.text}")
    return response

def test_create_vacation_allowance(employee_id):
    """Test creating a vacation allowance"""
    current_year = datetime.now().year
    allowance_data = {
        "employee_id": employee_id,
        "year": current_year,
        "annual_allowance": 30,
        "carryover_days": 5
    }
    
    response = requests.post(
        f"{BASE_URL}/vacation-allowances", 
        headers=headers,
        json=allowance_data
    )
    print(f"POST /vacation-allowances: {response.status_code}")
    if response.status_code == 201:
        allowance = response.json()
        print(f"Created vacation allowance: ID {allowance.get('id')}")
        print(f"  Employee: {allowance.get('employee_id')}")
        print(f"  Year: {allowance.get('year')}")
        print(f"  Annual: {allowance.get('annual_allowance')} days")
        print(f"  Carryover: {allowance.get('carryover_days')} days")
        print(f"  Total: {allowance.get('total_allowance')} days")
    else:
        print(f"Error: {response.text}")
    return response

def test_get_vacation_allowance_by_id(allowance_id):
    """Test getting vacation allowance by ID"""
    response = requests.get(f"{BASE_URL}/vacation-allowances/{allowance_id}", headers=headers)
    print(f"GET /vacation-allowances/{allowance_id}: {response.status_code}")
    if response.status_code == 200:
        allowance = response.json()
        print(f"Vacation allowance details:")
        print(f"  ID: {allowance.get('id')}")
        print(f"  Employee: {allowance.get('employee_id')}")
        print(f"  Year: {allowance.get('year')}")
        print(f"  Annual: {allowance.get('annual_allowance')} days")
        print(f"  Carryover: {allowance.get('carryover_days')} days")
        print(f"  Total: {allowance.get('total_allowance')} days")
        print(f"  Created: {allowance.get('created_at')}")
        print(f"  Updated: {allowance.get('updated_at')}")
    else:
        print(f"Error: {response.text}")
    return response

def test_update_vacation_allowance(allowance_id):
    """Test updating a vacation allowance"""
    update_data = {
        "annual_allowance": 32,
        "carryover_days": 3
    }
    
    response = requests.put(
        f"{BASE_URL}/vacation-allowances/{allowance_id}", 
        headers=headers,
        json=update_data
    )
    print(f"PUT /vacation-allowances/{allowance_id}: {response.status_code}")
    if response.status_code == 200:
        allowance = response.json()
        print(f"Updated vacation allowance:")
        print(f"  Annual: {allowance.get('annual_allowance')} days")
        print(f"  Carryover: {allowance.get('carryover_days')} days")
        print(f"  Total: {allowance.get('total_allowance')} days")
    else:
        print(f"Error: {response.text}")
    return response

def test_get_employee_vacation_allowances(employee_id):
    """Test getting vacation allowances for a specific employee"""
    response = requests.get(f"{BASE_URL}/employees/{employee_id}/vacation-allowances", headers=headers)
    print(f"GET /employees/{employee_id}/vacation-allowances: {response.status_code}")
    if response.status_code == 200:
        allowances = response.json()
        print(f"Employee {employee_id} has {len(allowances)} vacation allowances:")
        for allowance in allowances:
            print(f"  - {allowance.get('year')}: {allowance.get('total_allowance')} days")
    else:
        print(f"Error: {response.text}")
    return response

def test_delete_vacation_allowance(allowance_id):
    """Test deleting a vacation allowance"""
    response = requests.delete(f"{BASE_URL}/vacation-allowances/{allowance_id}", headers=headers)
    print(f"DELETE /vacation-allowances/{allowance_id}: {response.status_code}")
    if response.status_code == 204:
        print("Vacation allowance deleted successfully")
    else:
        print(f"Error: {response.text}")
    return response

def test_create_duplicate_vacation_allowance(employee_id):
    """Test creating duplicate vacation allowance (should fail)"""
    current_year = datetime.now().year
    allowance_data = {
        "employee_id": employee_id,
        "year": current_year,  # Same year as existing allowance
        "annual_allowance": 25,
        "carryover_days": 0
    }
    
    response = requests.post(
        f"{BASE_URL}/vacation-allowances", 
        headers=headers,
        json=allowance_data
    )
    print(f"POST /vacation-allowances (duplicate): {response.status_code} (expected 400/422)")
    if response.status_code != 201:
        print("Correctly prevented duplicate vacation allowance creation")
    else:
        print("ERROR: Duplicate vacation allowance was created!")
    return response

def test_vacation_allowance_validation():
    """Test validation errors for vacation allowance creation"""
    print("\n--- Testing Vacation Allowance Validation ---")
    
    # Test 1: Missing employee_id
    invalid_data = {
        "year": 2024,
        "annual_allowance": 30
    }
    response = requests.post(f"{BASE_URL}/vacation-allowances", headers=headers, json=invalid_data)
    print(f"Missing employee_id test: {response.status_code} (expected 422)")
    
    # Test 2: Invalid employee_id
    invalid_data = {
        "employee_id": 99999,  # Non-existent employee
        "year": 2024,
        "annual_allowance": 30
    }
    response = requests.post(f"{BASE_URL}/vacation-allowances", headers=headers, json=invalid_data)
    print(f"Invalid employee_id test: {response.status_code} (expected 400/422)")
    
    # Test 3: Negative values
    employee_id = create_test_employee()
    if employee_id:
        invalid_data = {
            "employee_id": employee_id,
            "year": 2024,
            "annual_allowance": -5,  # Negative allowance
            "carryover_days": -2     # Negative carryover
        }
        response = requests.post(f"{BASE_URL}/vacation-allowances", headers=headers, json=invalid_data)
        print(f"Negative values test: {response.status_code} (expected 422)")

if __name__ == "__main__":
    print("Testing VacationAllowance API endpoints...")
    print("=" * 60)
    
    # Create a test employee first
    print("\n1. Creating test employee...")
    employee_id = create_test_employee()
    
    if not employee_id:
        print("Failed to create test employee. Exiting.")
        exit(1)
    
    print(f"Created test employee with ID: {employee_id}")
    
    # Test getting empty list
    print("\n2. Getting current vacation allowances...")
    test_get_vacation_allowances()
    
    # Test validation errors
    test_vacation_allowance_validation()
    
    # Test creating vacation allowance
    print("\n3. Creating vacation allowance...")
    create_response = test_create_vacation_allowance(employee_id)
    
    if create_response.status_code == 201:
        allowance_id = create_response.json()["id"]
        
        # Test getting specific allowance
        print(f"\n4. Getting vacation allowance by ID...")
        test_get_vacation_allowance_by_id(allowance_id)
        
        # Test updating allowance
        print(f"\n5. Updating vacation allowance...")
        test_update_vacation_allowance(allowance_id)
        
        # Test getting updated allowance
        print(f"\n6. Getting updated vacation allowance...")
        test_get_vacation_allowance_by_id(allowance_id)
        
        # Test getting employee's allowances
        print(f"\n7. Getting employee's vacation allowances...")
        test_get_employee_vacation_allowances(employee_id)
        
        # Test duplicate creation (should fail)
        print(f"\n8. Testing duplicate creation...")
        test_create_duplicate_vacation_allowance(employee_id)
        
        # Test getting all allowances again
        print(f"\n9. Getting all vacation allowances...")
        test_get_vacation_allowances()
        
        # Test deleting allowance
        print(f"\n10. Deleting vacation allowance...")
        test_delete_vacation_allowance(allowance_id)
        
        # Final check
        print(f"\n11. Final vacation allowances list...")
        test_get_vacation_allowances()
    
    print("\n" + "=" * 60)
    print("VacationAllowance API testing completed!")
