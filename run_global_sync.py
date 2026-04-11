import sys
import os
import asyncio
import logging

# Add backend to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'backend')))

from sqlmodel import Session, create_engine, select, delete
from app.models.holiday import Holiday, DataSource, FederalState
from app.services.school_holiday_sync_service import SchoolHolidaySyncService, SyncStatus
from app.services.school_holiday_api_client import SchoolHolidayApiClient
from app.services.school_holiday_diff_service import SchoolHolidayDiffService, ConflictResolutionStrategy

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Db path (absolute to be safe)
db_path = "sqlite:///d:/Sebastian/Dokumente/Privat/Maria/Arbeit/GynOrg/backend/data/gynorg.db"
engine = create_engine(db_path)

async def main():
    logger.info("Starting Global School Vacation Sync...")
    
    with Session(engine) as session:
        # 1. Cleanup Manual Entries for BY 2025 (to prevent duplicates)
        # The sync service ignores DataSource.MANUAL when checking for existing implementation, 
        # so it would re-insert them as new if we don't delete.
        logger.info("Cleaning up manual entries for Bavaria 2025...")
        statement = delete(Holiday).where(
            Holiday.federal_state_code == 'BY',
            Holiday.year == 2025,
            Holiday.data_source == DataSource.MANUAL
        )
        result = session.exec(statement)
        session.commit()
        logger.info("Cleanup complete.")

        # 2. Initialize Services
        api_client = SchoolHolidayApiClient()
        diff_service = SchoolHolidayDiffService(session)
        sync_service = SchoolHolidaySyncService(
            session=session, 
            api_client=api_client, 
            diff_service=diff_service,
            conflict_strategy=ConflictResolutionStrategy.API_WINS
        )
        
        # 3. Run Sync
        # Using 2024, 2025, 2026 as target range
        years = [2024, 2025, 2026]
        logger.info(f"Syncing all states for years: {years}")
        
        # Calling the async method we just refactored
        result = await sync_service.sync_all_states(years=years)
        
        logger.info(f"Sync Finished with status: {result.status}")
        logger.info(f"Total Changes: {result.total_changes}")
        logger.info(f"Success Rate: {result.success_rate:.1%}")
        
        if result.failed_states:
            logger.error(f"Failed States: {result.failed_states}")
            for error in result.errors:
                logger.error(f"Error: {error.message}")

if __name__ == "__main__":
    asyncio.run(main())
