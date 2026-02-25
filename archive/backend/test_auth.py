"""
Simple test script to verify authentication functionality.
"""
import asyncio
import httpx
from app.core.auth import authenticate_user, create_access_token

async def test_auth():
    """Test authentication functions."""
    print("Testing authentication...")
    
    # Test password verification
    result = authenticate_user("MGanser", "M4rvelf4n")
    print(f"Authentication test (correct): {result}")
    
    result = authenticate_user("MGanser", "wrong_password")
    print(f"Authentication test (wrong password): {result}")
    
    result = authenticate_user("wrong_user", "M4rvelf4n")
    print(f"Authentication test (wrong user): {result}")
    
    # Test token creation
    token = create_access_token(data={"sub": "MGanser"})
    print(f"Generated token: {token[:50]}...")
    
    print("Authentication tests completed!")

if __name__ == "__main__":
    asyncio.run(test_auth())
