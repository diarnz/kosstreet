from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from kostreet_ai.schemas import IssueCategory

SCORING_CATEGORIES: tuple[str, ...] = tuple(cat.value for cat in IssueCategory)


@dataclass(frozen=True)
class PredictionRecord:
    sample_id: str
    filename: str
    expected_category: str
    expected_civic: bool
    predicted_category: str
    predicted_civic: bool
    confidence: float
    difficulty: str = "easy"
    source: str = "stock"
    notes: str = ""


@dataclass(frozen=True)
class CategoryScore:
    category: str
    precision: float
    recall: float
    f1: float
    support: int


@dataclass(frozen=True)
class EvalSummary:
    total_samples: int
    missing_samples: int
    civic_detection_rate: float
    category_accuracy: float
    clean_false_positive_rate: float
    per_category: dict[str, CategoryScore]
    confusion_matrix: dict[str, dict[str, int]]
    records: list[PredictionRecord] = field(default_factory=list)


DEFAULT_RECALL_GATES: dict[str, float] = {
    IssueCategory.garbage.value: 0.80,
    IssueCategory.pothole.value: 0.90,
}
DEFAULT_CLEAN_FP_MAX = 0.10


def _safe_rate(numerator: int, denominator: int) -> float:
    if denominator == 0:
        return 1.0
    return numerator / denominator


def civic_detection_rate(records: list[PredictionRecord]) -> float:
    if not records:
        return 0.0
    correct = sum(1 for r in records if r.predicted_civic == r.expected_civic)
    return _safe_rate(correct, len(records))


def category_accuracy(records: list[PredictionRecord]) -> float:
    civic_records = [r for r in records if r.expected_civic]
    if not civic_records:
        return 0.0
    correct = sum(1 for r in civic_records if r.predicted_category == r.expected_category)
    return _safe_rate(correct, len(civic_records))


def clean_false_positive_rate(records: list[PredictionRecord]) -> float:
    clean_records = [r for r in records if not r.expected_civic]
    if not clean_records:
        return 0.0
    false_positives = sum(1 for r in clean_records if r.predicted_civic)
    return _safe_rate(false_positives, len(clean_records))


def per_category_scores(records: list[PredictionRecord]) -> dict[str, CategoryScore]:
    civic_records = [r for r in records if r.expected_civic]
    scores: dict[str, CategoryScore] = {}

    for category in SCORING_CATEGORIES:
        support = sum(1 for r in civic_records if r.expected_category == category)
        true_positive = sum(
            1
            for r in civic_records
            if r.expected_category == category and r.predicted_category == category
        )
        false_negative = support - true_positive
        false_positive = sum(
            1
            for r in civic_records
            if r.expected_category != category and r.predicted_category == category
        )

        precision = _safe_rate(true_positive, true_positive + false_positive)
        recall = _safe_rate(true_positive, support)
        if precision + recall == 0:
            f1 = 0.0
        else:
            f1 = 2 * precision * recall / (precision + recall)

        scores[category] = CategoryScore(
            category=category,
            precision=precision,
            recall=recall,
            f1=f1,
            support=support,
        )

    return scores


def build_confusion_matrix(records: list[PredictionRecord]) -> dict[str, dict[str, int]]:
    matrix = {expected: {predicted: 0 for predicted in SCORING_CATEGORIES} for expected in SCORING_CATEGORIES}
    for record in records:
        if not record.expected_civic:
            continue
        matrix[record.expected_category][record.predicted_category] += 1
    return matrix


def format_confusion_matrix(matrix: dict[str, dict[str, int]]) -> str:
    header = f"{'expected \\ predicted':<22}" + "".join(f"{cat:>14}" for cat in SCORING_CATEGORIES)
    lines = [header, "-" * len(header)]
    for expected in SCORING_CATEGORIES:
        row = f"{expected:<22}" + "".join(f"{matrix[expected][predicted]:>14}" for predicted in SCORING_CATEGORIES)
        lines.append(row)
    return "\n".join(lines)


def summarize_predictions(records: list[PredictionRecord], *, missing_samples: int = 0) -> EvalSummary:
    return EvalSummary(
        total_samples=len(records) + missing_samples,
        missing_samples=missing_samples,
        civic_detection_rate=civic_detection_rate(records),
        category_accuracy=category_accuracy(records),
        clean_false_positive_rate=clean_false_positive_rate(records),
        per_category=per_category_scores(records),
        confusion_matrix=build_confusion_matrix(records),
        records=records,
    )


def filter_records(
    records: list[PredictionRecord],
    *,
    category: str | None = None,
    subset: str = "all",
) -> list[PredictionRecord]:
    filtered = records
    if category:
        filtered = [r for r in filtered if r.expected_category == category]
    if subset == "street_view_sim":
        filtered = [r for r in filtered if r.source == "synthetic_downscale"]
    elif subset == "images":
        filtered = [r for r in filtered if r.source != "synthetic_downscale"]
    return filtered


def check_recall_gates(
    summary: EvalSummary,
    gates: dict[str, float] | None = None,
) -> list[str]:
    gates = gates or DEFAULT_RECALL_GATES
    failures: list[str] = []
    for category, minimum in gates.items():
        score = summary.per_category.get(category)
        if score is None or score.support == 0:
            failures.append(f"{category}: no eval samples (need support > 0)")
            continue
        if score.recall < minimum:
            failures.append(f"{category} recall {score.recall:.1%} < {minimum:.0%}")
    return failures


def check_clean_fp_gate(summary: EvalSummary, maximum: float = DEFAULT_CLEAN_FP_MAX) -> str | None:
    if summary.clean_false_positive_rate > maximum:
        return (
            f"clean false-positive rate {summary.clean_false_positive_rate:.1%} > {maximum:.0%}"
        )
    return None


@dataclass(frozen=True)
class GateResult:
    passed: bool
    recall_failures: list[str]
    clean_fp_failure: str | None


def evaluate_gates(
    summary: EvalSummary,
    *,
    recall_gates: dict[str, float] | None = None,
    clean_fp_max: float = DEFAULT_CLEAN_FP_MAX,
) -> GateResult:
    recall_failures = check_recall_gates(summary, recall_gates)
    clean_fp_failure = check_clean_fp_gate(summary, clean_fp_max)
    passed = not recall_failures and clean_fp_failure is None
    return GateResult(
        passed=passed,
        recall_failures=recall_failures,
        clean_fp_failure=clean_fp_failure,
    )


def summary_to_report_dict(summary: EvalSummary, *, model_name: str, subset: str) -> dict[str, Any]:
    return {
        "model": model_name,
        "subset": subset,
        "total_samples": summary.total_samples,
        "missing_samples": summary.missing_samples,
        "civic_detection_rate": summary.civic_detection_rate,
        "category_accuracy": summary.category_accuracy,
        "clean_false_positive_rate": summary.clean_false_positive_rate,
        "per_category": {
            cat: {
                "precision": score.precision,
                "recall": score.recall,
                "f1": score.f1,
                "support": score.support,
            }
            for cat, score in summary.per_category.items()
            if score.support > 0
        },
        "confusion_matrix": summary.confusion_matrix,
        "predictions": [
            {
                "sample_id": r.sample_id,
                "filename": r.filename,
                "expected_category": r.expected_category,
                "expected_civic": r.expected_civic,
                "predicted_category": r.predicted_category,
                "predicted_civic": r.predicted_civic,
                "confidence": r.confidence,
                "difficulty": r.difficulty,
                "source": r.source,
            }
            for r in summary.records
        ],
    }


def compare_to_baseline(
    current: dict[str, Any],
    baseline: dict[str, Any],
    *,
    regression_tolerance: float = 0.05,
) -> list[str]:
    """Return human-readable regressions when key metrics drop beyond tolerance."""
    regressions: list[str] = []
    for metric in ("civic_detection_rate", "category_accuracy"):
        current_value = current.get(metric, 0.0)
        baseline_value = baseline.get(metric, 0.0)
        if baseline_value - current_value > regression_tolerance:
            regressions.append(
                f"{metric} dropped from {baseline_value:.1%} to {current_value:.1%}"
            )

    current_per_category = current.get("per_category", {})
    baseline_per_category = baseline.get("per_category", {})
    for category, baseline_score in baseline_per_category.items():
        current_score = current_per_category.get(category, {})
        baseline_recall = baseline_score.get("recall", 0.0)
        current_recall = current_score.get("recall", 0.0)
        if baseline_recall - current_recall > regression_tolerance:
            regressions.append(
                f"{category} recall dropped from {baseline_recall:.1%} to {current_recall:.1%}"
            )
    return regressions


def confidence_summary(detections: list) -> dict[str, float]:
    """Legacy helper used by detection experiments."""
    if not detections:
        return {"count": 0.0, "average_confidence": 0.0}

    average_confidence = sum(detection.confidence for detection in detections) / len(detections)
    return {"count": float(len(detections)), "average_confidence": average_confidence}
