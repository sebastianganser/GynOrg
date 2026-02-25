#!/usr/bin/env python3
"""
Database Cleanup Script
Bereinigt die Datenbank und lässt nur den Standard-Employee (Maria Ganser) übrig
"""

import sys
import os
from sqlmodel import Session

# Backend-Pfad hinzufügen
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import engine
from app.models.employee import Employee
from app.models.vacation_allowance import VacationAllowance
from app.models.federal_state import FederalState

def cleanup_database():
    """Bereinigt die Datenbank komplett und erstellt nur den Standard-Employee"""
    
    print("🔧 DATABASE CLEANUP")
    print("=" * 50)
    
    try:
        # Session erstellen
        with Session(engine) as db:
            print("📊 Aktuelle Datenbank-Inhalte:")
            
            # Aktuelle Anzahl anzeigen
            from sqlmodel import select
            employee_count = len(db.exec(select(Employee)).all())
            vacation_count = len(db.exec(select(VacationAllowance)).all())
            
            print(f"   Employees: {employee_count}")
            print(f"   Vacation Allowances: {vacation_count}")
            
            # Alle VacationAllowances löschen
            print("\n🗑️  Lösche alle Vacation Allowances...")
            vacations = db.exec(select(VacationAllowance)).all()
            for vacation in vacations:
                db.delete(vacation)
            print(f"   Gelöscht: {len(vacations)} Vacation Allowances")
            
            # Alle Employees außer Maria Ganser löschen
            print("\n🗑️  Lösche alle Employees außer Maria Ganser...")
            employees_to_delete = db.exec(select(Employee).where(Employee.email != "maria.ganser@gynorg.de")).all()
            for employee in employees_to_delete:
                db.delete(employee)
            print(f"   Gelöscht: {len(employees_to_delete)} Employees")
            
            # Prüfen ob Maria Ganser existiert
            maria = db.exec(select(Employee).where(Employee.email == "maria.ganser@gynorg.de")).first()
            
            if not maria:
                print("\n👤 Erstelle Standard-Employee Maria Ganser...")
                
                # Maria Ganser erstellen
                maria = Employee(
                    first_name="Maria",
                    last_name="Ganser",
                    email="maria.ganser@gynorg.de",
                    federal_state=FederalState.BAYERN,
                    active=True,
                    position="Praxisleitung"
                )
                
                db.add(maria)
                print("   ✅ Maria Ganser erstellt")
            else:
                print("\n👤 Maria Ganser bereits vorhanden")
                print("   ✅ Keine Änderungen nötig")
            
            # Änderungen speichern
            db.commit()
            
            # Finale Überprüfung
            print("\n📊 Finale Datenbank-Inhalte:")
            final_employee_count = len(db.exec(select(Employee)).all())
            final_vacation_count = len(db.exec(select(VacationAllowance)).all())
            
            print(f"   Employees: {final_employee_count}")
            print(f"   Vacation Allowances: {final_vacation_count}")
            
            # Überprüfung der Maria Ganser Daten
            maria_check = db.exec(select(Employee).where(Employee.email == "maria.ganser@gynorg.de")).first()
            if maria_check:
                print(f"\n👤 Standard-Employee Details:")
                print(f"   Email: {maria_check.email}")
                print(f"   Name: {maria_check.first_name} {maria_check.last_name}")
                print(f"   Position: {maria_check.position}")
                print(f"   Bundesland: {maria_check.federal_state}")
                print(f"   Active: {maria_check.active}")
            
            print(f"\n🎯 Cleanup erfolgreich!")
            print(f"   Login-Daten (hardcoded): MGanser / M4rvelf4n")
            return True
        
    except Exception as e:
        print(f"\n❌ Database error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = cleanup_database()
    if success:
        print("\n✅ Database cleanup completed successfully!")
    else:
        print("\n❌ Database cleanup failed!")
        sys.exit(1)
