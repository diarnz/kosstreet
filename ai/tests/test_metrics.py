from __future__ import annotations

from kostreet_ai.evaluation.metrics import (
    PredictionRecord,
    check_recall_gates,
    clean_false_positive_rate,
    compare_to_baseline,
    evaluate_gates,
    format_confusion_matrix,
    per_category_scores,
    summarize_predictions,
)


def _record(
    expected_category: str,
    predicted_category: str,
    *,
    expected_civic: bool = True,
    predicted_civic: bool = True,
    sample_id: str = "sample",
) -> PredictionRecord:
    return PredictionRecord(
        sample_id=sample_id,
        filename=f"{sample_id}.jpg",
        expected_category=expected_category,
        expected_civic=expected_civic,
        predicted_category=predicted_category,
        predicted_civic=predicted_civic,
        confidence=0.9,
    )


def test_per_category_recall_and_precision() -> None:
    records = [
        _record("garbage", "garbage", sample_id="g1"),
        _record("garbage", "pothole", sample_id="g2"),
        _record("pothole", "garbage", sample_id="p1"),
        _record("pothole", "pothole", sample_id="p2"),
    ]
    scores = per_category_scores(records)
    assert scores["garbage"].recall == 0.5
    assert scores["garbage"].precision == 0.5
    assert scores["pothole"].recall == 0.5


def test_clean_false_positive_rate() -> None:
    records = [
        _record("other", "other", expected_civic=False, predicted_civic=False, sample_id="c1"),
        _record("other", "garbage", expected_civic=False, predicted_civic=True, sample_id="c2"),
    ]
    assert clean_false_positive_rate(records) == 0.5


def test_confusion_matrix_counts_expected_rows() -> None:
    records = [
        _record("garbage", "garbage", sample_id="g1"),
        _record("garbage", "pothole", sample_id="g2"),
    ]
    summary = summarize_predictions(records)
    assert summary.confusion_matrix["garbage"]["garbage"] == 1
    assert summary.confusion_matrix["garbage"]["pothole"] == 1
    rendered = format_confusion_matrix(summary.confusion_matrix)
    assert "garbage" in rendered


def test_evaluate_gates_fails_on_low_garbage_recall() -> None:
    records = [
        _record("garbage", "garbage", sample_id="g1"),
        _record("garbage", "pothole", sample_id="g2"),
        _record("garbage", "pothole", sample_id="g3"),
        _record("garbage", "pothole", sample_id="g4"),
        _record("garbage", "pothole", sample_id="g5"),
    ]
    summary = summarize_predictions(records)
    gate = evaluate_gates(summary, recall_gates={"garbage": 0.80})
    assert gate.passed is False
    assert check_recall_gates(summary, {"garbage": 0.80})


def test_compare_to_baseline_detects_regression() -> None:
    current = {
        "civic_detection_rate": 0.70,
        "category_accuracy": 0.80,
        "per_category": {"garbage": {"recall": 0.60}},
    }
    baseline = {
        "civic_detection_rate": 0.90,
        "category_accuracy": 0.90,
        "per_category": {"garbage": {"recall": 0.90}},
    }
    regressions = compare_to_baseline(current, baseline)
    assert any("civic_detection_rate" in item for item in regressions)
    assert any("garbage" in item for item in regressions)
