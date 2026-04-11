from typing import List, Optional
from datetime import date, datetime, timedelta
from sqlmodel import Session, select, func
from sqlalchemy import extract
from app.models.auslastung import DailyEntry, DailyFremd
from app.models.auslastung_tag import CalendarTag, DayTag, TagMultiplier, MetricType, TagSource
from app.models.holiday import Holiday, HolidayType

class AuslastungService:
    @staticmethod
    def calculate_multipliers(session: Session):
        """
        Berechnet die Multiplikatoren für alle Tags basierend auf historischen Daten neu.
        Standardtage sind Tage ohne Feiertags- oder Ferientag.
        """
        # 1. Hole alle Einträge zur Basis-Berechnung
        # Für eine echte Implementierung müssten wir history + plan_beds via StationCapacity verknüpfen.
        # Hier ein vereinfachter Ansatz gemäß Konzept:
        
        # Finde alle CalendarTags
        tags = session.exec(select(CalendarTag)).all()
        
        # Zukünftige Ausbaustufe: Echte SQL-Aggregationen hier
        # Für den PoC fügen wir einen Dummy-Update-Mechanismus ein,
        # der die TagMultipliers aktuell hält.
        
        now = datetime.utcnow()
        calculated_count = 0
        
        for tag in tags:
            # Hole alle Dates mit diesem Tag
            day_tags = session.exec(select(DayTag).where(DayTag.tag_id == tag.id)).all()
            tag_dates = [dt.date for dt in day_tags]
            
            if len(tag_dates) < 5:
                # Konzept: Minimum 5 Datenpunkte für Konfidenz
                continue
                
            # Hier würde die komplexe Aggregation passieren:
            # avg_occupied_tag = SELECT AVG(occupied) FROM daily_entries WHERE date IN tag_dates
            # avg_occupied_std = SELECT AVG(occupied) FROM daily_entries WHERE date NOT IN (alle tag dates)
            
            # Dummy Berechnungen für den MVP, wird im nächsten Refactoring mit echten SQL-Statements gefüllt
            for metric in MetricType:
                stmt_existing = select(TagMultiplier).where(
                    TagMultiplier.tag_id == tag.id,
                    TagMultiplier.metric == metric
                )
                multiplier_row = session.exec(stmt_existing).first()
                if not multiplier_row:
                    multiplier_row = TagMultiplier(
                        tag_id=tag.id,
                        metric=metric,
                        multiplier=1.0,
                        sample_size=len(tag_dates),
                        confidence=0.5
                    )
                else:
                    multiplier_row.sample_size = len(tag_dates)
                    multiplier_row.last_calculated = now
                    
                session.add(multiplier_row)
                calculated_count += 1
                
        session.commit()
        return {"status": "success", "calculated_multipliers": calculated_count}

    @staticmethod
    def generate_auto_tags(session: Session, target_year: int):
        """
        Generiert automatische DayTags aus der bestehenden holidays Tabelle
        sowie Standard-Wochentage.
        """
        # Hole existierende Holidays für das Jahr
        holidays = session.exec(select(Holiday).where(extract('year', Holiday.date) == target_year)).all()
        
        # Dieses Skript würde:
        # 1. CalendarTags für "Heiligabend", "Sommerferien", "Wochentage" anlegen (falls noch nicht existent)
        # 2. DayTags verknüpfen
        # (Dies wird im zweiten Iterationsschritt vollständig ausprogrammiert)
        pass
