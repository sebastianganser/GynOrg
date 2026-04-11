import asyncio
import logging
import argparse
from sqlalchemy import create_engine
from alembic import command
from alembic.config import Config as AlembicConfig

from app.core.config import settings

# Configure logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def update_database(force=False):
    """
    Run Alembic migrations to update the PostgreSQL database schema.
    If force is True, this is equivalent to upgrading head.
    """
    logger.info(f"Target Database: {settings.DATABASE_URL}")
    
    try:
        import os
        # Base dir is the root of the project
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        backend_dir = os.path.join(base_dir, "backend")
        alembic_ini_path = os.path.join(backend_dir, "alembic.ini")
        
        # Load Alembic Config
        alembic_cfg = AlembicConfig(alembic_ini_path)
        
        # Change dir so alembic finds the scripts folder correctly
        os.chdir(backend_dir)
        
        # Ensure it uses the dynamic URL
        alembic_cfg.set_main_option("sqlalchemy.url", settings.DATABASE_URL)
        
        # Run the upgrade
        logger.info("Running database migration (Alembic upgrade head)...")
        command.upgrade(alembic_cfg, "head")
        
        logger.info("Database update completed successfully.")
        
    except Exception as e:
        logger.error(f"Database update failed: {str(e)}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Update PostgreSQL database schema")
    parser.add_argument("--force", action="store_true", help="Force database update")
    args = parser.parse_args()
    
    update_database(force=args.force)
