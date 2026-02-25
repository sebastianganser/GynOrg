#!/usr/bin/env python3
"""
Test script to verify authentication integration between frontend and backend.
"""

import requests
import json

# Test configuration
BASE_URL = "http://localhost:8000/api/v1"
USERNAME = "MGanser"
PASSWORD = "M4rvelf4n"

def test_login():
    """Test login endpoint"""
    print("Testing login...")
    
    # Prepare login data
    login_data = {
        'username': USERNAME,
        'password': PASSWORD
    }
    
    # Send login request
    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    
    if response.status_code == 200:
        token_data = response.json()
        print(f"✅ Login successful!")
        print(f"Token type: {token_data['token_type']}")
        print(f"Access token: {token_data['access_token'][:50]}...")
        return token_data['access_token']
    else:
        print(f"❌ Login failed: {response.status_code}")
        print(f"Response: {response.text}")
        return None

def test_protected_endpoint(token):
    """Test accessing protected employees endpoint"""
    print("\nTesting protected endpoint...")
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    response = requests.get(f"{BASE_URL}/employees/", headers=headers)
    
    if response.status_code == 200:
        employees = response.json()
        print(f"✅ Protected endpoint access successful!")
        print(f"Found {len(employees)} employees")
        return True
    else:
        print(f"❌ Protected endpoint access failed: {response.status_code}")
        print(f"Response: {response.text}")
        return False

def test_invalid_token():
    """Test with invalid token"""
    print("\nTesting with invalid token...")
    
    headers = {
        'Authorization': 'Bearer invalid_token',
        'Content-Type': 'application/json'
    }
    
    response = requests.get(f"{BASE_URL}/employees/", headers=headers)
    
    if response.status_code == 401:
        print("✅ Invalid token correctly rejected!")
        return True
    else:
        print(f"❌ Invalid token should be rejected but got: {response.status_code}")
        return False

def main():
    print("🔐 Testing Authentication Integration")
    print("=" * 50)
    
    # Test login
    token = test_login()
    if not token:
        print("❌ Cannot continue without valid token")
        return
    
    # Test protected endpoint with valid token
    if not test_protected_endpoint(token):
        print("❌ Protected endpoint test failed")
        return
    
    # Test with invalid token
    if not test_invalid_token():
        print("❌ Invalid token test failed")
        return
    
    print("\n🎉 All authentication tests passed!")
    print("\nFrontend should now be able to:")
    print("1. Login with MGanser / M4rvelf4n")
    print("2. Access employee data after login")
    print("3. Be redirected to login if token is invalid")

if __name__ == "__main__":
    main()
