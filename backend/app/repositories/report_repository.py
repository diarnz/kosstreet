import uuid
from datetime import datetime, timezone

from geoalchemy2.functions import ST_MakePoint
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.enums import ActorType, ReportSource, TicketStatus
from app.models.report import Report, ReportWorkflowEvent
from app.schemas.report import ReportCreate


class ReportRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def list(
        self,
        *,
        status: str | None = None,
        category: str | None = None,
        source: str | None = None,
    ) -> list[Report]:
        q = select(Report).order_by(Report.created_at.desc())
        if status:
            q = q.where(Report.status == status)
        if category:
            q = q.where(Report.category == category)
        if source:
            q = q.where(Report.source == source)
        result = await self.db.execute(q)
        return list(result.scalars().all())

    async def get(self, report_id: uuid.UUID) -> Report | None:
        result = await self.db.execute(select(Report).where(Report.id == report_id))
        return result.scalar_one_or_none()

    async def get_with_events(self, report_id: uuid.UUID) -> Report | None:
        result = await self.db.execute(
            select(Report)
            .options(selectinload(Report.workflow_events))
            .where(Report.id == report_id)
        )
        return result.scalar_one_or_none()

    async def create(
        self,
        data: ReportCreate,
        *,
        image_path: str | None = None,
    ) -> Report:
        now = datetime.now(timezone.utc)
        report = Report(
            id=uuid.uuid4(),
            category=data.category,
            status=TicketStatus.new,
            source=data.source,
            location=ST_MakePoint(data.longitude, data.latitude),
            latitude=data.latitude,
            longitude=data.longitude,
            description=data.description,
            confidence=data.confidence,
            image_path=image_path,
            created_at=now,
            updated_at=now,
        )
        self.db.add(report)
        await self.db.flush()

        event = ReportWorkflowEvent(
            id=uuid.uuid4(),
            report_id=report.id,
            from_status=None,
            to_status=TicketStatus.new,
            note="Report received.",
            actor_type=ActorType.system,
            actor_label="KoStreet",
            created_at=now,
        )
        self.db.add(event)
        await self.db.flush()
        return report

    async def update_status(
        self,
        report: Report,
        new_status: str,
        *,
        note: str | None,
        actor_label: str = "Municipal operator",
    ) -> Report:
        now = datetime.now(timezone.utc)
        event = ReportWorkflowEvent(
            id=uuid.uuid4(),
            report_id=report.id,
            from_status=report.status,
            to_status=new_status,
            note=note,
            actor_type=ActorType.municipality,
            actor_label=actor_label,
            created_at=now,
        )
        self.db.add(event)

        if new_status == TicketStatus.resolved and note:
            report.resolution_note = note
        if new_status == TicketStatus.rejected and note:
            report.rejection_reason = note

        report.status = new_status
        report.updated_at = now
        await self.db.flush()
        return report

    async def create_from_suggestion(
        self,
        *,
        category: str,
        latitude: float,
        longitude: float,
        description: str | None,
        confidence: float | None,
    ) -> Report:
        now = datetime.now(timezone.utc)
        report = Report(
            id=uuid.uuid4(),
            category=category,
            status=TicketStatus.new,
            source=ReportSource.street_audit,
            location=ST_MakePoint(longitude, latitude),
            latitude=latitude,
            longitude=longitude,
            description=description,
            confidence=confidence,
            created_at=now,
            updated_at=now,
        )
        self.db.add(report)
        await self.db.flush()

        event = ReportWorkflowEvent(
            id=uuid.uuid4(),
            report_id=report.id,
            from_status=None,
            to_status=TicketStatus.new,
            note="Created from AI street-audit suggestion.",
            actor_type=ActorType.system,
            actor_label="KoStreet AI Audit",
            created_at=now,
        )
        self.db.add(event)
        await self.db.flush()
        return report
