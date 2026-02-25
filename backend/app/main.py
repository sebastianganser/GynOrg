"""
Main FastAPI application entry point.
"""
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import create_db_and_tables, get_session
from app.api.v1.api import api_router
from app.models.employee import Employee  # Import to register table
from app.models.absence import Absence  # Import to register table
from app.models.absence_type import AbsenceType  # Import to register table
from app.models.vacation_allowance import VacationAllowance  # Import to register table
from app.models.vacation_entitlement import VacationEntitlement  # Import to register table
from app.models.federal_state import FederalState  # Import to register table
from app.models.holiday import Holiday  # Import to register table
from app.services.startup_service import StartupService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    debug=settings.DEBUG
)

# Set up CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)

async def ensure_holiday_data():
    """Stellt sicher, dass Holiday-Daten für 2020-2030 vorhanden sind."""
    try:
        session = next(get_session())
        startup_service = StartupService(session)
        
        # Automatische Holiday-Daten-Population
        result = await startup_service.ensure_holiday_data_complete(
            start_year=2020,
            end_year=2030
        )
        
        if result["success"]:
            if result.get("skipped_reason"):
                logger.info(f"Holiday-Daten bereits vollständig: {result['skipped_reason']}")
            else:
                imported = result.get("import_result", {}).get("total_imported", 0)
                logger.info(f"Holiday-Daten erfolgreich sichergestellt: {imported} Feiertage importiert")
        else:
            logger.warning(f"Holiday-Daten-Import mit Problemen: {result.get('error', 'Unbekannter Fehler')}")
        
        # Zeige Statistiken
        stats = startup_service.get_holiday_statistics()
        logger.info(f"Holiday-Statistiken: {stats['total_holidays']} Feiertage für {stats['year_range']['count']} Jahre ({stats['year_range']['min']}-{stats['year_range']['max']})")
        
        session.close()
        
    except Exception as e:
        logger.error(f"Fehler bei Holiday-Daten-Sicherstellung: {str(e)}")
        # Startup soll nicht fehlschlagen wegen Holiday-Problemen


@app.on_event("startup")
async def startup_event():
    """Initialize database tables and ensure holiday data on startup."""
    logger.info("Starting application...")
    
    try:
        # Datenbank-Tabellen erstellen
        create_db_and_tables()
        logger.info("Database tables initialized")
        
        # Holiday-Daten sicherstellen
        await ensure_holiday_data()
    except Exception as e:
        logger.error(f"Error during database initialization: {e}")
        logger.warning("Application started but database might not be fully configured")
    
    logger.info("Application startup completed")

@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": f"Welcome to {settings.PROJECT_NAME} API"}

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": settings.PROJECT_NAME}
