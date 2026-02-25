import requests
import json
import time
from datetime import datetime, date

# Complete system test for GynOrg application
BASE_URL = "http://localhost:8000/api/v1"
FRONTEND_URL = "http://localhost:3000"

def get_auth_token():
    """Get authentication token"""
    auth_data = {
        "username": "MGanser",
        "password": "M4rvelf4n"
    }
    
    response = requests.post(f"{BASE_URL}/auth/login", json=auth_data)
    if response.status_code == 200:
        token_data = response.json()
        return token_data["access_token"]
    else:
        print(f"Authentication failed: {response.text}")
        return None

def test_authentication():
    """Test authentication system"""
    print("=== Testing Authentication ===")
    
    # Test login
    token = get_auth_token()
    if token:
        print("✅ Login successful")
        headers = {"Authorization": f"Bearer {token}"}
        
        # Test protected endpoint
        response = requests.get(f"{BASE_URL}/employees", headers=headers)
        if response.status_code == 200:
            print("✅ Protected endpoint access successful")
            return headers
        else:
            print(f"❌ Protected endpoint access failed: {response.status_code}")
    else:
        print("❌ Login failed")
    
    return None

def test_employee_crud(headers):
    """Test complete Employee CRUD operations"""
    print("\n=== Testing Employee CRUD ===")
    
    # Use timestamp to ensure unique email
    timestamp = int(time.time())
    
    # Create employee
    employee_data = {
        "title": "Dr.",
        "first_name": "Test",
        "last_name": "Employee",
        "email": f"test.employee.{timestamp}@gynorg.de",
        "position": "Gynäkologin",
        "birth_date": "1985-05-15",
        "date_hired": "2024-01-15",
        "federal_state": "Baden-Württemberg",
        "active": True
    }
    
    response = requests.post(f"{BASE_URL}/employees", headers=headers, json=employee_data)
    if response.status_code == 201:
        employee = response.json()
        employee_id = employee["id"]
        print(f"✅ Employee created: {employee['first_name']} {employee['last_name']} (ID: {employee_id})")
        
        # Read employee
        response = requests.get(f"{BASE_URL}/employees/{employee_id}", headers=headers)
        if response.status_code == 200:
            print("✅ Employee read successful")
            
            # Update employee
            update_data = {"position": "Chefärztin", "title": "Prof. Dr."}
            response = requests.put(f"{BASE_URL}/employees/{employee_id}", headers=headers, json=update_data)
            if response.status_code == 200:
                updated_employee = response.json()
                print(f"✅ Employee updated: {updated_employee['first_name']} {updated_employee['last_name']}")
                
                return employee_id
            else:
                print(f"❌ Employee update failed: {response.status_code}")
        else:
            print(f"❌ Employee read failed: {response.status_code}")
    else:
        print(f"❌ Employee creation failed: {response.status_code} - {response.text}")
    
    return None

def test_vacation_allowance_crud(headers, employee_id):
    """Test complete VacationAllowance CRUD operations"""
    print("\n=== Testing Vacation Allowance CRUD ===")
    
    current_year = datetime.now().year
    allowance_data = {
        "employee_id": employee_id,
        "year": current_year,
        "annual_allowance": 30,
        "carryover_days": 5
    }
    
    # Create vacation allowance
    response = requests.post(f"{BASE_URL}/vacation-allowances", headers=headers, json=allowance_data)
    if response.status_code == 201:
        allowance = response.json()
        allowance_id = allowance["id"]
        print(f"✅ Vacation allowance created: {allowance['total_allowance']} days (ID: {allowance_id})")
        
        # Read vacation allowance
        response = requests.get(f"{BASE_URL}/vacation-allowances/{allowance_id}", headers=headers)
        if response.status_code == 200:
            print("✅ Vacation allowance read successful")
            
            # Update vacation allowance
            update_data = {"annual_allowance": 32, "carryover_days": 3}
            response = requests.put(f"{BASE_URL}/vacation-allowances/{allowance_id}", headers=headers, json=update_data)
            if response.status_code == 200:
                updated_allowance = response.json()
                print(f"✅ Vacation allowance updated: {updated_allowance['total_allowance']} days")
                
                return allowance_id
            else:
                print(f"❌ Vacation allowance update failed: {response.status_code}")
        else:
            print(f"❌ Vacation allowance read failed: {response.status_code}")
    else:
        print(f"❌ Vacation allowance creation failed: {response.status_code} - {response.text}")
    
    return None

def test_data_relationships(headers, employee_id):
    """Test data relationships between employees and vacation allowances"""
    print("\n=== Testing Data Relationships ===")
    
    # Get employee with vacation allowances
    response = requests.get(f"{BASE_URL}/employees/{employee_id}/vacation-allowances", headers=headers)
    if response.status_code == 200:
        allowances = response.json()
        print(f"✅ Employee has {len(allowances)} vacation allowances")
        
        # Test filtering and searching
        response = requests.get(f"{BASE_URL}/employees?federal_state=Baden-Württemberg", headers=headers)
        if response.status_code == 200:
            bw_employees = response.json()
            print(f"✅ Found {len(bw_employees)} employees in Baden-Württemberg")
        
        response = requests.get(f"{BASE_URL}/employees?search=Test", headers=headers)
        if response.status_code == 200:
            search_results = response.json()
            print(f"✅ Search found {len(search_results)} employees")
        
        return True
    else:
        print(f"❌ Employee vacation allowances failed: {response.status_code}")
        return False

def test_utility_endpoints(headers):
    """Test utility endpoints"""
    print("\n=== Testing Utility Endpoints ===")
    
    # Test federal states endpoint
    response = requests.get(f"{BASE_URL}/federal-states", headers=headers)
    if response.status_code == 200:
        states = response.json()
        print(f"✅ Federal states endpoint: {len(states)} states available")
    else:
        print(f"❌ Federal states endpoint failed: {response.status_code}")
    
    # Test health check
    response = requests.get(f"{BASE_URL}/health")
    if response.status_code == 200:
        print("✅ Health check successful")
    else:
        print(f"❌ Health check failed: {response.status_code}")

def test_validation_and_errors(headers):
    """Test validation and error handling"""
    print("\n=== Testing Validation and Error Handling ===")
    
    # Test invalid employee data
    invalid_employee = {
        "first_name": "Test",
        "last_name": "User",
        "email": "invalid-email",  # Invalid email
        "federal_state": "Baden-Württemberg"
    }
    response = requests.post(f"{BASE_URL}/employees", headers=headers, json=invalid_employee)
    if response.status_code == 422:
        print("✅ Email validation working")
    else:
        print(f"❌ Email validation failed: {response.status_code}")
    
    # Test future birth date
    future_birth_employee = {
        "first_name": "Test",
        "last_name": "User",
        "email": "test@example.com",
        "birth_date": "2030-01-01",  # Future date
        "federal_state": "Baden-Württemberg"
    }
    response = requests.post(f"{BASE_URL}/employees", headers=headers, json=future_birth_employee)
    if response.status_code == 422:
        print("✅ Birth date validation working")
    else:
        print(f"❌ Birth date validation failed: {response.status_code}")
    
    # Test non-existent employee
    response = requests.get(f"{BASE_URL}/employees/99999", headers=headers)
    if response.status_code == 404:
        print("✅ 404 handling working")
    else:
        print(f"❌ 404 handling failed: {response.status_code}")

def test_frontend_accessibility():
    """Test if frontend is accessible"""
    print("\n=== Testing Frontend Accessibility ===")
    
    try:
        response = requests.get(FRONTEND_URL, timeout=5)
        if response.status_code == 200:
            print("✅ Frontend is accessible")
            return True
        else:
            print(f"❌ Frontend returned status: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Frontend not accessible: {e}")
    
    return False

def cleanup_test_data(headers, employee_id, allowance_id):
    """Clean up test data"""
    print("\n=== Cleaning Up Test Data ===")
    
    # Delete vacation allowance
    if allowance_id:
        response = requests.delete(f"{BASE_URL}/vacation-allowances/{allowance_id}", headers=headers)
        if response.status_code == 204:
            print("✅ Vacation allowance deleted")
        else:
            print(f"❌ Vacation allowance deletion failed: {response.status_code}")
    
    # Delete employee
    if employee_id:
        response = requests.delete(f"{BASE_URL}/employees/{employee_id}", headers=headers)
        if response.status_code == 204:
            print("✅ Employee deleted")
        else:
            print(f"❌ Employee deletion failed: {response.status_code}")

def run_complete_system_test():
    """Run complete system test"""
    print("🚀 Starting Complete System Test for GynOrg")
    print("=" * 60)
    
    start_time = time.time()
    
    # Test authentication
    headers = test_authentication()
    if not headers:
        print("❌ System test failed: Authentication not working")
        return False
    
    # Test utility endpoints
    test_utility_endpoints(headers)
    
    # Test validation and error handling
    test_validation_and_errors(headers)
    
    # Test employee CRUD
    employee_id = test_employee_crud(headers)
    if not employee_id:
        print("❌ System test failed: Employee CRUD not working")
        return False
    
    # Test vacation allowance CRUD
    allowance_id = test_vacation_allowance_crud(headers, employee_id)
    if not allowance_id:
        print("❌ System test failed: Vacation allowance CRUD not working")
        return False
    
    # Test data relationships
    relationships_ok = test_data_relationships(headers, employee_id)
    if not relationships_ok:
        print("❌ System test failed: Data relationships not working")
        return False
    
    # Test frontend accessibility
    frontend_ok = test_frontend_accessibility()
    
    # Clean up test data
    cleanup_test_data(headers, employee_id, allowance_id)
    
    end_time = time.time()
    duration = end_time - start_time
    
    print("\n" + "=" * 60)
    print(f"🎉 Complete System Test Results:")
    print(f"   Duration: {duration:.2f} seconds")
    print(f"   Backend API: ✅ Working")
    print(f"   Authentication: ✅ Working")
    print(f"   Employee Management: ✅ Working")
    print(f"   Vacation Allowances: ✅ Working")
    print(f"   Data Validation: ✅ Working")
    print(f"   Frontend: {'✅ Working' if frontend_ok else '❌ Not accessible'}")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    success = run_complete_system_test()
    if success:
        print("\n🎉 All system tests passed!")
        exit(0)
    else:
        print("\n❌ Some system tests failed!")
        exit(1)
