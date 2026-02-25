import bcrypt

hash_str = b"$2b$12$8CDp40px7qcGwf/oB5IMFuhXA41WWuJhv8zC.OaZS2KLQgAJlNJ/e"
pwd = b"M4rvelf4n"

try:
    if bcrypt.checkpw(pwd, hash_str):
        print("MATCH")
    else:
        print("NO_MATCH")
except Exception as e:
    print(f"ERROR: {e}")
