#!/usr/bin/env python3
"""
Test zur Verifikation der Einstellungsdatum-Validierung
Testet sowohl Frontend- als auch Backend-Konsistenz
"""

import requests
import json
from datetime import date, timedelta

# Backend-URL
BASE_URL = "http://localhost:8000"

def test_future_hire_date():
    """Test: Zukünftige Einstellungsdaten bis 1 Jahr sollten erlaubt sein"""
    
    # Testdaten mit zukünftigem Einstellungsdatum (6 Monate)
    future_date = date.today() + timedelta(days=180)  # 6 Monate
    
    employee_data = {
        "first_name": "Test",
        "last_name": "Future",
        "email": "test.future@example.com",
        "date_hired": future_date.isoformat(),
        "federal_state": "BAYERN",
        "active": True
    }
    
    print(f"🧪 Teste zukünftiges Einstellungsdatum: {future_date}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/employees/",
            json=employee_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 201:
            print("✅ SUCCESS: Zukünftiges Einstellungsdatum (6 Monate) wurde akzeptiert")
            employee = response.json()
            print(f"   Erstellt: Employee ID {employee.get('id')}")
            return employee.get('id')
        else:
            print(f"❌ FAILED: Status {response.status_code}")
            print(f"   Response: {response.text}")
            return None
            
    except requests.exceptions.ConnectionError:
        print("❌ ERROR: Backend nicht erreichbar. Starte das Backend mit 'python start.py'")
        return None

def test_too_far_future_hire_date():
    """Test: Einstellungsdatum > 1 Jahr sollte abgelehnt werden"""
    
    # Testdaten mit zu weit zukünftigem Einstellungsdatum (2 Jahre)
    far_future_date = date.today() + timedelta(days=730)  # 2 Jahre
    
    employee_data = {
        "first_name": "Test",
        "last_name": "TooFar",
        "email": "test.toofar@example.com",
        "date_hired": far_future_date.isoformat(),
        "federal_state": "BAYERN",
        "active": True
    }
    
    print(f"🧪 Teste zu weit zukünftiges Einstellungsdatum: {far_future_date}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/employees/",
            json=employee_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 422:
            print("✅ SUCCESS: Zu weit zukünftiges Einstellungsdatum (2 Jahre) wurde korrekt abgelehnt")
            error_detail = response.json()
            print(f"   Fehlermeldung: {error_detail}")
        else:
            print(f"❌ FAILED: Erwartete 422, bekam {response.status_code}")
            print(f"   Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ ERROR: Backend nicht erreichbar. Starte das Backend mit 'python start.py'")

def cleanup_test_employee(employee_id):
    """Lösche Test-Employee nach erfolgreichem Test"""
    if employee_id:
        try:
            response = requests.delete(f"{BASE_URL}/api/v1/employees/{employee_id}")
            if response.status_code == 200:
                print(f"🧹 Test-Employee {employee_id} gelöscht")
            else:
                print(f"⚠️  Konnte Test-Employee {employee_id} nicht löschen")
        except:
            print(f"⚠️  Fehler beim Löschen von Test-Employee {employee_id}")

def main():
    print("=" * 60)
    print("🔧 BACKEND-VALIDIERUNG: Einstellungsdatum-Fix")
    print("=" * 60)
    
    # Test 1: Zukünftiges Datum (sollte funktionieren)
    employee_id = test_future_hire_date()
    
    print()
    
    # Test 2: Zu weit zukünftiges Datum (sollte fehlschlagen)
    test_too_far_future_hire_date()
    
    print()
    
    # Cleanup
    cleanup_test_employee(employee_id)
    
    print("=" * 60)
    print("✅ Backend-Validierung abgeschlossen")
    print("💡 Nächster Schritt: Frontend testen mit zukünftigem Einstellungsdatum")
    print("=" * 60)

if __name__ == "__main__":
    main()
