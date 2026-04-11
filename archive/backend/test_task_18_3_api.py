#!/usr/bin/env python3
"""
Test-Script für Task 18.3: API Endpoint für verfügbare Jahre mit detaillierten Informationen
"""

import asyncio
import sys
import os
import requests
import json
from datetime import datetime

# Füge das Backend-Verzeichnis zum Python-Pfad hinzu
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

# Base URL für die API (anpassen falls nötig)
BASE_URL = "http://localhost:8000/api/v1/holidays"


def test_api_endpoint(endpoint: str, description: str, params: dict = None):
    """Testet einen API-Endpoint und gibt das Ergebnis aus"""
    print(f"\n🧪 Test: {description}")
    print(f"   Endpoint: {endpoint}")
    
    try:
        url = f"{BASE_URL}{endpoint}"
        response = requests.get(url, params=params, timeout=10)
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Erfolgreich")
            
            # Zeige relevante Daten
            if "available_years" in data:
                years = data["available_years"]
                print(f"   📊 {len(years)} Jahre gefunden")
                if years:
                    complete_years = sum(1 for year in years if year.get("is_complete", False))
                    print(f"   📈 {complete_years} vollständige Jahre")
                    print(f"   📅 Jahresbereich: {years[0]['year']}-{years[-1]['year']}")
            
            elif "years" in data:
                years = data["years"]
                print(f"   📊 {len(years)} Jahre: {years}")
            
            elif "year" in data:
                year_data = data
                print(f"   📅 Jahr {year_data['year']}: {year_data['holiday_count']} Feiertage")
                print(f"   ✅ Vollständig: {year_data.get('is_complete', 'Unbekannt')}")
            
            return data
        else:
            print(f"   ❌ Fehler: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   💬 Details: {error_data.get('detail', 'Keine Details')}")
            except:
                print(f"   💬 Response: {response.text[:200]}...")
            return None
            
    except requests.exceptions.ConnectionError:
        print(f"   ❌ Verbindungsfehler: Server nicht erreichbar")
        print(f"   💡 Starte den Server mit: cd backend && python -m uvicorn app.main:app --reload")
        return None
    except Exception as e:
        print(f"   ❌ Fehler: {str(e)}")
        return None


def test_all_endpoints():
    """Testet alle neuen und bestehenden Endpoints"""
    print("🚀 Teste Task 18.3 API-Endpoints...")
    
    # Test 1: Bestehender /years Endpoint (Backward-Kompatibilität)
    test_api_endpoint(
        "/years",
        "Bestehender /years Endpoint (Backward-Kompatibilität)"
    )
    
    # Test 2: Neuer /years/detailed Endpoint (Standard)
    detailed_data = test_api_endpoint(
        "/years/detailed",
        "Neuer /years/detailed Endpoint (alle Jahre)"
    )
    
    # Test 3: /years/detailed mit Filter (nur vollständige Jahre)
    test_api_endpoint(
        "/years/detailed",
        "Detaillierte Jahre (nur vollständige)",
        params={"include_incomplete": False}
    )
    
    # Test 4: /years/detailed mit Bundesland-Filter
    test_api_endpoint(
        "/years/detailed",
        "Detaillierte Jahre (nur Bayern)",
        params={"federal_state": "BY"}
    )
    
    # Test 5: Jahr-Status für spezifisches Jahr
    current_year = datetime.now().year
    test_api_endpoint(
        f"/years/{current_year}/status",
        f"Jahr-Status für {current_year}"
    )
    
    # Test 6: Jahr-Status für ein Jahr mit Daten (falls verfügbar)
    if detailed_data and detailed_data.get("available_years"):
        test_year = detailed_data["available_years"][0]["year"]
        test_api_endpoint(
            f"/years/{test_year}/status",
            f"Jahr-Status für {test_year} (mit Daten)"
        )
    
    # Test 7: Jahr-Status für Jahr ohne Daten
    test_api_endpoint(
        "/years/1999/status",
        "Jahr-Status für 1999 (ohne Daten - sollte 404 geben)"
    )
    
    # Test 8: Ungültiges Jahr
    test_api_endpoint(
        "/years/1800/status",
        "Jahr-Status für ungültiges Jahr (sollte 400 geben)"
    )
    
    # Test 9: Ungültiges Bundesland
    test_api_endpoint(
        "/years/detailed",
        "Detaillierte Jahre mit ungültigem Bundesland",
        params={"federal_state": "INVALID"}
    )


def analyze_detailed_response(data):
    """Analysiert die detaillierte Response und zeigt Insights"""
    if not data or "available_years" not in data:
        return
    
    print("\n📊 Detaillierte Analyse der API-Response:")
    
    years = data["available_years"]
    summary = data.get("summary", {})
    
    print(f"   📅 Verfügbare Jahre: {len(years)}")
    print(f"   ✅ Vollständige Jahre: {summary.get('complete_years', 0)}")
    print(f"   ⚠️ Unvollständige Jahre: {summary.get('incomplete_years', 0)}")
    print(f"   🎯 Gesamte Feiertage: {summary.get('total_holidays', 0)}")
    print(f"   📈 Durchschnitt pro Jahr: {summary.get('average_holidays_per_year', 0):.1f}")
    
    if years:
        print(f"\n   📋 Jahr-Details (erste 3):")
        for year_data in years[:3]:
            year = year_data["year"]
            complete = "✅" if year_data["is_complete"] else "⚠️"
            count = year_data["holiday_count"]
            coverage = year_data["coverage_percentage"]
            print(f"      {complete} {year}: {count} Feiertage, {coverage:.0f}% Abdeckung")


def test_performance():
    """Testet die Performance der neuen Endpoints"""
    print("\n⚡ Performance-Test:")
    
    import time
    
    endpoints = [
        ("/years", "Einfacher /years"),
        ("/years/detailed", "Detaillierter /years/detailed"),
        ("/years/detailed?include_incomplete=false", "Gefiltert (nur vollständig)"),
    ]
    
    for endpoint, description in endpoints:
        start_time = time.time()
        response = requests.get(f"{BASE_URL}{endpoint}", timeout=10)
        end_time = time.time()
        
        duration = (end_time - start_time) * 1000  # in ms
        status = "✅" if response.status_code == 200 else "❌"
        
        print(f"   {status} {description}: {duration:.0f}ms")


if __name__ == "__main__":
    print("🧪 Task 18.3 API-Tests starten...")
    
    # Haupttests
    test_all_endpoints()
    
    # Detaillierte Analyse
    print("\n🔍 Führe detaillierte Analyse durch...")
    detailed_response = test_api_endpoint("/years/detailed", "Detaillierte Analyse")
    if detailed_response:
        analyze_detailed_response(detailed_response)
    
    # Performance-Tests
    try:
        test_performance()
    except Exception as e:
        print(f"⚠️ Performance-Test übersprungen: {str(e)}")
    
    print("\n✨ Task 18.3 API-Tests abgeschlossen!")
    print("\n💡 Nächste Schritte:")
    print("   - Frontend useHolidays Hook anpassen (Task 18.4)")
    print("   - AbsenceCalendar Jahr-Navigation implementieren (Task 18.5)")
    print("   - Absence Calculation Services erweitern (Task 18.6)")
