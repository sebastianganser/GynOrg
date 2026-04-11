import pytest
import requests
import os
from typing import Generator

# Base URL for API tests
BASE_URL = os.environ.get("TEST_API_BASE_URL", "http://localhost:8000/api/v1")

@pytest.fixture(scope="session")
def api_base_url():
    """Base URL for API tests"""
    return BASE_URL

@pytest.fixture(scope="session")
def auth_token():
    """Get authentication token for API tests"""
    login_data = {
        "username": os.environ.get("ADMIN_USERNAME", "admin"),
        "password": os.environ.get("ADMIN_PASSWORD", "admin")
    }
    
    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    assert response.status_code == 200
    
    token_data = response.json()
    return token_data["access_token"]

@pytest.fixture(scope="session")
def auth_headers(auth_token):
    """Get authorization headers for API tests"""
    return {"Authorization": f"Bearer {auth_token}"}

@pytest.fixture
def employee_id(auth_headers) -> Generator[int, None, None]:
    """Create a test employee and return its ID, cleanup after test"""
    import uuid
    unique_id = str(uuid.uuid4())[:8]
    
    # Create test employee
    employee_data = {
        "first_name": "Test",
        "last_name": "Employee", 
        "email": f"test.employee.{unique_id}@example.com",
        "position": "Test Position",
        "federal_state": "Bayern"
    }
    
    response = requests.post(f"{BASE_URL}/employees", json=employee_data, headers=auth_headers)
    assert response.status_code == 201
    
    employee = response.json()
    employee_id = employee["id"]
    
    yield employee_id
    
    # Cleanup: Delete the test employee
    try:
        requests.delete(f"{BASE_URL}/employees/{employee_id}/hard", headers=auth_headers)
    except:
        pass  # Ignore cleanup errors

@pytest.fixture
def allowance_id(employee_id: int, auth_headers) -> Generator[int, None, None]:
    """Create a test vacation allowance and return its ID, cleanup after test"""
    # Create test vacation allowance
    allowance_data = {
        "employee_id": employee_id,
        "year": 2024,
        "annual_allowance": 30,
        "carryover_days": 5
    }
    
    response = requests.post(f"{BASE_URL}/vacation-allowances", json=allowance_data, headers=auth_headers)
    assert response.status_code == 201
    
    allowance = response.json()
    allowance_id = allowance["id"]
    
    yield allowance_id
    
    # Cleanup: Delete the test allowance
    try:
        requests.delete(f"{BASE_URL}/vacation-allowances/{allowance_id}", headers=auth_headers)
    except:
        pass  # Ignore cleanup errors
