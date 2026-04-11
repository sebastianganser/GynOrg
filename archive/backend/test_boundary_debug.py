"""
Debug test for boundary values issue
"""
import pytest
import requests
from typing import Dict


def test_boundary_debug(api_base_url: str, auth_headers: Dict[str, str], employee_id: int):
    """Debug boundary values test"""
    boundary_cases = [
        {"year": 2020, "annual": 0, "carryover": 0},      # Minimum values
        {"year": 2050, "annual": 365, "carryover": 365},  # Maximum values
        {"year": 2024, "annual": 1, "carryover": 1},      # Just above minimum
        {"year": 2049, "annual": 364, "carryover": 364}   # Just below maximum
    ]
    
    for i, case in enumerate(boundary_cases):
        allowance_data = {
            "employee_id": employee_id,
            "year": case["year"] + i,  # Adjust year to avoid conflicts
            "annual_allowance": case["annual"],
            "carryover_days": case["carryover"]
        }
        
        print(f"\nTesting case {i}: {allowance_data}")
        
        response = requests.post(f"{api_base_url}/vacation-allowances", 
                               json=allowance_data, headers=auth_headers)
        
        print(f"Response status: {response.status_code}")
        print(f"Response body: {response.text}")
        
        if response.status_code != 201:
            print(f"FAILED on case {i}")
            break
        else:
            # Cleanup
            data = response.json()
            requests.delete(f"{api_base_url}/vacation-allowances/{data['id']}", headers=auth_headers)
            print(f"SUCCESS on case {i}")
