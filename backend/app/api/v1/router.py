from fastapi import APIRouter

from app.api.v1.routes import health, reports
from app.api.v1.routes.audit import audit_runs_router, audit_suggestions_router

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(reports.router, prefix="/reports", tags=["reports"])
api_router.include_router(audit_runs_router, prefix="/audit-runs", tags=["street-audit"])
api_router.include_router(
    audit_suggestions_router,
    prefix="/audit-suggestions",
    tags=["street-audit"],
)

