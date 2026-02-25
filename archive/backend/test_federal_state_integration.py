#!/usr/bin/env python3

from app.schemas.employee import EmployeeCreate, EmployeeUpdate
from app.models.federal_state import FederalState

def test_json_serialization():
    """Test JSON serialization with federal_state"""
    print("=== JSON Serialization Test ===")
    
    # Create employee with federal state
    emp = EmployeeCreate(
        first_name="Test",
        last_name="User",
        email="test.user@example.com",
        position="Developer", 
        federal_state=FederalState.BW
    )
    
    # Test JSON output
    json_str = emp.model_dump_json()
    print(f"JSON: {json_str}")
    
    # Test dict output
    dict_data = emp.model_dump()
    print(f"Dict federal_state: {dict_data['federal_state']}")
    print(f"Type: {type(dict_data['federal_state'])}")

def test_json_deserialization():
    """Test JSON deserialization with federal_state"""
    print("\n=== JSON Deserialization Test ===")
    
    # Test with full state name
    json_data = '{"first_name": "API", "last_name": "User", "email": "api.user@example.com", "federal_state": "Bayern"}'
    emp = EmployeeCreate.model_validate_json(json_data)
    print(f"Deserialized: {emp.first_name} {emp.last_name}, State: {emp.federal_state}")
    print(f"State type: {type(emp.federal_state)}")

def test_update_model():
    """Test EmployeeUpdate with federal_state"""
    print("\n=== EmployeeUpdate Test ===")
    
    # Test partial update
    update = EmployeeUpdate(federal_state=FederalState.NW)
    print(f"Update JSON: {update.model_dump_json()}")
    
    # Test update from JSON
    update_json = '{"federal_state": "Hessen"}'
    update2 = EmployeeUpdate.model_validate_json(update_json)
    print(f"Update from JSON: {update2.federal_state}")

if __name__ == "__main__":
    test_json_serialization()
    test_json_deserialization()
    test_update_model()
    print("\n✅ All federal_state integration tests passed!")
