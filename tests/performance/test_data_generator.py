#!/usr/bin/env python3
"""
Test Data Generator für Performance Tests
Generiert realistische Testdaten für Employee und VacationAllowance
"""

import random
import json
import time
from datetime import datetime, timedelta
from typing import List, Dict, Any
import requests
from faker import Faker

fake = Faker('de_DE')

class TestDataGenerator:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.auth_token = None
        self.federal_states = []
        self.created_employees = []
        self.created_vacation_allowances = []
        self.cleanup_retries = 3
        self.api_timeout = 30
    
    def authenticate(self, username: str = "MGanser", password: str = "M4rvelf4n"):
        """Authentifizierung für API-Zugriff"""
        try:
            response = self.session.post(
                f"{self.base_url}/api/v1/auth/login",
                json={"username": username, "password": password},
                headers={"Content-Type": "application/json"},
                timeout=self.api_timeout
            )
            if response.status_code == 200:
                self.auth_token = response.json().get("access_token")
                print(f"Authentication successful for user: {username}")
                return True
            else:
                print(f"Authentication failed with status: {response.status_code}")
                print(f"Response: {response.text}")
        except Exception as e:
            print(f"Authentication failed: {e}")
        return False
    
    def get_headers(self):
        """HTTP Headers mit Auth Token"""
        return {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json"
        }
    
    def load_federal_states(self):
        """Lade verfügbare Bundesländer"""
        try:
            response = self.session.get(
                f"{self.base_url}/api/v1/federal-states",
                headers=self.get_headers(),
                timeout=self.api_timeout
            )
            if response.status_code == 200:
                self.federal_states = response.json()
                print(f"Loaded {len(self.federal_states)} federal states")
        except Exception as e:
            print(f"Failed to load federal states: {e}")
    
    def generate_employee_data(self) -> Dict[str, Any]:
        """Generiert realistische Mitarbeiter-Daten"""
        gender = random.choice(['male', 'female'])
        first_name = fake.first_name_male() if gender == 'male' else fake.first_name_female()
        last_name = fake.last_name()
        
        # Realistische Geburtsdaten (25-65 Jahre)
        birth_date = fake.date_of_birth(minimum_age=25, maximum_age=65)
        
        # Einstellungsdatum (zwischen Geburt+18 und heute)
        min_hire_date = birth_date + timedelta(days=18*365)
        max_hire_date = datetime.now().date()
        hire_date = fake.date_between(start_date=min_hire_date, end_date=max_hire_date)
        
        # Zufälliges Bundesland (API gibt String-Array zurück)
        federal_state = random.choice(self.federal_states) if self.federal_states else "Bayern"
        
        return {
            "first_name": first_name,
            "last_name": last_name,
            "email": f"{first_name.lower()}.{last_name.lower()}@{fake.domain_name()}",
            "phone": fake.phone_number(),
            "birth_date": birth_date.isoformat(),
            "hire_date": hire_date.isoformat(),
            "position": fake.job(),
            "department": random.choice([
                "IT", "HR", "Finance", "Marketing", "Sales", "Operations", 
                "Legal", "R&D", "Customer Service", "Administration"
            ]),
            "salary": round(random.uniform(35000, 120000), 2),
            "federal_state": federal_state,
            "street": fake.street_address(),
            "city": fake.city(),
            "postal_code": fake.postcode(),
            "emergency_contact_name": fake.name(),
            "emergency_contact_phone": fake.phone_number(),
            "notes": fake.text(max_nb_chars=200) if random.random() > 0.7 else "",
            "active": True  # Wichtig: Mitarbeiter als aktiv markieren für Frontend-Anzeige
        }
    
    def create_employees(self, count: int = 1000) -> List[Dict]:
        """Erstellt Mitarbeiter über API"""
        print(f"Creating {count} employees...")
        created = []
        failed_count = 0
        
        for i in range(count):
            if i % 100 == 0:
                print(f"Progress: {i}/{count} employees created, {failed_count} failed")
            
            employee_data = self.generate_employee_data()
            
            # Retry-Logik für API-Aufrufe
            max_retries = 3
            retry_count = 0
            success = False
            
            while retry_count < max_retries and not success:
                try:
                    response = self.session.post(
                        f"{self.base_url}/api/v1/employees",
                        json=employee_data,
                        headers=self.get_headers(),
                        timeout=self.api_timeout
                    )
                    
                    if response.status_code == 201:
                        employee = response.json()
                        created.append(employee)
                        self.created_employees.append(employee["id"])
                        success = True
                    elif response.status_code == 422:
                        # Validierungsfehler - neue Daten generieren
                        print(f"Validation error for employee {i}, generating new data...")
                        employee_data = self.generate_employee_data()
                        retry_count += 1
                    elif response.status_code == 401:
                        # Auth-Fehler - neu authentifizieren
                        print(f"Auth error, re-authenticating...")
                        if self.authenticate():
                            retry_count += 1
                        else:
                            print(f"Re-authentication failed for employee {i}")
                            break
                    else:
                        print(f"Failed to create employee {i}: {response.status_code} - {response.text[:200]}")
                        retry_count += 1
                        
                except Exception as e:
                    print(f"Error creating employee {i} (attempt {retry_count + 1}): {e}")
                    retry_count += 1
            
            if not success:
                failed_count += 1
        
        print(f"Successfully created {len(created)} employees, {failed_count} failed")
        return created
    
    def generate_vacation_allowance_data(self, employee_id: int) -> Dict[str, Any]:
        """Generiert Urlaubsanspruch-Daten für einen Mitarbeiter"""
        current_year = datetime.now().year
        year = random.choice([current_year - 1, current_year, current_year + 1])
        
        # Realistische Urlaubstage (20-30 Tage)
        annual_allowance = random.randint(20, 30)
        used_days = random.randint(0, min(annual_allowance, 25))
        
        return {
            "employee_id": employee_id,
            "year": year,
            "annual_allowance": annual_allowance,
            "used_days": used_days,
            "notes": fake.text(max_nb_chars=100) if random.random() > 0.8 else ""
        }
    
    def create_vacation_allowances(self, employee_ids: List[int], entries_per_employee: int = 3) -> List[Dict]:
        """Erstellt Urlaubsansprüche für Mitarbeiter"""
        print(f"Creating vacation allowances for {len(employee_ids)} employees...")
        created = []
        failed_count = 0
        
        for i, employee_id in enumerate(employee_ids):
            if i % 100 == 0:
                print(f"Progress: {i}/{len(employee_ids)} employees processed, {failed_count} failed")
            
            # Mehrere Jahre pro Mitarbeiter - aber vermeiden von Duplikaten
            used_years = set()
            for _ in range(entries_per_employee):
                max_retries = 5
                retry_count = 0
                success = False
                
                while retry_count < max_retries and not success:
                    allowance_data = self.generate_vacation_allowance_data(employee_id)
                    
                    # Vermeiden von Duplikaten für gleichen Mitarbeiter/Jahr
                    year_key = (employee_id, allowance_data["year"])
                    if year_key in used_years:
                        # Neues Jahr generieren
                        current_year = datetime.now().year
                        available_years = [current_year - 1, current_year, current_year + 1]
                        unused_years = [y for y in available_years if (employee_id, y) not in used_years]
                        if unused_years:
                            allowance_data["year"] = random.choice(unused_years)
                        else:
                            # Alle Jahre für diesen Mitarbeiter verwendet
                            break
                    
                    try:
                        response = self.session.post(
                            f"{self.base_url}/api/v1/vacation-allowances",
                            json=allowance_data,
                            headers=self.get_headers(),
                            timeout=self.api_timeout
                        )
                        
                        if response.status_code == 201:
                            allowance = response.json()
                            created.append(allowance)
                            self.created_vacation_allowances.append(allowance["id"])
                            used_years.add((employee_id, allowance_data["year"]))
                            success = True
                        elif response.status_code == 400:
                            # Wahrscheinlich Duplikat - neues Jahr versuchen
                            retry_count += 1
                        elif response.status_code == 401:
                            # Auth-Fehler - neu authentifizieren
                            if self.authenticate():
                                retry_count += 1
                            else:
                                break
                        else:
                            print(f"Failed to create vacation allowance for employee {employee_id}: {response.status_code} - {response.text[:200]}")
                            retry_count += 1
                            
                    except Exception as e:
                        print(f"Error creating vacation allowance for employee {employee_id} (attempt {retry_count + 1}): {e}")
                        retry_count += 1
                
                if not success:
                    failed_count += 1
        
        print(f"Successfully created {len(created)} vacation allowances, {failed_count} failed")
        return created
    
    def get_all_employees(self) -> List[Dict]:
        """Holt alle Mitarbeiter aus der API (mit Cache-Bypass)"""
        all_employees = []
        
        try:
            # Cache-Bypass Headers hinzufügen
            headers = self.get_headers()
            headers.update({
                "Cache-Control": "no-cache, no-store, must-revalidate",
                "Pragma": "no-cache",
                "Expires": "0"
            })
            
            # Verschiedene Parameter-Kombinationen versuchen
            param_combinations = [
                {"active_only": "false"},  # Alle Mitarbeiter (aktive + inaktive)
                {"include_inactive": "true"},  # Alternative für inaktive
                {"all": "true"},  # Alle Mitarbeiter
                {},  # Ohne Parameter
            ]
            
            for params in param_combinations:
                try:
                    response = self.session.get(
                        f"{self.base_url}/api/v1/employees",
                        params=params,
                        headers=headers,
                        timeout=self.api_timeout
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        
                        # Prüfen ob die Antwort eine Liste ist
                        if isinstance(data, list):
                            all_employees = data
                            print(f"Got {len(data)} employees with params {params}")
                            break
                        elif isinstance(data, dict):
                            # Paginierte Antwort oder verschachtelte Struktur
                            employees = data.get("items", data.get("employees", data.get("data", [])))
                            if employees:
                                all_employees = employees
                                print(f"Got {len(employees)} employees from dict with params {params}")
                                break
                    else:
                        print(f"Failed to get employees with params {params}: {response.status_code}")
                        
                except Exception as e:
                    print(f"Error with params {params}: {e}")
                    continue
            
            # Wenn immer noch keine Mitarbeiter gefunden, versuche ohne Session
            if not all_employees:
                print("Trying direct requests without session...")
                try:
                    response = requests.get(
                        f"{self.base_url}/api/v1/employees",
                        headers=headers,
                        timeout=self.api_timeout
                    )
                    if response.status_code == 200:
                        data = response.json()
                        if isinstance(data, list):
                            all_employees = data
                            print(f"Direct request successful: Got {len(data)} employees")
                        elif isinstance(data, dict):
                            employees = data.get("items", data.get("employees", data.get("data", [])))
                            all_employees = employees
                            print(f"Direct request successful: Got {len(employees)} employees from dict")
                except Exception as e:
                    print(f"Direct request failed: {e}")
                    
        except Exception as e:
            print(f"Error getting employees: {e}")
            
        print(f"Final result: {len(all_employees)} employees retrieved")
        return all_employees
    
    def cleanup_existing_test_data(self, preserve_standard_user: bool = True):
        """Löscht vorhandene Testdaten vor dem Test"""
        print("=== Cleaning up existing test data ===")
        
        # Alle Mitarbeiter abrufen
        all_employees = self.get_all_employees()
        print(f"Found {len(all_employees)} existing employees")
        
        # Standard-Benutzer identifizieren (MGanser) - erweiterte Suche
        standard_user_id = None
        if preserve_standard_user:
            for emp in all_employees:
                # Verschiedene Möglichkeiten den Standard-User zu identifizieren
                email = emp.get("email", "").lower()
                first_name = emp.get("first_name", "").lower()
                last_name = emp.get("last_name", "").lower()
                
                if (email.startswith("mganser") or 
                    email.startswith("maria.ganser") or
                    email.startswith("m.ganser") or
                    (first_name == "maria" and last_name == "ganser") or
                    (first_name == "maria" and last_name.startswith("gans"))):
                    standard_user_id = emp["id"]
                    print(f"Preserving standard user: {emp['first_name']} {emp['last_name']} (ID: {emp['id']}, Email: {emp.get('email', 'N/A')})")
                    break
            
            # Fallback: Wenn kein Standard-User gefunden, den ersten Mitarbeiter als Standard betrachten
            if standard_user_id is None and all_employees:
                standard_user_id = all_employees[0]["id"]
                print(f"No standard user found, preserving first employee: {all_employees[0]['first_name']} {all_employees[0]['last_name']} (ID: {all_employees[0]['id']})")
        
        # Alle Urlaubsansprüche löschen (außer die des Standard-Benutzers)
        try:
            response = self.session.get(
                f"{self.base_url}/api/v1/vacation-allowances",
                headers=self.get_headers(),
                timeout=self.api_timeout
            )
            if response.status_code == 200:
                vacation_allowances = response.json()
                deleted_allowances = 0
                for allowance in vacation_allowances:
                    if not preserve_standard_user or allowance.get("employee_id") != standard_user_id:
                        try:
                            del_response = self.session.delete(
                                f"{self.base_url}/api/v1/vacation-allowances/{allowance['id']}",
                                headers=self.get_headers(),
                                timeout=self.api_timeout
                            )
                            if del_response.status_code in [200, 204]:
                                deleted_allowances += 1
                        except Exception as e:
                            print(f"Error deleting vacation allowance {allowance['id']}: {e}")
                print(f"Deleted {deleted_allowances} existing vacation allowances")
        except Exception as e:
            print(f"Error cleaning vacation allowances: {e}")
        
        # Alle Mitarbeiter löschen (außer Standard-Benutzer) - mit Retry-Logik
        deleted_employees = 0
        failed_deletions = []
        
        for employee in all_employees:
            if not preserve_standard_user or employee["id"] != standard_user_id:
                success = False
                for retry in range(self.cleanup_retries):
                    try:
                        response = self.session.delete(
                            f"{self.base_url}/api/v1/employees/{employee['id']}",
                            headers=self.get_headers(),
                            timeout=self.api_timeout
                        )
                        if response.status_code in [200, 204]:
                            deleted_employees += 1
                            print(f"Deleted employee: {employee.get('first_name', '')} {employee.get('last_name', '')} (ID: {employee['id']})")
                            success = True
                            break
                        elif response.status_code == 404:
                            # Mitarbeiter bereits gelöscht
                            print(f"Employee {employee['id']} already deleted")
                            success = True
                            break
                        else:
                            print(f"Delete attempt {retry + 1} failed for employee {employee['id']}: {response.status_code}")
                            if retry < self.cleanup_retries - 1:
                                time.sleep(0.5)  # Kurze Pause vor Retry
                    except Exception as e:
                        print(f"Error deleting employee {employee['id']} (attempt {retry + 1}): {e}")
                        if retry < self.cleanup_retries - 1:
                            time.sleep(0.5)
                
                if not success:
                    failed_deletions.append(employee['id'])
        
        print(f"Deleted {deleted_employees} existing employees")
        if failed_deletions:
            print(f"Failed to delete {len(failed_deletions)} employees: {failed_deletions}")
        
        # Kurze Pause für API-Konsistenz
        time.sleep(2)
        
        # Verifikation mit mehreren Versuchen
        for verification_attempt in range(3):
            remaining_employees = self.get_all_employees()
            print(f"Verification attempt {verification_attempt + 1}: {len(remaining_employees)} employees remain")
            
            if preserve_standard_user and len(remaining_employees) == 1:
                print("✅ Cleanup successful - only standard user remains")
                return True
            elif not preserve_standard_user and len(remaining_employees) == 0:
                print("✅ Cleanup successful - all employees deleted")
                return True
            elif verification_attempt < 2:
                print(f"Waiting for API consistency... (attempt {verification_attempt + 1}/3)")
                time.sleep(3)  # Längere Pause für API-Konsistenz
        
        # Detaillierte Ausgabe der verbleibenden Mitarbeiter
        if remaining_employees:
            print("Remaining employees:")
            for emp in remaining_employees:
                print(f"  - {emp.get('first_name', '')} {emp.get('last_name', '')} (ID: {emp['id']}, Email: {emp.get('email', 'N/A')})")
        
        expected_count = 1 if preserve_standard_user else 0
        if len(remaining_employees) > expected_count:
            print(f"⚠️ Cleanup completed but {len(remaining_employees)} employees remain (expected: {expected_count})")
            
            # Zusätzlicher Cleanup-Versuch wenn zu viele Mitarbeiter übrig sind
            print("Attempting additional cleanup...")
            additional_deleted = 0
            for emp in remaining_employees:
                if not preserve_standard_user or emp["id"] != standard_user_id:
                    try:
                        response = self.session.delete(
                            f"{self.base_url}/api/v1/employees/{emp['id']}",
                            headers=self.get_headers(),
                            timeout=self.api_timeout
                        )
                        if response.status_code in [200, 204]:
                            additional_deleted += 1
                            print(f"  Additional cleanup: Deleted {emp.get('first_name', '')} {emp.get('last_name', '')} (ID: {emp['id']})")
                    except Exception as e:
                        print(f"  Error in additional cleanup for employee {emp['id']}: {e}")
            
            if additional_deleted > 0:
                time.sleep(2)  # Pause für API-Konsistenz
                final_employees = self.get_all_employees()
                print(f"After additional cleanup: {len(final_employees)} employees remain")
                return len(final_employees) <= expected_count
        
        return len(remaining_employees) <= expected_count
    
    def cleanup_test_data(self):
        """Löscht alle erstellten Testdaten"""
        print("=== Cleaning up generated test data ===")
        
        deleted_allowances = 0
        deleted_employees = 0
        
        # Urlaubsansprüche löschen
        for allowance_id in self.created_vacation_allowances:
            try:
                response = requests.delete(
                    f"{self.base_url}/api/v1/vacation-allowances/{allowance_id}",
                    headers=self.get_headers()
                )
                if response.status_code in [200, 204]:
                    deleted_allowances += 1
            except Exception as e:
                print(f"Error deleting vacation allowance {allowance_id}: {e}")
        
        # Mitarbeiter löschen
        for employee_id in self.created_employees:
            try:
                response = requests.delete(
                    f"{self.base_url}/api/v1/employees/{employee_id}",
                    headers=self.get_headers()
                )
                if response.status_code in [200, 204]:
                    deleted_employees += 1
            except Exception as e:
                print(f"Error deleting employee {employee_id}: {e}")
        
        print(f"Cleanup completed: {deleted_employees}/{len(self.created_employees)} employees, {deleted_allowances}/{len(self.created_vacation_allowances)} vacation allowances deleted")
        
        # Listen zurücksetzen
        self.created_employees.clear()
        self.created_vacation_allowances.clear()
    
    def generate_full_dataset(self, employee_count: int = 40, vacation_entries_per_employee: int = 2, cleanup_before: bool = True):
        """Generiert kompletten Testdatensatz"""
        print("=== Starting Test Data Generation ===")
        
        # Authentifizierung
        if not self.authenticate():
            print("Authentication failed - cannot proceed")
            return False
        
        # Pre-Cleanup: Vorhandene Testdaten löschen
        if cleanup_before:
            if not self.cleanup_existing_test_data(preserve_standard_user=True):
                print("Pre-cleanup failed - continuing anyway")
        
        # Bundesländer laden
        self.load_federal_states()
        
        # Aktuelle Mitarbeiteranzahl vor der Generierung prüfen
        initial_employees = self.get_all_employees()
        print(f"Starting with {len(initial_employees)} existing employees")
        
        # Mitarbeiter erstellen
        employees = self.create_employees(employee_count)
        if not employees:
            print("No employees created - aborting")
            return False
        
        # Finale Mitarbeiteranzahl prüfen
        final_employees = self.get_all_employees()
        print(f"Total employees after generation: {len(final_employees)}")
        expected_total = len(initial_employees) + employee_count
        if len(final_employees) == expected_total:
            print(f"✅ Expected employee count reached: {len(final_employees)}")
        else:
            print(f"⚠️ Employee count mismatch: expected {expected_total}, got {len(final_employees)}")
        
        # Urlaubsansprüche erstellen
        employee_ids = [emp["id"] for emp in employees]
        vacation_allowances = self.create_vacation_allowances(
            employee_ids, 
            vacation_entries_per_employee
        )
        
        # Statistiken
        print("\n=== Test Data Generation Complete ===")
        print(f"Employees created: {len(employees)}")
        print(f"Vacation allowances created: {len(vacation_allowances)}")
        print(f"Total records: {len(employees) + len(vacation_allowances)}")
        
        # Testdaten-Info speichern
        test_info = {
            "generated_at": datetime.now().isoformat(),
            "employee_count": len(employees),
            "vacation_allowance_count": len(vacation_allowances),
            "employee_ids": self.created_employees,
            "vacation_allowance_ids": self.created_vacation_allowances
        }
        
        with open("tests/performance/test_data_info.json", "w") as f:
            json.dump(test_info, f, indent=2)
        
        return True

if __name__ == "__main__":
    generator = TestDataGenerator()
    
    # Kleine Testdaten für schnelle Tests
    success = generator.generate_full_dataset(
        employee_count=40,  # Für erste Tests (reduziert von 100)
        vacation_entries_per_employee=2
    )
    
    if success:
        print("\nTest data generation successful!")
        print("Run cleanup with: generator.cleanup_test_data()")
    else:
        print("\nTest data generation failed!")
