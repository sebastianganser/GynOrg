#!/usr/bin/env python3
"""
Test für verfügbare Jahre in der Schulferien-API
"""

from test_schulferien_sachsen_anhalt import SchoolHolidayTester

def main():
    tester = SchoolHolidayTester()
    print('🔍 Teste verschiedene Jahre um verfügbare Daten zu finden...')
    print()

    # Teste verschiedene Jahre
    for year in [2023, 2024, 2025, 2026]:
        print(f'📅 Teste Jahr {year}:')
        holidays = tester.fetch_holidays(year)
        if holidays and len(holidays) > 0:
            print(f'   ✅ {len(holidays)} Schulferien gefunden')
            for holiday in holidays[:3]:  # Zeige erste 3
                name = holiday.get('name', 'Unbekannt')
                start = holiday.get('start', '')[:10]
                end = holiday.get('end', '')[:10]
                print(f'   - {name}: {start} bis {end}')
            if len(holidays) > 3:
                print(f'   ... und {len(holidays)-3} weitere')
        else:
            print(f'   ❌ Keine Daten verfügbar')
        print()

if __name__ == "__main__":
    main()
