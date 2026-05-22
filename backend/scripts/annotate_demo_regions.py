import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
AUDIT_RESULTS_PATH = PROJECT_ROOT / "ai" / "data" / "demo" / "audit_results.json"

RADIUS = {"low": 0.06, "medium": 0.09, "high": 0.12, "critical": 0.14}


def regions_for(det: dict, index: int) -> list[dict[str, float]]:
    category = det["category"]
    heading = int(det.get("heading", 0))
    severity = det.get("severity", "medium")
    radius = RADIUS.get(severity, 0.09)
    lane_shift = (index % 4) * 0.03

    if category == "pothole":
        center_x = 0.46 + lane_shift
        center_y = 0.70 + (0.02 if heading in (0, 180) else 0.05)
    elif category == "garbage":
        center_x = 0.28 if heading in (90, 270) else 0.68
        center_y = 0.58 + lane_shift
    elif category == "broken_streetlight":
        center_x = 0.42 + lane_shift
        center_y = 0.24 + (0.03 if heading == 180 else 0.0)
    else:
        center_x, center_y = 0.5, 0.5

    return [
        {
            "center_x": round(min(max(center_x, 0.08), 0.92), 3),
            "center_y": round(min(max(center_y, 0.08), 0.92), 3),
            "radius": radius,
        }
    ]


def main() -> None:
    data = json.loads(AUDIT_RESULTS_PATH.read_text(encoding="utf-8"))
    detections = data.get("detections", [])

    for index, detection in enumerate(detections):
        detection["regions"] = regions_for(detection, index)

    AUDIT_RESULTS_PATH.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    print(f"Annotated {len(detections)} detections in {AUDIT_RESULTS_PATH}")


if __name__ == "__main__":
    main()
