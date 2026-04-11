"""
Comprehensive API Integration Tests for VacationAllowance Management
Tests all CRUD operations, business logic, error handling, and edge cases
"""
import pytest
import requests
from typing import Dict, Any


class TestVacationAllowanceAPI:
    """Test suite for VacationAllowance API endpoints"""

    def test_get_vacation_allowances_empty(self, api_base_url: str, auth_headers: Dict[str, str]):
        """Test GET /vacation-allowances/ returns empty list when no data"""
        response = requests.get(f"{api_base_url}/vacation-allowances", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_get_vacation_allowances_with_data(self, api_base_url: str, auth_headers: Dict[str, str], allowance_id: int):
        """Test GET /vacation-allowances/ returns data when allowances exist"""
        response = requests.get(f"{api_base_url}/vacation-allowances", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        
        # Verify structure of returned allowance
        allowance = next((a for a in data if a["id"] == allowance_id), None)
        assert allowance is not None
        assert "id" in allowance
        assert "employee_id" in allowance
        assert "year" in allowance
        assert "annual_allowance" in allowance
        assert "carryover_days" in allowance
        assert "total_allowance" in allowance
        assert "created_at" in allowance
        assert "updated_at" in allowance

    def test_get_vacation_allowances_filter_by_year(self, api_base_url: str, auth_headers: Dict[str, str], allowance_id: int):
        """Test GET /vacation-allowances/ with year filter"""
        # Test with existing year
        response = requests.get(f"{api_base_url}/vacation-allowances?year=2024", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert all(allowance["year"] == 2024 for allowance in data)
        
        # Test with non-existing year
        response = requests.get(f"{api_base_url}/vacation-allowances?year=2030", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 0

    def test_get_vacation_allowances_filter_by_employee(self, api_base_url: str, auth_headers: Dict[str, str], 
                                                       employee_id: int, allowance_id: int):
        """Test GET /vacation-allowances/ with employee_id filter"""
        response = requests.get(f"{api_base_url}/vacation-allowances?employee_id={employee_id}", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert all(allowance["employee_id"] == employee_id for allowance in data)
        assert len(data) >= 1

    def test_get_vacation_allowance_by_id(self, api_base_url: str, auth_headers: Dict[str, str], allowance_id: int):
        """Test GET /vacation-allowances/{id}"""
        response = requests.get(f"{api_base_url}/vacation-allowances/{allowance_id}", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == allowance_id
        assert "employee_id" in data
        assert "year" in data
        assert "annual_allowance" in data
        assert "carryover_days" in data
        assert "total_allowance" in data
        assert data["total_allowance"] == data["annual_allowance"] + data["carryover_days"]

    def test_get_vacation_allowance_by_id_not_found(self, api_base_url: str, auth_headers: Dict[str, str]):
        """Test GET /vacation-allowances/{id} with non-existing ID"""
        response = requests.get(f"{api_base_url}/vacation-allowances/99999", headers=auth_headers)
        
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"].lower()

    def test_create_vacation_allowance(self, api_base_url: str, auth_headers: Dict[str, str], employee_id: int):
        """Test POST /vacation-allowances/"""
        allowance_data = {
            "employee_id": employee_id,
            "year": 2025,
            "annual_allowance": 28,
            "carryover_days": 3
        }
        
        response = requests.post(f"{api_base_url}/vacation-allowances", json=allowance_data, headers=auth_headers)
        
        assert response.status_code == 201
        data = response.json()
        assert data["employee_id"] == employee_id
        assert data["year"] == 2025
        assert data["annual_allowance"] == 28
        assert data["carryover_days"] == 3
        assert data["total_allowance"] == 31
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data
        
        # Cleanup
        requests.delete(f"{api_base_url}/vacation-allowances/{data['id']}", headers=auth_headers)

    def test_create_vacation_allowance_with_defaults(self, api_base_url: str, auth_headers: Dict[str, str], employee_id: int):
        """Test POST /vacation-allowances/ with default carryover_days"""
        allowance_data = {
            "employee_id": employee_id,
            "year": 2026,
            "annual_allowance": 30
            # carryover_days should default to 0
        }
        
        response = requests.post(f"{api_base_url}/vacation-allowances", json=allowance_data, headers=auth_headers)
        
        assert response.status_code == 201
        data = response.json()
        assert data["carryover_days"] == 0
        assert data["total_allowance"] == 30
        
        # Cleanup
        requests.delete(f"{api_base_url}/vacation-allowances/{data['id']}", headers=auth_headers)

    def test_create_vacation_allowance_duplicate_employee_year(self, api_base_url: str, auth_headers: Dict[str, str], 
                                                              employee_id: int, allowance_id: int):
        """Test POST /vacation-allowances/ with duplicate employee_id + year"""
        allowance_data = {
            "employee_id": employee_id,
            "year": 2024,  # Same year as existing allowance
            "annual_allowance": 25,
            "carryover_days": 2
        }
        
        response = requests.post(f"{api_base_url}/vacation-allowances", json=allowance_data, headers=auth_headers)
        
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "already exists" in data["detail"].lower()

    def test_create_vacation_allowance_invalid_employee(self, api_base_url: str, auth_headers: Dict[str, str]):
        """Test POST /vacation-allowances/ with non-existing employee"""
        allowance_data = {
            "employee_id": 99999,
            "year": 2024,
            "annual_allowance": 30,
            "carryover_days": 0
        }
        
        response = requests.post(f"{api_base_url}/vacation-allowances", json=allowance_data, headers=auth_headers)
        
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "employee not found" in data["detail"].lower()

    def test_update_vacation_allowance(self, api_base_url: str, auth_headers: Dict[str, str], allowance_id: int):
        """Test PUT /vacation-allowances/{id}"""
        update_data = {
            "annual_allowance": 32,
            "carryover_days": 8
        }
        
        response = requests.put(f"{api_base_url}/vacation-allowances/{allowance_id}", 
                               json=update_data, headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == allowance_id
        assert data["annual_allowance"] == 32
        assert data["carryover_days"] == 8
        assert data["total_allowance"] == 40

    def test_update_vacation_allowance_partial(self, api_base_url: str, auth_headers: Dict[str, str], allowance_id: int):
        """Test PUT /vacation-allowances/{id} with partial update"""
        # Get current data
        response = requests.get(f"{api_base_url}/vacation-allowances/{allowance_id}", headers=auth_headers)
        original_data = response.json()
        
        # Update only annual_allowance
        update_data = {
            "annual_allowance": 35
        }
        
        response = requests.put(f"{api_base_url}/vacation-allowances/{allowance_id}", 
                               json=update_data, headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["annual_allowance"] == 35
        assert data["carryover_days"] == original_data["carryover_days"]  # Should remain unchanged

    def test_update_vacation_allowance_not_found(self, api_base_url: str, auth_headers: Dict[str, str]):
        """Test PUT /vacation-allowances/{id} with non-existing ID"""
        update_data = {
            "annual_allowance": 30
        }
        
        response = requests.put(f"{api_base_url}/vacation-allowances/99999", 
                               json=update_data, headers=auth_headers)
        
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"].lower()

    def test_delete_vacation_allowance(self, api_base_url: str, auth_headers: Dict[str, str], employee_id: int):
        """Test DELETE /vacation-allowances/{id}"""
        # Create allowance to delete
        allowance_data = {
            "employee_id": employee_id,
            "year": 2027,
            "annual_allowance": 30,
            "carryover_days": 0
        }
        
        create_response = requests.post(f"{api_base_url}/vacation-allowances", 
                                       json=allowance_data, headers=auth_headers)
        assert create_response.status_code == 201
        allowance_id = create_response.json()["id"]
        
        # Delete the allowance
        response = requests.delete(f"{api_base_url}/vacation-allowances/{allowance_id}", headers=auth_headers)
        assert response.status_code == 204
        
        # Verify it's deleted
        get_response = requests.get(f"{api_base_url}/vacation-allowances/{allowance_id}", headers=auth_headers)
        assert get_response.status_code == 404

    def test_delete_vacation_allowance_not_found(self, api_base_url: str, auth_headers: Dict[str, str]):
        """Test DELETE /vacation-allowances/{id} with non-existing ID"""
        response = requests.delete(f"{api_base_url}/vacation-allowances/99999", headers=auth_headers)
        
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"].lower()

    def test_get_vacation_allowance_by_employee_and_year(self, api_base_url: str, auth_headers: Dict[str, str], 
                                                        employee_id: int, allowance_id: int):
        """Test GET /vacation-allowances/employee/{employee_id}/year/{year}"""
        response = requests.get(f"{api_base_url}/vacation-allowances/employee/{employee_id}/year/2024", 
                               headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == allowance_id
        assert data["employee_id"] == employee_id
        assert data["year"] == 2024

    def test_get_vacation_allowance_by_employee_and_year_not_found(self, api_base_url: str, auth_headers: Dict[str, str], 
                                                                  employee_id: int):
        """Test GET /vacation-allowances/employee/{employee_id}/year/{year} with non-existing year"""
        response = requests.get(f"{api_base_url}/vacation-allowances/employee/{employee_id}/year/2030", 
                               headers=auth_headers)
        
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "no vacation allowance found" in data["detail"].lower()

    def test_get_vacation_allowance_by_invalid_employee(self, api_base_url: str, auth_headers: Dict[str, str]):
        """Test GET /vacation-allowances/employee/{employee_id}/year/{year} with non-existing employee"""
        response = requests.get(f"{api_base_url}/vacation-allowances/employee/99999/year/2024", 
                               headers=auth_headers)
        
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "employee not found" in data["detail"].lower()

    def test_create_vacation_allowance_for_employee(self, api_base_url: str, auth_headers: Dict[str, str], 
                                                   employee_id: int):
        """Test POST /vacation-allowances/employee/{employee_id}"""
        allowance_data = {
            "year": 2028,
            "annual_allowance": 29,
            "carryover_days": 4,
            "employee_id": 999  # This should be overridden by URL parameter
        }
        
        response = requests.post(f"{api_base_url}/vacation-allowances/employee/{employee_id}", 
                                json=allowance_data, headers=auth_headers)
        
        assert response.status_code == 201
        data = response.json()
        assert data["employee_id"] == employee_id  # Should use URL parameter, not body
        assert data["year"] == 2028
        assert data["annual_allowance"] == 29
        assert data["carryover_days"] == 4
        
        # Cleanup
        requests.delete(f"{api_base_url}/vacation-allowances/{data['id']}", headers=auth_headers)

    def test_create_vacation_allowance_for_invalid_employee(self, api_base_url: str, auth_headers: Dict[str, str]):
        """Test POST /vacation-allowances/employee/{employee_id} with non-existing employee"""
        allowance_data = {
            "year": 2024,
            "annual_allowance": 30,
            "carryover_days": 0
        }
        
        response = requests.post(f"{api_base_url}/vacation-allowances/employee/99999", 
                                json=allowance_data, headers=auth_headers)
        
        # Could be 404 (employee not found) or 422 (validation error)
        assert response.status_code in [404, 422]
        data = response.json()
        assert "detail" in data


class TestVacationAllowanceValidation:
    """Test suite for VacationAllowance data validation"""

    def test_create_vacation_allowance_invalid_year_too_low(self, api_base_url: str, auth_headers: Dict[str, str], 
                                                           employee_id: int):
        """Test POST with year below minimum (2020)"""
        allowance_data = {
            "employee_id": employee_id,
            "year": 2019,
            "annual_allowance": 30,
            "carryover_days": 0
        }
        
        response = requests.post(f"{api_base_url}/vacation-allowances", json=allowance_data, headers=auth_headers)
        
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data

    def test_create_vacation_allowance_invalid_year_too_high(self, api_base_url: str, auth_headers: Dict[str, str], 
                                                            employee_id: int):
        """Test POST with year above maximum (2050)"""
        allowance_data = {
            "employee_id": employee_id,
            "year": 2051,
            "annual_allowance": 30,
            "carryover_days": 0
        }
        
        response = requests.post(f"{api_base_url}/vacation-allowances", json=allowance_data, headers=auth_headers)
        
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data

    def test_create_vacation_allowance_invalid_annual_allowance_negative(self, api_base_url: str, auth_headers: Dict[str, str], 
                                                                        employee_id: int):
        """Test POST with negative annual_allowance"""
        allowance_data = {
            "employee_id": employee_id,
            "year": 2024,
            "annual_allowance": -5,
            "carryover_days": 0
        }
        
        response = requests.post(f"{api_base_url}/vacation-allowances", json=allowance_data, headers=auth_headers)
        
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data

    def test_create_vacation_allowance_invalid_annual_allowance_too_high(self, api_base_url: str, auth_headers: Dict[str, str], 
                                                                        employee_id: int):
        """Test POST with annual_allowance above maximum (365)"""
        allowance_data = {
            "employee_id": employee_id,
            "year": 2024,
            "annual_allowance": 366,
            "carryover_days": 0
        }
        
        response = requests.post(f"{api_base_url}/vacation-allowances", json=allowance_data, headers=auth_headers)
        
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data

    def test_create_vacation_allowance_invalid_carryover_negative(self, api_base_url: str, auth_headers: Dict[str, str], 
                                                                 employee_id: int):
        """Test POST with negative carryover_days"""
        allowance_data = {
            "employee_id": employee_id,
            "year": 2024,
            "annual_allowance": 30,
            "carryover_days": -2
        }
        
        response = requests.post(f"{api_base_url}/vacation-allowances", json=allowance_data, headers=auth_headers)
        
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data

    def test_create_vacation_allowance_invalid_carryover_too_high(self, api_base_url: str, auth_headers: Dict[str, str], 
                                                                 employee_id: int):
        """Test POST with carryover_days above maximum (365)"""
        allowance_data = {
            "employee_id": employee_id,
            "year": 2024,
            "annual_allowance": 30,
            "carryover_days": 366
        }
        
        response = requests.post(f"{api_base_url}/vacation-allowances", json=allowance_data, headers=auth_headers)
        
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data

    def test_create_vacation_allowance_missing_required_fields(self, api_base_url: str, auth_headers: Dict[str, str]):
        """Test POST with missing required fields"""
        allowance_data = {
            "year": 2024,
            "annual_allowance": 30
            # Missing employee_id
        }
        
        response = requests.post(f"{api_base_url}/vacation-allowances", json=allowance_data, headers=auth_headers)
        
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data

    def test_update_vacation_allowance_invalid_data(self, api_base_url: str, auth_headers: Dict[str, str], 
                                                   allowance_id: int):
        """Test PUT with invalid validation data"""
        update_data = {
            "annual_allowance": -10,  # Invalid negative value
            "carryover_days": 400     # Invalid too high value
        }
        
        response = requests.put(f"{api_base_url}/vacation-allowances/{allowance_id}", 
                               json=update_data, headers=auth_headers)
        
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data


class TestVacationAllowanceAuthentication:
    """Test suite for VacationAllowance authentication and authorization"""

    def test_get_vacation_allowances_without_auth(self, api_base_url: str):
        """Test GET /vacation-allowances/ without authentication"""
        response = requests.get(f"{api_base_url}/vacation-allowances")
        
        assert response.status_code == 401

    def test_get_vacation_allowance_by_id_without_auth(self, api_base_url: str):
        """Test GET /vacation-allowances/{id} without authentication"""
        response = requests.get(f"{api_base_url}/vacation-allowances/1")
        
        assert response.status_code == 401

    def test_create_vacation_allowance_without_auth(self, api_base_url: str):
        """Test POST /vacation-allowances/ without authentication"""
        allowance_data = {
            "employee_id": 1,
            "year": 2024,
            "annual_allowance": 30,
            "carryover_days": 0
        }
        
        response = requests.post(f"{api_base_url}/vacation-allowances", json=allowance_data)
        
        assert response.status_code == 401

    def test_update_vacation_allowance_without_auth(self, api_base_url: str):
        """Test PUT /vacation-allowances/{id} without authentication"""
        update_data = {
            "annual_allowance": 32
        }
        
        response = requests.put(f"{api_base_url}/vacation-allowances/1", json=update_data)
        
        # Could be 401 (unauthorized) or 403 (forbidden)
        assert response.status_code in [401, 403]

    def test_delete_vacation_allowance_without_auth(self, api_base_url: str):
        """Test DELETE /vacation-allowances/{id} without authentication"""
        response = requests.delete(f"{api_base_url}/vacation-allowances/1")
        
        # Could be 401 (unauthorized) or 403 (forbidden)
        assert response.status_code in [401, 403]

    def test_vacation_allowances_with_invalid_token(self, api_base_url: str):
        """Test API endpoints with invalid authentication token"""
        invalid_headers = {"Authorization": "Bearer invalid_token_here"}
        
        response = requests.get(f"{api_base_url}/vacation-allowances", headers=invalid_headers)
        assert response.status_code == 401


class TestVacationAllowanceBusinessLogic:
    """Test suite for VacationAllowance business logic and calculations"""

    def test_total_allowance_calculation(self, api_base_url: str, auth_headers: Dict[str, str], employee_id: int):
        """Test that total_allowance is correctly calculated"""
        test_cases = [
            {"annual": 30, "carryover": 0, "expected_total": 30},
            {"annual": 25, "carryover": 5, "expected_total": 30},
            {"annual": 20, "carryover": 15, "expected_total": 35},
            {"annual": 0, "carryover": 10, "expected_total": 10},
            {"annual": 365, "carryover": 0, "expected_total": 365}
        ]
        
        created_allowances = []
        
        for i, case in enumerate(test_cases):
            allowance_data = {
                "employee_id": employee_id,
                "year": 2030 + i,  # Use different years to avoid conflicts
                "annual_allowance": case["annual"],
                "carryover_days": case["carryover"]
            }
            
            response = requests.post(f"{api_base_url}/vacation-allowances", 
                                   json=allowance_data, headers=auth_headers)
            assert response.status_code == 201
            
            data = response.json()
            assert data["total_allowance"] == case["expected_total"]
            created_allowances.append(data["id"])
        
        # Cleanup
        for allowance_id in created_allowances:
            requests.delete(f"{api_base_url}/vacation-allowances/{allowance_id}", headers=auth_headers)

    def test_unique_constraint_employee_year(self, api_base_url: str, auth_headers: Dict[str, str], employee_id: int):
        """Test that unique constraint on employee_id + year is enforced"""
        # Create first allowance
        allowance_data = {
            "employee_id": employee_id,
            "year": 2029,
            "annual_allowance": 30,
            "carryover_days": 0
        }
        
        response1 = requests.post(f"{api_base_url}/vacation-allowances", 
                                 json=allowance_data, headers=auth_headers)
        assert response1.status_code == 201
        allowance_id = response1.json()["id"]
        
        # Try to create duplicate
        response2 = requests.post(f"{api_base_url}/vacation-allowances", 
                                 json=allowance_data, headers=auth_headers)
        assert response2.status_code == 400
        assert "already exists" in response2.json()["detail"].lower()
        
        # Cleanup
        requests.delete(f"{api_base_url}/vacation-allowances/{allowance_id}", headers=auth_headers)

    def test_multiple_years_same_employee(self, api_base_url: str, auth_headers: Dict[str, str], employee_id: int):
        """Test that same employee can have allowances for different years"""
        allowances = []
        years = [2031, 2032, 2033]
        
        for year in years:
            allowance_data = {
                "employee_id": employee_id,
                "year": year,
                "annual_allowance": 30,
                "carryover_days": 0
            }
            
            response = requests.post(f"{api_base_url}/vacation-allowances", 
                                   json=allowance_data, headers=auth_headers)
            assert response.status_code == 201
            allowances.append(response.json()["id"])
        
        # Verify all were created
        response = requests.get(f"{api_base_url}/vacation-allowances?employee_id={employee_id}", 
                               headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        
        created_years = [a["year"] for a in data if a["id"] in allowances]
        assert set(created_years) == set(years)
        
        # Cleanup
        for allowance_id in allowances:
            requests.delete(f"{api_base_url}/vacation-allowances/{allowance_id}", headers=auth_headers)

    def test_boundary_values(self, api_base_url: str, auth_headers: Dict[str, str], employee_id: int):
        """Test boundary values for year, annual_allowance, and carryover_days"""
        boundary_cases = [
            {"year": 2035, "annual": 0, "carryover": 0},      # Minimum values (using safe year)
            {"year": 2036, "annual": 365, "carryover": 365},  # Maximum values
            {"year": 2037, "annual": 1, "carryover": 1},      # Just above minimum
            {"year": 2038, "annual": 364, "carryover": 364}   # Just below maximum
        ]
        
        created_allowances = []
        
        for case in boundary_cases:
            allowance_data = {
                "employee_id": employee_id,
                "year": case["year"],
                "annual_allowance": case["annual"],
                "carryover_days": case["carryover"]
            }
            
            response = requests.post(f"{api_base_url}/vacation-allowances", 
                                   json=allowance_data, headers=auth_headers)
            assert response.status_code == 201
            
            data = response.json()
            assert data["year"] == allowance_data["year"]
            assert data["annual_allowance"] == case["annual"]
            assert data["carryover_days"] == case["carryover"]
            created_allowances.append(data["id"])
        
        # Cleanup
        for allowance_id in created_allowances:
            requests.delete(f"{api_base_url}/vacation-allowances/{allowance_id}", headers=auth_headers)
