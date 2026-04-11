import sqlite3
import os

# Die richtige Datenbank-Datei
db_path = './data/gynorg.db'

if not os.path.exists(db_path):
    print(f"❌ Datenbank nicht gefunden: {db_path}")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print(f"Verbunden mit: {db_path}")

# Prüfen ob die Tabelle existiert
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='calendar_settings'")
table_exists = cursor.fetchone()

if not table_exists:
    print("❌ Tabelle calendar_settings existiert nicht!")
    conn.close()
    exit(1)

print("✅ Tabelle calendar_settings gefunden")

# Aktuelle Spalten anzeigen
cursor.execute('PRAGMA table_info(calendar_settings)')
columns = cursor.fetchall()
print("\nAktuelle Spalten:")
for col in columns:
    print(f"  {col[1]} ({col[2]})")

# Prüfen ob show_calendar_weeks bereits existiert
column_names = [col[1] for col in columns]
if 'show_calendar_weeks' in column_names:
    print("\n✅ Spalte show_calendar_weeks existiert bereits!")
else:
    print("\n➕ Füge Spalte show_calendar_weeks hinzu...")
    try:
        cursor.execute('''
            ALTER TABLE calendar_settings 
            ADD COLUMN show_calendar_weeks BOOLEAN NOT NULL DEFAULT 0
        ''')
        conn.commit()
        print("✅ Spalte show_calendar_weeks erfolgreich hinzugefügt!")
    except Exception as e:
        print(f"❌ Fehler beim Hinzufügen der Spalte: {e}")
        conn.rollback()

# Finale Spalten anzeigen
cursor.execute('PRAGMA table_info(calendar_settings)')
columns = cursor.fetchall()
print("\nFinale Spalten:")
for col in columns:
    print(f"  {col[1]} ({col[2]})")

# Einträge anzeigen
cursor.execute('SELECT * FROM calendar_settings')
rows = cursor.fetchall()
print(f"\nAnzahl Einträge: {len(rows)}")
if rows:
    for row in rows:
        print(f"  {row}")

conn.close()
