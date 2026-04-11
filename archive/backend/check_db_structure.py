import sqlite3

conn = sqlite3.connect('app.db')
cursor = conn.cursor()

print("Employees table:")
cursor.execute('PRAGMA table_info(employees)')
for row in cursor.fetchall():
    print(row)

print("\nVacation allowances table:")
cursor.execute('PRAGMA table_info(vacation_allowances)')
for row in cursor.fetchall():
    print(row)

print("\nAlembic version:")
try:
    cursor.execute('SELECT * FROM alembic_version')
    for row in cursor.fetchall():
        print(row)
except:
    print("No alembic_version table found")

conn.close()
