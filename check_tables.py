import asyncio
import logging
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.models.employee import Employee
from app.models.absence import Absence
from app.models.holiday import Holiday
from app.models.calendar_settings import CalendarSettings
from app.models.vacation_allowance import VacationAllowance
from app.models.school_holiday_notification import SchoolHolidayNotification

# Configure logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_db_tables():
    """Check if all required tables exist and count their records."""
    logger.info(f"Connecting to database: {settings.DATABASE_URL}")
    
    try:
        # Create engine
        engine = create_engine(settings.DATABASE_URL)
        
        # Check connection and tables
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        if not tables:
            logger.warning("No tables found in the database! Run Alembic migrations first.")
            return

        logger.info(f"Found {len(tables)} tables in database:")
        
        # Create session to count rows
        Session = sessionmaker(bind=engine)
        session = Session()
        
        # Define models to check
        models_to_check = {
            "employees": Employee,
            "absences": Absence,
            "holidays": Holiday,
            "calendar_settings": CalendarSettings,
            "vacation_allowances": VacationAllowance,
            "school_holiday_notifications": SchoolHolidayNotification
        }
        
        for table_name in sorted(tables):
            # Check if we have an ORM model mapping for this table
            if table_name in models_to_check:
                try:
                    count = session.query(models_to_check[table_name]).count()
                    logger.info(f"  - {table_name}: {count} records found")
                except Exception as e:
                    logger.error(f"  - {table_name}: Error counting records - {e}")
            else:
                logger.info(f"  - {table_name}: (No ORM mapping to count)")
                
        session.close()
        logger.info("Database check completed successfully.")
        
    except Exception as e:
        logger.error(f"Database connection or inspection failed: {str(e)}")

if __name__ == "__main__":
    check_db_tables()
