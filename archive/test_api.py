import os
#!/usr/bin/env python3
import requests
import json

# Test Login
print("=== Testing Login ===")
login_response = requests.post('http://localhost:8000/api/v1/auth/login', 
                              json={'username': os.environ.get('ADMIN_USERNAME', 'admin'), 'password': os.environ.get('ADMIN_PASSWORD', 'admin')})
print(f"Login Status: {login_response.status_code}")

if login_response.status_code == 200:
    token = login_response.json().get('access_token')
    print(f"Token received: {token[:50]}...")
    
    # Test Employee API
    print("\n=== Testing Employee API ===")
    headers = {'Authorization': f'Bearer {token}'}
    emp_response = requests.get('http://localhost:8000/api/v1/employees/', headers=headers)
    print(f"Employee API Status: {emp_response.status_code}")
    
    if emp_response.status_code == 200:
        employees = emp_response.json()
        print(f"Number of employees: {len(employees)}")
        print("✅ SUCCESS: Employee API is working!")
    else:
        print(f"❌ ERROR: {emp_response.text}")
else:
    print(f"❌ Login failed: {login_response.text}")
