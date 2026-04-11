"""
GynOrg Backend - FastAPI Application
"""
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.api.llm import router as llm_router
from app.api.v1.api import api_router

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format=settings.LOG_FORMAT
)
logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    description="GynOrg - Abwesenheitsplanungstool für Einzelnutzer",
    debug=settings.DEBUG,
    openapi_url=f"{settings.API_V1_STR}/openapi.json" if settings.DEBUG else None,
    docs_url=f"{settings.API_V1_STR}/docs" if settings.DEBUG else None,
    redoc_url=f"{settings.API_V1_STR}/redoc" if settings.DEBUG else None,
)

# CRITICAL: Add CORS middleware FIRST - before any other middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Application startup event."""
    logger.info(f"Starting {settings.PROJECT_NAME} v{settings.PROJECT_VERSION}")
    logger.info(f"Debug mode: {settings.DEBUG}")
    logger.info(f"Database URL: {settings.DATABASE_URL}")
    logger.info(f"CORS Origins: {settings.get_cors_origins()}")
    
    # Holiday Data Auto-Import
    if settings.HOLIDAY_AUTO_IMPORT_ON_STARTUP:
        try:
            from app.services.holiday_startup_service import ensure_holiday_data_on_startup
            logger.info("Checking holiday data...")
            result = await ensure_holiday_data_on_startup()
            
            if result["action"] == "imported":
                logger.info(
                    f"Holiday import: {result['import_result']['total_imported']} "
                    f"holidays imported for years {result['missing_years']}"
                )
            elif result["action"] == "none_needed":
                logger.info("Holiday data: All years already present")
            elif result["action"] == "error":
                logger.warning(f"Holiday import failed: {result.get('error', 'Unknown error')}")
            elif result["action"] == "critical_error":
                logger.error(f"Critical holiday import error: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            logger.error(f"Failed to initialize holiday data: {e}")
            # App startet trotzdem (graceful degradation)
    else:
        logger.info("Holiday auto-import is disabled")
    
    # Holiday Scheduler
    if settings.HOLIDAY_SCHEDULER_ENABLED:
        try:
            from app.services.holiday_scheduler import start_holiday_scheduler
            logger.info("Starting Holiday Scheduler...")
            scheduler = start_holiday_scheduler()
            
            # Get next run time
            job_info = scheduler.get_job_info(scheduler.JOB_ID)
            if job_info and job_info.get('next_run_time'):
                logger.info(f"Holiday Scheduler started. Next run: {job_info['next_run_time']}")
            else:
                logger.info("Holiday Scheduler started")
                
        except Exception as e:
            logger.error(f"Failed to start Holiday Scheduler: {e}")
            # App startet trotzdem (graceful degradation)
    else:
        logger.info("Holiday Scheduler is disabled")


@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event."""
    logger.info(f"Shutting down {settings.PROJECT_NAME}")
    
    # Stop Holiday Scheduler
    if settings.HOLIDAY_SCHEDULER_ENABLED:
        try:
            from app.services.holiday_scheduler import stop_holiday_scheduler
            stop_holiday_scheduler()
            logger.info("Holiday Scheduler stopped")
        except Exception as e:
            logger.error(f"Failed to stop Holiday Scheduler: {e}")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": f"Welcome to {settings.PROJECT_NAME} API",
        "version": settings.PROJECT_VERSION,
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.PROJECT_VERSION
    }


@app.get("/api/v1/info")
async def api_info():
    """API information endpoint."""
    return {
        "name": settings.PROJECT_NAME,
        "version": settings.PROJECT_VERSION,
        "api_version": settings.API_V1_STR,
        "debug": settings.DEBUG
    }


# Include routers
app.include_router(api_router, prefix=settings.API_V1_STR)
app.include_router(llm_router)


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host=settings.CONTAINER_HOST,
        port=settings.CONTAINER_PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )
