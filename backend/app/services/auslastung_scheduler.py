import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from app.core.database import get_session
from app.services.auslastung_service import AuslastungService

logger = logging.getLogger(__name__)

# Single instance of background scheduler
_scheduler = None

def run_daily_calculation():
    """Wrapper function to get session and run calculation"""
    try:
        logger.info("Starte nächtliche Belegungsstatistik-Berechnung...")
        session = next(get_session())
        
        # 1. Tags sicherstellen
        import datetime
        current_year = datetime.datetime.now().year
        AuslastungService.generate_auto_tags(session, current_year)
        
        # 2. Multiplikatoren berechnen
        result = AuslastungService.calculate_multipliers(session)
        logger.info(f"Belegungsstatistik-Berechnung abgeschlossen: {result}")
        session.close()
    except Exception as e:
        logger.error(f"Fehler bei der automatischen Belegungsstatistik-Berechnung: {e}")


def start_auslastung_cron():
    """
    Startet einen täglichen Cronjob zur Berechnung der Multiplikatoren
    """
    global _scheduler
    
    if _scheduler is None:
        _scheduler = BackgroundScheduler()
        
        # Täglich um 03:00 Uhr nachts ausführen
        trigger = CronTrigger(hour=3, minute=0)
        
        _scheduler.add_job(
            func=run_daily_calculation,
            trigger=trigger,
            id="auslastung_daily_calc",
            name="Daily Auslastung Multipliers sync",
            replace_existing=True
        )
        
        _scheduler.start()
        logger.info("Auslastungs-Cronjob (03:00) gestartet.")
    
    return _scheduler

def stop_auslastung_cron():
    global _scheduler
    if _scheduler:
        _scheduler.shutdown()
        _scheduler = None
