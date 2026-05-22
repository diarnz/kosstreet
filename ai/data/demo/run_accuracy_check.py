"""
Validate classifier accuracy against all demo fixture images.
Run from the ai/ directory:

    python data/demo/run_accuracy_check.py

Reports two metrics:
  1. Civic detection rate  — did the model correctly detect a civic issue exists?
  2. Category accuracy     — did the model pick the right category?

The gate uses civic detection rate >= 75%.
Category accuracy is informational — stock images are not ideal for category testing.
Replace images in data/demo/ with team-captured Kosovo street photos for full accuracy.
"""

import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "src"))

from kostreet_ai.inference.classifier import get_classifier
from kostreet_ai.preprocessing.image import encode_image_to_base64

DEMO_DIR = pathlib.Path(__file__).parent
FIXTURES_FILE = DEMO_DIR / "fixtures.json"
CIVIC_DETECTION_THRESHOLD = 0.75

COL_F = 30
COL_E = 22
COL_A = 22
DIVIDER = "-" * 95


def run() -> None:
    fixtures = json.loads(FIXTURES_FILE.read_text(encoding="utf-8"))
    classifier = get_classifier()

    print(f"\nKoStreet AI - Demo Accuracy Check")
    print(f"Model  : {classifier.model_name}")
    print(f"Images : {len(fixtures)}")
    print(f"Gate   : civic detection >= {int(CIVIC_DETECTION_THRESHOLD * 100)}%\n")

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

    civic_correct = 0
    category_correct = 0
    civic_total = 0
    category_total = 0
    missing: list[str] = []
    failures: list[str] = []

    for fixture in fixtures:
        filename = fixture["filename"]
        image_path = DEMO_DIR / filename

        if not image_path.exists():
            print(f"  MISSING  {filename}")
            missing.append(filename)
            continue

        image_bytes = image_path.read_bytes()
        b64 = encode_image_to_base64(image_bytes)
        result = classifier.classify(b64)

        expected_civic = fixture["expected_civic"]
        expected_cat = fixture["expected_category"]

        # Civic detection: model must agree on whether this is a civic issue
        civic_match = result.is_civic_issue == expected_civic
        civic_total += 1
        if civic_match:
            civic_correct += 1

        # Category accuracy: only scored for images that are civic issues
        cat_match_str = "n/a"
        if expected_civic:
            category_total += 1
            cat_match = result.category.value == expected_cat
            if cat_match:
                category_correct += 1
            cat_match_str = "OK" if cat_match else "MISS"
            if not cat_match:
                failures.append(f"{filename} (got {result.category.value})")

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

    print(DIVIDER)

    civic_rate = civic_correct / civic_total if civic_total else 0
    cat_rate = category_correct / category_total if category_total else 0
    gate_passed = civic_rate >= CIVIC_DETECTION_THRESHOLD

    print(f"\nCivic detection : {civic_correct}/{civic_total} ({civic_rate * 100:.1f}%)  <- gate metric")
    print(f"Category match  : {category_correct}/{category_total} ({cat_rate * 100:.1f}%)  <- informational")
    print(f"\nGate : {'PASSED' if gate_passed else 'FAILED'} (threshold {int(CIVIC_DETECTION_THRESHOLD * 100)}%)")

    if missing:
        print(f"\nMissing files: {', '.join(missing)}")
        print("Run data/demo/download_demo_images.py to download them.")

    if not gate_passed:
        print("\nCivic detection is below the gate threshold.")
        print("The most likely cause is low-quality stock images.")
        print()
        print("ACTION REQUIRED - Replace these images with real team-captured photos:")
        for f in fixtures:
            if f["expected_civic"] and (DEMO_DIR / f["filename"]).exists():
                path = DEMO_DIR / f["filename"]
                b64 = encode_image_to_base64(path.read_bytes())
                r = classifier.classify(b64)
                if r.is_civic_issue != f["expected_civic"]:
                    print(f"  - {f['filename']}  (label: {f['label']})")
        sys.exit(1)

    if failures:
        print(f"\nCategory misses (informational): {len(failures)}")
        for f in failures:
            print(f"  - {f}")
        print("\nThese mismatches are expected with generic stock images.")
        print("Replace with team-captured Prishtina street photos for full category accuracy.")


if __name__ == "__main__":
    run()
