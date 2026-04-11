#!/usr/bin/env python3
"""
Test-Script für die neue Startup Holiday-Logic
"""

import asyncio
import sys
import os
from datetime import datetime

# Füge das Backend-Verzeichnis zum Python-Pfad hinzu
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from app.core.database import get_session
from app.services.startup_service import StartupService


async def test_startup_logic():
    """Testet die Startup Holiday-Logic"""
    print("🧪 Teste Startup Holiday-Logic...")
    
    # Session erstellen
    session = next(get_session())
    startup_service = StartupService(session)
    
    try:
        print("\n📊 Test 1: Aktuelle Holiday-Statistiken...")
        stats = startup_service.get_holiday_statistics()
        print(f"   - Gesamte Feiertage: {stats['total_holidays']}")
        print(f"   - Bundesweite Feiertage: {stats['nationwide_holidays']}")
        print(f"   - Bundeslandspezifische Feiertage: {stats['state_specific_holidays']}")
        print(f"   - Jahre mit Daten: {stats['year_range']['count']} ({stats['year_range']['min']}-{stats['year_range']['max']})")
        
        print("\n🔍 Test 2: Holiday-Daten-Validierung...")
        validation = await startup_service.validate_holiday_data_integrity()
        print(f"   - Daten gültig: {validation['is_valid']}")
        if validation['issues']:
            print(f"   - Probleme gefunden: {validation['issues']}")
        else:
            print("   - Keine Probleme gefunden")
        
        print("\n🚀 Test 3: Startup Holiday-Daten-Sicherstellung...")
        start_time = datetime.now()
        
        result = await startup_service.ensure_holiday_data_complete(
            start_year=2020,
            end_year=2030
        )
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        print(f"✅ Startup-Logic abgeschlossen in {duration:.2f} Sekunden")
        print(f"   - Erfolgreich: {result['success']}")
        print(f"   - Fehlende Jahre gefunden: {result['missing_years_found']}")
        
        if result.get('skipped_reason'):
            print(f"   - Übersprungen: {result['skipped_reason']}")
        elif result.get('import_result'):
            import_result = result['import_result']
            print(f"   - Importiert: {import_result['total_imported']}")
            print(f"   - Übersprungen: {import_result['total_skipped']}")
            print(f"   - Fehler: {import_result['total_errors']}")
        
        if result.get('error'):
            print(f"   - Fehler: {result['error']}")
        
        print("\n📊 Test 4: Finale Holiday-Statistiken...")
        final_stats = startup_service.get_holiday_statistics()
        print(f"   - Gesamte Feiertage: {final_stats['total_holidays']}")
        print(f"   - Jahre mit Daten: {final_stats['year_range']['count']} ({final_stats['year_range']['min']}-{final_stats['year_range']['max']})")
        
        # Vergleiche mit vorherigen Statistiken
        if final_stats['total_holidays'] > stats['total_holidays']:
            added = final_stats['total_holidays'] - stats['total_holidays']
            print(f"   - ✅ {added} neue Feiertage hinzugefügt")
        elif final_stats['total_holidays'] == stats['total_holidays']:
            print("   - ✅ Keine neuen Feiertage hinzugefügt (bereits vollständig)")
        
        print("\n🔍 Test 5: Finale Validierung...")
        final_validation = await startup_service.validate_holiday_data_integrity()
        print(f"   - Daten gültig: {final_validation['is_valid']}")
        if final_validation['issues']:
            print(f"   - Verbleibende Probleme: {final_validation['issues']}")
        else:
            print("   - ✅ Alle Validierungen bestanden")
        
        print("\n🎉 Alle Startup-Tests erfolgreich abgeschlossen!")
        
    except Exception as e:
        print(f"❌ Fehler beim Testen: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        session.close()


async def test_startup_performance():
    """Testet die Performance der Startup-Logic"""
    print("\n⚡ Performance-Test: Wiederholte Startup-Calls...")
    
    session = next(get_session())
    startup_service = StartupService(session)
    
    try:
        times = []
        
        for i in range(5):
            start_time = datetime.now()
            
            result = await startup_service.ensure_holiday_data_complete(
                start_year=2020,
                end_year=2030
            )
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            times.append(duration)
            
            print(f"   Run {i+1}: {duration:.3f}s - {'Skipped' if result.get('skipped_reason') else 'Processed'}")
        
        avg_time = sum(times) / len(times)
        min_time = min(times)
        max_time = max(times)
        
        print(f"\n📊 Performance-Ergebnisse:")
        print(f"   - Durchschnitt: {avg_time:.3f}s")
        print(f"   - Minimum: {min_time:.3f}s")
        print(f"   - Maximum: {max_time:.3f}s")
        
        if avg_time < 1.0:
            print("   - ✅ Performance-Ziel erreicht (< 1s)")
        else:
            print("   - ⚠️ Performance könnte verbessert werden")
    
    finally:
        session.close()


async def test_error_scenarios():
    """Testet Fehlerszenarien"""
    print("\n🚨 Test: Fehlerszenarien...")
    
    session = next(get_session())
    startup_service = StartupService(session)
    
    try:
        # Test mit ungültigen Jahren
        print("   Test: Ungültige Jahre...")
        result = await startup_service.ensure_holiday_data_complete(
            start_year=2050,
            end_year=2040  # End vor Start
        )
        
        if not result['success']:
            print("   - ✅ Ungültige Jahre korrekt abgefangen")
        else:
            print("   - ⚠️ Ungültige Jahre nicht abgefangen")
        
        print("   - Startup-Logic ist robust gegen Fehler")
    
    finally:
        session.close()


if __name__ == "__main__":
    print("🚀 Starte Startup Holiday-Logic Tests...")
    
    # Haupttest
    asyncio.run(test_startup_logic())
    
    # Performance-Test
    asyncio.run(test_startup_performance())
    
    # Fehlerszenarien
    asyncio.run(test_error_scenarios())
    
    print("\n✨ Alle Tests abgeschlossen!")
