import uuid
from datetime import datetime, timedelta, timezone

from geoalchemy2.functions import ST_MakePoint
from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit import AuditFrame, AuditRun, AuditSuggestion
from app.models.enums import AuditRunStatus, AuditSuggestionStatus, AuditScanSource
from app.schemas.audit import AuditRunCreate


class AuditRunRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def list(self) -> list[AuditRun]:
        result = await self.db.execute(
            select(AuditRun).order_by(AuditRun.created_at.desc())
        )
        return list(result.scalars().all())

    async def get(self, run_id: uuid.UUID) -> AuditRun | None:
        result = await self.db.execute(select(AuditRun).where(AuditRun.id == run_id))
        return result.scalar_one_or_none()

    async def create(self, data: AuditRunCreate) -> AuditRun:
        now = datetime.now(timezone.utc)
        route_name = data.route_name
        if not route_name and data.latitude is not None and data.longitude is not None:
            route_name = f"Coordinates: {data.latitude:.6f}, {data.longitude:.6f}"

        run = AuditRun(
            id=uuid.uuid4(),
            municipality=data.municipality,
            route_name=route_name,
            scan_latitude=data.latitude,
            scan_longitude=data.longitude,
            notes=data.notes,
            status=AuditRunStatus.queued,
            frames_total=0,
            frames_done=0,
            created_at=now,
            updated_at=now,
        )
        self.db.add(run)
        await self.db.flush()
        return run

    async def set_status(self, run_id: uuid.UUID, status: str) -> None:
        await self.db.execute(
            update(AuditRun)
            .where(AuditRun.id == run_id)
            .values(status=status, updated_at=datetime.now(timezone.utc))
        )
        await self.db.flush()

    async def set_frames_total(self, run_id: uuid.UUID, total: int) -> None:
        await self.db.execute(
            update(AuditRun)
            .where(AuditRun.id == run_id)
            .values(frames_total=total, updated_at=datetime.now(timezone.utc))
        )
        await self.db.flush()

    async def increment_frames_done(self, run_id: uuid.UUID) -> None:
        result = await self.db.execute(select(AuditRun).where(AuditRun.id == run_id))
        run = result.scalar_one_or_none()
        if run:
            run.frames_done += 1
            run.updated_at = datetime.now(timezone.utc)
            await self.db.flush()


class AuditSuggestionRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def list_for_run(self, run_id: uuid.UUID) -> list[AuditSuggestion]:
        result = await self.db.execute(
            select(AuditSuggestion)
            .where(AuditSuggestion.audit_run_id == run_id)
            .order_by(AuditSuggestion.created_at.asc())
        )
        return list(result.scalars().all())

    async def get(self, suggestion_id: uuid.UUID) -> AuditSuggestion | None:
        result = await self.db.execute(
            select(AuditSuggestion).where(AuditSuggestion.id == suggestion_id)
        )
        return result.scalar_one_or_none()

    async def create_bulk(self, suggestions: list[dict]) -> list[AuditSuggestion]:
        objs = []
        for s in suggestions:
            obj = AuditSuggestion(
                id=uuid.uuid4(),
                audit_run_id=s["audit_run_id"],
                category=s["category"],
                status=AuditSuggestionStatus.pending_review,
                location=ST_MakePoint(s["longitude"], s["latitude"]),
                latitude=s["latitude"],
                longitude=s["longitude"],
                confidence=s["confidence"],
                severity=s.get("severity"),
                description=s.get("description"),
                model_name=s.get("model_name"),
                explanation=s.get("explanation"),
                image_url=s.get("image_url"),
                image_attribution=s.get("image_attribution"),
                department=s.get("department"),
                heading=s.get("heading"),
                pitch=s.get("pitch"),
                frame_index=s.get("frame_index"),
                detection_regions=s.get("detection_regions"),
                created_at=s.get("created_at", datetime.now(timezone.utc)),
            )
            self.db.add(obj)
            objs.append(obj)
        await self.db.flush()
        return objs

    async def review(
        self,
        suggestion: AuditSuggestion,
        status: str,
        reviewer_note: str | None,
    ) -> AuditSuggestion:
        suggestion.status = status
        suggestion.reviewer_note = reviewer_note
        await self.db.flush()
        return suggestion

    async def convert_to_report(
        self,
        suggestion: AuditSuggestion,
        report_id: uuid.UUID,
    ) -> AuditSuggestion:
        suggestion.status = AuditSuggestionStatus.converted_to_report
        suggestion.converted_report_id = report_id
        await self.db.flush()
        return suggestion


class AuditFrameRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def list_for_run(self, run_id: uuid.UUID) -> list[AuditFrame]:
        result = await self.db.execute(
            select(AuditFrame)
            .where(AuditFrame.audit_run_id == run_id)
            .order_by(AuditFrame.frame_index.asc())
        )
        return list(result.scalars().all())

    async def get_by_index(self, run_id: uuid.UUID, frame_index: int) -> AuditFrame | None:
        result = await self.db.execute(
            select(AuditFrame).where(
                AuditFrame.audit_run_id == run_id,
                AuditFrame.frame_index == frame_index,
            )
        )
        return result.scalar_one_or_none()

    async def get_max_frame_index(self, run_id: uuid.UUID) -> int | None:
        result = await self.db.execute(
            select(func.max(AuditFrame.frame_index)).where(AuditFrame.audit_run_id == run_id)
        )
        return result.scalar_one_or_none()

    async def count_on_demand_since(self, run_id: uuid.UUID, since: datetime) -> int:
        result = await self.db.execute(
            select(func.count())
            .select_from(AuditFrame)
            .where(
                AuditFrame.audit_run_id == run_id,
                AuditFrame.scan_source == AuditScanSource.on_demand,
                AuditFrame.created_at >= since,
            )
        )
        return int(result.scalar_one())

    async def update(self, frame: AuditFrame, data: dict) -> AuditFrame:
        for key, value in data.items():
            setattr(frame, key, value)
        await self.db.flush()
        return frame

    async def create(self, data: dict) -> AuditFrame:
        obj = AuditFrame(
            id=uuid.uuid4(),
            audit_run_id=data["audit_run_id"],
            frame_index=data["frame_index"],
            latitude=data["latitude"],
            longitude=data["longitude"],
            heading=data["heading"],
            pitch=data.get("pitch", 0),
            is_civic_issue=data.get("is_civic_issue", False),
            category=data.get("category"),
            confidence=data.get("confidence"),
            severity=data.get("severity"),
            description=data.get("description"),
            image_url=data.get("image_url"),
            detection_regions=data.get("detection_regions"),
            scan_source=data.get("scan_source", AuditScanSource.pipeline),
            model_name=data.get("model_name"),
            suggestion_id=data.get("suggestion_id"),
            created_at=data.get("created_at", datetime.now(timezone.utc)),
        )
        self.db.add(obj)
        await self.db.flush()
        return obj
