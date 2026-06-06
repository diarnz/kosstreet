"""
Validate classifier accuracy against demo fixture images.
Run from the ai/ directory:

    python data/demo/run_accuracy_check.py
    python data/demo/run_accuracy_check.py --category garbage

Reports civic detection rate and category accuracy using the shared eval metrics.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "src"))

from kostreet_ai.evaluation.metrics import (
    PredictionRecord,
    format_confusion_matrix,
    summarize_predictions,
)
from kostreet_ai.inference.classifier import get_classifier
from kostreet_ai.preprocessing.image import encode_image_to_base64

DEMO_DIR = pathlib.Path(__file__).parent
FIXTURES_FILE = DEMO_DIR / "fixtures.json"
CIVIC_DETECTION_THRESHOLD = 0.75

COL_F = 30
COL_E = 22
COL_A = 22
DIVIDER = "-" * 95


def _load_fixtures(category: str | None) -> list[dict]:
    fixtures = json.loads(FIXTURES_FILE.read_text(encoding="utf-8"))
    if category:
        fixtures = [f for f in fixtures if f["expected_category"] == category]
    return fixtures


def run(category: str | None = None) -> int:
    fixtures = _load_fixtures(category)
    classifier = get_classifier()
    records: list[PredictionRecord] = []
    missing: list[str] = []

    print("\nKoStreet AI - Demo Accuracy Check")
    print(f"Model    : {classifier.model_name}")
    print(f"Images   : {len(fixtures)}")
    if category:
        print(f"Category : {category}")
    print(f"Gate     : civic detection >= {int(CIVIC_DETECTION_THRESHOLD * 100)}%\n")

    header = (
        f"{'filename':<{COL_F}}"
        f"{'expected_category':<{COL_E}}"
        f"{'predicted':<{COL_A}}"
        f"{'conf':>6}"
        f"  {'civic':>5}"
        f"  {'cat':>4}"
    )
    print(header)
    print(DIVIDER)

    for fixture in fixtures:
        filename = fixture["filename"]
        image_path = DEMO_DIR / filename

        if not image_path.exists():
            print(f"  MISSING  {filename}")
            missing.append(filename)
            continue

        b64 = encode_image_to_base64(image_path.read_bytes())
        result = classifier.classify(b64)

        expected_civic = fixture["expected_civic"]
        expected_cat = fixture["expected_category"]
        civic_match = result.is_civic_issue == expected_civic

        cat_match_str = "n/a"
        if expected_civic:
            cat_match = result.category.value == expected_cat
            cat_match_str = "OK" if cat_match else "MISS"

        civic_str = "OK" if civic_match else "MISS"
        expected_label = expected_cat if expected_civic else f"{expected_cat}(clean)"

        print(
            f"{filename:<{COL_F}}"
            f"{expected_label:<{COL_E}}"
            f"{result.category.value:<{COL_A}}"
            f"{result.confidence:>6.2f}"
            f"  {civic_str:>5}"
            f"  {cat_match_str:>4}"
        )

        records.append(
            PredictionRecord(
                sample_id=pathlib.Path(filename).stem,
                filename=filename,
                expected_category=expected_cat,
                expected_civic=expected_civic,
                predicted_category=result.category.value,
                predicted_civic=result.is_civic_issue,
                confidence=result.confidence,
                difficulty="easy",
                source="stock",
                notes=fixture.get("label", ""),
            )
        )

    print(DIVIDER)

    summary = summarize_predictions(records, missing_samples=len(missing))
    gate_passed = summary.civic_detection_rate >= CIVIC_DETECTION_THRESHOLD

    print(
        f"\nCivic detection : {summary.civic_detection_rate * 100:.1f}%  "
        f"({len([r for r in records if r.predicted_civic == r.expected_civic])}/{len(records)})"
    )
    print(f"Category match  : {summary.category_accuracy * 100:.1f}%  <- informational")
    print(f"\nGate : {'PASSED' if gate_passed else 'FAILED'} (threshold {int(CIVIC_DETECTION_THRESHOLD * 100)}%)")

    if records:
        print("\nConfusion matrix:")
        print(format_confusion_matrix(summary.confusion_matrix))

    if missing:
        print(f"\nMissing files: {', '.join(missing)}")
        print("Run data/demo/download_demo_images.py to download them.")
        return 1

    if not gate_passed:
        print("\nCivic detection is below the gate threshold.")
        for record in records:
            if record.expected_civic and not record.predicted_civic:
                print(f"  - {record.filename}  ({record.notes})")
        return 1

    failures = [
        f"{r.filename} (got {r.predicted_category})"
        for r in records
        if r.expected_civic and r.predicted_category != r.expected_category
    ]
    if failures:
        print(f"\nCategory misses (informational): {len(failures)}")
        for failure in failures:
            print(f"  - {failure}")

    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Demo fixture accuracy check")
    parser.add_argument("--category", default=None, help="Filter to one expected category")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    sys.exit(run(category=args.category))
