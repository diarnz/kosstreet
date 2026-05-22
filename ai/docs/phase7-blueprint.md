# Phase 7 Blueprint: Test Suite

## Goal

Write a pytest test suite that covers every core module without making live
OpenRouter API calls. All model calls are mocked so tests run instantly offline,
cost nothing, and pass in CI with no API key.

After this phase:
- `pytest tests/ -v` runs all tests and passes in under 10 seconds
- Every module that contains non-trivial logic has at least one test
- Edge cases and failure paths are covered
- The existing `test_street_audit_planner.py` continues to pass

---

## Current Project State

```
ai/tests/
└── test_street_audit_planner.py  ← existing, passing

ai/src/kostreet_ai/
├── schemas.py
├── preprocessing/image.py
├── inference/client.py
├── inference/classifier.py
├── street_audit/planner.py
└── geospatial/deduplication.py
```

What Phase 7 adds:

```
ai/tests/
├── test_street_audit_planner.py  ← keep, untouched
├── test_preprocessing.py         ← CREATE
├── test_classifier.py            ← CREATE
└── test_deduplication.py         ← CREATE
```

No source package files are modified.

---

## File 1: `tests/test_preprocessing.py`

Tests for `preprocessing/image.py`. All pure functions, no mocks needed.

### Tests to write

**`test_validate_image_returns_true_for_valid_jpeg`**
- Build a 100×100 red JPEG in memory with Pillow
- Assert `validate_image(bytes) is True`

**`test_validate_image_returns_false_for_empty_bytes`**
- Assert `validate_image(b"") is False`

**`test_validate_image_returns_false_for_garbage_bytes`**
- Assert `validate_image(b"not an image") is False`

**`test_encode_image_to_base64_returns_string`**
- Build a 200×200 JPEG in memory
- Call `encode_image_to_base64(bytes)`
- Assert result is a non-empty `str`
- Assert `base64.b64decode(result)` does not raise (valid base64)

**`test_encode_image_resizes_to_max_size`**
- Build a 2000×2000 JPEG in memory
- Call `encode_image_to_base64(bytes, max_size_px=64)`
- Decode the result back to bytes
- Open with Pillow and assert both dimensions are <= 64

**`test_decode_base64_to_bytes_roundtrip`**
- Build a JPEG, encode to base64, decode back
- Assert decoded bytes are a valid image

**`test_decode_base64_strips_data_uri_prefix`**
- Build a base64 string
- Prepend `data:image/jpeg;base64,`
- Call `decode_base64_to_bytes()`
- Assert result equals decoding the raw base64 without the prefix

---

## File 2: `tests/test_classifier.py`

Tests for `inference/classifier.py`. Uses `monkeypatch` to replace
`OpenRouterClient.chat` so no real HTTP calls are made.

### Helper fixture

```python
@pytest.fixture
def mock_client(monkeypatch):
    """Return a factory that patches OpenRouterClient.chat with a fixed response."""
    def _patch(json_response: str):
        monkeypatch.setattr(
            "kostreet_ai.inference.client.OpenRouterClient.chat",
            lambda self, messages, response_format=None: json_response,
        )
    return _patch
```

### Tests to write

**`test_classify_returns_correct_category(mock_client)`**
- Patch `chat` to return valid JSON with `category=pothole, confidence=0.87, severity=medium, is_civic_issue=true`
- Call `get_classifier().classify("fake_b64")`
- Assert `result.category == IssueCategory.pothole`
- Assert `result.confidence == 0.87`
- Assert `result.is_civic_issue is True`

**`test_classify_returns_fallback_on_invalid_json(mock_client)`**
- Patch `chat` to return `"this is not json"`
- Call `get_classifier().classify("fake_b64")`
- Assert `result.category == IssueCategory.other`
- Assert `result.confidence == 0.0`
- Assert `result.is_civic_issue is False`
- (Proves: no exception raised, fallback is returned cleanly)

**`test_classify_returns_fallback_on_missing_keys(mock_client)`**
- Patch `chat` to return `"{}"` (empty JSON object)
- Assert `result.category == IssueCategory.other`
- Assert `result.confidence == 0.0`

**`test_classify_coerces_unknown_category_to_other(mock_client)`**
- Patch `chat` to return JSON with `category="road_crack"` (not in enum)
- Assert `result.category == IssueCategory.other`

**`test_classify_clamps_confidence_above_1(mock_client)`**
- Patch `chat` to return JSON with `confidence=1.5`
- Assert `result.confidence == 1.0`

**`test_classify_clamps_confidence_below_0(mock_client)`**
- Patch `chat` to return JSON with `confidence=-0.3`
- Assert `result.confidence == 0.0`

**`test_severity_floor_broken_streetlight(mock_client)`**
- Patch `chat` to return `category=broken_streetlight, severity=low`
- Assert `result.severity == IssueSeverity.high`
- (Proves: severity floor overrides model output)

**`test_severity_floor_pothole_upgrades_low_to_medium(mock_client)`**
- Patch `chat` to return `category=pothole, severity=low`
- Assert `result.severity == IssueSeverity.medium`

**`test_severity_floor_does_not_downgrade_high(mock_client)`**
- Patch `chat` to return `category=pothole, severity=high`
- Assert `result.severity == IssueSeverity.high`

**`test_classify_returns_fallback_on_network_error(monkeypatch)`**
- Patch `OpenRouterClient.chat` to raise `httpx.ConnectError`
- Assert fallback is returned (no exception bubbles up)

---

## File 3: `tests/test_deduplication.py`

Tests for `geospatial/deduplication.py`. Pure functions, no mocks needed.

### Helper

```python
def make_detection(category, confidence, lat, lng):
    return DetectionWithLocation(
        category=category, confidence=confidence,
        severity=IssueSeverity.medium, description="test",
        is_civic_issue=True, latitude=lat, longitude=lng,
        heading=0, pitch=0,
    )
```

### Tests to write

**`test_haversine_known_distance`**
- Call `haversine_meters(42.6629, 21.1655, 42.6638, 21.1655)`
- Assert `95 < result < 105` (should be ~100m north)

**`test_haversine_same_point_is_zero`**
- Assert `haversine_meters(42.66, 21.16, 42.66, 21.16) == 0.0`

**`test_deduplicate_collapses_nearby_same_category`**
- 2 potholes 12m apart → only 1 survives (the higher-confidence one)
- Assert `len(result) == 1`
- Assert `result[0].confidence == 0.91` (the higher one)

**`test_deduplicate_keeps_far_same_category`**
- 2 potholes 60m apart → both survive
- Assert `len(result) == 2`

**`test_deduplicate_keeps_different_categories_at_same_location`**
- 1 pothole + 1 garbage at the same coordinates → both survive
- Assert `len(result) == 2`

**`test_deduplicate_empty_list`**
- Assert `deduplicate_detections([]) == []`

**`test_filter_by_confidence_keeps_at_threshold`**
- Detection with `confidence=0.55`, threshold=0.55
- Assert it is kept (>= not >)

**`test_filter_by_confidence_drops_below_threshold`**
- Detection with `confidence=0.54`, threshold=0.55
- Assert it is dropped

**`test_deduplicate_and_filter_full_pipeline`**
- 3 detections: pothole 0.91, pothole 0.74 (near), garbage 0.30 (below threshold)
- After `deduplicate_and_filter(threshold=0.55, radius=20)`
- Assert `len(result) == 1`
- Assert `result[0].category == IssueCategory.pothole`
- Assert `result[0].confidence == 0.91`

**`test_deduplicate_result_sorted_by_confidence_descending`**
- 3 surviving detections with confidence 0.6, 0.9, 0.75
- Assert result order is 0.9, 0.75, 0.6

**`test_compute_centroid_two_points`**
- `compute_centroid([(42.66, 21.16), (42.68, 21.18)])`
- Assert result == `(42.67, 21.17)`

---

## Running the Tests

From the `ai/` directory with the venv active:

```powershell
# Run all tests
pytest tests/ -v

# Run one file at a time
pytest tests/test_preprocessing.py -v
pytest tests/test_classifier.py -v
pytest tests/test_deduplication.py -v
pytest tests/test_street_audit_planner.py -v
```

Expected output:
```
tests/test_street_audit_planner.py::test_build_heading_plan_... PASSED
tests/test_preprocessing.py::test_validate_image_...           PASSED  (x7)
tests/test_classifier.py::test_classify_returns_correct_...    PASSED  (x10)
tests/test_deduplication.py::test_haversine_...                PASSED  (x11)

29 passed in 2.XX seconds
```

---

## Files Changed Summary

| File | Action |
|---|---|
| `tests/test_preprocessing.py` | Create |
| `tests/test_classifier.py` | Create |
| `tests/test_deduplication.py` | Create |
| `tests/test_street_audit_planner.py` | Keep, untouched |

---

## Gate to Pass Before Phase 8

`pytest tests/ -v` exits 0 with all tests passing.
No test makes a real HTTP call.
Total runtime under 10 seconds.
