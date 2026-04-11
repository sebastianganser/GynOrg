"""
Wendet die fehlenden Migrationen direkt auf die Datenbank an
"""
import sqlite3
import os

db_path = "./data/gynorg.db"

if not os.path.exists(db_path):
    print(f"❌ Datenbank nicht gefunden: {db_path}")
    exit(1)

print("=" * 80)
print("ANWENDUNG DER FEHLENDEN MIGRATIONEN")
print("=" * 80)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    # 1. Füge show_calendar_weeks hinzu (falls noch nicht vorhanden)
    print("\n1️⃣ Füge show_calendar_weeks hinzu...")
    try:
        cursor.execute("""
            ALTER TABLE calendar_settings 
            ADD COLUMN show_calendar_weeks BOOLEAN NOT NULL DEFAULT 0
        """)
        print("   ✅ show_calendar_weeks hinzugefügt")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e).lower():
            print("   ℹ️  show_calendar_weeks existiert bereits")
        else:
            raise

    # 2. Füge die neuen Filter-Felder hinzu
    print("\n2️⃣ Füge Filter-Felder hinzu...")
    
    filter_fields = [
        ('show_holidays', 'BOOLEAN NOT NULL DEFAULT 1'),
        ('show_school_vacations', 'BOOLEAN NOT NULL DEFAULT 1'),
        ('show_vacation_absences', 'BOOLEAN NOT NULL DEFAULT 1'),
        ('show_sick_leave', 'BOOLEAN NOT NULL DEFAULT 1'),
        ('show_training', 'BOOLEAN NOT NULL DEFAULT 1'),
        ('show_special_leave', 'BOOLEAN NOT NULL DEFAULT 1'),
        ('visible_employee_ids', 'JSON')
    ]
    
    for field_name, field_type in filter_fields:
        try:
            cursor.execute(f"""
                ALTER TABLE calendar_settings 
                ADD COLUMN {field_name} {field_type}
            """)
            print(f"   ✅ {field_name} hinzugefügt")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e).lower():
                print(f"   ℹ️  {field_name} existiert bereits")
            else:
                raise
    
    conn.commit()
    
    # 3. Verifiziere das Schema
    print("\n3️⃣ Verifiziere Schema...")
    cursor.execute("PRAGMA table_info(calendar_settings)")
    columns = cursor.fetchall()
    
    column_names = [col[1] for col in columns]
    
    required_fields = [
        'show_calendar_weeks',
        'show_holidays',
        'show_school_vacations',
        'show_vacation_absences',
        'show_sick_leave',
        'show_training',
        'show_special_leave',
        'visible_employee_ids'
    ]
    
    all_present = True
    for field in required_fields:
        if field in column_names:
            print(f"   ✅ {field}")
        else:
            print(f"   ❌ {field} FEHLT!")
            all_present = False
    
    if all_present:
        print("\n" + "=" * 80)
        print("✅ ALLE MIGRATIONEN ERFOLGREICH ANGEWENDET!")
        print("=" * 80)
    else:
        print("\n" + "=" * 80)
        print("❌ EINIGE FELDER FEHLEN NOCH!")
        print("=" * 80)
        
except Exception as e:
    print(f"\n❌ FEHLER: {e}")
    conn.rollback()
    raise
finally:
    conn.close()
