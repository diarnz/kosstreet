from fastapi import APIRouter

from app.api.v1.routes import audit, health, reports

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(reports.router, prefix="/reports", tags=["reports"])
api_router.include_router(audit.router, prefix="/audit-runs", tags=["street-audit"])

