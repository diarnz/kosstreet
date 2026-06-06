"""
Classify LIVE Google Street View frames in real time (no bulk image storage).

Run from ai/:

    python data/eval/run_street_view_live_eval.py
    python data/eval/run_street_view_live_eval.py --route bill_clinton_audit --headings 0,90
    python data/eval/run_street_view_live_eval.py --max-points 3 --report

Requires GOOGLE_MAPS_API_KEY and KOSTREET_AI_OPENROUTER_API_KEY in the root .env file.

Note: probe coordinates are scan locations, not labeled ground truth. This script
reports what the AI detects on real Street View — use it for integration testing
and manual review, not category accuracy scoring against fixtures.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import sys
from collections import Counter
from datetime import UTC, datetime

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "src"))

from kostreet_ai.config import settings
from kostreet_ai.inference.classifier import get_classifier
from kostreet_ai.inference.prompts import ClassificationContext
from kostreet_ai.integrations.street_view import (
    GoogleStreetViewClient,
    StreetViewFrameRequest,
    is_no_imagery_placeholder,
)
from kostreet_ai.preprocessing.image import encode_image_to_base64

EVAL_DIR = pathlib.Path(__file__).parent
PROBES_FILE = EVAL_DIR / "street_view_probes.json"
REPORT_FILE = EVAL_DIR / "street_view_live_report.json"

DEFAULT_HEADINGS = (0, 90, 180, 270)
DEFAULT_PITCHES = (0,)


def _load_probes(route: str | None) -> list[dict]:
    probes = json.loads(PROBES_FILE.read_text(encoding="utf-8"))
    if route:
        probes = [probe for probe in probes if probe.get("route") == route]
    return probes


def _parse_int_list(raw: str) -> tuple[int, ...]:
    return tuple(int(part.strip()) for part in raw.split(",") if part.strip())


def _print_row(
    probe_id: str,
    heading: int,
    pitch: int,
    *,
    category: str,
    confidence: float,
    civic: bool,
    snapped: bool,
    no_imagery: bool,
) -> None:
    status = "NO_IMG" if no_imagery else ("SNAP" if snapped else "OK")
    civic_label = "civic" if civic else "clean"
    print(
        f"{probe_id:<22}"
        f"h={heading:>3} p={pitch:>3}  "
        f"{category:<20}"
        f"{confidence:>6.2f}  "
        f"{civic_label:<6}  "
        f"{status}"
    )


def run_live_eval(
    *,
    route: str | None,
    headings: tuple[int, ...],
    pitches: tuple[int, ...],
    max_points: int | None,
    report_path: pathlib.Path | None,
) -> int:
    if not settings.google_maps_api_key:
        print("Missing GOOGLE_MAPS_API_KEY in root .env")
        return 1

    probes = _load_probes(route)
    if max_points is not None:
        probes = probes[:max_points]
    if not probes:
        print("No Street View probe points matched your filters.")
        return 1

    gsv = GoogleStreetViewClient(api_key=settings.google_maps_api_key, size=640)
    classifier = get_classifier()

    print("\nKoStreet AI — Live Street View Evaluation")
    print(f"Model     : {classifier.model_name}")
    print(f"Probes    : {len(probes)}")
    print(f"Headings  : {headings}")
    print(f"Pitches   : {pitches}")
    print(f"Frames    : {len(probes) * len(headings) * len(pitches)} (fetched in real time)\n")

    print(f"{'probe':<22}{'view':<14}{'predicted':<20}{'conf':>6}  {'issue':<6}  status")
    print("-" * 82)

    frame_results: list[dict] = []
    skipped_no_imagery = 0
    detections = 0
    category_counts: Counter[str] = Counter()

    for probe in probes:
        for heading in headings:
            for pitch in pitches:
                request = StreetViewFrameRequest(
                    latitude=probe["latitude"],
                    longitude=probe["longitude"],
                    heading=heading,
                    pitch=pitch,
                )
                try:
                    frame = gsv.fetch_frame(request)
                except Exception as exc:
                    print(f"{probe['id']:<22}h={heading:>3} p={pitch:>3}  FETCH_FAILED  {exc}")
                    continue

                no_imagery = is_no_imagery_placeholder(frame.data)
                if no_imagery:
                    skipped_no_imagery += 1
                    _print_row(
                        probe["id"],
                        heading,
                        pitch,
                        category="other",
                        confidence=0.0,
                        civic=False,
                        snapped=frame.snapped,
                        no_imagery=True,
                    )
                    frame_results.append(
                        {
                            "probe_id": probe["id"],
                            "label": probe.get("label", ""),
                            "latitude": frame.latitude,
                            "longitude": frame.longitude,
                            "heading": heading,
                            "pitch": pitch,
                            "snapped": frame.snapped,
                            "no_imagery": True,
                            "skipped": True,
                        }
                    )
                    continue

                b64 = encode_image_to_base64(frame.data, settings.max_image_size_px)
                result = classifier.classify(b64, context=ClassificationContext.street_audit)

                if result.is_civic_issue:
                    detections += 1
                    category_counts[result.category.value] += 1

                _print_row(
                    probe["id"],
                    heading,
                    pitch,
                    category=result.category.value,
                    confidence=result.confidence,
                    civic=result.is_civic_issue,
                    snapped=frame.snapped,
                    no_imagery=False,
                )

                frame_results.append(
                    {
                        "probe_id": probe["id"],
                        "label": probe.get("label", ""),
                        "latitude": frame.latitude,
                        "longitude": frame.longitude,
                        "heading": heading,
                        "pitch": pitch,
                        "snapped": frame.snapped,
                        "no_imagery": False,
                        "skipped": False,
                        "predicted_category": result.category.value,
                        "predicted_civic": result.is_civic_issue,
                        "confidence": result.confidence,
                        "severity": result.severity.value,
                        "description": result.description,
                    }
                )

    scored_frames = [item for item in frame_results if not item.get("skipped")]
    civic_rate = detections / len(scored_frames) if scored_frames else 0.0

    print("-" * 82)
    print(f"\nScored frames      : {len(scored_frames)}")
    print(f"No-imagery skipped : {skipped_no_imagery}")
    print(f"Civic detections   : {detections} ({civic_rate * 100:.1f}% of scored frames)")
    if category_counts:
        print("Detection mix      :", ", ".join(f"{k}={v}" for k, v in category_counts.most_common()))

    notable = [
        item
        for item in frame_results
        if item.get("predicted_civic") and not item.get("skipped")
    ]
    if notable:
        print("\nNotable detections (manual review):")
        for item in notable:
            print(
                f"  - {item['probe_id']} h={item['heading']} "
                f"{item['predicted_category']} ({item['confidence']:.2f}): {item['description']}"
            )

    if report_path is not None:
        payload = {
            "generated_at": datetime.now(UTC).isoformat(),
            "model": classifier.model_name,
            "route_filter": route,
            "headings": list(headings),
            "pitches": list(pitches),
            "scored_frames": len(scored_frames),
            "civic_detections": detections,
            "category_counts": dict(category_counts),
            "frames": frame_results,
        }
        report_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        print(f"\nWrote JSON report: {report_path}")

    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Live Google Street View AI evaluation")
    parser.add_argument(
        "--route",
        default=None,
        help="Filter probes by route tag (e.g. bill_clinton_audit, fixture_coords)",
    )
    parser.add_argument("--headings", default=",".join(str(h) for h in DEFAULT_HEADINGS))
    parser.add_argument("--pitches", default="0")
    parser.add_argument("--max-points", type=int, default=None, help="Limit probe count")
    parser.add_argument("--report", action="store_true", help="Write street_view_live_report.json")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    exit_code = run_live_eval(
        route=args.route,
        headings=_parse_int_list(args.headings),
        pitches=_parse_int_list(args.pitches),
        max_points=args.max_points,
        report_path=REPORT_FILE if args.report else None,
    )
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
