"""
Pre-compute street audit detection results for the demo route.
Run ONCE before the hackathon pitch. Saves audit_results.json which the
backend serves during the demo instead of calling the AI live.

Run from the ai/ directory:
    python data/demo/precompute_audit.py

Requires: AI service running on port 8001
    uvicorn kostreet_ai.main:app --port 8001
"""

import json
import pathlib
import sys
from datetime import datetime, timezone
from itertools import cycle

import httpx

DEMO_DIR = pathlib.Path(__file__).parent
AI_BASE = "http://localhost:8001"

ROUTE_NAME = "Bill Clinton Boulevard Audit"
MUNICIPALITY = "Kosovo"

# Reduced demo scan — fast enough to pre-compute, impressive enough to show
DEMO_WAYPOINTS = [
    {"lat": 42.6596, "lng": 21.1545},
    {"lat": 42.6617, "lng": 21.1578},
    {"lat": 42.6640, "lng": 21.1611},
]
DEMO_STEP_METERS = 50
DEMO_HEADINGS = [0, 90, 180, 270]
DEMO_PITCHES = [0]

# Images cycled across frames — civic issues guaranteed
FRAME_IMAGES = [
    "pothole_01.jpg",
    "garbage_01.jpg",
    "streetlight_02.jpg",
    "clean_01.jpg",
    "pothole_01.jpg",
    "clean_01.jpg",
]

DEPARTMENT_MAP = {
    "pothole": "Roads / Public Works",
    "garbage": "Sanitation",
    "broken_streetlight": "Electrical / Infrastructure",
    "blocked_sidewalk": "Urban Maintenance",
    "damaged_sign": "Public Works",
    "other": "General",
}


def check_service() -> bool:
    try:
        r = httpx.get(f"{AI_BASE}/health", timeout=5.0)
        return r.status_code == 200
    except Exception:
        return False


def get_scan_plan(client: httpx.Client) -> list[dict]:
    payload = {
        "waypoints": DEMO_WAYPOINTS,
        "step_meters": DEMO_STEP_METERS,
        "headings": DEMO_HEADINGS,
        "pitches": DEMO_PITCHES,
    }
    r = client.post(f"{AI_BASE}/api/v1/audit/plan", json=payload, timeout=10.0)
    r.raise_for_status()
    return r.json()["scan_points"]


def analyze_frame(client: httpx.Client, image_path: pathlib.Path, scan_point: dict) -> dict | None:
    image_bytes = image_path.read_bytes()
    import base64
    b64 = base64.b64encode(image_bytes).decode()
    payload = {
        "image_base64": b64,
        "latitude": scan_point["latitude"],
        "longitude": scan_point["longitude"],
        "heading": scan_point["heading"],
        "pitch": scan_point["pitch"],
    }
    r = client.post(f"{AI_BASE}/api/v1/audit/analyze-frame", json=payload, timeout=30.0)
    r.raise_for_status()
    data = r.json()
    return data["detections"][0] if data["detections"] else None


def run() -> None:
    print("KoStreet AI - Pre-compute Street Audit Results")
    print("=" * 50)

    if not check_service():
        print("ERROR: AI service is not running on port 8001.")
        print("Start it with: uvicorn kostreet_ai.main:app --port 8001")
        sys.exit(1)
    print("AI service: OK")

    image_cycle = cycle(FRAME_IMAGES)
    all_detections: list[dict] = []
    frames_analyzed = 0

    with httpx.Client(timeout=35.0) as client:
        scan_points = get_scan_plan(client)
        print(f"Scan plan: {len(scan_points)} frames")
        print()

        for i, point in enumerate(scan_points):
            image_name = next(image_cycle)
            image_path = DEMO_DIR / image_name
            if not image_path.exists():
                print(f"  [{i+1:3}/{len(scan_points)}] SKIP   {image_name} not found")
                continue

            detection = analyze_frame(client, image_path, point)
            frames_analyzed += 1

            if detection:
                detection["department"] = DEPARTMENT_MAP.get(detection["category"], "General")
                detection["source"] = "street_audit"
                all_detections.append(detection)
                print(f"  [{i+1:3}/{len(scan_points)}] FOUND  {detection['category']:20s} conf={detection['confidence']:.2f}  ({image_name})")
            else:
                print(f"  [{i+1:3}/{len(scan_points)}] clean  {image_name}")

    # Deduplication via the geospatial module directly
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "src"))
    from kostreet_ai.geospatial.deduplication import deduplicate_and_filter
    from kostreet_ai.schemas import DetectionWithLocation, IssueCategory, IssueSeverity

    det_objects = [
        DetectionWithLocation(
            category=IssueCategory(d["category"]),
            confidence=d["confidence"],
            severity=IssueSeverity(d["severity"]),
            description=d["description"],
            is_civic_issue=d["is_civic_issue"],
            latitude=d["latitude"],
            longitude=d["longitude"],
            heading=d["heading"],
            pitch=d["pitch"],
        )
        for d in all_detections
    ]

    deduped = deduplicate_and_filter(det_objects, radius_meters=20.0, confidence_threshold=0.55)

    final_detections = []
    for d in deduped:
        final_detections.append({
            "category": d.category.value,
            "confidence": d.confidence,
            "severity": d.severity.value,
            "description": d.description,
            "is_civic_issue": d.is_civic_issue,
            "latitude": d.latitude,
            "longitude": d.longitude,
            "heading": d.heading,
            "pitch": d.pitch,
            "department": DEPARTMENT_MAP.get(d.category.value, "General"),
            "source": "street_audit",
        })

    by_category: dict[str, int] = {}
    for d in final_detections:
        by_category[d["category"]] = by_category.get(d["category"], 0) + 1

    output = {
        "route_name": ROUTE_NAME,
        "municipality": MUNICIPALITY,
        "scanned_at": datetime.now(timezone.utc).isoformat(),
        "total_frames_analyzed": frames_analyzed,
        "detections": final_detections,
        "summary": {
            "total_detections": len(final_detections),
            "by_category": by_category,
        },
    }

    out_path = DEMO_DIR / "audit_results.json"
    out_path.write_text(json.dumps(output, indent=2), encoding="utf-8")

    print()
    print("=" * 50)
    print(f"Frames analyzed : {frames_analyzed}")
    print(f"Raw detections  : {len(all_detections)}")
    print(f"After dedup     : {len(final_detections)}")
    print(f"By category     : {by_category}")
    print(f"Saved to        : {out_path}")
    print()
    if len(final_detections) >= 3:
        print("audit_results.json is READY for the demo.")
    else:
        print("WARNING: fewer than 3 detections. Add more civic images to FRAME_IMAGES.")


if __name__ == "__main__":
    run()
