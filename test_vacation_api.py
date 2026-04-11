import os
import requests

def test_api():
    base_url = os.environ.get("API_BASE_URL", "http://localhost:8000")
    username = os.environ.get("ADMIN_USERNAME", "admin")
    password = os.environ.get("ADMIN_PASSWORD", "admin")
    
    try:
        r = requests.post(f"{base_url}/api/v1/login/access-token", data={"username": username, "password": password})
        if r.status_code == 200:
            token = r.json().get("access_token")
            r2 = requests.get(f"{base_url}/api/v1/employees/2/vacation-summary?year=2026", headers={"Authorization": f"Bearer {token}"})
            print("Status:", r2.status_code)
            print("Response:", r2.text)
        else:
            print("Login failed:", r.status_code, r.text)

    except Exception as e:
        print("Error:", e)

test_api()
