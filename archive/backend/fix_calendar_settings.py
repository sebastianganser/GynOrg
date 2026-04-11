import sqlite3
import json

conn = sqlite3.connect('gynorg.db')
cursor = conn.cursor()

print("Erstelle Standard-Einstellungen...")

# Standard-Einstellungen mit korrektem JSON-Format
default_settings = {
    'user_id': 'default',
    'selected_federal_states': json.dumps(['NW']),  # Als JSON-String
    'show_nationwide_holidays': 1,  # True = 1
    'show_calendar_weeks': 0,  # False = 0
}

cursor.execute('''
    INSERT INTO calendar_settings 
    (user_id, selected_federal_states, show_nationwide_holidays, show_calendar_weeks)
    VALUES (?, ?, ?, ?)
''', (
    default_settings['user_id'],
    default_settings['selected_federal_states'],
    default_settings['show_nationwide_holidays'],
    default_settings['show_calendar_weeks']
))

conn.commit()
print("✅ Standard-Einstellungen erfolgreich erstellt")

# Prüfen
cursor.execute('SELECT * FROM calendar_settings')
row = cursor.fetchone()
print("\nEinstellungen in der Datenbank:")
print(f"  ID: {row[0]}")
print(f"  User ID: {row[1]}")
print(f"  Selected Federal States: {row[2]}")
print(f"  Show Nationwide Holidays: {row[3]}")
print(f"  Show Calendar Weeks: {row[4]}")
print(f"  Created At: {row[5]}")
print(f"  Updated At: {row[6]}")

conn.close()
