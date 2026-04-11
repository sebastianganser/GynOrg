import os
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
    result = authenticate_user(os.environ.get("ADMIN_USERNAME", "admin"), os.environ.get("ADMIN_PASSWORD", "admin"))
    print(f"Authentication test (correct): {result}")
    
    result = authenticate_user(os.environ.get("ADMIN_USERNAME", "admin"), "wrong_password")
    print(f"Authentication test (wrong password): {result}")
    
    result = authenticate_user("wrong_user", os.environ.get("ADMIN_PASSWORD", "admin"))
    print(f"Authentication test (wrong user): {result}")
    
    # Test token creation
    token = create_access_token(data={"sub": os.environ.get("ADMIN_USERNAME", "admin")})
    print(f"Generated token: {token[:50]}...")
    
    print("Authentication tests completed!")

if __name__ == "__main__":
    asyncio.run(test_auth())
