import sys
import os
import asyncio
import logging

# Add backend to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'backend')))

from sqlmodel import Session, create_engine, select, delete
from app.models.holiday import Holiday, DataSource
from app.services.school_holiday_sync_service import SchoolHolidaySyncService, SyncStatus
from app.services.school_holiday_api_client import SchoolHolidayApiClient
from app.services.school_holiday_diff_service import SchoolHolidayDiffService, ConflictResolutionStrategy

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Db path
db_path = "sqlite:///d:/Sebastian/Dokumente/Privat/Maria/Arbeit/GynOrg/backend/data/gynorg.db"
engine = create_engine(db_path)

async def main():
    logger.info("Starting Cleanup and Resync...")
    
    with Session(engine) as session:
        # 1. DELETE ALL API-IMPORTED HOLIDAYS (Because they have invalid state codes)
        logger.info("Cleaning up corrupted API data...")
        statement = delete(Holiday).where(
            Holiday.data_source == DataSource.MEHR_SCHULFERIEN_API
        )
        result = session.exec(statement)
        session.commit()
        logger.info(f"Deleted corrupted entries.")

        # 2. Re-Run Sync
        api_client = SchoolHolidayApiClient()
        diff_service = SchoolHolidayDiffService(session)
        sync_service = SchoolHolidaySyncService(
            session=session, 
            api_client=api_client, 
            diff_service=diff_service,
            conflict_strategy=ConflictResolutionStrategy.API_WINS
        )
        
        years = [2024, 2025, 2026]
        logger.info(f"Re-syncing all states for years: {years}")
        
        result = await sync_service.sync_all_states(years=years)
        
        logger.info(f"Sync Finished with status: {result.status}")
        logger.info(f"Total Changes: {result.total_changes}")

if __name__ == "__main__":
    asyncio.run(main())
