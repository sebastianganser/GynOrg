import httpx
import asyncio

URL = "https://www.mehr-schulferien.de/api/v2.1/federal-states/bayern/periods?start_date=2025-01-01&end_date=2025-12-31"

async def test_api():
    print(f"Testing API: {URL}")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(URL)
            print(f"Status Code: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"Success! Fetched {len(data)} items.")
                if data:
                    print(f"Sample: {data[0].get('name')}")
            else:
                print(f"Error: {response.text}")
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    asyncio.run(test_api())
