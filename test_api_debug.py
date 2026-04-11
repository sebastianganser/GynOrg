import httpx
import asyncio
import json

URL = "https://www.mehr-schulferien.de/api/v2.1/federal-states/bayern/periods?start_date=2025-01-01&end_date=2025-12-31"

async def test_api():
    print(f"Testing API: {URL}")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(URL)
            print(f"Status Code: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"Data Type: {type(data)}")
                if isinstance(data, list):
                    print(f"List length: {len(data)}")
                    if len(data) > 0:
                        print(f"First item type: {type(data[0])}")
                        print(f"First item: {data[0]}")
                elif isinstance(data, dict):
                    print(f"Dict keys: {data.keys()}")
                print("Raw Data Sample:")
                print(json.dumps(data, indent=2)[:500]) # First 500 chars
            else:
                print(f"Error: {response.text}")
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    asyncio.run(test_api())
