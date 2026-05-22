import json
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile
from fastapi import status as http_status
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.engine import get_db
from app.models.enums import IssueCategory, ReportSource, TicketStatus
from app.schemas.report import (
    ImageAnalysisResult,
    ReportCreate,
    ReportDetail,
    ReportStatusUpdate,
    ReportSummary,
)
from app.services.report_service import ReportService

router = APIRouter()


def get_report_service(db: AsyncSession = Depends(get_db)) -> ReportService:
    return ReportService(db)


@router.get("", response_model=list[ReportSummary])
async def list_reports(
    status: TicketStatus | None = None,
    category: IssueCategory | None = None,
    source: ReportSource | None = None,
    service: ReportService = Depends(get_report_service),
) -> list[ReportSummary]:
    reports = await service.list_reports(
        status_filter=status,
        category=category,
        source=source,
    )
    return [ReportSummary.model_validate(report) for report in reports]


@router.post("/analyze-image", response_model=ImageAnalysisResult)
async def analyze_report_image(
    image: Annotated[UploadFile, File()],
    service: ReportService = Depends(get_report_service),
) -> ImageAnalysisResult:
    if image.content_type not in {"image/jpeg", "image/png", "image/webp"}:
        raise HTTPException(
            status_code=http_status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Unsupported image type",
        )
    return await service.analyze_image(image)


@router.post(
    "",
    response_model=ReportSummary,
    status_code=http_status.HTTP_201_CREATED,
)
async def create_report(
    request: Request,
    data: Annotated[str | None, Form()] = None,
    image: Annotated[UploadFile | None, File()] = None,
    service: ReportService = Depends(get_report_service),
) -> ReportSummary:
    payload = await _parse_report_create_payload(request, data)
    report = await service.create_report(payload, image)
    return ReportSummary.model_validate(report)


@router.get("/{report_id}", response_model=ReportDetail)
async def get_report(
    report_id: UUID,
    service: ReportService = Depends(get_report_service),
) -> ReportDetail:
    report = await service.get_report_detail(report_id)
    return ReportDetail.model_validate(report)


@router.patch("/{report_id}/status", response_model=ReportDetail)
async def update_report_status(
    report_id: UUID,
    payload: ReportStatusUpdate,
    service: ReportService = Depends(get_report_service),
) -> ReportDetail:
    report = await service.update_status(report_id, payload)
    return ReportDetail.model_validate(report)


async def _parse_report_create_payload(request: Request, data: str | None) -> ReportCreate:
    try:
        if data is not None:
            raw_payload = json.loads(data)
        else:
            raw_payload = await request.json()
        return ReportCreate.model_validate(raw_payload)
    except json.JSONDecodeError as exc:
        raise HTTPException(
            status_code=http_status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid report JSON payload",
        ) from exc
    except ValidationError as exc:
        raise HTTPException(
            status_code=http_status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=exc.errors(),
        ) from exc

