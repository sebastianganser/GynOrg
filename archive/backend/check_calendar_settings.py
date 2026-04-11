import sqlite3

conn = sqlite3.connect('gynorg.db')
cursor = conn.cursor()

print("Spalten in calendar_settings:")
cursor.execute('PRAGMA table_info(calendar_settings)')
for row in cursor.fetchall():
    print(f"  {row[1]} ({row[2]})")

print("\nEinträge in calendar_settings:")
cursor.execute('SELECT * FROM calendar_settings')
rows = cursor.fetchall()
if rows:
    for row in rows:
        print(f"  {row}")
else:
    print("  Keine Einträge vorhanden")

conn.close()
