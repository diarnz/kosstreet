import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from geoalchemy2.functions import ST_MakePoint
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.audit import AuditFrame, AuditRun, AuditSuggestion
from app.models.enums import (
    ActorType,
    AuditRunStatus,
    AuditSuggestionStatus,
    ReportSource,
    TicketStatus,
)
from app.models.report import Report, ReportWorkflowEvent
from app.services.audit_service import HEADINGS, KNOWN_ROUTES

SEED_NAMESPACE = uuid.UUID("4ee7f9ee-bd6b-4983-9551-87dc2590e2f3")
PROJECT_ROOT = Path(__file__).resolve().parents[3]
AUDIT_RESULTS_PATH = PROJECT_ROOT / "ai" / "data" / "demo" / "audit_results.json"
DEMO_ROUTE_KEY = "bill clinton boulevard"


def _seed_uuid(name: str) -> uuid.UUID:
    return uuid.uuid5(SEED_NAMESPACE, name)


def _dt(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _frame_key(
    latitude: float,
    longitude: float,
    heading: int,
    pitch: int = 0,
) -> tuple[float, float, int, int]:
    return (round(latitude, 10), round(longitude, 10), heading, pitch)


def build_demo_frame_plan() -> list[dict[str, float | int]]:
    waypoints = KNOWN_ROUTES[DEMO_ROUTE_KEY]
    plan: list[dict[str, float | int]] = []
    frame_index = 0

    for latitude, longitude in waypoints:
        for heading in HEADINGS:
            plan.append(
                {
                    "frame_index": frame_index,
                    "latitude": latitude,
                    "longitude": longitude,
                    "heading": heading,
                    "pitch": 0,
                }
            )
            frame_index += 1

    return plan


def index_demo_detections(detections: list[dict[str, Any]]) -> dict[tuple[float, float, int, int], dict[str, Any]]:
    indexed: dict[tuple[float, float, int, int], dict[str, Any]] = {}

    for detection in detections:
        key = _frame_key(
            float(detection["latitude"]),
            float(detection["longitude"]),
            int(detection.get("heading", 0)),
            int(detection.get("pitch", 0)),
        )
        indexed[key] = detection

    return indexed


def regions_from_detection(detection: dict[str, Any]) -> list[dict[str, float]] | None:
    raw_regions = detection.get("regions")
    if not isinstance(raw_regions, list) or not raw_regions:
        return None

    regions: list[dict[str, float]] = []
    for item in raw_regions:
        if not isinstance(item, dict):
            continue
        try:
            regions.append(
                {
                    "center_x": float(item["center_x"]),
                    "center_y": float(item["center_y"]),
                    "radius": float(item["radius"]),
                }
            )
        except (KeyError, TypeError, ValueError):
            continue

    return regions or None


async def seed_demo_data(db: AsyncSession) -> None:
    existing_reports = await db.scalar(select(func.count()).select_from(Report))
    if existing_reports and existing_reports > 0:
        return

    _seed_reports(db)
    _seed_audit_run_frames_and_suggestions(db)
    await db.flush()


def _seed_reports(db: AsyncSession) -> None:
    report_specs = [
        {
            "name": "demo-report-pothole-001",
            "category": "pothole",
            "status": TicketStatus.in_progress,
            "latitude": 42.6629,
            "longitude": 21.1655,
            "description": "Large road-surface damage near a busy junction; vehicles are slowing sharply.",
            "created_at": "2026-05-22T08:12:00+00:00",
            "updated_at": "2026-05-22T10:35:00+00:00",
            "events": [
                (None, TicketStatus.new, "Citizen report received through the mobile flow.", "2026-05-22T08:12:00+00:00"),
                (TicketStatus.new, TicketStatus.verified, "Municipal intake verified the road defect and location.", "2026-05-22T09:05:00+00:00"),
                (TicketStatus.verified, TicketStatus.in_progress, "Roads/Public Works prepared a repair task.", "2026-05-22T10:35:00+00:00"),
            ],
        },
        {
            "name": "demo-report-garbage-001",
            "category": "garbage",
            "status": TicketStatus.assigned,
            "latitude": 42.6598,
            "longitude": 21.1587,
            "description": "Illegal dumping next to public bins; bags are blocking pedestrian movement.",
            "created_at": "2026-05-22T07:44:00+00:00",
            "updated_at": "2026-05-22T09:30:00+00:00",
            "events": [
                (None, TicketStatus.new, "Citizen report received.", "2026-05-22T07:44:00+00:00"),
                (TicketStatus.verified, TicketStatus.assigned, "Sanitation team selected as suggested department.", "2026-05-22T09:30:00+00:00"),
            ],
        },
        {
            "name": "demo-report-light-001",
            "category": "broken_streetlight",
            "status": TicketStatus.verified,
            "latitude": 42.6671,
            "longitude": 21.1623,
            "description": "Streetlight fixture appears damaged near the pedestrian crossing.",
            "created_at": "2026-05-21T19:20:00+00:00",
            "updated_at": "2026-05-22T08:25:00+00:00",
            "events": [
                (None, TicketStatus.new, "Citizen report received after dark.", "2026-05-21T19:20:00+00:00"),
                (TicketStatus.new, TicketStatus.verified, "Issue verified for electrical infrastructure review.", "2026-05-22T08:25:00+00:00"),
            ],
        },
        {
            "name": "demo-report-sidewalk-001",
            "category": "blocked_sidewalk",
            "status": TicketStatus.new,
            "latitude": 42.6609,
            "longitude": 21.1701,
            "description": "Construction material is blocking most of the sidewalk near a school route.",
            "created_at": "2026-05-22T11:02:00+00:00",
            "updated_at": "2026-05-22T11:02:00+00:00",
            "events": [
                (None, TicketStatus.new, "Citizen report received and awaiting municipal review.", "2026-05-22T11:02:00+00:00"),
            ],
        },
        {
            "name": "demo-report-sign-001",
            "category": "damaged_sign",
            "status": TicketStatus.resolved,
            "latitude": 42.6645,
            "longitude": 21.1569,
            "description": "Bent traffic sign is difficult to read from the right lane.",
            "resolution_note": "Damaged sign replaced by Public Works team in the demo scenario.",
            "created_at": "2026-05-20T13:16:00+00:00",
            "updated_at": "2026-05-21T15:10:00+00:00",
            "events": [
                (None, TicketStatus.new, "Citizen report received.", "2026-05-20T13:16:00+00:00"),
                (TicketStatus.in_progress, TicketStatus.resolved, "Damaged sign replaced by Public Works team in the demo scenario.", "2026-05-21T15:10:00+00:00"),
            ],
        },
    ]

    for spec in report_specs:
        report_id = _seed_uuid(spec["name"])
        db.add(
            Report(
                id=report_id,
                category=spec["category"],
                status=spec["status"],
                source=ReportSource.citizen,
                location=ST_MakePoint(spec["longitude"], spec["latitude"]),
                latitude=spec["latitude"],
                longitude=spec["longitude"],
                description=spec["description"],
                confidence=None,
                resolution_note=spec.get("resolution_note"),
                rejection_reason=None,
                created_at=_dt(spec["created_at"]),
                updated_at=_dt(spec["updated_at"]),
            )
        )
        for index, (from_status, to_status, note, created_at) in enumerate(spec["events"]):
            db.add(
                ReportWorkflowEvent(
                    id=_seed_uuid(f"{spec['name']}-event-{index}"),
                    report_id=report_id,
                    from_status=from_status,
                    to_status=to_status,
                    note=note,
                    actor_type=ActorType.system if from_status is None else ActorType.municipality,
                    actor_label="KoStreet demo",
                    created_at=_dt(created_at),
                )
            )


def _seed_audit_run_frames_and_suggestions(db: AsyncSession) -> None:
    audit_data = _load_audit_results()
    run_id = _seed_uuid("bill-clinton-blvd-001")
    scanned_at = _dt(audit_data.get("scanned_at", "2026-05-22T00:00:00+00:00"))
    detections = audit_data.get("detections", [])
    detections_by_frame = index_demo_detections(detections)
    frame_plan = build_demo_frame_plan()

    db.add(
        AuditRun(
            id=run_id,
            municipality=audit_data.get("municipality", "Prishtina"),
            route_name=audit_data.get("route_name", "Bill Clinton Boulevard Audit"),
            notes="Seeded from prepared AI street-audit demo results.",
            status=AuditRunStatus.completed,
            frames_total=len(frame_plan),
            frames_done=len(frame_plan),
            created_at=scanned_at,
            updated_at=scanned_at,
        )
    )

    frame_index_by_key = {
        _frame_key(
            float(spec["latitude"]),
            float(spec["longitude"]),
            int(spec["heading"]),
            int(spec["pitch"]),
        ): int(spec["frame_index"])
        for spec in frame_plan
    }

    for frame_spec in frame_plan:
        frame_index = int(frame_spec["frame_index"])
        latitude = float(frame_spec["latitude"])
        longitude = float(frame_spec["longitude"])
        heading = int(frame_spec["heading"])
        pitch = int(frame_spec["pitch"])
        frame_key = _frame_key(latitude, longitude, heading, pitch)
        detection = detections_by_frame.get(frame_key)
        regions = regions_from_detection(detection) if detection else None

        db.add(
            AuditFrame(
                id=_seed_uuid(f"bill-clinton-blvd-001-frame-{frame_index}"),
                audit_run_id=run_id,
                frame_index=frame_index,
                latitude=latitude,
                longitude=longitude,
                heading=heading,
                pitch=pitch,
                image_url=_build_street_view_url(latitude, longitude, heading, pitch),
                is_civic_issue=detection is not None,
                category=detection["category"] if detection else None,
                confidence=float(detection["confidence"]) if detection else None,
                severity=detection.get("severity") if detection else None,
                description=detection.get("description") if detection else None,
                detection_regions=regions,
                model_name=settings.ai_model_name if detection else None,
                created_at=scanned_at,
            )
        )

    for index, detection in enumerate(detections):
        latitude = float(detection["latitude"])
        longitude = float(detection["longitude"])
        heading = int(detection.get("heading", 0))
        pitch = int(detection.get("pitch", 0))
        frame_key = _frame_key(latitude, longitude, heading, pitch)
        frame_index = frame_index_by_key.get(frame_key)
        if frame_index is None:
            continue

        suggestion_id = _seed_uuid(f"bill-clinton-blvd-001-suggestion-{index}")
        regions = regions_from_detection(detection)

        db.add(
            AuditSuggestion(
                id=suggestion_id,
                audit_run_id=run_id,
                category=detection["category"],
                status=AuditSuggestionStatus.pending_review,
                location=ST_MakePoint(longitude, latitude),
                latitude=latitude,
                longitude=longitude,
                confidence=float(detection["confidence"]),
                severity=detection.get("severity"),
                description=detection.get("description"),
                model_name=settings.ai_model_name,
                explanation="Seeded AI detection from prepared street-audit results.",
                image_url=_build_street_view_url(latitude, longitude, heading, pitch),
                image_attribution="Google Street View",
                department=detection.get("department"),
                heading=heading,
                pitch=pitch,
                frame_index=frame_index,
                detection_regions=regions,
                created_at=scanned_at,
            )
        )

    _link_seeded_frame_suggestions(db, detections, frame_plan)


def _link_seeded_frame_suggestions(
    db: AsyncSession,
    detections: list[dict[str, Any]],
    frame_plan: list[dict[str, float | int]],
) -> None:
    frame_index_by_key = {
        _frame_key(
            float(spec["latitude"]),
            float(spec["longitude"]),
            int(spec["heading"]),
            int(spec["pitch"]),
        ): int(spec["frame_index"])
        for spec in frame_plan
    }

    for index, detection in enumerate(detections):
        frame_key = _frame_key(
            float(detection["latitude"]),
            float(detection["longitude"]),
            int(detection.get("heading", 0)),
            int(detection.get("pitch", 0)),
        )
        frame_index = frame_index_by_key.get(frame_key)
        if frame_index is None:
            continue

        suggestion_id = _seed_uuid(f"bill-clinton-blvd-001-suggestion-{index}")
        frame_id = _seed_uuid(f"bill-clinton-blvd-001-frame-{frame_index}")

        for obj in db.new:
            if isinstance(obj, AuditFrame) and obj.id == frame_id:
                obj.suggestion_id = suggestion_id
                break


def _load_audit_results() -> dict[str, Any]:
    if not AUDIT_RESULTS_PATH.exists():
        return {
            "route_name": "Bill Clinton Boulevard Audit",
            "municipality": "Prishtina",
            "scanned_at": datetime.now(timezone.utc).isoformat(),
            "total_frames_analyzed": 0,
            "detections": [],
        }
    return json.loads(AUDIT_RESULTS_PATH.read_text(encoding="utf-8"))


def _build_street_view_url(latitude: float, longitude: float, heading: int, pitch: int) -> str:
    return (
        "https://maps.googleapis.com/maps/api/streetview"
        f"?size={settings.gsv_frame_size}x{settings.gsv_frame_size}"
        f"&location={latitude},{longitude}"
        f"&heading={heading}"
        f"&pitch={pitch}"
        f"&key={settings.google_maps_api_key}"
    )
