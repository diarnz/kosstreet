from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import require_admin
from app.db.engine import get_db
from app.schemas.audit import (
    AdminAuditRunContent,
    AdminAuditRunSummary,
    AuditRunAdminUpdate,
    AuditRunSummary,
    AuditSuggestionAdminUpdate,
    AuditSuggestionRead,
    audit_suggestion_to_read,
)
from app.services.audit_service import AuditService

router = APIRouter(dependencies=[Depends(require_admin)])


def get_audit_service(db: AsyncSession = Depends(get_db)) -> AuditService:
    return AuditService(db)


@router.get("/audit-runs", response_model=list[AdminAuditRunSummary])
async def admin_list_audit_runs(
    service: AuditService = Depends(get_audit_service),
) -> list[AdminAuditRunSummary]:
    return await service.admin_list_runs()


@router.get("/audit-runs/{run_id}", response_model=AuditRunSummary)
async def admin_get_audit_run(
    run_id: UUID,
    service: AuditService = Depends(get_audit_service),
) -> AuditRunSummary:
    run = await service.get_run(run_id, include_hidden=True)
    return AuditRunSummary.model_validate(run)


@router.get("/audit-runs/{run_id}/content", response_model=AdminAuditRunContent)
async def admin_get_audit_run_content(
    run_id: UUID,
    service: AuditService = Depends(get_audit_service),
) -> AdminAuditRunContent:
    return await service.admin_get_run_content(run_id)


@router.patch("/audit-runs/{run_id}", response_model=AuditRunSummary)
async def admin_update_audit_run(
    run_id: UUID,
    payload: AuditRunAdminUpdate,
    service: AuditService = Depends(get_audit_service),
) -> AuditRunSummary:
    run = await service.admin_update_run(run_id, payload)
    return AuditRunSummary.model_validate(run)


@router.delete("/audit-runs/{run_id}", status_code=status.HTTP_204_NO_CONTENT)
async def admin_delete_audit_run(
    run_id: UUID,
    service: AuditService = Depends(get_audit_service),
) -> None:
    await service.admin_delete_run(run_id)


@router.patch("/audit-suggestions/{suggestion_id}", response_model=AuditSuggestionRead)
async def admin_update_audit_suggestion(
    suggestion_id: UUID,
    payload: AuditSuggestionAdminUpdate,
    service: AuditService = Depends(get_audit_service),
) -> AuditSuggestionRead:
    suggestion = await service.admin_update_suggestion(suggestion_id, payload)
    return audit_suggestion_to_read(suggestion)


@router.delete("/audit-suggestions/{suggestion_id}", status_code=status.HTTP_204_NO_CONTENT)
async def admin_delete_audit_suggestion(
    suggestion_id: UUID,
    service: AuditService = Depends(get_audit_service),
) -> None:
    await service.admin_delete_suggestion(suggestion_id)
