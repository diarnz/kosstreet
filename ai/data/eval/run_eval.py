"""
Run the full KoStreet AI evaluation harness.

Usage (from ai/ directory):

    python data/eval/bootstrap_dataset.py   # first-time setup
    python data/eval/run_eval.py --report
    python data/eval/run_eval.py --subset street_view_sim --category garbage
    python data/eval/run_eval.py --update-baseline

Writes eval_report.json and optionally compares against eval_baseline.json.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import sys
from datetime import UTC, datetime

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "src"))

from kostreet_ai.evaluation.metrics import (
    DEFAULT_CLEAN_FP_MAX,
    DEFAULT_RECALL_GATES,
    PredictionRecord,
    compare_to_baseline,
    evaluate_gates,
    filter_records,
    format_confusion_matrix,
    summarize_predictions,
    summary_to_report_dict,
)
from kostreet_ai.inference.prompts import ClassificationContext
from kostreet_ai.preprocessing.image import encode_image_to_base64

EVAL_DIR = pathlib.Path(__file__).parent
MANIFEST_FILE = EVAL_DIR / "manifest.json"
REPORT_FILE = EVAL_DIR / "eval_report.json"
BASELINE_FILE = EVAL_DIR / "eval_baseline.json"


def _load_manifest() -> list[dict]:
    if not MANIFEST_FILE.exists():
        print(f"Manifest not found: {MANIFEST_FILE}")
        print("Run: python data/eval/bootstrap_dataset.py")
        sys.exit(1)
    return json.loads(MANIFEST_FILE.read_text(encoding="utf-8"))


def _resolve_context(entry: dict, context: str) -> ClassificationContext:
    if context != "auto":
        return ClassificationContext(context)
    if entry.get("source") == "synthetic_downscale":
        return ClassificationContext.street_audit
    return ClassificationContext.citizen_upload


def _configure_runtime(*, hybrid: bool) -> None:
    import os

    if hybrid:
        os.environ["KOSTREET_AI_HYBRID_ENABLED"] = "true"
    from kostreet_ai.config import get_settings

    get_settings.cache_clear()


def _run_predictions(
    manifest: list[dict],
    *,
    category: str | None,
    subset: str,
    context: str,
) -> tuple[list[PredictionRecord], list[str]]:
    from kostreet_ai.inference.classifier import get_classifier

    classifier = get_classifier()
    records: list[PredictionRecord] = []
    missing: list[str] = []

    for entry in manifest:
        if category and entry["expected_category"] != category:
            continue
        if subset == "street_view_sim" and entry.get("source") != "synthetic_downscale":
            continue
        if subset == "images" and entry.get("source") == "synthetic_downscale":
            continue

        image_path = EVAL_DIR / entry["filename"]
        if not image_path.exists():
            missing.append(entry["filename"])
            continue

        b64 = encode_image_to_base64(image_path.read_bytes())
        result = classifier.classify(b64, context=_resolve_context(entry, context))

        records.append(
            PredictionRecord(
                sample_id=entry["id"],
                filename=entry["filename"],
                expected_category=entry["expected_category"],
                expected_civic=entry["expected_civic"],
                predicted_category=result.category.value,
                predicted_civic=result.is_civic_issue,
                confidence=result.confidence,
                difficulty=entry.get("difficulty", "easy"),
                source=entry.get("source", "stock"),
                notes=entry.get("notes", ""),
            )
        )

    return records, missing


def _print_summary(summary, *, model_name: str, subset: str, missing: list[str]) -> None:
    print(f"\nKoStreet AI - Evaluation Harness")
    print(f"Model   : {model_name}")
    print(f"Subset  : {subset}")
    print(f"Samples : {len(summary.records)} scored, {len(missing)} missing\n")

    print(f"Civic detection rate     : {summary.civic_detection_rate * 100:.1f}%")
    print(f"Category accuracy        : {summary.category_accuracy * 100:.1f}%")
    print(f"Clean false-positive rate: {summary.clean_false_positive_rate * 100:.1f}%\n")

    print("Per-category scores (civic samples only):")
    print(f"{'category':<20}{'precision':>12}{'recall':>10}{'f1':>10}{'support':>10}")
    print("-" * 62)
    for category, score in summary.per_category.items():
        if score.support == 0:
            continue
        print(
            f"{category:<20}"
            f"{score.precision:>11.1%}"
            f"{score.recall:>10.1%}"
            f"{score.f1:>10.1%}"
            f"{score.support:>10}"
        )

    print("\nConfusion matrix:")
    print(format_confusion_matrix(summary.confusion_matrix))

    if missing:
        print(f"\nMissing images ({len(missing)}):")
        for path in missing:
            print(f"  - {path}")
        print("Run: python data/eval/bootstrap_dataset.py")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="KoStreet AI evaluation harness")
    parser.add_argument(
        "--subset",
        choices=("all", "images", "street_view_sim"),
        default="all",
        help="Evaluate all manifest entries, originals only, or simulations only",
    )
    parser.add_argument(
        "--category",
        default=None,
        help="Filter to one expected category (e.g. garbage, pothole)",
    )
    parser.add_argument(
        "--context",
        choices=("auto", "street_audit", "citizen_upload"),
        default="auto",
        help="Classifier context override (default: sim→street_audit, stock→citizen_upload)",
    )
    parser.add_argument(
        "--report",
        action="store_true",
        help="Write eval_report.json",
    )
    parser.add_argument(
        "--update-baseline",
        action="store_true",
        help="Save eval_report.json as eval_baseline.json after the run",
    )
    parser.add_argument(
        "--fail-on-gate",
        action="store_true",
        help="Exit 1 when per-category recall or clean FP gates fail",
    )
    parser.add_argument(
        "--fail-on-regression",
        action="store_true",
        help="Exit 1 when metrics regress vs eval_baseline.json",
    )
    parser.add_argument(
        "--hybrid",
        action="store_true",
        help="Enable local YOLO garbage detector merge (requires trained model weights)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    _configure_runtime(hybrid=args.hybrid)
    manifest = _load_manifest()

    records, missing = _run_predictions(
        manifest,
        category=args.category,
        subset=args.subset,
        context=args.context,
    )
    from kostreet_ai.inference.classifier import get_classifier

    classifier = get_classifier()
    summary = summarize_predictions(records, missing_samples=len(missing))
    _print_summary(summary, model_name=classifier.model_name, subset=args.subset, missing=missing)

    report = summary_to_report_dict(summary, model_name=classifier.model_name, subset=args.subset)
    report["hybrid_enabled"] = args.hybrid
    report["generated_at"] = datetime.now(UTC).isoformat()
    report["missing_files"] = missing

    if args.report or args.update_baseline:
        REPORT_FILE.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        print(f"\nWrote report: {REPORT_FILE}")

    if BASELINE_FILE.exists():
        baseline = json.loads(BASELINE_FILE.read_text(encoding="utf-8"))
        regressions = compare_to_baseline(report, baseline)
        if regressions:
            print("\nRegressions vs baseline:")
            for item in regressions:
                print(f"  - {item}")
            if args.fail_on_regression:
                sys.exit(1)
        else:
            print("\nNo regressions vs baseline.")
    elif args.fail_on_regression:
        print(f"\nBaseline not found: {BASELINE_FILE}")
        print("Run once with --update-baseline to create it.")

    gate_result = evaluate_gates(summary)
    print("\nGate checks:")
    print(f"  Recall gates: {DEFAULT_RECALL_GATES}")
    print(f"  Clean FP max: {DEFAULT_CLEAN_FP_MAX:.0%}")
    if gate_result.recall_failures:
        for failure in gate_result.recall_failures:
            print(f"  FAIL  {failure}")
    else:
        print("  OK    per-category recall gates")
    if gate_result.clean_fp_failure:
        print(f"  FAIL  {gate_result.clean_fp_failure}")
    else:
        print("  OK    clean false-positive gate")
    print(f"\nGate : {'PASSED' if gate_result.passed else 'FAILED'}")

    if args.update_baseline:
        BASELINE_FILE.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        print(f"Updated baseline: {BASELINE_FILE}")

    if args.fail_on_gate and not gate_result.passed:
        sys.exit(1)

    if missing and args.fail_on_gate:
        sys.exit(1)


if __name__ == "__main__":
    main()
