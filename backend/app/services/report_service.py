from uuid import UUID

from fastapi import HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.enums import IssueCategory, ReportSource, TicketStatus
from app.models.report import Report
from app.repositories.report_repository import ReportRepository
from app.schemas.report import ImageAnalysisResult, ReportAdminUpdate, ReportCreate, ReportStatusUpdate
from app.services.ai_service import AIService
from app.storage.factory import get_file_storage

DEPARTMENT_MAP: dict[IssueCategory, str] = {
    IssueCategory.pothole: "Roads / Public Works",
    IssueCategory.garbage: "Sanitation",
    IssueCategory.broken_streetlight: "Electrical / Infrastructure",
    IssueCategory.blocked_sidewalk: "Roads / Public Works",
    IssueCategory.damaged_sign: "Roads / Public Works",
    IssueCategory.other: "General Services",
}

VALID_TRANSITIONS: dict[TicketStatus, set[TicketStatus]] = {
    TicketStatus.new: {TicketStatus.verified, TicketStatus.rejected},
    TicketStatus.verified: {TicketStatus.assigned, TicketStatus.rejected},
    TicketStatus.assigned: {TicketStatus.in_progress, TicketStatus.rejected},
    TicketStatus.in_progress: {TicketStatus.resolved, TicketStatus.rejected},
    TicketStatus.resolved: set(),
    TicketStatus.rejected: set(),
}


class ReportService:
    def __init__(self, db: AsyncSession) -> None:
        self.repository = ReportRepository(db)
        self.storage = get_file_storage()
        self.ai_service = AIService(settings)

    async def list_reports(
        self,
        *,
        status_filter: TicketStatus | None = None,
        category: IssueCategory | None = None,
        source: ReportSource | None = None,
    ) -> list[Report]:
        return await self.repository.list(
            status=status_filter,
            category=category,
            source=source,
            visible_only=True,
        )

    async def list_all_reports(
        self,
        *,
        status_filter: TicketStatus | None = None,
        category: IssueCategory | None = None,
        source: ReportSource | None = None,
    ) -> list[Report]:
        return await self.repository.list(
            status=status_filter,
            category=category,
            source=source,
            visible_only=False,
        )

    async def create_report(
        self,
        payload: ReportCreate,
        image: UploadFile | None = None,
    ) -> Report:
        image_path: str | None = None
        create_payload = payload

        if image is not None:
            image_bytes = await image.read()
            suffix = ".jpg"
            if image.filename and "." in image.filename:
                suffix = f".{image.filename.rsplit('.', 1)[-1].lower()}"
            image_path = self.storage.save_bytes(image_bytes, suffix=suffix)

            if not payload.detection_regions:
                analysis = await self.ai_service.analyze_image_bytes(image_bytes)
                create_payload = payload.model_copy(
                    update={
                        "confidence": payload.confidence or analysis.confidence,
                        "description": payload.description or analysis.description,
                        "severity": payload.severity or analysis.severity,
                        "detection_regions": analysis.regions,
                    }
                )

        return await self.repository.create(create_payload, image_path=image_path)

    async def get_report_detail(self, report_id: UUID, *, include_hidden: bool = False) -> Report:
        report = await self.repository.get_with_events(report_id)
        if report is None or (not include_hidden and not report.is_visible):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Report not found",
            )
        return report

    async def admin_update_report(self, report_id: UUID, payload: ReportAdminUpdate) -> Report:
        report = await self.get_report_detail(report_id, include_hidden=True)
        await self.repository.update_fields(
            report,
            category=payload.category,
            status=payload.status,
            latitude=payload.latitude,
            longitude=payload.longitude,
            source=payload.source,
            description=payload.description,
            confidence=payload.confidence,
            is_visible=payload.is_visible,
        )
        refreshed = await self.repository.get_with_events(report_id)
        if refreshed is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Report not found",
            )
        return refreshed

    async def admin_delete_report(self, report_id: UUID) -> None:
        report = await self.repository.get(report_id)
        if report is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Report not found",
            )
        await self.repository.delete(report)

    async def update_status(
        self,
        report_id: UUID,
        payload: ReportStatusUpdate,
    ) -> Report:
        report = await self.get_report_detail(report_id)
        current_status = TicketStatus(report.status)
        allowed_statuses = VALID_TRANSITIONS[current_status]

        if payload.status not in allowed_statuses:
            allowed = ", ".join(status.value for status in sorted(allowed_statuses)) or "none"
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=(
                    f"Cannot move from '{current_status.value}' to '{payload.status.value}'. "
                    f"Allowed next statuses: {allowed}."
                ),
            )

        await self.repository.update_status(
            report,
            payload.status,
            note=payload.note,
        )
        refreshed = await self.repository.get_with_events(report_id)
        if refreshed is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Report not found",
            )
        return refreshed

    async def get_report_image(self, report_id: UUID) -> tuple[bytes, str]:
        report = await self.get_report_detail(report_id)
        if not report.image_path:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Report has no image",
            )

        try:
            return self.storage.read_bytes(report.image_path)
        except FileNotFoundError as exc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Report image not found",
            ) from exc

    async def analyze_image(self, image: UploadFile) -> ImageAnalysisResult:
        try:
            return await self.ai_service.analyze_upload(image)
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=str(exc),
            ) from exc


def get_department_for_category(category: IssueCategory) -> str:
    return DEPARTMENT_MAP[category]

