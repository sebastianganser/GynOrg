#!/usr/bin/env python3
"""
Testskript für Schulferien Sachsen-Anhalt
==========================================

Dieses Skript testet die ferien-api.de API und ruft die Schulferien 
für Sachsen-Anhalt (ST) für die Jahre 2026 und 2027 ab.

API-Dokumentation: https://ferien-api.de/
Bundesland-Code: ST (Sachsen-Anhalt)
"""

import requests
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import sys


class SchoolHolidayTester:
    """Klasse zum Testen der Schulferien-API für Sachsen-Anhalt"""
    
    BASE_URL = "https://ferien-api.de/api/v1/holidays"
    STATE_CODE = "ST"  # Sachsen-Anhalt
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'GynOrg-SchoolHoliday-Tester/1.0',
            'Accept': 'application/json'
        })
    
    def fetch_holidays(self, year: int) -> Optional[List[Dict]]:
        """
        Ruft Schulferien für ein bestimmtes Jahr ab
        
        Args:
            year: Das Jahr für das die Schulferien abgerufen werden sollen
            
        Returns:
            Liste der Schulferien oder None bei Fehler
        """
        url = f"{self.BASE_URL}/{self.STATE_CODE}/{year}"
        
        try:
            print(f"📡 API-Aufruf: {url}")
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            print(f"✅ Erfolgreich {len(data)} Schulferien für {year} abgerufen")
            return data
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Fehler beim API-Aufruf für {year}: {e}")
            return None
        except json.JSONDecodeError as e:
            print(f"❌ JSON-Parsing-Fehler für {year}: {e}")
            return None
    
    def parse_holiday_date(self, date_str: str) -> datetime:
        """
        Parst ISO8601-Datum aus der API-Response
        
        Args:
            date_str: Datum-String im Format "2026-04-14T22:00"
            
        Returns:
            datetime-Objekt
        """
        # Entferne Zeitzone-Info falls vorhanden und parse
        if date_str.endswith('Z'):
            date_str = date_str[:-1]
        elif '+' in date_str:
            date_str = date_str.split('+')[0]
        
        return datetime.fromisoformat(date_str)
    
    def calculate_duration(self, start_str: str, end_str: str) -> int:
        """
        Berechnet die Dauer der Ferien in Tagen
        
        Args:
            start_str: Start-Datum als String
            end_str: End-Datum als String
            
        Returns:
            Anzahl der Ferientage
        """
        start_date = self.parse_holiday_date(start_str)
        end_date = self.parse_holiday_date(end_str)
        
        # Berechne Differenz in Tagen
        duration = (end_date - start_date).days + 1
        return duration
    
    def format_holiday_name(self, name: str) -> str:
        """
        Formatiert den Feriename für bessere Lesbarkeit
        
        Args:
            name: Roher Ferienname aus der API
            
        Returns:
            Formatierter Ferienname
        """
        # Mapping für deutsche Feriename
        name_mapping = {
            'osterferien': 'Osterferien',
            'sommerferien': 'Sommerferien',
            'herbstferien': 'Herbstferien',
            'weihnachtsferien': 'Weihnachtsferien',
            'winterferien': 'Winterferien',
            'pfingstferien': 'Pfingstferien',
            'himmelfahrt': 'Himmelfahrt (verlängertes Wochenende)',
            'fronleichnam': 'Fronleichnam (verlängertes Wochenende)'
        }
        
        return name_mapping.get(name.lower(), name.title())
    
    def print_holiday_summary(self, holidays: List[Dict], year: int):
        """
        Gibt eine formatierte Übersicht der Schulferien aus
        
        Args:
            holidays: Liste der Schulferien
            year: Jahr
        """
        print(f"\n🎓 SCHULFERIEN SACHSEN-ANHALT {year}")
        print("=" * 50)
        
        if not holidays:
            print("❌ Keine Schulferien gefunden")
            return
        
        # Sortiere nach Startdatum
        sorted_holidays = sorted(holidays, key=lambda x: x['start'])
        
        total_days = 0
        
        for i, holiday in enumerate(sorted_holidays, 1):
            start_date = self.parse_holiday_date(holiday['start'])
            end_date = self.parse_holiday_date(holiday['end'])
            duration = self.calculate_duration(holiday['start'], holiday['end'])
            name = self.format_holiday_name(holiday['name'])
            
            total_days += duration
            
            print(f"{i:2d}. {name}")
            print(f"    📅 {start_date.strftime('%d.%m.%Y')} - {end_date.strftime('%d.%m.%Y')}")
            print(f"    ⏱️  {duration} Tage")
            print(f"    🔗 Slug: {holiday.get('slug', 'N/A')}")
            print()
        
        print(f"📊 ZUSAMMENFASSUNG {year}:")
        print(f"   • Anzahl Ferienperioden: {len(sorted_holidays)}")
        print(f"   • Gesamte Ferientage: {total_days}")
        print(f"   • Bundesland: Sachsen-Anhalt (ST)")
        print()
    
    def test_api_connectivity(self) -> bool:
        """
        Testet die grundlegende API-Konnektivität
        
        Returns:
            True wenn API erreichbar ist
        """
        try:
            # Test mit einem einfachen Request
            response = self.session.get(f"{self.BASE_URL}/{self.STATE_CODE}", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def run_test(self, years: List[int] = [2026, 2027]):
        """
        Führt den kompletten Test für die angegebenen Jahre durch
        
        Args:
            years: Liste der zu testenden Jahre
        """
        print("🚀 SCHULFERIEN-API TEST GESTARTET")
        print("=" * 50)
        print(f"🎯 Ziel: Schulferien für Sachsen-Anhalt")
        print(f"📅 Jahre: {', '.join(map(str, years))}")
        print(f"🌐 API: {self.BASE_URL}")
        print()
        
        # API-Konnektivität testen
        print("🔍 Teste API-Konnektivität...")
        if not self.test_api_connectivity():
            print("❌ API nicht erreichbar! Test abgebrochen.")
            return False
        print("✅ API ist erreichbar")
        print()
        
        all_holidays = {}
        success_count = 0
        
        # Für jedes Jahr die Daten abrufen
        for year in years:
            holidays = self.fetch_holidays(year)
            if holidays is not None:
                all_holidays[year] = holidays
                success_count += 1
                self.print_holiday_summary(holidays, year)
            else:
                print(f"❌ Fehler beim Abrufen der Daten für {year}")
                print()
        
        # Gesamtstatistik
        print("📈 GESAMTSTATISTIK")
        print("=" * 50)
        print(f"✅ Erfolgreich: {success_count}/{len(years)} Jahre")
        
        if all_holidays:
            total_periods = sum(len(holidays) for holidays in all_holidays.values())
            total_days = 0
            
            for year, holidays in all_holidays.items():
                for holiday in holidays:
                    duration = self.calculate_duration(holiday['start'], holiday['end'])
                    total_days += duration
            
            print(f"📊 Gesamte Ferienperioden: {total_periods}")
            print(f"📊 Gesamte Ferientage: {total_days}")
            
            # Ferienarten-Analyse
            holiday_types = {}
            for holidays in all_holidays.values():
                for holiday in holidays:
                    name = self.format_holiday_name(holiday['name'])
                    holiday_types[name] = holiday_types.get(name, 0) + 1
            
            print(f"\n🎯 FERIENARTEN-VERTEILUNG:")
            for name, count in sorted(holiday_types.items()):
                print(f"   • {name}: {count}x")
        
        print(f"\n🎉 Test abgeschlossen!")
        return success_count == len(years)


def main():
    """Hauptfunktion"""
    print("🎓 SCHULFERIEN-TESTER FÜR SACHSEN-ANHALT")
    print("Version 1.0 - GynOrg Integration Test")
    print("=" * 60)
    print()
    
    tester = SchoolHolidayTester()
    
    # Test für 2026 und 2027 durchführen
    success = tester.run_test([2026, 2027])
    
    if success:
        print("✅ Alle Tests erfolgreich!")
        sys.exit(0)
    else:
        print("❌ Einige Tests sind fehlgeschlagen!")
        sys.exit(1)


if __name__ == "__main__":
    main()
