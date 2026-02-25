import pytest
import json
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.app.main import app
from backend.app.core.database import get_db
from backend.app.models.employee import Employee
from backend.app.models.employee_school_holiday_preferences import EmployeeSchoolHolidayPreferences
from backend.app.models.federal_state import FederalState
from backend.app.schemas.employee_school_holiday_preferences import SchoolVacationType

client = TestClient(app)

# Test data
TEST_EMPLOYEE_DATA = {
    "first_name": "Max",
    "last_name": "Mustermann",
    "email": "max.mustermann@example.com",
    "federal_state": FederalState.NORDRHEIN_WESTFALEN
}

TEST_PREFERENCES_DATA = {
    "primary_federal_state": "Nordrhein-Westfalen",
    "additional_federal_states": ["Bayern", "Hessen"],
    "children_federal_states": ["Baden-Württemberg"],
    "relevant_vacation_types": ["SUMMER", "WINTER", "EASTER"],
    "show_all_states": False,
    "notification_enabled": True,
    "notification_days_advance": 14
}

@pytest.fixture
def db_session():
    """Get database session for testing"""
    return next(get_db())

@pytest.fixture
def test_employee(db_session: Session):
    """Create a test employee"""
    employee = Employee(**TEST_EMPLOYEE_DATA)
    db_session.add(employee)
    db_session.commit()
    db_session.refresh(employee)
    return employee

@pytest.fixture
def test_preferences(db_session: Session, test_employee: Employee):
    """Create test preferences for employee"""
    preferences = EmployeeSchoolHolidayPreferences(
        employee_id=test_employee.id,
        primary_federal_state=TEST_PREFERENCES_DATA["primary_federal_state"],
        additional_federal_states=TEST_PREFERENCES_DATA["additional_federal_states"],
        children_federal_states=TEST_PREFERENCES_DATA["children_federal_states"],
        relevant_vacation_types=[SchoolVacationType(t) for t in TEST_PREFERENCES_DATA["relevant_vacation_types"]],
        show_all_states=TEST_PREFERENCES_DATA["show_all_states"],
        notification_enabled=TEST_PREFERENCES_DATA["notification_enabled"],
        notification_days_advance=TEST_PREFERENCES_DATA["notification_days_advance"]
    )
    db_session.add(preferences)
    db_session.commit()
    db_session.refresh(preferences)
    return preferences

class TestEmployeePreferencesAPI:
    """Test suite for Employee Preferences API endpoints"""

    def test_get_employee_preferences_success(self, test_employee: Employee, test_preferences: EmployeeSchoolHolidayPreferences):
        """Test successful retrieval of employee preferences"""
        response = client.get(f"/api/v1/employees/{test_employee.id}/school-holiday-preferences")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["employee_id"] == test_employee.id
        assert data["primary_federal_state"] == TEST_PREFERENCES_DATA["primary_federal_state"]
        assert data["additional_federal_states"] == TEST_PREFERENCES_DATA["additional_federal_states"]
        assert data["children_federal_states"] == TEST_PREFERENCES_DATA["children_federal_states"]
        assert data["relevant_vacation_types"] == TEST_PREFERENCES_DATA["relevant_vacation_types"]
        assert data["show_all_states"] == TEST_PREFERENCES_DATA["show_all_states"]
        assert data["notification_enabled"] == TEST_PREFERENCES_DATA["notification_enabled"]
        assert data["notification_days_advance"] == TEST_PREFERENCES_DATA["notification_days_advance"]

    def test_get_employee_preferences_not_found(self):
        """Test retrieval of preferences for non-existent employee"""
        response = client.get("/api/v1/employees/99999/school-holiday-preferences")
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_create_employee_preferences_success(self, test_employee: Employee):
        """Test successful creation of employee preferences"""
        response = client.post(
            f"/api/v1/employees/{test_employee.id}/school-holiday-preferences",
            json=TEST_PREFERENCES_DATA
        )
        
        assert response.status_code == 201
        data = response.json()
        
        assert data["employee_id"] == test_employee.id
        assert data["primary_federal_state"] == TEST_PREFERENCES_DATA["primary_federal_state"]
        assert data["additional_federal_states"] == TEST_PREFERENCES_DATA["additional_federal_states"]

    def test_create_employee_preferences_invalid_employee(self):
        """Test creation of preferences for non-existent employee"""
        response = client.post(
            "/api/v1/employees/99999/school-holiday-preferences",
            json=TEST_PREFERENCES_DATA
        )
        
        assert response.status_code == 400

    def test_create_employee_preferences_duplicate(self, test_employee: Employee, test_preferences: EmployeeSchoolHolidayPreferences):
        """Test creation of duplicate preferences"""
        response = client.post(
            f"/api/v1/employees/{test_employee.id}/school-holiday-preferences",
            json=TEST_PREFERENCES_DATA
        )
        
        assert response.status_code == 400

    def test_update_employee_preferences_success(self, test_employee: Employee, test_preferences: EmployeeSchoolHolidayPreferences):
        """Test successful update of employee preferences"""
        update_data = {
            "primary_federal_state": "Bayern",
            "notification_days_advance": 21
        }
        
        response = client.put(
            f"/api/v1/employees/{test_employee.id}/school-holiday-preferences",
            json=update_data
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["primary_federal_state"] == "Bayern"
        assert data["notification_days_advance"] == 21
        # Other fields should remain unchanged
        assert data["additional_federal_states"] == TEST_PREFERENCES_DATA["additional_federal_states"]

    def test_update_employee_preferences_not_found(self):
        """Test update of preferences for non-existent employee"""
        response = client.put(
            "/api/v1/employees/99999/school-holiday-preferences",
            json={"primary_federal_state": "Bayern"}
        )
        
        assert response.status_code == 404

    def test_delete_employee_preferences_success(self, test_employee: Employee, test_preferences: EmployeeSchoolHolidayPreferences):
        """Test successful deletion of employee preferences"""
        response = client.delete(f"/api/v1/employees/{test_employee.id}/school-holiday-preferences")
        
        assert response.status_code == 204

        # Verify preferences are deleted
        get_response = client.get(f"/api/v1/employees/{test_employee.id}/school-holiday-preferences")
        assert get_response.status_code == 404

    def test_delete_employee_preferences_not_found(self):
        """Test deletion of preferences for non-existent employee"""
        response = client.delete("/api/v1/employees/99999/school-holiday-preferences")
        
        assert response.status_code == 404

    def test_bulk_create_default_preferences(self, db_session: Session):
        """Test bulk creation of default preferences"""
        # Create multiple employees without preferences
        employees = []
        for i in range(3):
            employee = Employee(
                first_name=f"Test{i}",
                last_name="User",
                email=f"test{i}@example.com",
                federal_state=FederalState.NORDRHEIN_WESTFALEN
            )
            db_session.add(employee)
            employees.append(employee)
        
        db_session.commit()
        
        response = client.post("/api/v1/employees/school-holiday-preferences/bulk-create-defaults")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["created_count"] >= 3
        assert "Created default preferences" in data["message"]

    def test_get_preferences_summary(self, test_employee: Employee, test_preferences: EmployeeSchoolHolidayPreferences):
        """Test retrieval of preferences summary"""
        response = client.get("/api/v1/employees/school-holiday-preferences/summary")
        
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list)
        assert len(data) >= 1
        
        # Check if our test employee is in the summary
        test_summary = next((item for item in data if item["employee_id"] == test_employee.id), None)
        assert test_summary is not None
        assert test_summary["employee_name"] == f"{test_employee.first_name} {test_employee.last_name}"

    def test_get_preferences_statistics(self, test_employee: Employee, test_preferences: EmployeeSchoolHolidayPreferences):
        """Test retrieval of preferences statistics"""
        response = client.get("/api/v1/employees/school-holiday-preferences/statistics")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "total_employees" in data
        assert "total_preferences" in data
        assert "coverage_percentage" in data
        assert "notifications_enabled" in data
        assert "with_children_states" in data
        assert "show_all_states" in data
        assert "notification_enabled_percentage" in data
        
        assert data["total_employees"] >= 1
        assert data["total_preferences"] >= 1

    def test_get_preferences_options(self):
        """Test retrieval of preferences options"""
        response = client.get("/api/v1/school-holiday-preferences/options")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "federal_states" in data
        assert "vacation_types" in data
        assert "notification_days_options" in data
        
        assert isinstance(data["federal_states"], list)
        assert isinstance(data["vacation_types"], list)
        assert isinstance(data["notification_days_options"], list)
        
        # Check federal states structure
        if data["federal_states"]:
            state = data["federal_states"][0]
            assert "value" in state
            assert "label" in state
            assert "code" in state
        
        # Check vacation types structure
        if data["vacation_types"]:
            vacation_type = data["vacation_types"][0]
            assert "value" in vacation_type
            assert "label" in vacation_type
            assert "description" in vacation_type

    def test_get_filtered_holidays_for_employee(self, test_employee: Employee, test_preferences: EmployeeSchoolHolidayPreferences):
        """Test retrieval of filtered holidays for employee"""
        response = client.get(f"/api/v1/employees/{test_employee.id}/holidays/filtered")
        
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list)
        # The actual content depends on available holidays in the database

    def test_get_filtered_holidays_with_parameters(self, test_employee: Employee, test_preferences: EmployeeSchoolHolidayPreferences):
        """Test retrieval of filtered holidays with year and month parameters"""
        response = client.get(f"/api/v1/employees/{test_employee.id}/holidays/filtered?year=2025&month=12")
        
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list)

    def test_get_relevant_holidays_for_employee(self, test_employee: Employee, test_preferences: EmployeeSchoolHolidayPreferences):
        """Test retrieval of relevant holidays for employee (alias endpoint)"""
        response = client.get(f"/api/v1/employees/{test_employee.id}/holidays/relevant")
        
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list)

    def test_get_employees_interested_in_federal_state(self, test_employee: Employee, test_preferences: EmployeeSchoolHolidayPreferences):
        """Test retrieval of employees interested in a federal state"""
        response = client.get("/api/v1/federal-states/Nordrhein-Westfalen/interested-employees")
        
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list)
        assert test_employee.id in data

    def test_get_employees_interested_in_vacation_type(self, test_employee: Employee, test_preferences: EmployeeSchoolHolidayPreferences):
        """Test retrieval of employees interested in a vacation type"""
        response = client.get("/api/v1/vacation-types/SUMMER/interested-employees")
        
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list)
        assert test_employee.id in data

    def test_validation_errors(self, test_employee: Employee):
        """Test validation errors for invalid data"""
        invalid_data = {
            "primary_federal_state": "InvalidState",
            "notification_days_advance": -1,
            "relevant_vacation_types": ["INVALID_TYPE"]
        }
        
        response = client.post(
            f"/api/v1/employees/{test_employee.id}/school-holiday-preferences",
            json=invalid_data
        )
        
        assert response.status_code == 400

    def test_preferences_with_empty_arrays(self, test_employee: Employee):
        """Test preferences with empty arrays"""
        minimal_data = {
            "primary_federal_state": "Nordrhein-Westfalen",
            "additional_federal_states": [],
            "children_federal_states": [],
            "relevant_vacation_types": [],
            "show_all_states": False,
            "notification_enabled": False,
            "notification_days_advance": 7
        }
        
        response = client.post(
            f"/api/v1/employees/{test_employee.id}/school-holiday-preferences",
            json=minimal_data
        )
        
        assert response.status_code == 201
        data = response.json()
        
        assert data["additional_federal_states"] == []
        assert data["children_federal_states"] == []
        assert data["relevant_vacation_types"] == []

    def test_preferences_all_relevant_federal_states_calculation(self, test_employee: Employee):
        """Test that all_relevant_federal_states is calculated correctly"""
        preferences_data = {
            "primary_federal_state": "Nordrhein-Westfalen",
            "additional_federal_states": ["Bayern"],
            "children_federal_states": ["Hessen", "Baden-Württemberg"],
            "relevant_vacation_types": ["SUMMER"],
            "show_all_states": False,
            "notification_enabled": True,
            "notification_days_advance": 14
        }
        
        response = client.post(
            f"/api/v1/employees/{test_employee.id}/school-holiday-preferences",
            json=preferences_data
        )
        
        assert response.status_code == 201
        data = response.json()
        
        expected_states = {"Nordrhein-Westfalen", "Bayern", "Hessen", "Baden-Württemberg"}
        actual_states = set(data["all_relevant_federal_states"])
        
        assert actual_states == expected_states

if __name__ == "__main__":
    pytest.main([__file__])
