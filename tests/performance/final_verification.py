#!/usr/bin/env python3
"""
Finale Überprüfung der bereinigten Datenbank
"""

import requests
import json

def final_verification():
    print("🔍 Finale Überprüfung der bereinigten Datenbank")
    print("=" * 50)
    
    try:
        # Login testen
        print("\n1. 🔐 Login-Test mit MGanser / M4rvelf4n")
        login_data = {'username': 'MGanser', 'password': 'M4rvelf4n'}
        response = requests.post('http://localhost:8000/api/v1/auth/login', json=login_data)
        
        if response.status_code != 200:
            print(f"❌ Login fehlgeschlagen: {response.status_code}")
            print(f"Response: {response.text}")
            return
        
        print("✅ Login erfolgreich!")
        token = response.json()['access_token']
        headers = {'Authorization': f'Bearer {token}'}

        # Mitarbeiter prüfen
        print("\n2. 👥 Mitarbeiter-Check")
        response = requests.get('http://localhost:8000/api/v1/employees', headers=headers)
        
        if response.status_code != 200:
            print(f"❌ Mitarbeiter abrufen fehlgeschlagen: {response.status_code}")
            return
            
        employees = response.json()
        print(f"   Anzahl Mitarbeiter: {len(employees)}")
        
        if len(employees) == 1:
            emp = employees[0]
            print(f"   ✅ Einziger Mitarbeiter: {emp['first_name']} {emp['last_name']} ({emp['email']})")
            if emp['email'] == 'maria.ganser@gynorg.de':
                print("   ✅ Korrekte E-Mail-Adresse")
            else:
                print(f"   ⚠️  Unerwartete E-Mail: {emp['email']}")
        else:
            print(f"   ⚠️  Falsche Anzahl Mitarbeiter: {len(employees)} (erwartet: 1)")

        # Urlaubsansprüche prüfen
        print("\n3. 🏖️ Urlaubsansprüche-Check")
        response = requests.get('http://localhost:8000/api/v1/vacation-allowances', headers=headers)
        
        if response.status_code != 200:
            print(f"❌ Urlaubsansprüche abrufen fehlgeschlagen: {response.status_code}")
            return
            
        vacation_allowances = response.json()
        print(f"   Anzahl Urlaubsansprüche: {len(vacation_allowances)}")
        
        if len(vacation_allowances) == 0:
            print("   ✅ Keine Urlaubsansprüche (wie erwartet)")
        else:
            print(f"   ⚠️  Unerwartete Urlaubsansprüche gefunden: {len(vacation_allowances)}")

        # Zusammenfassung
        print("\n" + "=" * 50)
        print("📋 ZUSAMMENFASSUNG")
        print("=" * 50)
        
        if (len(employees) == 1 and 
            employees[0]['email'] == 'maria.ganser@gynorg.de' and 
            len(vacation_allowances) == 0):
            print("🎉 ERFOLGREICH! Datenbank ist korrekt bereinigt.")
            print("   - Nur Maria Ganser ist als Mitarbeiter vorhanden")
            print("   - Keine Urlaubsansprüche in der Datenbank")
            print("   - Login funktioniert mit MGanser / M4rvelf4n")
        else:
            print("⚠️  PROBLEM! Datenbank ist nicht vollständig bereinigt.")
            
    except Exception as e:
        print(f"❌ Fehler bei der Überprüfung: {e}")

if __name__ == "__main__":
    final_verification()
