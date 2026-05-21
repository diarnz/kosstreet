from fastapi import APIRouter, status

from app.schemas.audit import AuditRunCreate, AuditRunRead
from app.services.audit_service import audit_service

router = APIRouter()


@router.get("", response_model=list[AuditRunRead])
def list_audit_runs() -> list[AuditRunRead]:
    return audit_service.list_audit_runs()


@router.post("", response_model=AuditRunRead, status_code=status.HTTP_201_CREATED)
def create_audit_run(payload: AuditRunCreate) -> AuditRunRead:
    return audit_service.create_audit_run(payload)

