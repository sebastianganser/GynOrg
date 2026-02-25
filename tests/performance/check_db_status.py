#!/usr/bin/env python3
"""
Quick DB Status Check
"""

import requests
import json

def check_db_status():
    try:
        # Login
        login_data = {'username': 'MGanser', 'password': 'M4rvelf4n'}
        response = requests.post('http://localhost:8000/api/v1/auth/login', json=login_data)
        token = response.json()['access_token']
        headers = {'Authorization': f'Bearer {token}'}

        # Aktuelle Mitarbeiter abrufen
        response = requests.get('http://localhost:8000/api/v1/employees?active_only=false', headers=headers)
        employees = response.json()

        print(f'Anzahl Mitarbeiter: {len(employees)}')
        for emp in employees[:10]:
            print(f'  - {emp["first_name"]} {emp["last_name"]} (ID: {emp["id"]}, Email: {emp["email"]})')
        if len(employees) > 10:
            print(f'  ... und {len(employees) - 10} weitere')
            
        # Maria Ganser suchen
        maria_found = False
        for emp in employees:
            if 'maria' in emp['first_name'].lower() and 'ganser' in emp['last_name'].lower():
                print(f'\n✅ Maria Ganser gefunden: ID {emp["id"]}, Email: {emp["email"]}')
                maria_found = True
                break
        
        if not maria_found:
            print('\n❌ Maria Ganser nicht gefunden!')
            
    except Exception as e:
        print(f'Fehler: {e}')

if __name__ == "__main__":
    check_db_status()
