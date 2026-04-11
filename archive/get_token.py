import os
import requests

# Login to get a fresh token
login_data = {
    "username": os.environ.get("ADMIN_USERNAME", "admin"),
    "password": os.environ.get("ADMIN_PASSWORD", "admin")
}

response = requests.post("http://localhost:8000/api/v1/auth/login", json=login_data)

if response.status_code == 200:
    token_data = response.json()
    print(f"New token: {token_data['access_token']}")
else:
    print(f"Login failed: {response.status_code} - {response.text}")
