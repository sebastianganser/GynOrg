import requests
import json

# Test all Employee API endpoints
BASE_URL = "http://localhost:8000/api/v1"
headers = {"Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJNR2Fuc2VyIiwiZXhwIjoxNzUzMTk1MjE1fQ.JKUwfsABM0UjrEZLEwlafLd0ybEg7FejVIu5806PI8A"}

def test_create_employee():
    """Test creating a new employee"""
    employee_data = {
        "title": "Dr.",
        "first_name": "Anna",
        "last_name": "Schmidt",
        "email": "anna.schmidt@gynorg.de",
        "position": "Assistenzärztin",
        "date_hired": "2024-03-01",
        "federal_state": "Baden-Württemberg",
        "active": True
    }
    
    response = requests.post(
        f"{BASE_URL}/employees/", 
        headers=headers,
        json=employee_data
    )
    print(f"POST /employees/: {response.status_code}")
    print(f"Response: {response.json()}")
    return response

def test_update_employee(employee_id):
    """Test updating an employee"""
    update_data = {
        "position": "Oberärztin",
        "title": "Prof. Dr."
    }
    
    response = requests.put(
        f"{BASE_URL}/employees/{employee_id}", 
        headers=headers,
        json=update_data
    )
    print(f"PUT /employees/{employee_id}: {response.status_code}")
    print(f"Response: {response.json()}")
    return response

def test_soft_delete_employee(employee_id):
    """Test soft deleting an employee"""
    response = requests.delete(f"{BASE_URL}/employees/{employee_id}", headers=headers)
    print(f"DELETE /employees/{employee_id}: {response.status_code}")
    return response

def test_hard_delete_employee(employee_id):
    """Test hard deleting an employee"""
    response = requests.delete(f"{BASE_URL}/employees/{employee_id}/hard", headers=headers)
    print(f"DELETE /employees/{employee_id}/hard: {response.status_code}")
    return response

def test_get_employees():
    """Test getting all employees"""
    response = requests.get(f"{BASE_URL}/employees/", headers=headers)
    print(f"GET /employees/: {response.status_code}")
    print(f"Response: {response.json()}")
    return response

if __name__ == "__main__":
    print("Testing full Employee CRUD API...")
    
    # Create a new employee
    print("\n1. Creating employee...")
    create_response = test_create_employee()
    
    if create_response.status_code == 201:
        employee_id = create_response.json()["id"]
        
        # Update the employee
        print(f"\n2. Updating employee {employee_id}...")
        test_update_employee(employee_id)
        
        # Get all employees to see the update
        print(f"\n3. Getting all employees after update...")
        test_get_employees()
        
        # Soft delete the employee
        print(f"\n4. Soft deleting employee {employee_id}...")
        test_soft_delete_employee(employee_id)
        
        # Get all employees to see soft delete effect
        print(f"\n5. Getting all employees after soft delete...")
        test_get_employees()
        
        # Create another employee for hard delete test
        print(f"\n6. Creating another employee for hard delete test...")
        create_response2 = test_create_employee()
        
        if create_response2.status_code == 201:
            employee_id2 = create_response2.json()["id"]
            
            # Hard delete the second employee
            print(f"\n7. Hard deleting employee {employee_id2}...")
            test_hard_delete_employee(employee_id2)
            
            # Final check
            print(f"\n8. Final employee list...")
            test_get_employees()
