import urllib.request
import json
import time

def verify():
    print("Verifying API...")
    
    # 1. Health Check
    try:
        with urllib.request.urlopen("http://localhost:8000/health") as response:
            print(f"Health Check: {response.getcode()}")
            print(response.read().decode('utf-8'))
    except Exception as e:
        print(f"Health Check FAILED: {e}")
        return

    # 2. Employees Endpoint (This was failing with 500)
    try:
        # Note: This endpoint might require auth if strict, but let's try plain GET first 
        # as the error was 500 (Server Error), not 401 (Unauthorized). 
        # If it returns 401, that's GOOD (means DB query didn't crash server).
        url = "http://localhost:8000/api/v1/employees/?skip=0&limit=10"
        req = urllib.request.Request(url)
        # Add a dummy text/plain header just in case
        
        with urllib.request.urlopen(req) as response:
            print(f"Employees Endpoint: {response.getcode()}")
            data = json.loads(response.read().decode('utf-8'))
            print(f"Successfully fetched {len(data)} employees")
    except urllib.error.HTTPError as e:
        print(f"Employees Endpoint returned HTTP {e.code}: {e.reason}")
        if e.code == 401:
            print("Auth required (Expected). Server is reachable and NOT crashing.")
        elif e.code == 500:
            print("CRITICAL: Server still returning 500 Internal Server Error.")
        else:
            print(f"Response: {e.read().decode('utf-8')}")
    except Exception as e:
        print(f"Employees Endpoint FAILED: {e}")

if __name__ == "__main__":
    # Wait a sec for server to be fully ready
    time.sleep(2)
    verify()
