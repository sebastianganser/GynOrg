import requests
import pytest

# Test Employee API endpoints
BASE_URL = "http://localhost:8000/api/v1"

def test_get_employees(auth_headers):
    """Test getting all employees"""
    response = requests.get(f"{BASE_URL}/employees", headers=auth_headers)
    assert response.status_code == 200
    return response

def test_create_employee(auth_headers):
    """Test creating a new employee"""
    employee_data = {
        "first_name": "Maria",
        "last_name": "Ganser",
        "email": "maria.ganser@gynorg.de",
        "position": "Gynäkologin",
        "federal_state": "Bayern"
    }
    
    response = requests.post(f"{BASE_URL}/employees", json=employee_data, headers=auth_headers)
    # Should fail because email already exists
    assert response.status_code == 400
    return response

def test_get_employee_by_id(employee_id: int, auth_headers):
    """Test getting a specific employee by ID"""
    response = requests.get(f"{BASE_URL}/employees/{employee_id}", headers=auth_headers)
    assert response.status_code == 200
    
    employee = response.json()
    assert employee["id"] == employee_id
    assert employee["first_name"] == "Test"
    assert employee["last_name"] == "Employee"
    assert employee["email"].startswith("test.employee.")
    assert employee["email"].endswith("@example.com")
    
    return response
