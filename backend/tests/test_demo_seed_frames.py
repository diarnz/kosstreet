import json
from pathlib import Path

from app.seeds.demo import (
    build_demo_frame_plan,
    index_demo_detections,
    regions_from_detection,
)

AUDIT_RESULTS_PATH = (
    Path(__file__).resolve().parents[2] / "ai" / "data" / "demo" / "audit_results.json"
)


def test_build_demo_frame_plan_has_64_frames() -> None:
    plan = build_demo_frame_plan()
    assert len(plan) == 64
    assert plan[0]["frame_index"] == 0
    assert plan[-1]["frame_index"] == 63


def test_demo_audit_results_include_regions_for_all_detections() -> None:
    data = json.loads(AUDIT_RESULTS_PATH.read_text(encoding="utf-8"))
    detections = data["detections"]

    assert len(detections) == 36
    for detection in detections:
        regions = regions_from_detection(detection)
        assert regions is not None
        assert len(regions) == 1
        assert 0.0 <= regions[0]["center_x"] <= 1.0
        assert 0.0 <= regions[0]["center_y"] <= 1.0
        assert 0.04 <= regions[0]["radius"] <= 0.18


def test_index_demo_detections_maps_unique_frame_keys() -> None:
    data = json.loads(AUDIT_RESULTS_PATH.read_text(encoding="utf-8"))
    indexed = index_demo_detections(data["detections"])
    assert len(indexed) == 36


def test_every_detection_matches_a_demo_frame() -> None:
    data = json.loads(AUDIT_RESULTS_PATH.read_text(encoding="utf-8"))
    indexed = index_demo_detections(data["detections"])
    plan = build_demo_frame_plan()

    matched = 0
    for spec in plan:
        key = (
            round(float(spec["latitude"]), 10),
            round(float(spec["longitude"]), 10),
            int(spec["heading"]),
            int(spec["pitch"]),
        )
        if key in indexed:
            matched += 1

    assert matched == 36
