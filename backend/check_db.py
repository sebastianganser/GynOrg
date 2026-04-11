import os
import psycopg2

try:
    db_url = os.environ.get("DATABASE_URL", "postgresql://localhost:5432/GynOrg")
    conn = psycopg2.connect(db_url)
    cur = conn.cursor()
    cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name='employees';")
    columns = [c[0] for c in cur.fetchall()]
    print("Columns in employees:", columns)
    
    if 'youngest_child_birth_year' in columns:
        print("Column youngest_child_birth_year is present in the database.")
    else:
        print("Column youngest_child_birth_year is MISSING from the database.")
except Exception as e:
    print(f"Error connecting to DB: {e}")
