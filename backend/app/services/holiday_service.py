from typing import List, Dict, Optional, Any
from datetime import date, datetime, timedelta
from calendar import monthrange
from sqlmodel import Session, select
from ..models.holiday import Holiday, HolidayCreate, HolidayFilter, HolidayType
from ..models.federal_state import FederalState
from ..core.database import get_session


class GermanHolidayCalculator:
    """Berechnet deutsche Feiertage für ein gegebenes Jahr"""
    
    @staticmethod
    def calculate_easter(year: int) -> date:
        """Berechnet das Osterdatum nach dem Gregorianischen Kalender"""
        # Algorithmus von Carl Friedrich Gauss
        a = year % 19
        b = year // 100
        c = year % 100
        d = b // 4
        e = b % 4
        f = (b + 8) // 25
        g = (b - f + 1) // 3
        h = (19 * a + b - d - g + 15) % 30
        i = c // 4
        k = c % 4
        l = (32 + 2 * e + 2 * i - h - k) % 7
        m = (a + 11 * h + 22 * l) // 451
        month = (h + l - 7 * m + 114) // 31
        day = ((h + l - 7 * m + 114) % 31) + 1
        return date(year, month, day)
    
    @classmethod
    def get_nationwide_holidays(cls, year: int) -> List[Dict]:
        """Gibt alle bundesweiten Feiertage für ein Jahr zurück"""
        easter = cls.calculate_easter(year)
        
        holidays = [
            {"name": "Neujahr", "date": date(year, 1, 1), "description": "Neujahrstag"},
            {"name": "Karfreitag", "date": easter - timedelta(days=2), "description": "Karfreitag vor Ostern"},
            {"name": "Ostermontag", "date": easter + timedelta(days=1), "description": "Ostermontag"},
            {"name": "Tag der Arbeit", "date": date(year, 5, 1), "description": "Maifeiertag"},
            {"name": "Christi Himmelfahrt", "date": easter + timedelta(days=39), "description": "39 Tage nach Ostern"},
            {"name": "Pfingstmontag", "date": easter + timedelta(days=50), "description": "50 Tage nach Ostern"},
            {"name": "Tag der Deutschen Einheit", "date": date(year, 10, 3), "description": "Nationalfeiertag"},
            {"name": "1. Weihnachtsfeiertag", "date": date(year, 12, 25), "description": "Weihnachten"},
            {"name": "2. Weihnachtsfeiertag", "date": date(year, 12, 26), "description": "Zweiter Weihnachtsfeiertag"},
        ]
        
        return holidays
    
    @classmethod
    def get_state_specific_holidays(cls, year: int, federal_state: FederalState) -> List[Dict]:
        """Gibt bundeslandspezifische Feiertage zurück"""
        easter = cls.calculate_easter(year)
        holidays = []
        
        # Heilige Drei Könige (BW, BY, ST)
        if federal_state in [FederalState.BADEN_WUERTTEMBERG, FederalState.BAYERN, FederalState.SACHSEN_ANHALT]:
            holidays.append({
                "name": "Heilige Drei Könige",
                "date": date(year, 1, 6),
                "description": "Epiphanias"
            })
        
        # Fronleichnam (BW, BY, HE, NW, RP, SL, teilweise SN, TH)
        if federal_state in [FederalState.BADEN_WUERTTEMBERG, FederalState.BAYERN, FederalState.HESSEN,
                           FederalState.NORDRHEIN_WESTFALEN, FederalState.RHEINLAND_PFALZ, FederalState.SAARLAND]:
            holidays.append({
                "name": "Fronleichnam",
                "date": easter + timedelta(days=60),
                "description": "60 Tage nach Ostern"
            })
        
        # Mariä Himmelfahrt (BY, SL)
        if federal_state in [FederalState.BAYERN, FederalState.SAARLAND]:
            holidays.append({
                "name": "Mariä Himmelfahrt",
                "date": date(year, 8, 15),
                "description": "Mariä Himmelfahrt"
            })
        
        # Reformationstag (BB, MV, SN, ST, TH, HB, HH, NI, SH)
        if federal_state in [FederalState.BRANDENBURG, FederalState.MECKLENBURG_VORPOMMERN, FederalState.SACHSEN,
                           FederalState.SACHSEN_ANHALT, FederalState.THUERINGEN, FederalState.BREMEN,
                           FederalState.HAMBURG, FederalState.NIEDERSACHSEN, FederalState.SCHLESWIG_HOLSTEIN]:
            holidays.append({
                "name": "Reformationstag",
                "date": date(year, 10, 31),
                "description": "Reformationstag"
            })
        
        # Allerheiligen (BW, BY, NW, RP, SL)
        if federal_state in [FederalState.BADEN_WUERTTEMBERG, FederalState.BAYERN, FederalState.NORDRHEIN_WESTFALEN,
                           FederalState.RHEINLAND_PFALZ, FederalState.SAARLAND]:
            holidays.append({
                "name": "Allerheiligen",
                "date": date(year, 11, 1),
                "description": "Allerheiligen"
            })
        
        # Buß- und Bettag (nur SN)
        if federal_state == FederalState.SACHSEN:
            # Buß- und Bettag: Mittwoch vor dem 23. November
            nov_23 = date(year, 11, 23)
            days_to_wednesday = (nov_23.weekday() - 2) % 7
            buss_und_bettag = nov_23 - timedelta(days=days_to_wednesday)
            holidays.append({
                "name": "Buß- und Bettag",
                "date": buss_und_bettag,
                "description": "Buß- und Bettag"
            })
        
        # Weltfrauentag (BE)
        if federal_state == FederalState.BERLIN:
            holidays.append({
                "name": "Internationaler Frauentag",
                "date": date(year, 3, 8),
                "description": "Weltfrauentag"
            })
        
        # Weltkindertag (TH)
        if federal_state == FederalState.THUERINGEN:
            holidays.append({
                "name": "Weltkindertag",
                "date": date(year, 9, 20),
                "description": "Weltkindertag"
            })
        
        return holidays
    
    @classmethod
    def get_all_holidays(cls, year: int, federal_state: Optional[FederalState] = None) -> List[Dict]:
        """Gibt alle Feiertage für ein Jahr zurück (bundesweit + bundeslandspezifisch)"""
        holidays = cls.get_nationwide_holidays(year)
        
        if federal_state:
            state_holidays = cls.get_state_specific_holidays(year, federal_state)
            holidays.extend(state_holidays)
        
        # Nach Datum sortieren
        holidays.sort(key=lambda x: x["date"])
        return holidays


class HolidayService:
    """Service für die Verwaltung von Feiertagen"""
    
    def __init__(self, session: Session):
        self.session = session
    
    def import_holidays_for_year(self, year: int, federal_states: Optional[List[FederalState]] = None) -> Dict[str, int]:
        """Importiert Feiertage für ein Jahr"""
        result = {"imported": 0, "skipped": 0, "errors": 0}
        
        try:
            # Bundesweite Feiertage importieren
            nationwide_holidays = GermanHolidayCalculator.get_nationwide_holidays(year)
            for holiday_data in nationwide_holidays:
                if not self._holiday_exists(holiday_data["date"], None):
                    holiday = Holiday(
                        name=holiday_data["name"],
                        date=holiday_data["date"],
                        federal_state=None,
                        is_nationwide=True,
                        year=year,
                        notes=holiday_data["description"]
                    )
                    self.session.add(holiday)
                    result["imported"] += 1
                else:
                    result["skipped"] += 1
            
            # Bundeslandspezifische Feiertage importieren
            states_to_import = federal_states or list(FederalState)
            for state in states_to_import:
                state_holidays = GermanHolidayCalculator.get_state_specific_holidays(year, state)
                for holiday_data in state_holidays:
                    if not self._holiday_exists(holiday_data["date"], state):
                        holiday = Holiday(
                            name=holiday_data["name"],
                            date=holiday_data["date"],
                            federal_state=state,
                            is_nationwide=False,
                            year=year,
                            notes=holiday_data["description"]
                        )
                        self.session.add(holiday)
                        result["imported"] += 1
                    else:
                        result["skipped"] += 1
            
            self.session.commit()
            
        except Exception as e:
            self.session.rollback()
            result["errors"] += 1
            raise e
        
        return result
    
    def get_holidays(self, filter_params: HolidayFilter) -> List[Holiday]:
        """Gibt Feiertage basierend auf Filterparametern zurück"""
        query = select(Holiday)
        
        if filter_params.year:
            query = query.where(Holiday.year == filter_params.year)
        
        if filter_params.month:
            # Filtere nach Monat
            start_date = date(filter_params.year or datetime.now().year, filter_params.month, 1)
            _, last_day = monthrange(start_date.year, start_date.month)
            end_date = date(start_date.year, start_date.month, last_day)
            query = query.where(Holiday.date >= start_date, Holiday.date <= end_date)
        
        if filter_params.federal_state:
            # Bundeslandspezifische Feiertage + bundesweite (wenn gewünscht)
            if filter_params.include_nationwide:
                query = query.where(
                    (Holiday.federal_state == filter_params.federal_state) |
                    (Holiday.is_nationwide == True)
                )
            else:
                query = query.where(Holiday.federal_state == filter_params.federal_state)
        elif not filter_params.include_nationwide:
            # Nur bundeslandspezifische Feiertage (ohne bundesweite)
            query = query.where(Holiday.is_nationwide == False)
        
        # Filter nach HolidayType (PUBLIC_HOLIDAY vs SCHOOL_VACATION)
        if filter_params.holiday_type:
            query = query.where(Holiday.holiday_type == filter_params.holiday_type)
            
        # Filter nach SchoolVacationType (WINTER, EASTER, etc.)
        if filter_params.school_vacation_type:
            query = query.where(Holiday.school_vacation_type == filter_params.school_vacation_type)
        
        query = query.order_by(Holiday.date)
        return self.session.exec(query).all()
    
    def get_upcoming_holidays(self, federal_state: Optional[FederalState] = None, days: int = 30) -> List[Holiday]:
        """Gibt kommende Feiertage zurück"""
        today = date.today()
        end_date = today + timedelta(days=days)
        
        query = select(Holiday).where(
            Holiday.date >= today,
            Holiday.date <= end_date
        )
        
        if federal_state:
            query = query.where(
                (Holiday.federal_state == federal_state) |
                (Holiday.is_nationwide == True)
            )
        
        query = query.order_by(Holiday.date)
        return self.session.exec(query).all()
    
    def is_holiday(self, check_date: date, federal_state: Optional[FederalState] = None) -> Optional[Holiday]:
        """Prüft ob ein Datum ein Feiertag ist"""
        query = select(Holiday).where(Holiday.date == check_date)
        
        if federal_state:
            query = query.where(
                (Holiday.federal_state == federal_state) |
                (Holiday.is_nationwide == True)
            )
        
        return self.session.exec(query).first()
    
    def _holiday_exists(self, holiday_date: date, federal_state: Optional[FederalState]) -> bool:
        """Prüft ob ein Feiertag bereits existiert"""
        if federal_state is None:
            # Bundesweite Feiertage: federal_state IS NULL
            query = select(Holiday).where(
                Holiday.date == holiday_date,
                Holiday.federal_state.is_(None)
            )
        else:
            # Bundeslandspezifische Feiertage: federal_state = specific_state
            query = select(Holiday).where(
                Holiday.date == holiday_date,
                Holiday.federal_state == federal_state
            )
        return self.session.exec(query).first() is not None
    
    def delete_holidays_for_year(self, year: int) -> int:
        """Löscht alle Feiertage für ein Jahr"""
        query = select(Holiday).where(Holiday.year == year)
        holidays = self.session.exec(query).all()
        count = len(holidays)
        
        for holiday in holidays:
            self.session.delete(holiday)
        
        self.session.commit()
        return count

    def bulk_import_holidays_range(self, start_year: int, end_year: int, federal_states: Optional[List[FederalState]] = None) -> Dict[str, int]:
        """Importiert Feiertage für einen Jahresbereich (Bulk-Import)"""
        result = {
            "total_imported": 0,
            "total_skipped": 0,
            "total_errors": 0,
            "years_processed": 0,
            "details": {}
        }
        
        states_to_import = federal_states or list(FederalState)
        
        try:
            for year in range(start_year, end_year + 1):
                try:
                    year_result = self.import_holidays_for_year(year, states_to_import)
                    result["total_imported"] += year_result["imported"]
                    result["total_skipped"] += year_result["skipped"]
                    result["total_errors"] += year_result["errors"]
                    result["years_processed"] += 1
                    result["details"][year] = year_result
                    
                    # Commit nach jedem Jahr für bessere Fehlerbehandlung
                    self.session.commit()
                    
                except Exception as e:
                    # Rollback für das aktuelle Jahr, aber weiter mit nächstem Jahr
                    self.session.rollback()
                    result["total_errors"] += 1
                    result["details"][year] = {
                        "imported": 0,
                        "skipped": 0,
                        "errors": 1,
                        "error_message": str(e)
                    }
                    continue
            
        except Exception as e:
            self.session.rollback()
            raise e
        
        return result

    def get_missing_years(self, start_year: int, end_year: int, federal_states: Optional[List[FederalState]] = None) -> List[int]:
        """Ermittelt Jahre, für die noch keine vollständigen Feiertage-Daten vorhanden sind"""
        missing_years = []
        states_to_check = federal_states or list(FederalState)
        
        for year in range(start_year, end_year + 1):
            if not self._is_year_complete(year, states_to_check):
                missing_years.append(year)
        
        return missing_years

    def import_missing_years(self, missing_years: List[int], federal_states: Optional[List[FederalState]] = None) -> Dict[str, int]:
        """Importiert Feiertage nur für fehlende Jahre"""
        result = {
            "total_imported": 0,
            "total_skipped": 0,
            "total_errors": 0,
            "years_processed": 0,
            "details": {}
        }
        
        states_to_import = federal_states or list(FederalState)
        
        try:
            for year in missing_years:
                try:
                    year_result = self.import_holidays_for_year(year, states_to_import)
                    result["total_imported"] += year_result["imported"]
                    result["total_skipped"] += year_result["skipped"]
                    result["total_errors"] += year_result["errors"]
                    result["years_processed"] += 1
                    result["details"][year] = year_result
                    
                    # Commit nach jedem Jahr
                    self.session.commit()
                    
                except Exception as e:
                    self.session.rollback()
                    result["total_errors"] += 1
                    result["details"][year] = {
                        "imported": 0,
                        "skipped": 0,
                        "errors": 1,
                        "error_message": str(e)
                    }
                    continue
            
        except Exception as e:
            self.session.rollback()
            raise e
        
        return result

    def get_missing_school_vacation_years(self, start_year: int, end_year: int, federal_states: Optional[List[FederalState]] = None) -> List[int]:
        """Ermittelt Jahre, für die noch keine Schulferien vorhanden sind"""
        missing_years = []
        states_to_check = federal_states or list(FederalState)
        
        for year in range(start_year, end_year + 1):
            if not self._has_school_vacations_for_year(year, states_to_check):
                missing_years.append(year)
        
        return missing_years

    def _has_school_vacations_for_year(self, year: int, federal_states: List[FederalState]) -> bool:
        """Prüft ob ein Jahr Schulferien-Daten für alle relevanten Bundesländer hat"""
        for state in federal_states:
            vacation_count = self.session.exec(
                select(Holiday).where(
                    Holiday.year == year,
                    Holiday.federal_state == state,
                    Holiday.holiday_type == HolidayType.SCHOOL_VACATION
                )
            ).all()
            
            # Ein Jahr gilt als unvollständig bzgl. Schulferien, wenn für ein Bundesland garkeine Ferien existieren
            if len(vacation_count) == 0:
                return False
                
        return True


    def _is_year_complete(self, year: int, federal_states: List[FederalState]) -> bool:
        """Prüft ob ein Jahr vollständige Feiertage-Daten hat"""
        # Prüfe bundesweite Feiertage
        nationwide_count = self.session.exec(
            select(Holiday).where(
                Holiday.year == year,
                Holiday.is_nationwide == True
            )
        ).all()
        
        # Erwarte mindestens 9 bundesweite Feiertage
        if len(nationwide_count) < 9:
            return False
        
        # Prüfe bundeslandspezifische Feiertage für jedes Bundesland
        for state in federal_states:
            state_holidays = self.session.exec(
                select(Holiday).where(
                    Holiday.year == year,
                    Holiday.federal_state == state,
                    Holiday.is_nationwide == False
                )
            ).all()
            
            # Jedes Bundesland sollte mindestens 1 spezifischen Feiertag haben
            # (außer Bundesländer ohne spezifische Feiertage)
            expected_count = self._get_expected_state_holidays_count(state)
            if len(state_holidays) < expected_count:
                return False
        
        return True

    def _get_expected_state_holidays_count(self, state: FederalState) -> int:
        """Gibt die erwartete Anzahl bundeslandspezifischer Feiertage zurück"""
        # Mapping der erwarteten Feiertage pro Bundesland
        state_holiday_counts = {
            FederalState.BADEN_WUERTTEMBERG: 3,  # Heilige Drei Könige, Fronleichnam, Allerheiligen
            FederalState.BAYERN: 3,  # Heilige Drei Könige, Fronleichnam, Mariä Himmelfahrt
            FederalState.BERLIN: 1,  # Internationaler Frauentag
            FederalState.BRANDENBURG: 1,  # Reformationstag
            FederalState.BREMEN: 1,  # Reformationstag
            FederalState.HAMBURG: 1,  # Reformationstag
            FederalState.HESSEN: 1,  # Fronleichnam
            FederalState.MECKLENBURG_VORPOMMERN: 1,  # Reformationstag
            FederalState.NIEDERSACHSEN: 1,  # Reformationstag
            FederalState.NORDRHEIN_WESTFALEN: 2,  # Fronleichnam, Allerheiligen
            FederalState.RHEINLAND_PFALZ: 2,  # Fronleichnam, Allerheiligen
            FederalState.SAARLAND: 3,  # Fronleichnam, Mariä Himmelfahrt, Allerheiligen
            FederalState.SACHSEN: 2,  # Reformationstag, Buß- und Bettag
            FederalState.SACHSEN_ANHALT: 2,  # Heilige Drei Könige, Reformationstag
            FederalState.SCHLESWIG_HOLSTEIN: 1,  # Reformationstag
            FederalState.THUERINGEN: 2,  # Reformationstag, Weltkindertag
        }
        
        return state_holiday_counts.get(state, 0)

    def get_holidays_in_date_range(self, start_date: date, end_date: date, federal_state: Optional[FederalState] = None) -> List[Holiday]:
        """Gibt alle Feiertage in einem Datumsbereich zurück"""
        query = select(Holiday).where(
            Holiday.date >= start_date,
            Holiday.date <= end_date
        )
        
        if federal_state:
            query = query.where(
                (Holiday.federal_state == federal_state) |
                (Holiday.is_nationwide == True)
            )
        
        query = query.order_by(Holiday.date)
        return self.session.exec(query).all()

    def count_holidays_in_range(self, start_date: date, end_date: date, federal_state: Optional[FederalState] = None) -> int:
        """Zählt Feiertage in einem Datumsbereich"""
        holidays = self.get_holidays_in_date_range(start_date, end_date, federal_state)
        return len(holidays)

    def get_federal_states_for_year(self, year: int) -> List[FederalState]:
        """Gibt alle Bundesländer zurück, für die Feiertage in einem Jahr vorhanden sind"""
        from sqlmodel import select
        
        query = select(Holiday.federal_state).where(
            Holiday.year == year,
            Holiday.is_nationwide == False,
            Holiday.federal_state.is_not(None)
        ).distinct()
        
        states = self.session.exec(query).all()
        return [state for state in states if state is not None]

    def get_year_completeness_status(self, year: int) -> Dict[str, Any]:
        """Gibt detaillierte Vollständigkeits-Informationen für ein Jahr zurück"""
        from sqlmodel import select, func
        
        # Gesamtanzahl Feiertage für das Jahr
        total_query = select(func.count(Holiday.id)).where(Holiday.year == year)
        total_count = self.session.exec(total_query).first() or 0
        
        # Bundesweite Feiertage
        nationwide_query = select(func.count(Holiday.id)).where(
            Holiday.year == year,
            Holiday.is_nationwide == True
        )
        nationwide_count = self.session.exec(nationwide_query).first() or 0
        
        # Bundeslandspezifische Feiertage
        state_specific_count = total_count - nationwide_count
        
        # Abgedeckte Bundesländer
        covered_states = self.get_federal_states_for_year(year)
        all_states = list(FederalState)
        missing_states = [state for state in all_states if state not in covered_states]
        
        # Vollständigkeitsprüfung
        is_complete = self._is_year_complete(year, all_states)
        
        return {
            "year": year,
            "is_complete": is_complete,
            "holiday_count": total_count,
            "nationwide_count": nationwide_count,
            "state_specific_count": state_specific_count,
            "federal_states_covered": [state.name for state in covered_states],
            "missing_states": [state.name for state in missing_states],
            "coverage_percentage": len(covered_states) / len(all_states) * 100 if all_states else 0
        }

    def get_detailed_year_coverage(self, include_incomplete: bool = True, federal_state_filter: Optional[FederalState] = None) -> Dict[str, Any]:
        """Gibt detaillierte Informationen über Jahr-Abdeckung zurück"""
        from sqlmodel import select
        
        # Alle Jahre mit Feiertagen ermitteln
        years_query = select(Holiday.year).distinct().order_by(Holiday.year)
        all_years = self.session.exec(years_query).all()
        
        if not all_years:
            return {
                "available_years": [],
                "summary": {
                    "total_years": 0,
                    "complete_years": 0,
                    "incomplete_years": 0,
                    "year_range": None,
                    "total_holidays": 0
                },
                "current_year": datetime.now().year,
                "recommended_range": {"start": 2020, "end": 2030}
            }
        
        # Detaillierte Informationen für jedes Jahr sammeln
        year_details = []
        complete_years = 0
        total_holidays = 0
        
        for year in all_years:
            year_status = self.get_year_completeness_status(year)
            
            # Filterung nach Bundesland (falls angegeben)
            if federal_state_filter:
                if federal_state_filter.name not in year_status["federal_states_covered"]:
                    continue
            
            # Filterung nach Vollständigkeit
            if not include_incomplete and not year_status["is_complete"]:
                continue
            
            year_details.append(year_status)
            total_holidays += year_status["holiday_count"]
            
            if year_status["is_complete"]:
                complete_years += 1
        
        # Zusammenfassung erstellen
        incomplete_years = len(year_details) - complete_years
        year_range = {
            "min": min(all_years) if all_years else None,
            "max": max(all_years) if all_years else None
        } if all_years else None
        
        summary = {
            "total_years": len(year_details),
            "complete_years": complete_years,
            "incomplete_years": incomplete_years,
            "year_range": year_range,
            "total_holidays": total_holidays,
            "average_holidays_per_year": total_holidays / len(year_details) if year_details else 0
        }
        
        return {
            "available_years": year_details,
            "summary": summary,
            "current_year": datetime.now().year,
            "recommended_range": {"start": 2020, "end": 2030},
            "filter_applied": {
                "include_incomplete": include_incomplete,
                "federal_state": federal_state_filter.name if federal_state_filter else None
            }
        }


def get_holiday_service() -> HolidayService:
    """Dependency für HolidayService"""
    session = next(get_session())
    return HolidayService(session)
