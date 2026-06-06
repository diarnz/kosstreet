import asyncio
import logging
import re
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from uuid import UUID

import httpx
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.engine import AsyncSessionLocal
from app.integrations.street_imagery import (
    GoogleStreetViewClient,
    StreetImageryFrameRequest,
    expand_point_to_corridor,
    is_no_imagery_placeholder,
)
from app.models.audit import AuditFrame, AuditRun, AuditSuggestion
from app.models.enums import AuditRunStatus, AuditScanSource, AuditSuggestionStatus, IssueCategory
from app.repositories.audit_repository import (
    AuditFrameRepository,
    AuditRunRepository,
    AuditSuggestionRepository,
)
from app.repositories.report_repository import ReportRepository
from app.schemas.audit import (
    AdminAuditRunContent,
    AdminAuditRunSummary,
    AuditRunAdminUpdate,
    AuditRunCreate,
    AuditSuggestionAdminUpdate,
    AuditSuggestionReview,
    SuggestionConversionResult,
    audit_frame_to_summary,
    audit_suggestion_to_read,
)
from app.services.ai_service import AIService
from app.services.report_service import get_department_for_category
from app.utils.route_geometry import build_scan_frames

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class PipelineFrame:
    index: int
    latitude: float
    longitude: float
    heading: int
    pitch: int = 0


KNOWN_ROUTES: dict[str, list[tuple[float, float]]] = {
    "bill clinton boulevard": [
        (42.6596, 21.1545),
        (42.65989424147778, 21.154962379465083),
        (42.66018848295556, 21.155424758930167),
        (42.66048272443334, 21.15588713839525),
        (42.660776965911126, 21.156349517860335),
        (42.66107120738891, 21.15681189732542),
        (42.66136544886669, 21.157274276790506),
        (42.661659690344464, 21.15773665625559),
        (42.66205170247266, 21.1583046165912),
        (42.66236102874594, 21.158748432548524),
        (42.66267035501923, 21.15919224850585),
        (42.66297968129252, 21.159636064463175),
        (42.6632890075658, 21.1600798804205),
        (42.66359833383909, 21.160523696377822),
        (42.66390766011238, 21.160967512335148),
        (42.664, 21.1611),
    ],
}

COORDINATE_ROUTE_RE = re.compile(
    r"^coordinates:\s*(?P<latitude>-?\d+(?:\.\d+)?)\s*,\s*(?P<longitude>-?\d+(?:\.\d+)?)$",
    re.IGNORECASE,
)


class AuditService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.run_repository = AuditRunRepository(db)
        self.suggestion_repository = AuditSuggestionRepository(db)
        self.frame_repository = AuditFrameRepository(db)
        self.report_repository = ReportRepository(db)
        self.gsv_client = GoogleStreetViewClient(
            api_key=settings.google_maps_api_key,
            size=settings.gsv_frame_size,
        )
        self.ai_service = AIService(settings)

    async def list_runs(self) -> list[AuditRun]:
        return await self.run_repository.list(visible_only=True)

    async def get_run(self, run_id: UUID, *, include_hidden: bool = False) -> AuditRun:
        run = await self.run_repository.get(run_id)
        if run is None or (not include_hidden and not run.is_visible):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Audit run not found",
            )
        return run

    async def create_run(
        self,
        payload: AuditRunCreate,
    ) -> AuditRun:
        run = await self.run_repository.create(payload)
        await self.db.commit()
        self._schedule_pipeline(run.id)
        return run

    def _schedule_pipeline(self, run_id: UUID) -> None:
        task = asyncio.create_task(self._run_pipeline(run_id))
        task.add_done_callback(
            lambda completed_task: self._log_pipeline_task_exception(run_id, completed_task)
        )

    @staticmethod
    def _log_pipeline_task_exception(run_id: UUID, task: asyncio.Task[None]) -> None:
        if task.cancelled():
            logger.info("Audit pipeline task was cancelled for run %s", run_id)
            return

        try:
            task.result()
        except Exception:
            logger.exception("Audit pipeline task crashed for run %s", run_id)

    async def list_suggestions(self, run_id: UUID) -> list[AuditSuggestion]:
        await self.get_run(run_id)
        return await self.suggestion_repository.list_for_run(run_id, visible_only=True)

    async def get_suggestion(self, suggestion_id: UUID, *, include_hidden: bool = False) -> AuditSuggestion:
        return await self._get_suggestion_or_404(suggestion_id, include_hidden=include_hidden)

    async def admin_list_runs(self) -> list[AdminAuditRunSummary]:
        runs = await self.run_repository.list_with_details(visible_only=False)
        return [
            AdminAuditRunSummary(
                id=run.id,
                municipality=run.municipality,
                route_name=run.route_name,
                scan_latitude=run.scan_latitude,
                scan_longitude=run.scan_longitude,
                notes=run.notes,
                status=run.status,
                frames_total=run.frames_total,
                frames_done=run.frames_done,
                is_visible=run.is_visible,
                created_at=run.created_at,
                suggestion_count=len(run.suggestions),
                civic_frame_count=sum(1 for frame in run.frames if frame.is_civic_issue),
            )
            for run in runs
        ]

    async def admin_get_run_content(self, run_id: UUID) -> AdminAuditRunContent:
        await self.get_run(run_id, include_hidden=True)
        suggestions = await self.suggestion_repository.list_for_run(run_id, visible_only=False)
        frames = await self.frame_repository.list_for_run(run_id)
        civic_frames = [frame for frame in frames if frame.is_civic_issue]
        return AdminAuditRunContent(
            suggestions=[audit_suggestion_to_read(suggestion) for suggestion in suggestions],
            frames=[audit_frame_to_summary(frame) for frame in civic_frames],
        )

    async def admin_update_run(self, run_id: UUID, payload: AuditRunAdminUpdate) -> AuditRun:
        run = await self.get_run(run_id, include_hidden=True)
        return await self.run_repository.update_fields(
            run,
            is_visible=payload.is_visible,
            notes=payload.notes,
        )

    async def admin_delete_run(self, run_id: UUID) -> None:
        run = await self.run_repository.get(run_id)
        if run is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Audit run not found",
            )
        await self.run_repository.delete(run)

    async def admin_update_suggestion(
        self,
        suggestion_id: UUID,
        payload: AuditSuggestionAdminUpdate,
    ) -> AuditSuggestion:
        suggestion = await self._get_suggestion_or_404(suggestion_id, include_hidden=True)
        return await self.suggestion_repository.update_fields(
            suggestion,
            is_visible=payload.is_visible,
        )

    async def admin_delete_suggestion(self, suggestion_id: UUID) -> None:
        suggestion = await self.suggestion_repository.get(suggestion_id)
        if suggestion is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Audit suggestion not found",
            )
        await self.suggestion_repository.delete(suggestion)

    async def review_suggestion(
        self,
        suggestion_id: UUID,
        payload: AuditSuggestionReview,
    ) -> AuditSuggestion:
        suggestion = await self._get_suggestion_or_404(suggestion_id)
        if suggestion.status == AuditSuggestionStatus.converted_to_report:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Audit suggestion is already converted to a report",
            )
        return await self.suggestion_repository.review(
            suggestion,
            payload.status,
            payload.reviewer_note,
        )

    async def list_frames(self, run_id: UUID) -> list[AuditFrame]:
        await self.get_run(run_id)
        return await self.frame_repository.list_for_run(run_id)

    async def list_scan_path(self, run_id: UUID) -> list[AuditFrame]:
        await self.get_run(run_id)
        return await self.frame_repository.list_for_run(run_id)

    async def get_on_demand_quota(self, run_id: UUID) -> dict[str, int | datetime]:
        await self.get_run(run_id)
        since = datetime.now(timezone.utc) - timedelta(hours=1)
        used = await self.frame_repository.count_on_demand_since(run_id, since)
        limit = settings.audit_on_demand_max_per_run_per_hour
        return {
            "limit": limit,
            "used": used,
            "remaining": max(0, limit - used),
            "resets_at": since + timedelta(hours=1),
        }

    async def analyze_view(
        self,
        run_id: UUID,
        latitude: float,
        longitude: float,
        heading: int,
        pitch: int,
    ) -> AuditFrame:
        await self.get_run(run_id)

        since = datetime.now(timezone.utc) - timedelta(hours=1)
        recent_on_demand = await self.frame_repository.count_on_demand_since(run_id, since)
        if recent_on_demand >= settings.audit_on_demand_max_per_run_per_hour:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="On-demand analyze rate limit reached for this audit run",
            )

        existing_frames = await self.frame_repository.list_for_run(run_id)
        existing = self._find_matching_frame(existing_frames, latitude, longitude, heading, pitch)
        frame_index = (
            existing.frame_index
            if existing is not None
            else (await self.frame_repository.get_max_frame_index(run_id) or -1) + 1
        )

        frame = PipelineFrame(
            index=frame_index,
            latitude=latitude,
            longitude=longitude,
            heading=heading,
            pitch=pitch,
        )

        request = StreetImageryFrameRequest(
            latitude=frame.latitude,
            longitude=frame.longitude,
            heading=frame.heading,
            pitch=frame.pitch,
        )
        street_frame = await asyncio.to_thread(self.gsv_client.fetch_frame, request)
        if is_no_imagery_placeholder(street_frame.data):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="No Street View imagery available for this view",
            )

        ai_result = await self.ai_service.analyze_image_bytes(street_frame.data)
        confidence = ai_result.confidence or 0.0
        regions = [region.model_dump() for region in ai_result.regions]
        is_actionable_issue = (
            ai_result.is_civic_issue
            and ai_result.category is not None
            and confidence >= settings.ai_confidence_threshold
        )

        suggestion_id: UUID | None = existing.suggestion_id if existing else None
        if is_actionable_issue and suggestion_id is None:
            category = IssueCategory(ai_result.category)
            suggestions = await self.suggestion_repository.create_bulk(
                [
                    {
                        "audit_run_id": run_id,
                        "category": category,
                        "latitude": frame.latitude,
                        "longitude": frame.longitude,
                        "confidence": confidence,
                        "severity": ai_result.severity,
                        "description": ai_result.description,
                        "model_name": settings.ai_model_name,
                        "explanation": "AI on-demand street view analysis.",
                        "image_url": self.gsv_client.build_frame_url(request),
                        "image_attribution": "Google Street View",
                        "department": get_department_for_category(category),
                        "heading": frame.heading,
                        "pitch": frame.pitch,
                        "frame_index": frame.index,
                        "detection_regions": regions or None,
                    }
                ]
            )
            suggestion_id = suggestions[0].id

        frame_payload = {
            "latitude": frame.latitude,
            "longitude": frame.longitude,
            "heading": frame.heading,
            "pitch": frame.pitch,
            "is_civic_issue": is_actionable_issue,
            "category": ai_result.category if is_actionable_issue else None,
            "confidence": confidence if ai_result.is_civic_issue else None,
            "severity": ai_result.severity if is_actionable_issue else None,
            "description": ai_result.description if is_actionable_issue else None,
            "image_url": self.gsv_client.build_frame_url(request),
            "detection_regions": regions or None,
            "model_name": settings.ai_model_name if ai_result.is_civic_issue else None,
            "suggestion_id": suggestion_id,
            "scan_source": AuditScanSource.on_demand,
        }

        if existing is not None:
            saved = await self.frame_repository.update(existing, frame_payload)
        else:
            saved = await self.frame_repository.create(
                {
                    "audit_run_id": run_id,
                    "frame_index": frame.index,
                    **frame_payload,
                }
            )

        await self.db.commit()
        return saved

    async def get_frame(self, run_id: UUID, frame_index: int) -> AuditFrame:
        await self.get_run(run_id)
        frame = await self.frame_repository.get_by_index(run_id, frame_index)
        if frame is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Audit frame not found",
            )
        return frame

    async def get_frame_image(self, run_id: UUID, frame_index: int) -> tuple[bytes, str]:
        frame = await self.get_frame(run_id, frame_index)
        return await self._fetch_frame_image(
            frame.latitude,
            frame.longitude,
            frame.heading,
            frame.pitch,
        )

    async def get_suggestion_frame_image(self, suggestion_id: UUID) -> tuple[bytes, str]:
        suggestion = await self._get_suggestion_or_404(suggestion_id)
        return await self._fetch_frame_image(
            suggestion.latitude,
            suggestion.longitude,
            suggestion.heading or 0,
            suggestion.pitch or 0,
        )

    async def _fetch_frame_image(
        self,
        latitude: float,
        longitude: float,
        heading: int,
        pitch: int,
    ) -> tuple[bytes, str]:
        request = StreetImageryFrameRequest(
            latitude=latitude,
            longitude=longitude,
            heading=heading,
            pitch=pitch,
        )
        street_frame = await asyncio.to_thread(self.gsv_client.fetch_frame, request)
        return street_frame.data, street_frame.content_type

    async def convert_to_report(self, suggestion_id: UUID) -> SuggestionConversionResult:
        suggestion = await self._get_suggestion_or_404(suggestion_id)
        if suggestion.status == AuditSuggestionStatus.converted_to_report:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Audit suggestion is already converted to a report",
            )

        report = await self.report_repository.create_from_suggestion(
            category=suggestion.category,
            latitude=suggestion.latitude,
            longitude=suggestion.longitude,
            description=suggestion.description,
            confidence=suggestion.confidence,
        )
        await self.suggestion_repository.convert_to_report(suggestion, report.id)
        return SuggestionConversionResult(report_id=report.id)

    async def _get_suggestion_or_404(
        self,
        suggestion_id: UUID,
        *,
        include_hidden: bool = False,
    ) -> AuditSuggestion:
        suggestion = await self.suggestion_repository.get(suggestion_id)
        if suggestion is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Audit suggestion not found",
            )
        if not include_hidden:
            if not suggestion.is_visible:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Audit suggestion not found",
                )
            run = await self.run_repository.get(suggestion.audit_run_id)
            if run is None or not run.is_visible:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Audit suggestion not found",
                )
        return suggestion

    async def _run_pipeline(self, run_id: UUID) -> None:
        async with AsyncSessionLocal() as db:
            run_repository = AuditRunRepository(db)
            suggestion_repository = AuditSuggestionRepository(db)
            frame_repository = AuditFrameRepository(db)

            try:
                await run_repository.set_status(run_id, AuditRunStatus.running)
                await db.commit()

                run = await run_repository.get(run_id)
                if run is None:
                    logger.warning("Audit run %s disappeared before pipeline start", run_id)
                    return

                waypoints = await self._resolve_waypoints(run)
                frames = self._build_frames(waypoints)

                await run_repository.set_frames_total(run_id, len(frames))
                await db.commit()

                for frame in frames:
                    try:
                        await self._process_frame(
                            run_id,
                            frame,
                            frame_repository,
                            suggestion_repository,
                        )
                    except Exception:
                        logger.exception("Failed to process audit frame for run %s", run_id)
                        await db.rollback()
                    finally:
                        await run_repository.increment_frames_done(run_id)
                        await db.commit()

                await run_repository.set_status(run_id, AuditRunStatus.completed)
                await db.commit()
            except Exception:
                logger.exception("Audit pipeline failed for run %s", run_id)
                await db.rollback()
                await run_repository.set_status(run_id, AuditRunStatus.failed)
                await db.commit()

    async def _process_frame(
        self,
        run_id: UUID,
        frame: PipelineFrame,
        frame_repository: AuditFrameRepository,
        suggestion_repository: AuditSuggestionRepository,
    ) -> None:
        request = StreetImageryFrameRequest(
            latitude=frame.latitude,
            longitude=frame.longitude,
            heading=frame.heading,
            pitch=frame.pitch,
        )
        street_frame = await asyncio.to_thread(self.gsv_client.fetch_frame, request)
        if is_no_imagery_placeholder(street_frame.data):
            logger.warning(
                "Skipping AI analysis for frame %s at %s,%s (no Street View imagery)",
                frame.index,
                frame.latitude,
                frame.longitude,
            )
            await frame_repository.create(
                {
                    "audit_run_id": run_id,
                    "frame_index": frame.index,
                    "latitude": frame.latitude,
                    "longitude": frame.longitude,
                    "heading": frame.heading,
                    "pitch": frame.pitch,
                    "is_civic_issue": False,
                    "category": None,
                    "confidence": None,
                    "severity": None,
                    "description": None,
                    "image_url": None,
                    "detection_regions": None,
                    "model_name": None,
                    "suggestion_id": None,
                    "scan_source": AuditScanSource.pipeline,
                }
            )
            return

        ai_result = await self.ai_service.analyze_image_bytes(street_frame.data)

        confidence = ai_result.confidence or 0.0
        regions = [region.model_dump() for region in ai_result.regions]
        is_actionable_issue = (
            ai_result.is_civic_issue
            and ai_result.category is not None
            and confidence >= settings.ai_confidence_threshold
        )
        suggestion_id: UUID | None = None

        if is_actionable_issue:
            category = IssueCategory(ai_result.category)
            suggestions = await suggestion_repository.create_bulk(
                [
                    {
                        "audit_run_id": run_id,
                        "category": category,
                        "latitude": frame.latitude,
                        "longitude": frame.longitude,
                        "confidence": confidence,
                        "severity": ai_result.severity,
                        "description": ai_result.description,
                        "model_name": settings.ai_model_name,
                        "explanation": "AI street-audit frame analysis.",
                        "image_url": self.gsv_client.build_frame_url(request),
                        "image_attribution": "Google Street View",
                        "department": get_department_for_category(category),
                        "heading": frame.heading,
                        "pitch": frame.pitch,
                        "frame_index": frame.index,
                        "detection_regions": regions or None,
                    }
                ]
            )
            suggestion_id = suggestions[0].id

        await frame_repository.create(
            {
                "audit_run_id": run_id,
                "frame_index": frame.index,
                "latitude": frame.latitude,
                "longitude": frame.longitude,
                "heading": frame.heading,
                "pitch": frame.pitch,
                "is_civic_issue": is_actionable_issue,
                "category": ai_result.category if is_actionable_issue else None,
                "confidence": confidence if ai_result.is_civic_issue else None,
                "severity": ai_result.severity if is_actionable_issue else None,
                "description": ai_result.description if is_actionable_issue else None,
                "image_url": self.gsv_client.build_frame_url(request),
                "detection_regions": regions or None,
                "model_name": settings.ai_model_name if ai_result.is_civic_issue else None,
                "suggestion_id": suggestion_id,
                "scan_source": AuditScanSource.pipeline,
            }
        )

    async def _resolve_waypoints(self, run: AuditRun) -> list[tuple[float, float]]:
        if run.scan_latitude is not None and run.scan_longitude is not None:
            return self._expand_scan_waypoints(run.scan_latitude, run.scan_longitude)

        route_name = run.route_name
        normalized = route_name.strip().lower()
        coordinate_match = COORDINATE_ROUTE_RE.match(route_name.strip())
        if coordinate_match:
            return self._expand_scan_waypoints(
                float(coordinate_match.group("latitude")),
                float(coordinate_match.group("longitude")),
            )

        if normalized in KNOWN_ROUTES:
            return KNOWN_ROUTES[normalized]

        if not settings.google_maps_api_key:
            raise ValueError("Google Maps API key is required for unknown audit routes")

        municipality = (run.municipality or "").strip()
        if municipality and municipality.lower() != "kosovo":
            query = f"{route_name}, {municipality}, Kosovo"
        else:
            query = f"{route_name}, Kosovo"
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.get(
                "https://maps.googleapis.com/maps/api/geocode/json",
                params={"address": query, "key": settings.google_maps_api_key},
            )
        response.raise_for_status()
        data = response.json()

        if not data.get("results"):
            raise ValueError(f"Could not geocode audit route: {route_name}")

        location = data["results"][0]["geometry"]["location"]
        return self._expand_scan_waypoints(float(location["lat"]), float(location["lng"]))

    def _expand_scan_waypoints(self, latitude: float, longitude: float) -> list[tuple[float, float]]:
        if not settings.google_maps_api_key:
            return [(latitude, longitude)]

        return expand_point_to_corridor(
            settings.google_maps_api_key,
            latitude,
            longitude,
        )

    def _build_frames(self, waypoints: list[tuple[float, float]]) -> list[PipelineFrame]:
        return [
            PipelineFrame(
                index=spec.index,
                latitude=spec.latitude,
                longitude=spec.longitude,
                heading=spec.heading,
                pitch=spec.pitch,
            )
            for spec in build_scan_frames(waypoints)
        ]

    @staticmethod
    def _find_matching_frame(
        frames: list[AuditFrame],
        latitude: float,
        longitude: float,
        heading: int,
        pitch: int,
    ) -> AuditFrame | None:
        for frame in frames:
            if (
                round(frame.latitude, 5) == round(latitude, 5)
                and round(frame.longitude, 5) == round(longitude, 5)
                and abs(frame.heading - heading) <= 15
                and abs(frame.pitch - pitch) <= 10
            ):
                return frame
        return None

