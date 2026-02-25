import requests
import io
from PIL import Image
import os

# Test configuration
BASE_URL = "http://localhost:8000/api/v1"
TEST_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJNR2Fuc2VyIiwiZXhwIjoxNzUzMDkyODM2fQ.2WCTj6bptYyAJiljBuM-pwcwBxenzzJNgKeAQyBT5W4"

headers = {
    "Authorization": f"Bearer {TEST_TOKEN}",
    "Content-Type": "application/json"
}

def create_test_image():
    """Create a test image in memory"""
    # Create a simple test image
    img = Image.new('RGB', (100, 100), color='red')
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    return img_bytes

def test_avatar_upload():
    """Test avatar upload functionality"""
    print("Testing Avatar Upload Functionality...")
    
    # First, create a test employee
    employee_data = {
        "first_name": "Test",
        "last_name": "Avatar",
        "email": "test.avatar@example.com",
        "position": "Tester",
        "vacation_allowance": 25,
        "date_hired": "2024-01-01",
        "active": True,
        "federal_state": "Bayern"
    }
    
    print("1. Creating test employee...")
    response = requests.post(
        f"{BASE_URL}/employees",
        headers=headers,
        json=employee_data
    )
    
    if response.status_code != 201:
        print(f"Failed to create employee: {response.status_code} - {response.text}")
        return
    
    employee = response.json()
    employee_id = employee["id"]
    print(f"✓ Employee created with ID: {employee_id}")
    
    # Test avatar upload
    print("2. Testing avatar upload...")
    test_image = create_test_image()
    
    files = {
        'file': ('test_avatar.png', test_image, 'image/png')
    }
    
    # Remove Content-Type header for file upload
    upload_headers = {
        "Authorization": f"Bearer {TEST_TOKEN}"
    }
    
    response = requests.post(
        f"{BASE_URL}/employees/{employee_id}/avatar",
        headers=upload_headers,
        files=files
    )
    
    if response.status_code == 200:
        updated_employee = response.json()
        print(f"✓ Avatar uploaded successfully")
        print(f"  Profile image path: {updated_employee.get('profile_image_path', 'None')}")
    else:
        print(f"✗ Avatar upload failed: {response.status_code} - {response.text}")
        return
    
    # Test avatar retrieval
    print("3. Testing avatar retrieval...")
    response = requests.get(
        f"{BASE_URL}/employees/{employee_id}/avatar",
        headers=upload_headers
    )
    
    if response.status_code == 200:
        print(f"✓ Avatar retrieved successfully")
        print(f"  Content-Type: {response.headers.get('content-type')}")
        print(f"  Content-Length: {len(response.content)} bytes")
    else:
        print(f"✗ Avatar retrieval failed: {response.status_code} - {response.text}")
    
    # Test initials update
    print("4. Testing initials update...")
    response = requests.put(
        f"{BASE_URL}/employees/{employee_id}/initials?initials=TA",
        headers=upload_headers
    )
    
    if response.status_code == 200:
        updated_employee = response.json()
        print(f"✓ Initials updated successfully: {updated_employee.get('initials')}")
    else:
        print(f"✗ Initials update failed: {response.status_code} - {response.text}")
    
    # Test avatar deletion
    print("5. Testing avatar deletion...")
    response = requests.delete(
        f"{BASE_URL}/employees/{employee_id}/avatar",
        headers=upload_headers
    )
    
    if response.status_code == 204:
        print("✓ Avatar deleted successfully")
    else:
        print(f"✗ Avatar deletion failed: {response.status_code} - {response.text}")
    
    # Verify avatar is gone
    print("6. Verifying avatar deletion...")
    response = requests.get(
        f"{BASE_URL}/employees/{employee_id}/avatar",
        headers=upload_headers
    )
    
    if response.status_code == 404:
        print("✓ Avatar correctly not found after deletion")
    else:
        print(f"✗ Avatar should be gone but got: {response.status_code}")
    
    # Clean up - delete test employee
    print("7. Cleaning up test employee...")
    response = requests.delete(
        f"{BASE_URL}/employees/{employee_id}/hard",
        headers=upload_headers
    )
    
    if response.status_code == 204:
        print("✓ Test employee deleted successfully")
    else:
        print(f"✗ Failed to delete test employee: {response.status_code}")
    
    print("\nAvatar upload test completed!")

if __name__ == "__main__":
    test_avatar_upload()
