#!/usr/bin/env python3
"""
Direktes Database Cleanup Script
Bereinigt die Datenbank direkt und lässt nur den Standard-User Maria Ganser übrig
"""

import sys
import os
import requests
import time

def authenticate(base_url="http://localhost:8000", username="MGanser", password="M4rvelf4n"):
    """Authentifizierung für API-Zugriff"""
    try:
        response = requests.post(
            f"{base_url}/api/v1/auth/login",
            json={"username": username, "password": password},
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        if response.status_code == 200:
            token = response.json().get("access_token")
            print(f"✅ Authentication successful for user: {username}")
            return token
        else:
            print(f"❌ Authentication failed with status: {response.status_code}")
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"❌ Authentication failed: {e}")
    return None

def get_headers(token):
    """HTTP Headers mit Auth Token"""
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Cache-Control": "no-cache, no-store, must-revalidate",
        "Pragma": "no-cache",
        "Expires": "0"
    }

def get_all_employees(base_url, token):
    """Holt alle Mitarbeiter aus der API"""
    headers = get_headers(token)
    
    try:
        # Verschiedene Parameter versuchen
        for params in [{"active_only": "false"}, {}]:
            response = requests.get(
                f"{base_url}/api/v1/employees",
                params=params,
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    return data
                elif isinstance(data, dict):
                    return data.get("items", data.get("employees", data.get("data", [])))
    except Exception as e:
        print(f"Error getting employees: {e}")
    
    return []

def delete_employee(base_url, token, employee_id):
    """Löscht einen Mitarbeiter"""
    headers = get_headers(token)
    
    try:
        response = requests.delete(
            f"{base_url}/api/v1/employees/{employee_id}",
            headers=headers,
            timeout=30
        )
        return response.status_code in [200, 204, 404]  # 404 = bereits gelöscht
    except Exception as e:
        print(f"Error deleting employee {employee_id}: {e}")
        return False

def delete_vacation_allowances(base_url, token):
    """Löscht alle Urlaubsansprüche"""
    headers = get_headers(token)
    deleted_count = 0
    
    try:
        response = requests.get(
            f"{base_url}/api/v1/vacation-allowances",
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            allowances = response.json()
            for allowance in allowances:
                try:
                    del_response = requests.delete(
                        f"{base_url}/api/v1/vacation-allowances/{allowance['id']}",
                        headers=headers,
                        timeout=30
                    )
                    if del_response.status_code in [200, 204]:
                        deleted_count += 1
                except Exception as e:
                    print(f"Error deleting vacation allowance {allowance['id']}: {e}")
    except Exception as e:
        print(f"Error getting vacation allowances: {e}")
    
    return deleted_count

def main():
    print("=== Direct Database Cleanup Script ===")
    print("Bereinige Datenbank - nur Standard-User wird beibehalten")
    
    base_url = "http://localhost:8000"
    
    # Authentifizierung
    token = authenticate(base_url)
    if not token:
        print("❌ Authentifizierung fehlgeschlagen")
        return False
    
    # Alle Urlaubsansprüche löschen
    print("\n🗑️ Lösche alle Urlaubsansprüche...")
    deleted_allowances = delete_vacation_allowances(base_url, token)
    print(f"✅ {deleted_allowances} Urlaubsansprüche gelöscht")
    
    # Alle Mitarbeiter außer Standard-User löschen
    print("\n🗑️ Lösche alle Mitarbeiter außer Standard-User...")
    
    # Standard-User identifizieren
    all_employees = get_all_employees(base_url, token)
    print(f"📊 {len(all_employees)} Mitarbeiter gefunden")
    
    standard_user_id = None
    for emp in all_employees:
        email = emp.get("email", "").lower()
        first_name = emp.get("first_name", "").lower()
        last_name = emp.get("last_name", "").lower()
        
        if (email.startswith("mganser") or 
            email.startswith("maria.ganser") or
            email.startswith("m.ganser") or
            (first_name == "maria" and last_name == "ganser") or
            (first_name == "maria" and last_name.startswith("gans"))):
            standard_user_id = emp["id"]
            print(f"🔒 Standard-User gefunden: {emp['first_name']} {emp['last_name']} (ID: {emp['id']}, Email: {emp.get('email', 'N/A')})")
            break
    
    if not standard_user_id:
        print("⚠️ Kein Standard-User gefunden - alle Mitarbeiter werden gelöscht!")
    
    # Mitarbeiter löschen (außer Standard-User)
    deleted_count = 0
    failed_count = 0
    
    for emp in all_employees:
        if emp["id"] != standard_user_id:
            if delete_employee(base_url, token, emp["id"]):
                deleted_count += 1
                print(f"✅ Gelöscht: {emp.get('first_name', '')} {emp.get('last_name', '')} (ID: {emp['id']})")
            else:
                failed_count += 1
                print(f"❌ Fehler beim Löschen: {emp.get('first_name', '')} {emp.get('last_name', '')} (ID: {emp['id']})")
    
    print(f"\n📊 {deleted_count} Mitarbeiter gelöscht, {failed_count} Fehler")
    
    # Warten auf API-Konsistenz
    print("\n⏳ Warte auf API-Konsistenz...")
    time.sleep(3)
    
    # Verifikation
    print("\n🔍 Verifikation...")
    remaining_employees = get_all_employees(base_url, token)
    print(f"📊 {len(remaining_employees)} Mitarbeiter verbleiben")
    
    if remaining_employees:
        print("\nVerbleibende Mitarbeiter:")
        for emp in remaining_employees:
            print(f"  - {emp.get('first_name', '')} {emp.get('last_name', '')} (ID: {emp['id']}, Email: {emp.get('email', 'N/A')})")
    
    # Erfolg prüfen
    expected_count = 1 if standard_user_id else 0
    if len(remaining_employees) == expected_count:
        print(f"\n✅ Cleanup erfolgreich! {len(remaining_employees)} Mitarbeiter verbleiben (erwartet: {expected_count})")
        return True
    else:
        print(f"\n⚠️ Cleanup unvollständig! {len(remaining_employees)} Mitarbeiter verbleiben (erwartet: {expected_count})")
        
        # Zusätzlicher Cleanup-Versuch
        if len(remaining_employees) > expected_count:
            print("\n🔄 Zusätzlicher Cleanup-Versuch...")
            additional_deleted = 0
            
            for emp in remaining_employees:
                if emp["id"] != standard_user_id:
                    if delete_employee(base_url, token, emp["id"]):
                        additional_deleted += 1
                        print(f"✅ Zusätzlich gelöscht: {emp.get('first_name', '')} {emp.get('last_name', '')} (ID: {emp['id']})")
            
            if additional_deleted > 0:
                time.sleep(2)
                final_employees = get_all_employees(base_url, token)
                print(f"\n📊 Nach zusätzlichem Cleanup: {len(final_employees)} Mitarbeiter verbleiben")
                return len(final_employees) == expected_count
        
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🎉 Database Cleanup erfolgreich abgeschlossen!")
    else:
        print("\n💥 Database Cleanup fehlgeschlagen!")
        sys.exit(1)
