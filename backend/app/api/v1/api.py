"""
API v1 router configuration.
"""
from fastapi import APIRouter

from app.api.v1.endpoints import auth, employees, vacation_allowances, federal_states, absences, absence_types, holidays, admin_sync, holiday_admin, vacation_entitlements, job_positions, auslastung, system_settings
from app.api.v1.endpoints import goae, patienten, rechnungen, praxis_einstellungen
from app.api.v1 import calendar_settings

api_router = APIRouter()

# Health check endpoint
@api_router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "GynOrg API"}

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(employees.router, prefix="/employees", tags=["employees"])
api_router.include_router(vacation_allowances.router, prefix="/vacation-allowances", tags=["vacation-allowances"])
api_router.include_router(vacation_entitlements.router, prefix="/vacation-entitlements", tags=["vacation-entitlements"])
api_router.include_router(federal_states.router, prefix="/federal-states", tags=["federal-states"])
api_router.include_router(absences.router, prefix="/absences", tags=["absences"])
api_router.include_router(absence_types.router, prefix="/absence-types", tags=["absence-types"])
api_router.include_router(holidays.router, prefix="/holidays", tags=["holidays"])
api_router.include_router(calendar_settings.router, prefix="/calendar-settings", tags=["calendar-settings"])
api_router.include_router(admin_sync.router, prefix="/admin/sync", tags=["admin-sync"])
api_router.include_router(holiday_admin.router, prefix="/holidays/admin", tags=["holiday-admin"])
api_router.include_router(job_positions.router, prefix="/job-positions", tags=["job-positions"])
api_router.include_router(auslastung.router, prefix="/auslastung", tags=["auslastung"])
api_router.include_router(system_settings.router, prefix="/system-settings", tags=["system-settings"])

# GOÄ-Rechnungsmodul
api_router.include_router(goae.router, prefix="/goae", tags=["goae"])
api_router.include_router(patienten.router, prefix="/patienten", tags=["patienten"])
api_router.include_router(rechnungen.router, prefix="/rechnungen", tags=["rechnungen"])
api_router.include_router(praxis_einstellungen.router, prefix="/praxis-einstellungen", tags=["praxis-einstellungen"])
