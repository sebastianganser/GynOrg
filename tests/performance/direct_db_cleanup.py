#!/usr/bin/env python3
"""
Direkter Datenbankzugriff für Cleanup - umgeht API-Caching
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import time

# Database URL - korrekte Pfad zur Datenbank
DATABASE_URL = "sqlite:///./backend/app.db"

def direct_database_cleanup():
    """Direkte Datenbankbereinigung ohne API"""
    print("🔧 DIRECT DATABASE CLEANUP")
    print("=" * 50)
    
    try:
        # Engine erstellen
        engine = create_engine(DATABASE_URL)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        
        with SessionLocal() as db:
            # Zuerst alle Mitarbeiter anzeigen
            result = db.execute(text("SELECT id, first_name, last_name FROM employees"))
            employees = result.fetchall()
            
            print(f"📊 Found {len(employees)} employees:")
            maria_id = None
            for emp in employees:
                print(f"  - ID {emp[0]}: {emp[1]} {emp[2]}")
                if emp[1] == "Maria" and emp[2] == "Ganser":
                    maria_id = emp[0]
            
            if maria_id is None:
                print("❌ Maria Ganser not found!")
                return False
            
            print(f"👤 Maria Ganser found with ID: {maria_id}")
            
            # Vacation allowances löschen (außer für Maria)
            print("\n🏖️ Deleting vacation allowances...")
            result = db.execute(text("DELETE FROM vacation_allowances WHERE employee_id != :maria_id"), 
                              {"maria_id": maria_id})
            print(f"  ✅ Deleted {result.rowcount} vacation allowances")
            
            # Mitarbeiter löschen (außer Maria)
            print("\n👥 Deleting employees...")
            result = db.execute(text("DELETE FROM employees WHERE id != :maria_id"), 
                              {"maria_id": maria_id})
            print(f"  ✅ Deleted {result.rowcount} employees")
            
            # Commit
            db.commit()
            
            # Verification
            print("\n🔍 Verification:")
            result = db.execute(text("SELECT COUNT(*) FROM employees"))
            emp_count = result.scalar()
            
            result = db.execute(text("SELECT COUNT(*) FROM vacation_allowances"))
            va_count = result.scalar()
            
            print(f"  📊 Employees remaining: {emp_count}")
            print(f"  📊 Vacation allowances remaining: {va_count}")
            
            if emp_count == 1:
                result = db.execute(text("SELECT first_name, last_name FROM employees"))
                remaining = result.fetchone()
                print(f"  👤 Remaining employee: {remaining[0]} {remaining[1]}")
                
                if remaining[0] == "Maria" and remaining[1] == "Ganser":
                    print("✅ SUCCESS: Only Maria Ganser remains!")
                    return True
                else:
                    print("❌ FAILED: Wrong employee remains!")
                    return False
            else:
                print(f"❌ FAILED: {emp_count} employees remain (should be 1)")
                return False
                
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False

if __name__ == "__main__":
    success = direct_database_cleanup()
    print(f"\n🎯 Final result: {'✅ SUCCESS' if success else '❌ FAILED'}")
