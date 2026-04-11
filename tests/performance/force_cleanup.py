#!/usr/bin/env python3
"""
Force Database Cleanup - Aggressive approach
"""

import requests
import json
import time
import os

def force_cleanup():
    try:
        # Login
        login_data = {'username': os.environ.get('ADMIN_USERNAME', 'admin'), 'password': os.environ.get('ADMIN_PASSWORD', 'admin')}
        response = requests.post('http://localhost:8000/api/v1/auth/login', json=login_data)
        if response.status_code != 200:
            print(f"Login failed: {response.status_code}")
            return
        
        token = response.json()['access_token']
        headers = {'Authorization': f'Bearer {token}'}
        print("✅ Login erfolgreich")

        # Maria Ganser ID finden und merken
        response = requests.get('http://localhost:8000/api/v1/employees?active_only=false', headers=headers)
        employees = response.json()
        
        maria_id = None
        for emp in employees:
            if 'maria' in emp['first_name'].lower() and 'ganser' in emp['last_name'].lower():
                maria_id = emp['id']
                print(f"✅ Maria Ganser gefunden: ID {maria_id}")
                break
        
        if not maria_id:
            print("❌ Maria Ganser nicht gefunden!")
            return

        # Mehrere Bereinigungsrunden
        for round_num in range(5):
            print(f"\n=== Bereinigungsrunde {round_num + 1} ===")
            
            # Aktuelle Mitarbeiter abrufen
            response = requests.get('http://localhost:8000/api/v1/employees?active_only=false', headers=headers)
            employees = response.json()
            print(f"Gefunden: {len(employees)} Mitarbeiter")
            
            if len(employees) <= 1:
                print("✅ Nur noch Maria Ganser vorhanden!")
                break
            
            # Alle außer Maria Ganser löschen
            deleted_count = 0
            for emp in employees:
                if emp['id'] != maria_id:
                    try:
                        delete_response = requests.delete(f'http://localhost:8000/api/v1/employees/{emp["id"]}', headers=headers)
                        if delete_response.status_code in [200, 204]:
                            deleted_count += 1
                            print(f"  Gelöscht: {emp['first_name']} {emp['last_name']} (ID: {emp['id']})")
                        else:
                            print(f"  Fehler beim Löschen von ID {emp['id']}: {delete_response.status_code}")
                    except Exception as e:
                        print(f"  Fehler beim Löschen von ID {emp['id']}: {e}")
            
            print(f"Gelöscht: {deleted_count} Mitarbeiter")
            
            # Kurz warten für DB-Konsistenz
            time.sleep(2)
        
        # Final verification
        print("\n=== Finale Verifikation ===")
        response = requests.get('http://localhost:8000/api/v1/employees?active_only=false', headers=headers)
        employees = response.json()
        
        print(f"Verbleibende Mitarbeiter: {len(employees)}")
        for emp in employees:
            print(f"  - {emp['first_name']} {emp['last_name']} (ID: {emp['id']}, Email: {emp['email']})")
        
        if len(employees) == 1 and employees[0]['id'] == maria_id:
            print("\n🎉 Bereinigung erfolgreich! Nur Maria Ganser ist noch vorhanden.")
        else:
            print(f"\n⚠️ Bereinigung unvollständig. {len(employees)} Mitarbeiter verbleiben.")
            
    except Exception as e:
        print(f'Fehler: {e}')

if __name__ == "__main__":
    force_cleanup()
