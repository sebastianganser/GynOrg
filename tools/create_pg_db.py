import psycopg2
from psycopg2 import sql
import time

def create_database():
    # Connect to the default 'postgres' database (or 'crypto_data' as seen in the image)
    # in order to create the new database
    conn = None
    try:
        # We use crypto_data because the screenshot shows it as the POSTGRES_DB
        print("Connecting to PostgreSQL server...")
        conn = psycopg2.connect(
            dbname="crypto_data", 
            user="sebastian", 
            password="1Asport,,M4rvelf4n", 
            host="192.168.1.93", 
            port="5432"
        )
        # We must set isolation level to autocommit to create a database
        conn.autocommit = True
        
        with conn.cursor() as cursor:
            # Check if GynOrg database exists
            cursor.execute("SELECT 1 FROM pg_database WHERE datname='GynOrg'")
            exists = cursor.fetchone()
            
            if not exists:
                print("Creating GynOrg database...")
                cursor.execute('CREATE DATABASE "GynOrg"')
                print("Database GynOrg created successfully!")
            else:
                print("Database GynOrg already exists.")
                
            # Create test database while we're at it
            cursor.execute("SELECT 1 FROM pg_database WHERE datname='GynOrg_test'")
            test_exists = cursor.fetchone()
            
            if not test_exists:
                print("Creating GynOrg_test database...")
                cursor.execute('CREATE DATABASE "GynOrg_test"')
                print("Database GynOrg_test created successfully!")
            else:
                print("Database GynOrg_test already exists.")
                
    except Exception as e:
        print(f"Error creating database: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    create_database()
