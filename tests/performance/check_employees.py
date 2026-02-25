#!/usr/bin/env python3
"""
Überprüft die aktuellen Mitarbeiter in der Datenbank
"""

import requests
import json

def check_employees():
    try:
        # Login
        login_data = {'username': 'MGanser', 'password': 'M4rvelf4n'}
        response = requests.post('http://localhost:8000/api/v1/auth/login', json=login_data)
        
        if response.status_code != 200:
            print(f"❌ Login fehlgeschlagen: {response.status_code}")
            return
            
        token = response.json()['access_token']
        headers = {'Authorization': f'Bearer {token}'}

        # Alle Mitarbeiter abrufen
        response = requests.get('http://localhost:8000/api/v1/employees', headers=headers)
        
        if response.status_code != 200:
            print(f"❌ Mitarbeiter abrufen fehlgeschlagen: {response.status_code}")
            return
            
        employees = response.json()

        print(f'📊 Anzahl Mitarbeiter: {len(employees)}')
        print("\n👥 Aktuelle Mitarbeiter:")
        
        for emp in employees:
            print(f'  - {emp["first_name"]} {emp["last_name"]} (ID: {emp["id"]}, Email: {emp["email"]})')
            
        # Prüfen ob nur Maria Ganser vorhanden ist
        if len(employees) == 1 and employees[0]["email"] == "maria.ganser@gynorg.de":
            print("\n✅ Perfekt! Nur Maria Ganser ist in der Datenbank.")
        else:
            print(f"\n⚠️  Problem: {len(employees)} Mitarbeiter gefunden, sollte nur 1 sein (Maria Ganser)")
            
    except Exception as e:
        print(f"❌ Fehler: {e}")

if __name__ == "__main__":
    check_employees()
