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
from app.services.audit_service import KNOWN_ROUTES
from app.utils.route_geometry import build_scan_frames
from app.models.report import Report, ReportWorkflowEvent
from app.utils.detection_regions import sanitize_detection_regions

SEED_NAMESPACE = uuid.UUID("4ee7f9ee-bd6b-4983-9551-87dc2590e2f3")
PROJECT_ROOT = Path(__file__).resolve().parents[3]
AUDIT_RESULTS_PATH = PROJECT_ROOT / "ai" / "data" / "demo" / "audit_results.json"


def _seed_uuid(name: str) -> uuid.UUID:
    return uuid.uuid5(SEED_NAMESPACE, name)


def _dt(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


async def seed_demo_data(db: AsyncSession) -> None:
    existing_reports = await db.scalar(select(func.count()).select_from(Report))
    if existing_reports and existing_reports > 0:
        return

    _seed_reports(db)
    _seed_audit_run_and_suggestions(db)
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


def _seed_audit_run_and_suggestions(db: AsyncSession) -> None:
    audit_data = _load_audit_results()
    run_id = _seed_uuid("bill-clinton-blvd-001")
    scanned_at = _dt(audit_data.get("scanned_at", "2026-05-22T00:00:00+00:00"))
    route_frames = _build_demo_route_frames()
    detections_by_frame = _index_detections_by_frame(
        audit_data.get("detections", []),
        route_frames,
    )

    db.add(
        AuditRun(
            id=run_id,
            municipality=audit_data.get("municipality", "Kosovo"),
            route_name=audit_data.get("route_name", "Bill Clinton Boulevard Audit"),
            notes="Seeded from prepared AI street-audit demo results.",
            status=AuditRunStatus.completed,
            frames_total=len(route_frames),
            frames_done=len(route_frames),
            created_at=scanned_at,
            updated_at=scanned_at,
        )
    )

    suggestion_ids_by_frame: dict[int, uuid.UUID] = {}

    for frame_index, detection in detections_by_frame.items():
        latitude = float(detection["latitude"])
        longitude = float(detection["longitude"])
        heading = int(detection.get("heading", 0))
        pitch = int(detection.get("pitch", 0))
        severity = detection.get("severity")
        regions = _demo_detection_regions(frame_index, severity)
        suggestion_id = _seed_uuid(f"bill-clinton-blvd-001-suggestion-{frame_index}")

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
                severity=severity,
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
        suggestion_ids_by_frame[frame_index] = suggestion_id

    for frame in route_frames:
        frame_index = frame["frame_index"]
        detection = detections_by_frame.get(frame_index)
        regions = _demo_detection_regions(frame_index, detection.get("severity") if detection else None)

        db.add(
            AuditFrame(
                id=_seed_uuid(f"bill-clinton-blvd-001-frame-{frame_index}"),
                audit_run_id=run_id,
                frame_index=frame_index,
                latitude=frame["latitude"],
                longitude=frame["longitude"],
                heading=frame["heading"],
                pitch=frame["pitch"],
                is_civic_issue=detection is not None,
                category=detection["category"] if detection else None,
                confidence=float(detection["confidence"]) if detection else None,
                severity=detection.get("severity") if detection else None,
                description=detection.get("description") if detection else None,
                image_url=_build_street_view_url(
                    float(frame["latitude"]),
                    float(frame["longitude"]),
                    int(frame["heading"]),
                    int(frame["pitch"]),
                )
                if detection
                else None,
                detection_regions=regions if detection else None,
                scan_source="pipeline",
                model_name=settings.ai_model_name if detection else None,
                suggestion_id=suggestion_ids_by_frame.get(frame_index),
                created_at=scanned_at,
            )
        )


def _build_demo_route_frames() -> list[dict[str, float | int]]:
    waypoints = KNOWN_ROUTES["bill clinton boulevard"]
    return [
        {
            "frame_index": spec.index,
            "latitude": spec.latitude,
            "longitude": spec.longitude,
            "heading": spec.heading,
            "pitch": spec.pitch,
        }
        for spec in build_scan_frames(waypoints)
    ]


def _frame_match_key(
    latitude: float,
    longitude: float,
) -> tuple[float, float]:
    return (round(latitude, 8), round(longitude, 8))


def _index_detections_by_frame(
    detections: list[dict[str, Any]],
    route_frames: list[dict[str, float | int]],
) -> dict[int, dict[str, Any]]:
    frame_lookup = {
        _frame_match_key(float(frame["latitude"]), float(frame["longitude"])): int(
            frame["frame_index"]
        )
        for frame in route_frames
    }
    indexed: dict[int, dict[str, Any]] = {}
    for detection in detections:
        key = _frame_match_key(float(detection["latitude"]), float(detection["longitude"]))
        frame_index = frame_lookup.get(key)
        if frame_index is not None and frame_index not in indexed:
            indexed[frame_index] = detection
    return indexed


def _demo_detection_regions(frame_index: int, severity: str | None) -> list[dict[str, float]] | None:
    if severity is None:
        return None

    centers = [
        (0.42, 0.68),
        (0.55, 0.62),
        (0.38, 0.58),
        (0.61, 0.71),
        (0.47, 0.54),
    ]
    center_x, center_y = centers[frame_index % len(centers)]
    return sanitize_detection_regions(
        [{"center_x": center_x, "center_y": center_y}],
        severity,
    ) or None


def _load_audit_results() -> dict[str, Any]:
    if not AUDIT_RESULTS_PATH.exists():
        return {
            "route_name": "Bill Clinton Boulevard Audit",
            "municipality": "Kosovo",
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
