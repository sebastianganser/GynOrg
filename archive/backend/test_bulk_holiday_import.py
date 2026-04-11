#!/usr/bin/env python3
"""
Test-Script für die neuen Bulk-Import Holiday-Funktionen
"""

import asyncio
import sys
import os
from datetime import datetime

# Füge das Backend-Verzeichnis zum Python-Pfad hinzu
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from app.core.database import get_session
from app.services.holiday_service import HolidayService
from app.models.federal_state import FederalState


async def test_bulk_import():
    """Testet die Bulk-Import-Funktionalität"""
    print("🧪 Teste Bulk-Import Holiday-Funktionen...")
    
    # Session erstellen
    session = next(get_session())
    holiday_service = HolidayService(session)
    
    try:
        # Test 1: Bulk-Import für einen kleinen Bereich (2024-2025)
        print("\n📅 Test 1: Bulk-Import für 2024-2025...")
        start_time = datetime.now()
        
        result = holiday_service.bulk_import_holidays_range(2024, 2025)
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        print(f"✅ Bulk-Import abgeschlossen in {duration:.2f} Sekunden")
        print(f"   - Importiert: {result['total_imported']}")
        print(f"   - Übersprungen: {result['total_skipped']}")
        print(f"   - Fehler: {result['total_errors']}")
        print(f"   - Jahre verarbeitet: {result['years_processed']}")
        
        # Test 2: Prüfe fehlende Jahre
        print("\n🔍 Test 2: Prüfe fehlende Jahre für 2020-2030...")
        missing_years = holiday_service.get_missing_years(2020, 2030)
        print(f"   Fehlende Jahre: {missing_years}")
        
        # Test 3: Ensure-Range für 2020-2030
        if missing_years:
            print(f"\n🔧 Test 3: Ensure-Range für fehlende Jahre...")
            start_time = datetime.now()
            
            ensure_result = holiday_service.import_missing_years(missing_years)
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            print(f"✅ Ensure-Range abgeschlossen in {duration:.2f} Sekunden")
            print(f"   - Importiert: {ensure_result['total_imported']}")
            print(f"   - Jahre verarbeitet: {ensure_result['years_processed']}")
        else:
            print("✅ Alle Jahre bereits vollständig vorhanden!")
        
        # Test 4: Statistiken anzeigen
        print("\n📊 Test 4: Statistiken...")
        from sqlmodel import select, func
        from app.models.holiday import Holiday
        
        # Gesamtanzahl Feiertage
        total_query = select(func.count(Holiday.id))
        total_holidays = session.exec(total_query).first()
        
        # Jahre mit Daten
        years_query = select(Holiday.year).distinct().order_by(Holiday.year)
        years = session.exec(years_query).all()
        
        print(f"   - Gesamte Feiertage in DB: {total_holidays}")
        print(f"   - Jahre mit Daten: {min(years) if years else 'Keine'} - {max(years) if years else 'Keine'}")
        print(f"   - Anzahl Jahre: {len(years)}")
        
        # Test 5: Datumsbereich-Abfrage
        print("\n📅 Test 5: Datumsbereich-Abfrage...")
        from datetime import date
        
        holidays_2025 = holiday_service.get_holidays_in_date_range(
            date(2025, 1, 1), 
            date(2025, 12, 31),
            FederalState.ST  # Sachsen-Anhalt
        )
        
        print(f"   - Feiertage 2025 in Sachsen-Anhalt: {len(holidays_2025)}")
        for holiday in holidays_2025[:5]:  # Zeige erste 5
            print(f"     • {holiday.date}: {holiday.name}")
        
        print("\n🎉 Alle Tests erfolgreich abgeschlossen!")
        
    except Exception as e:
        print(f"❌ Fehler beim Testen: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        session.close()


def test_expected_holiday_counts():
    """Testet die erwarteten Feiertage-Anzahlen pro Bundesland"""
    print("\n🧮 Teste erwartete Feiertage-Anzahlen...")
    
    session = next(get_session())
    holiday_service = HolidayService(session)
    
    try:
        for state in FederalState:
            expected = holiday_service._get_expected_state_holidays_count(state)
            print(f"   {state.name} ({state.value}): {expected} spezifische Feiertage")
    
    finally:
        session.close()


if __name__ == "__main__":
    print("🚀 Starte Holiday Bulk-Import Tests...")
    
    # Teste erwartete Anzahlen
    test_expected_holiday_counts()
    
    # Teste Bulk-Import
    asyncio.run(test_bulk_import())
    
    print("\n✨ Test-Script abgeschlossen!")
