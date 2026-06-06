from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import require_admin
from app.db.engine import get_db
from app.models.enums import IssueCategory, ReportSource, TicketStatus
from app.schemas.report import ReportAdminUpdate, ReportCreate, ReportDetail, ReportSummary
from app.schemas.report_helpers import report_to_detail, report_to_summary
from app.services.report_service import ReportService

router = APIRouter(dependencies=[Depends(require_admin)])


def get_report_service(db: AsyncSession = Depends(get_db)) -> ReportService:
    return ReportService(db)


@router.get("", response_model=list[ReportSummary])
async def admin_list_reports(
    status: TicketStatus | None = None,
    category: IssueCategory | None = None,
    source: ReportSource | None = None,
    service: ReportService = Depends(get_report_service),
) -> list[ReportSummary]:
    reports = await service.list_all_reports(
        status_filter=status,
        category=category,
        source=source,
    )
    return [report_to_summary(report) for report in reports]


@router.post("", response_model=ReportSummary, status_code=status.HTTP_201_CREATED)
async def admin_create_report(
    payload: ReportCreate,
    service: ReportService = Depends(get_report_service),
) -> ReportSummary:
    report = await service.create_report(payload)
    return report_to_summary(report)


@router.get("/{report_id}", response_model=ReportDetail)
async def admin_get_report(
    report_id: UUID,
    service: ReportService = Depends(get_report_service),
) -> ReportDetail:
    report = await service.get_report_detail(report_id, include_hidden=True)
    return report_to_detail(report)


@router.patch("/{report_id}", response_model=ReportDetail)
async def admin_update_report(
    report_id: UUID,
    payload: ReportAdminUpdate,
    service: ReportService = Depends(get_report_service),
) -> ReportDetail:
    report = await service.admin_update_report(report_id, payload)
    return report_to_detail(report)


@router.delete("/{report_id}", status_code=status.HTTP_204_NO_CONTENT)
async def admin_delete_report(
    report_id: UUID,
    service: ReportService = Depends(get_report_service),
) -> None:
    await service.admin_delete_report(report_id)
