#!/usr/bin/env python3
"""
Überprüft die aktuellen Urlaubsansprüche in der Datenbank
"""

import requests
import json
import os

def check_vacation_allowances():
    try:
        # Login
        login_data = {'username': os.environ.get('ADMIN_USERNAME', 'admin'), 'password': os.environ.get('ADMIN_PASSWORD', 'admin')}
        response = requests.post('http://localhost:8000/api/v1/auth/login', json=login_data)
        
        if response.status_code != 200:
            print(f"❌ Login fehlgeschlagen: {response.status_code}")
            return
            
        token = response.json()['access_token']
        headers = {'Authorization': f'Bearer {token}'}

        # Alle Urlaubsansprüche abrufen
        response = requests.get('http://localhost:8000/api/v1/vacation-allowances', headers=headers)
        
        if response.status_code != 200:
            print(f"❌ Urlaubsansprüche abrufen fehlgeschlagen: {response.status_code}")
            return
            
        vacation_allowances = response.json()

        print(f'📊 Anzahl Urlaubsansprüche: {len(vacation_allowances)}')
        
        if vacation_allowances:
            print("\n🏖️ Aktuelle Urlaubsansprüche:")
            for va in vacation_allowances:
                print(f'  - Mitarbeiter ID: {va["employee_id"]}, Jahr: {va["year"]}, Tage: {va["days"]}')
        else:
            print("\n✅ Keine Urlaubsansprüche in der Datenbank.")
            
    except Exception as e:
        print(f"❌ Fehler: {e}")

if __name__ == "__main__":
    check_vacation_allowances()
