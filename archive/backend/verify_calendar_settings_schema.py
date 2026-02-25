"""
Verifiziert das Schema der calendar_settings Tabelle
"""
import sqlite3
import os

# Pfad zur Datenbank
db_path = "./data/gynorg.db"

if not os.path.exists(db_path):
    print(f"❌ Datenbank nicht gefunden: {db_path}")
    exit(1)

print("=" * 80)
print("SCHEMA-VERIFIKATION: calendar_settings Tabelle")
print("=" * 80)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Prüfe ob Tabelle existiert
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='calendar_settings'")
table_exists = cursor.fetchone()

if not table_exists:
    print("\n❌ Tabelle 'calendar_settings' existiert nicht!")
    print("   Führe zuerst die Migrationen aus: cd backend && python -m alembic upgrade heads")
    conn.close()
    exit(1)

print("\n✅ Tabelle 'calendar_settings' existiert")

# Hole alle Spalten
cursor.execute("PRAGMA table_info(calendar_settings)")
columns = cursor.fetchall()

print("\n📋 Vorhandene Spalten:")
print("-" * 80)

expected_columns = {
    'id': 'INTEGER',
    'user_id': 'VARCHAR',
    'selected_federal_states': 'JSON',
    'show_nationwide_holidays': 'BOOLEAN',
    'show_calendar_weeks': 'BOOLEAN',
    'show_holidays': 'BOOLEAN',
    'show_school_vacations': 'BOOLEAN',
    'show_vacation_absences': 'BOOLEAN',
    'show_sick_leave': 'BOOLEAN',
    'show_training': 'BOOLEAN',
    'show_special_leave': 'BOOLEAN',
    'visible_employee_ids': 'JSON',
    'created_at': 'DATETIME',
    'updated_at': 'DATETIME'
}

found_columns = {}
for col in columns:
    col_id, col_name, col_type, not_null, default_val, pk = col
    found_columns[col_name] = col_type
    status = "✅" if col_name in expected_columns else "⚠️"
    print(f"{status} {col_name:30} {col_type:15} {'NOT NULL' if not_null else ''} {f'DEFAULT {default_val}' if default_val else ''}")

print("\n" + "=" * 80)
print("VERIFIKATION DER NEUEN FELDER (Subtask 24.2):")
print("=" * 80)

new_fields = [
    'show_holidays',
    'show_school_vacations', 
    'show_vacation_absences',
    'show_sick_leave',
    'show_training',
    'show_special_leave',
    'visible_employee_ids'
]

all_present = True
for field in new_fields:
    if field in found_columns:
        print(f"✅ {field:30} vorhanden ({found_columns[field]})")
    else:
        print(f"❌ {field:30} FEHLT!")
        all_present = False

# Prüfe Daten
cursor.execute("SELECT COUNT(*) FROM calendar_settings")
count = cursor.fetchone()[0]

print(f"\n📊 Anzahl Einträge in calendar_settings: {count}")

if count > 0:
    cursor.execute("SELECT * FROM calendar_settings LIMIT 1")
    row = cursor.fetchone()
    col_names = [description[0] for description in cursor.description]
    
    print("\n📋 Beispiel-Eintrag:")
    for i, col_name in enumerate(col_names):
        if col_name in new_fields:
            print(f"   {col_name:30} = {row[i]}")

conn.close()

print("\n" + "=" * 80)
if all_present:
    print("✅ ALLE NEUEN FELDER VORHANDEN - Subtask 24.2 erfolgreich!")
else:
    print("❌ EINIGE FELDER FEHLEN - Migration muss erneut ausgeführt werden!")
print("=" * 80)
