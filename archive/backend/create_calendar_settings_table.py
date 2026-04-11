import sqlite3

conn = sqlite3.connect('gynorg.db')
cursor = conn.cursor()

print("Erstelle calendar_settings Tabelle...")

cursor.execute('''
CREATE TABLE IF NOT EXISTS calendar_settings (
    id INTEGER PRIMARY KEY,
    user_id VARCHAR(50) DEFAULT 'default',
    selected_federal_states JSON NOT NULL,
    show_nationwide_holidays BOOLEAN NOT NULL DEFAULT 1,
    show_calendar_weeks BOOLEAN NOT NULL DEFAULT 0,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
)
''')

conn.commit()
print("✅ Tabelle calendar_settings erfolgreich erstellt")

# Prüfen
cursor.execute('PRAGMA table_info(calendar_settings)')
print("\nSpalten in calendar_settings:")
for row in cursor.fetchall():
    print(f"  {row[1]} ({row[2]})")

conn.close()
