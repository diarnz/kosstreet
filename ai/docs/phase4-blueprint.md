# Phase 4 Blueprint: Geospatial Deduplication

## Goal

When the Street Audit Agent scans a 728m route with 288 frames, the same pothole
will be detected 4–8 times from different headings and neighboring scan points.
Sending all of those as separate tickets to the municipal dashboard is useless noise.

This phase collapses nearby same-category detections into one high-confidence
detection so the backend receives clean, non-duplicate results.

After this phase:
- A list of raw detections from multiple frames can be deduplicated in one call
- Only the highest-confidence detection survives within each spatial cluster
- Different categories at the same location are kept separately
  (a pothole and garbage on the same corner are two different tickets)
- The haversine function from Phase 3 is reused here — no reimplementation

---

## Current Project State

What already exists after Phases 0–3:

```
ai/src/kostreet_ai/
├── config.py
├── main.py
├── schemas.py             ← DetectionWithLocation defined and ready
├── preprocessing/image.py
├── inference/
│   ├── client.py
│   └── classifier.py
└── street_audit/
    └── planner.py         ← haversine_meters lives here, will be imported

ai/tests/
└── test_street_audit_planner.py  ← passing
```

What Phase 4 adds:

```
ai/src/kostreet_ai/
└── geospatial/
    ├── __init__.py        ← empty
    └── deduplication.py   ← all deduplication logic
```

---

## File to Create: `geospatial/deduplication.py`

### Import strategy

`haversine_meters` already exists in `street_audit/planner.py`.
Import it from there — do not rewrite it.

```python
from kostreet_ai.street_audit.planner import haversine_meters
```

---

### Function 1: `deduplicate_detections`

```python
def deduplicate_detections(
    detections: list[DetectionWithLocation],
    radius_meters: float = 20.0,
) -> list[DetectionWithLocation]:
```

**Input:** A flat list of `DetectionWithLocation` objects — the raw output from
running the classifier on multiple frames of the same street segment.

**Output:** A deduplicated list where no two entries of the same category are
within `radius_meters` of each other.

**Algorithm — greedy confidence-first spatial merge:**

1. Sort all detections by `confidence` descending (highest confidence first).
2. Initialize `kept: list[DetectionWithLocation] = []`
3. For each detection `d` in the sorted list:
   - Check every detection already in `kept`
   - If any kept detection has the **same `category`** AND is within
     `radius_meters` of `d` → skip `d` (it is a duplicate of a better detection)
   - If no such kept detection exists → append `d` to `kept`
4. Return `kept`

**Why confidence-first sort matters:**
By sorting highest-confidence first, the first detection we keep for any
cluster is always the best one. Every subsequent detection of the same category
nearby is guaranteed to be equal or worse confidence, so we safely discard it.

**Why category must match for deduplication:**
A pothole and garbage at the same corner are two different civic issues
requiring two different departments. They must never be merged.

**Example:**
```
Input (5 detections):
  pothole  @ (42.6629, 21.1655)  confidence=0.91  ← kept (best pothole in cluster)
  pothole  @ (42.6630, 21.1656)  confidence=0.74  ← 12m from first → DROPPED
  pothole  @ (42.6630, 21.1657)  confidence=0.68  ← 15m from first → DROPPED
  garbage  @ (42.6629, 21.1655)  confidence=0.82  ← kept (different category)
  pothole  @ (42.6680, 21.1700)  confidence=0.55  ← kept (60m away, new cluster)

Output (3 detections):
  pothole  @ (42.6629, 21.1655)  confidence=0.91
  garbage  @ (42.6629, 21.1655)  confidence=0.82
  pothole  @ (42.6680, 21.1700)  confidence=0.55
```

---

### Function 2: `compute_centroid`

```python
def compute_centroid(
    points: list[tuple[float, float]],
) -> tuple[float, float]:
```

Returns the arithmetic mean of a list of `(lat, lng)` tuples.

```python
avg_lat = sum(p[0] for p in points) / len(points)
avg_lng = sum(p[1] for p in points) / len(points)
return (avg_lat, avg_lng)
```

Used optionally when the caller wants to place a merged detection at the
geographic center of its cluster rather than at the position of the
highest-confidence detection. Not called by `deduplicate_detections` itself —
exposed as a utility for the API layer.

---

### Function 3: `filter_by_confidence`

```python
def filter_by_confidence(
    detections: list[DetectionWithLocation],
    threshold: float,
) -> list[DetectionWithLocation]:
```

Returns only detections where `confidence >= threshold`.
Applied before deduplication to drop low-confidence noise early.

```python
return [d for d in detections if d.confidence >= threshold]
```

---

### Function 4: `deduplicate_and_filter`

```python
def deduplicate_and_filter(
    detections: list[DetectionWithLocation],
    radius_meters: float = 20.0,
    confidence_threshold: float = 0.55,
) -> list[DetectionWithLocation]:
```

Convenience wrapper combining both steps in the correct order:
1. Call `filter_by_confidence(detections, confidence_threshold)`
2. Call `deduplicate_detections(filtered, radius_meters)`
3. Return result sorted by `confidence` descending (highest priority first)

This is the function called by the audit endpoint in Phase 6.

---

## Data Flow After Phase 4

```
288 raw frame analysis results (from Phase 6 audit scan)
           │
           ▼
filter_by_confidence(threshold=0.55)
  → drops low-confidence noise
           │
           ▼
deduplicate_detections(radius_meters=20.0)
  → collapses nearby same-category clusters
  → keeps highest-confidence detection per cluster
           │
           ▼
Clean list of unique DetectionWithLocation objects
  → sent to backend as AI-suggested municipal tickets
  → typically 3-8 real issues from a 728m route scan
```

---

## Verification Plan

### Step 1 — Core deduplication logic

```python
from kostreet_ai.geospatial.deduplication import deduplicate_detections
from kostreet_ai.schemas import DetectionWithLocation, IssueCategory, IssueSeverity

def make_detection(category, confidence, lat, lng):
    return DetectionWithLocation(
        category=category, confidence=confidence,
        severity=IssueSeverity.medium, description="test",
        is_civic_issue=True, latitude=lat, longitude=lng,
        heading=0, pitch=0,
    )

detections = [
    make_detection(IssueCategory.pothole, 0.91, 42.6629, 21.1655),  # best
    make_detection(IssueCategory.pothole, 0.74, 42.6630, 21.1656),  # 12m → DROPPED
    make_detection(IssueCategory.pothole, 0.68, 42.6630, 21.1657),  # 15m → DROPPED
    make_detection(IssueCategory.garbage, 0.82, 42.6629, 21.1655),  # diff category → KEPT
    make_detection(IssueCategory.pothole, 0.55, 42.6680, 21.1700),  # 60m away → KEPT
]

result = deduplicate_detections(detections, radius_meters=20.0)
assert len(result) == 3
assert result[0].confidence == 0.91
assert result[0].category == IssueCategory.pothole
print("Deduplication test PASSED")
```

### Step 2 — Different categories at same location both kept

```python
result = deduplicate_detections([
    make_detection(IssueCategory.pothole, 0.80, 42.6629, 21.1655),
    make_detection(IssueCategory.garbage, 0.75, 42.6629, 21.1655),
], radius_meters=20.0)
assert len(result) == 2
print("Category separation test PASSED")
```

### Step 3 — Confidence filter

```python
from kostreet_ai.geospatial.deduplication import filter_by_confidence

raw = [
    make_detection(IssueCategory.pothole, 0.90, 42.66, 21.16),
    make_detection(IssueCategory.garbage, 0.30, 42.66, 21.16),  # below threshold
]
filtered = filter_by_confidence(raw, threshold=0.55)
assert len(filtered) == 1
print("Confidence filter test PASSED")
```

### Step 4 — Full combined function

```python
from kostreet_ai.geospatial.deduplication import deduplicate_and_filter

mixed = [
    make_detection(IssueCategory.pothole, 0.91, 42.6629, 21.1655),
    make_detection(IssueCategory.pothole, 0.74, 42.6630, 21.1656),  # near + weaker
    make_detection(IssueCategory.garbage, 0.30, 42.6629, 21.1655),  # below threshold
]
result = deduplicate_and_filter(mixed, radius_meters=20.0, confidence_threshold=0.55)
assert len(result) == 1
assert result[0].category == IssueCategory.pothole
assert result[0].confidence == 0.91
print("Full pipeline test PASSED")
```

---

## Files Changed Summary

| File | Action |
|---|---|
| `geospatial/__init__.py` | Create (empty) |
| `geospatial/deduplication.py` | Create |

No existing files are modified.

---

## Gate to Pass Before Phase 5

All 4 verification steps above must print PASSED with zero assertion errors.
