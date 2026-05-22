from uuid import UUID

from fastapi import APIRouter, Depends
from fastapi import status as http_status
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.engine import get_db
from app.schemas.audit import (
    AnalyzeViewRequest,
    AuditFrameDetail,
    AuditFrameSummary,
    AuditRunCreate,
    AuditRunSummary,
    AuditScanPoint,
    AuditSuggestionRead,
    AuditSuggestionReview,
    OnDemandAnalyzeQuota,
    SuggestionConversionResult,
    audit_frame_to_detail,
    audit_frame_to_scan_point,
    audit_frame_to_summary,
    audit_suggestion_to_read,
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


@audit_runs_router.get("/{run_id}/scan-path", response_model=list[AuditScanPoint])
async def list_audit_scan_path(
    run_id: UUID,
    service: AuditService = Depends(get_audit_service),
) -> list[AuditScanPoint]:
    frames = await service.list_scan_path(run_id)
    return [audit_frame_to_scan_point(frame) for frame in frames]


@audit_runs_router.get("/{run_id}/frames", response_model=list[AuditFrameSummary])
async def list_audit_frames(
    run_id: UUID,
    service: AuditService = Depends(get_audit_service),
) -> list[AuditFrameSummary]:
    frames = await service.list_frames(run_id)
    return [audit_frame_to_summary(frame) for frame in frames]


@audit_runs_router.get("/{run_id}/frames/{frame_index}", response_model=AuditFrameDetail)
async def get_audit_frame(
    run_id: UUID,
    frame_index: int,
    service: AuditService = Depends(get_audit_service),
) -> AuditFrameDetail:
    frame = await service.get_frame(run_id, frame_index)
    return audit_frame_to_detail(frame)


@audit_runs_router.get("/{run_id}/frames/{frame_index}/image")
async def get_audit_frame_image(
    run_id: UUID,
    frame_index: int,
    service: AuditService = Depends(get_audit_service),
) -> Response:
    image_bytes, content_type = await service.get_frame_image(run_id, frame_index)
    return Response(content=image_bytes, media_type=content_type)


@audit_runs_router.get("/{run_id}/on-demand-quota", response_model=OnDemandAnalyzeQuota)
async def get_on_demand_analyze_quota(
    run_id: UUID,
    service: AuditService = Depends(get_audit_service),
) -> OnDemandAnalyzeQuota:
    quota = await service.get_on_demand_quota(run_id)
    return OnDemandAnalyzeQuota.model_validate(quota)


@audit_runs_router.post("/{run_id}/analyze-view", response_model=AuditFrameDetail)
async def analyze_audit_view(
    run_id: UUID,
    payload: AnalyzeViewRequest,
    service: AuditService = Depends(get_audit_service),
) -> AuditFrameDetail:
    frame = await service.analyze_view(
        run_id,
        payload.latitude,
        payload.longitude,
        payload.heading,
        payload.pitch,
    )
    return audit_frame_to_detail(frame)


@audit_runs_router.get("/{run_id}/suggestions", response_model=list[AuditSuggestionRead])
async def list_audit_suggestions(
    run_id: UUID,
    service: AuditService = Depends(get_audit_service),
) -> list[AuditSuggestionRead]:
    suggestions = await service.list_suggestions(run_id)
    return [audit_suggestion_to_read(suggestion) for suggestion in suggestions]


@audit_suggestions_router.patch("/{suggestion_id}", response_model=AuditSuggestionRead)
async def review_audit_suggestion(
    suggestion_id: UUID,
    payload: AuditSuggestionReview,
    service: AuditService = Depends(get_audit_service),
) -> AuditSuggestionRead:
    suggestion = await service.review_suggestion(suggestion_id, payload)
    return audit_suggestion_to_read(suggestion)


@audit_suggestions_router.get("/{suggestion_id}", response_model=AuditSuggestionRead)
async def get_audit_suggestion(
    suggestion_id: UUID,
    service: AuditService = Depends(get_audit_service),
) -> AuditSuggestionRead:
    suggestion = await service.get_suggestion(suggestion_id)
    return audit_suggestion_to_read(suggestion)


@audit_suggestions_router.get("/{suggestion_id}/frame-image")
async def get_audit_suggestion_frame_image(
    suggestion_id: UUID,
    service: AuditService = Depends(get_audit_service),
) -> Response:
    image_bytes, content_type = await service.get_suggestion_frame_image(suggestion_id)
    return Response(content=image_bytes, media_type=content_type)


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
