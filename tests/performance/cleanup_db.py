#!/usr/bin/env python3
"""
Database Cleanup Script
Bereinigt die Datenbank und lässt nur den Standard-User Maria Ganser übrig
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from test_data_generator import TestDataGenerator

def main():
    print("=== Database Cleanup Script ===")
    print("Bereinige Datenbank - nur Standard-User wird beibehalten")
    
    # Generator initialisieren
    generator = TestDataGenerator()
    
    # Authentifizierung
    if not generator.authenticate():
        print("❌ Authentifizierung fehlgeschlagen")
        return False
    
    # Cleanup durchführen
    success = generator.cleanup_existing_test_data(preserve_standard_user=True)
    
    if success:
        print("✅ Datenbank erfolgreich bereinigt")
        
        # Verifikation
        remaining_employees = generator.get_all_employees()
        print(f"Verbleibende Mitarbeiter: {len(remaining_employees)}")
        
        if remaining_employees:
            for emp in remaining_employees:
                print(f"  - {emp.get('first_name', '')} {emp.get('last_name', '')} (ID: {emp['id']}, Email: {emp.get('email', 'N/A')})")
        
        return True
    else:
        print("❌ Cleanup fehlgeschlagen")
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🎉 Cleanup abgeschlossen!")
    else:
        print("\n💥 Cleanup fehlgeschlagen!")
        sys.exit(1)
