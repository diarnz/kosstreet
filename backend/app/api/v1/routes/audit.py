from uuid import UUID

from fastapi import APIRouter, Depends
from fastapi import status as http_status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.engine import get_db
from app.schemas.audit import (
    AuditRunCreate,
    AuditRunSummary,
    AuditSuggestionRead,
    AuditSuggestionReview,
    SuggestionConversionResult,
)
from app.services.audit_service import AuditService

audit_runs_router = APIRouter()
audit_suggestions_router = APIRouter()


def get_audit_service(db: AsyncSession = Depends(get_db)) -> AuditService:
    return AuditService(db)


@audit_runs_router.get("", response_model=list[AuditRunSummary])
async def list_audit_runs(
    service: AuditService = Depends(get_audit_service),
) -> list[AuditRunSummary]:
    runs = await service.list_runs()
    return [AuditRunSummary.model_validate(run) for run in runs]


@audit_runs_router.post(
    "",
    response_model=AuditRunSummary,
    status_code=http_status.HTTP_201_CREATED,
)
async def create_audit_run(
    payload: AuditRunCreate,
    service: AuditService = Depends(get_audit_service),
) -> AuditRunSummary:
    run = await service.create_run(payload)
    return AuditRunSummary.model_validate(run)


@audit_runs_router.get("/{run_id}", response_model=AuditRunSummary)
async def get_audit_run(
    run_id: UUID,
    service: AuditService = Depends(get_audit_service),
) -> AuditRunSummary:
    run = await service.get_run(run_id)
    return AuditRunSummary.model_validate(run)


@audit_runs_router.get("/{run_id}/suggestions", response_model=list[AuditSuggestionRead])
async def list_audit_suggestions(
    run_id: UUID,
    service: AuditService = Depends(get_audit_service),
) -> list[AuditSuggestionRead]:
    suggestions = await service.list_suggestions(run_id)
    return [AuditSuggestionRead.model_validate(suggestion) for suggestion in suggestions]


@audit_suggestions_router.patch("/{suggestion_id}", response_model=AuditSuggestionRead)
async def review_audit_suggestion(
    suggestion_id: UUID,
    payload: AuditSuggestionReview,
    service: AuditService = Depends(get_audit_service),
) -> AuditSuggestionRead:
    suggestion = await service.review_suggestion(suggestion_id, payload)
    return AuditSuggestionRead.model_validate(suggestion)


@audit_suggestions_router.get("/{suggestion_id}", response_model=AuditSuggestionRead)
async def get_audit_suggestion(
    suggestion_id: UUID,
    service: AuditService = Depends(get_audit_service),
) -> AuditSuggestionRead:
    suggestion = await service.get_suggestion(suggestion_id)
    return AuditSuggestionRead.model_validate(suggestion)


@audit_suggestions_router.post(
    "/{suggestion_id}/convert-to-report",
    response_model=SuggestionConversionResult,
    status_code=http_status.HTTP_201_CREATED,
)
async def convert_audit_suggestion_to_report(
    suggestion_id: UUID,
    service: AuditService = Depends(get_audit_service),
) -> SuggestionConversionResult:
    return await service.convert_to_report(suggestion_id)

