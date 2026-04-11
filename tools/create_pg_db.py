import os
import psycopg2
from psycopg2 import sql
import time

def create_database():
    conn = None
    try:
        print("Connecting to PostgreSQL server...")
        
        # Load connection details from environment variables
        db_host = os.environ.get("PG_HOST", "localhost")
        db_port = os.environ.get("PG_PORT", "5432")
        db_user = os.environ.get("PG_USER", "postgres")
        db_password = os.environ.get("PG_PASSWORD", "")
        db_name = os.environ.get("PG_DEFAULT_DB", "postgres")
        
        conn = psycopg2.connect(
            dbname=db_name, 
            user=db_user, 
            password=db_password, 
            host=db_host, 
            port=db_port
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
