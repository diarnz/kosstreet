import asyncio
import logging
import re
from dataclasses import dataclass
from uuid import UUID

import httpx
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.engine import AsyncSessionLocal
from app.integrations.street_imagery import (
    GoogleStreetViewClient,
    StreetImageryFrameRequest,
)
from app.models.audit import AuditRun, AuditSuggestion
from app.models.enums import AuditRunStatus, AuditSuggestionStatus, IssueCategory
from app.repositories.audit_repository import AuditRunRepository, AuditSuggestionRepository
from app.repositories.report_repository import ReportRepository
from app.schemas.audit import (
    AuditRunCreate,
    AuditSuggestionReview,
    SuggestionConversionResult,
)
from app.services.ai_service import AIService
from app.services.report_service import get_department_for_category

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class AuditFrame:
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

HEADINGS = (0, 90, 180, 270)
COORDINATE_ROUTE_RE = re.compile(
    r"^coordinates:\s*(?P<latitude>-?\d+(?:\.\d+)?)\s*,\s*(?P<longitude>-?\d+(?:\.\d+)?)$",
    re.IGNORECASE,
)


class AuditService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.run_repository = AuditRunRepository(db)
        self.suggestion_repository = AuditSuggestionRepository(db)
        self.report_repository = ReportRepository(db)
        self.gsv_client = GoogleStreetViewClient(
            api_key=settings.google_maps_api_key,
            size=settings.gsv_frame_size,
        )
        self.ai_service = AIService(settings)

    async def list_runs(self) -> list[AuditRun]:
        return await self.run_repository.list()

    async def get_run(self, run_id: UUID) -> AuditRun:
        run = await self.run_repository.get(run_id)
        if run is None:
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
        return await self.suggestion_repository.list_for_run(run_id)

    async def get_suggestion(self, suggestion_id: UUID) -> AuditSuggestion:
        return await self._get_suggestion_or_404(suggestion_id)

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

    async def _get_suggestion_or_404(self, suggestion_id: UUID) -> AuditSuggestion:
        suggestion = await self.suggestion_repository.get(suggestion_id)
        if suggestion is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Audit suggestion not found",
            )
        return suggestion

    async def _run_pipeline(self, run_id: UUID) -> None:
        async with AsyncSessionLocal() as db:
            run_repository = AuditRunRepository(db)
            suggestion_repository = AuditSuggestionRepository(db)

            try:
                await run_repository.set_status(run_id, AuditRunStatus.running)
                await db.commit()

                run = await run_repository.get(run_id)
                if run is None:
                    logger.warning("Audit run %s disappeared before pipeline start", run_id)
                    return

                waypoints = await self._resolve_waypoints(run.route_name)
                frames = self._build_frames(waypoints)

                await run_repository.set_frames_total(run_id, len(frames))
                await db.commit()

                for frame in frames:
                    try:
                        await self._process_frame(
                            run_id,
                            frame,
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
        frame: AuditFrame,
        suggestion_repository: AuditSuggestionRepository,
    ) -> None:
        request = StreetImageryFrameRequest(
            latitude=frame.latitude,
            longitude=frame.longitude,
            heading=frame.heading,
            pitch=frame.pitch,
        )
        street_frame = await asyncio.to_thread(self.gsv_client.fetch_frame, request)
        ai_result = await self.ai_service.analyze_image_bytes(street_frame.data)

        confidence = ai_result.confidence or 0.0
        if (
            not ai_result.is_civic_issue
            or ai_result.category is None
            or confidence < settings.ai_confidence_threshold
        ):
            return

        category = IssueCategory(ai_result.category)
        await suggestion_repository.create_bulk(
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
                }
            ]
        )

    async def _resolve_waypoints(self, route_name: str) -> list[tuple[float, float]]:
        normalized = route_name.strip().lower()
        coordinate_match = COORDINATE_ROUTE_RE.match(route_name.strip())
        if coordinate_match:
            return [
                (
                    float(coordinate_match.group("latitude")),
                    float(coordinate_match.group("longitude")),
                )
            ]

        if normalized in KNOWN_ROUTES:
            return KNOWN_ROUTES[normalized]

        if not settings.google_maps_api_key:
            raise ValueError("Google Maps API key is required for unknown audit routes")

        query = f"{route_name}, Prishtina, Kosovo"
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
        return [(float(location["lat"]), float(location["lng"]))]

    def _build_frames(self, waypoints: list[tuple[float, float]]) -> list[AuditFrame]:
        return [
            AuditFrame(latitude=latitude, longitude=longitude, heading=heading)
            for latitude, longitude in waypoints
            for heading in HEADINGS
        ]

