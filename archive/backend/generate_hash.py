"""
Generate bcrypt hash for the password.
"""
import bcrypt

password = "M4rvelf4n"
salt = bcrypt.gensalt()
hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
print(f"Password: {password}")
print(f"Hash: {hashed.decode('utf-8')}")

# Test verification
test_result = bcrypt.checkpw(password.encode('utf-8'), hashed)
print(f"Verification test: {test_result}")
