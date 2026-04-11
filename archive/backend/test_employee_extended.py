#!/usr/bin/env python3

from datetime import date, timedelta
from pydantic import ValidationError
from app.models import EmployeeCreate, EmployeeUpdate, FederalState

def test_employee_create_with_new_fields():
    """Test EmployeeCreate with all new fields"""
    print("=== Employee Create Test ===")
    
    # Test with all fields
    emp = EmployeeCreate(
        title="Dr.",
        first_name="Maria",
        last_name="Müller",
        email="maria.mueller@example.com",
        position="Gynäkologin",
        birth_date=date(1980, 5, 15),
        date_hired=date(2020, 1, 1),
        federal_state=FederalState.BW,
        active=True
    )
    
    print(f"Full name: {emp.full_name}")
    print(f"Display name: {emp.display_name}")
    print(f"Email: {emp.email}")
    print(f"Federal state: {emp.federal_state}")
    
    # Test JSON serialization
    json_data = emp.model_dump_json()
    print(f"JSON: {json_data}")

def test_employee_create_minimal():
    """Test EmployeeCreate with minimal required fields"""
    print("\n=== Employee Create Minimal Test ===")
    
    emp = EmployeeCreate(
        first_name="Anna",
        last_name="Schmidt",
        email="anna.schmidt@example.com",
        federal_state=FederalState.BY
    )
    
    print(f"Full name: {emp.full_name}")
    print(f"Display name: {emp.display_name}")
    assert emp.active == True  # Default value
    assert emp.title is None
    assert emp.position is None

def test_employee_validation_errors():
    """Test validation errors for invalid data"""
    print("\n=== Employee Validation Test ===")
    
    # Test future birth date
    try:
        EmployeeCreate(
            first_name="Test",
            last_name="User",
            email="test@example.com",
            birth_date=date.today() + timedelta(days=1),
            federal_state=FederalState.NW
        )
        assert False, "Should have raised ValidationError for future birth date"
    except ValidationError as e:
        print(f"✅ Birth date validation: {e.errors()[0]['msg']}")
    
    # Test future hire date
    try:
        EmployeeCreate(
            first_name="Test",
            last_name="User",
            email="test@example.com",
            date_hired=date.today() + timedelta(days=1),
            federal_state=FederalState.NW
        )
        assert False, "Should have raised ValidationError for future hire date"
    except ValidationError as e:
        print(f"✅ Hire date validation: {e.errors()[0]['msg']}")
    
    # Test hire date before birth date
    try:
        EmployeeCreate(
            first_name="Test",
            last_name="User",
            email="test@example.com",
            birth_date=date(1990, 1, 1),
            date_hired=date(1985, 1, 1),
            federal_state=FederalState.NW
        )
        assert False, "Should have raised ValidationError for hire date before birth date"
    except ValidationError as e:
        print(f"✅ Hire before birth validation: {e.errors()[0]['msg']}")

def test_employee_update():
    """Test EmployeeUpdate model"""
    print("\n=== Employee Update Test ===")
    
    # Test partial update
    update = EmployeeUpdate(
        email="new.email@example.com",
        position="Senior Gynäkologin",
        federal_state=FederalState.HE
    )
    
    json_data = update.model_dump_json(exclude_unset=True)
    print(f"Update JSON: {json_data}")
    
    # Test update with validation
    update2 = EmployeeUpdate(
        birth_date=date(1985, 3, 20),
        date_hired=date(2021, 6, 1)
    )
    
    print(f"Update with dates: {update2.model_dump_json(exclude_unset=True)}")

def test_email_validation():
    """Test email validation"""
    print("\n=== Email Validation Test ===")
    
    # Valid email
    emp = EmployeeCreate(
        first_name="Test",
        last_name="User",
        email="valid.email@domain.com",
        federal_state=FederalState.SH
    )
    print(f"✅ Valid email: {emp.email}")
    
    # Invalid email should raise ValidationError
    try:
        EmployeeCreate(
            first_name="Test",
            last_name="User",
            email="invalid-email",
            federal_state=FederalState.SH
        )
        assert False, "Should have raised ValidationError for invalid email"
    except ValidationError as e:
        print(f"✅ Invalid email validation: {e.errors()[0]['msg']}")

if __name__ == "__main__":
    test_employee_create_with_new_fields()
    test_employee_create_minimal()
    test_employee_validation_errors()
    test_employee_update()
    test_email_validation()
    print("\n✅ All extended employee model tests passed!")
