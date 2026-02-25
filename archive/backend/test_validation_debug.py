#!/usr/bin/env python3
"""
Debug script to test Pydantic validation
"""

from app.schemas.vacation_allowance import VacationAllowanceCreate, VacationAllowanceUpdate
from pydantic import ValidationError

def test_validation():
    print("Testing VacationAllowanceCreate validation...")
    
    # Test year validation
    try:
        result = VacationAllowanceCreate.model_validate({
            "employee_id": 1, 
            "year": 2019, 
            "annual_allowance": 30
        })
        print(f"ERROR: Year 2019 should have failed but got: {result}")
    except ValidationError as e:
        print(f"SUCCESS: Year 2019 validation failed as expected: {e}")
    
    try:
        result = VacationAllowanceCreate.model_validate({
            "employee_id": 1, 
            "year": 2051, 
            "annual_allowance": 30
        })
        print(f"ERROR: Year 2051 should have failed but got: {result}")
    except ValidationError as e:
        print(f"SUCCESS: Year 2051 validation failed as expected: {e}")
    
    # Test annual_allowance validation
    try:
        result = VacationAllowanceCreate.model_validate({
            "employee_id": 1, 
            "year": 2024, 
            "annual_allowance": -5
        })
        print(f"ERROR: Negative annual_allowance should have failed but got: {result}")
    except ValidationError as e:
        print(f"SUCCESS: Negative annual_allowance validation failed as expected: {e}")
    
    try:
        result = VacationAllowanceCreate.model_validate({
            "employee_id": 1, 
            "year": 2024, 
            "annual_allowance": 366
        })
        print(f"ERROR: annual_allowance 366 should have failed but got: {result}")
    except ValidationError as e:
        print(f"SUCCESS: annual_allowance 366 validation failed as expected: {e}")

if __name__ == "__main__":
    test_validation()
