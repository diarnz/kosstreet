from fastapi import APIRouter

from kostreet_ai.api.v1.audit import router as audit_router
from kostreet_ai.api.v1.classify import router as classify_router

api_router = APIRouter()
api_router.include_router(classify_router, tags=["classify"])
api_router.include_router(audit_router, prefix="/audit", tags=["audit"])
