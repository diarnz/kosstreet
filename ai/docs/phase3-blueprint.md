# Phase 3 Blueprint: Street Audit Planner

## Goal

Build the spatial logic that converts a street route into a complete set of
scan frames. Each frame represents one (latitude, longitude, heading, pitch)
position that the Street Audit Agent will photograph and analyze.

After this phase:
- The one existing failing test passes
- The backend can call `POST /api/v1/audit/plan` and receive a full list of frames
  for any street route in Prishtina
- The demo route on Bill Clinton Boulevard is ready to scan

---

## Current Project State

What already exists after Phases 0, 1, and 2:

```
ai/src/kostreet_ai/
├── config.py              ← reads .env, settings singleton
├── main.py                ← FastAPI on port 8001, /health works
├── schemas.py             ← FramePlan, AuditPlanRequest/Response, Waypoint defined
├── preprocessing/
│   └── image.py           ← encode, validate, decode
├── inference/
│   ├── client.py          ← OpenRouter HTTP wrapper
│   └── classifier.py      ← Gemma 4 classify(), get_classifier()
└── street_audit/
    └── __init__.py        ← empty (directory exists, no planner yet)

ai/tests/
└── test_street_audit_planner.py  ← EXISTS, currently FAILING
```

What Phase 3 adds:

```
ai/src/kostreet_ai/
└── street_audit/
    └── planner.py         ← build_heading_plan, interpolate_route_points,
                              build_audit_scan_plan
```

No other files are created or modified.

---

## The Existing Failing Test

This test already exists at `tests/test_street_audit_planner.py`.
It imports `build_heading_plan` from a module that does not exist yet.
Phase 3 makes it pass with zero changes to the test file.

```python
from kostreet_ai.street_audit.planner import build_heading_plan

def test_build_heading_plan_combines_headings_and_pitches() -> None:
    frames = build_heading_plan(42.6629, 21.1655, headings=(0, 90), pitches=(-10, 0))

    assert len(frames) == 4
    assert frames[0].heading == 0
    assert frames[-1].pitch == 0
```

What the test proves:
- `headings=(0, 90)` × `pitches=(-10, 0)` = 4 frames (cartesian product)
- First frame has `heading=0`
- Last frame has `pitch=0` → meaning last frame is `(heading=90, pitch=0)`

---

## File to Create: `street_audit/planner.py`

### Function 1: `build_heading_plan`

```python
def build_heading_plan(
    latitude: float,
    longitude: float,
    headings: tuple[int, ...] | list[int] = (0, 60, 120, 180, 240, 300),
    pitches: tuple[int, ...] | list[int] = (-10, 0),
) -> list[FramePlan]:
```

**Logic:** Cartesian product of `headings` × `pitches`, outer loop headings,
inner loop pitches. Returns a flat list of `FramePlan` objects.

For `headings=(0, 90), pitches=(-10, 0)` the output order is:
```
index 0 → FramePlan(lat, lng, heading=0,  pitch=-10)
index 1 → FramePlan(lat, lng, heading=0,  pitch=0)
index 2 → FramePlan(lat, lng, heading=90, pitch=-10)
index 3 → FramePlan(lat, lng, heading=90, pitch=0)
```

`frames[0].heading == 0` ✓
`frames[-1].pitch == 0` ✓ (index 3 has pitch=0)

Uses `FramePlan` imported from `kostreet_ai.schemas`.

---

### Function 2: `haversine_meters`

```python
def haversine_meters(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
```

Standard haversine formula. Earth radius = 6,371,000 meters.
Returns straight-line distance in meters between two (lat, lng) points.

```
R = 6_371_000
φ1, φ2 = radians(lat1), radians(lat2)
Δφ = radians(lat2 - lat1)
Δλ = radians(lon2 - lon1)
a  = sin(Δφ/2)² + cos(φ1) · cos(φ2) · sin(Δλ/2)²
c  = 2 · atan2(√a, √(1 − a))
return R · c
```

This function is also used later in Phase 4 (deduplication). Defining it here
keeps all distance math in one place.

---

### Function 3: `interpolate_route_points`

```python
def interpolate_route_points(
    waypoints: list[tuple[float, float]],
    step_meters: float = 30.0,
) -> list[tuple[float, float]]:
```

Takes a polyline defined by `waypoints` (list of `(lat, lng)` tuples) and
returns a new list of points placed every `step_meters` along the route.

**Algorithm — segment walk:**

1. Start with `result = [waypoints[0]]`
2. Track `remainder = 0.0` — leftover meters from the previous segment
3. For each consecutive pair (A, B):
   a. Compute `segment_len = haversine_meters(A, B)`
   b. Set `walked = remainder` (pick up where the last segment left off)
   c. While `walked + step_meters <= segment_len`:
      - `walked += step_meters`
      - `t = walked / segment_len` — linear interpolation factor (0.0 to 1.0)
      - `new_lat = A[0] + t * (B[0] - A[0])`
      - `new_lng = A[1] + t * (B[1] - A[1])`
      - Append `(new_lat, new_lng)` to result
   d. `remainder = segment_len - walked` — carry over to next segment
4. Always append the final waypoint
5. Return result

**Why linear interpolation is accurate enough here:**
At city scale (< 1 km segments), linear interpolation in geographic coordinates
introduces less than 0.1 meter of error. No need for geodesic math.

**Edge case:** If a segment is shorter than `step_meters`, no points are
added for that segment and the remainder carries forward to the next one.

---

### Function 4: `build_audit_scan_plan`

```python
def build_audit_scan_plan(
    waypoints: list[tuple[float, float]],
    step_meters: float = 30.0,
    headings: list[int] = (0, 60, 120, 180, 240, 300),
    pitches: list[int] = (-10, 0),
) -> list[FramePlan]:
```

Combines `interpolate_route_points` and `build_heading_plan`.

Steps:
1. Call `interpolate_route_points(waypoints, step_meters)` → list of scan points
2. For each scan point, call `build_heading_plan(lat, lng, headings, pitches)`
3. Flatten all results into one list
4. Return the complete frame plan for the entire route

This is the function the API endpoint calls directly.

---

## Demo Route Output

The Prishtina demo route defined in the main AI_BLUEPRINT.md:

```json
{
  "waypoints": [
    {"lat": 42.6596, "lng": 21.1545},
    {"lat": 42.6617, "lng": 21.1578},
    {"lat": 42.6640, "lng": 21.1611}
  ],
  "step_meters": 30,
  "headings": [0, 60, 120, 180, 240, 300],
  "pitches": [-10, 0]
}
```

Expected output:
- ~12–15 scan points interpolated along the two segments
- × 6 headings × 2 pitches = 12 frames per scan point
- Total: approximately 144–180 `FramePlan` objects

For the live demo a reduced set is used (step_meters=50, pitches=[-10] only)
to keep demo runtime under 30 seconds.

---

## Data Flow After Phase 3

```
Route waypoints [(lat,lng), (lat,lng), ...]
           │
           ▼
interpolate_route_points(waypoints, step_meters=30)
  → scan points every 30m along the route
           │
           ▼
for each scan point:
  build_heading_plan(lat, lng, headings, pitches)
  → 12 FramePlan objects per scan point
           │
           ▼
Flat list of FramePlan
  [FramePlan(lat, lng, heading=0,   pitch=-10),
   FramePlan(lat, lng, heading=0,   pitch=0),
   FramePlan(lat, lng, heading=60,  pitch=-10),
   ...]
           │
           ▼
(Phase 6) POST /api/v1/audit/plan returns this list to the backend
  Backend uses each FramePlan to fetch a Street View image
  Then calls POST /api/v1/audit/analyze-frame per image
```

---

## Verification Plan

### Step 1 — Existing test passes

```powershell
cd c:\Users\diar\Desktop\itpprizren\kostreet\ai
.venv\Scripts\activate
pytest tests/test_street_audit_planner.py -v
```

Expected:
```
PASSED tests/test_street_audit_planner.py::test_build_heading_plan_combines_headings_and_pitches
```

### Step 2 — Route interpolation sanity check

Run manually to verify the demo route produces a reasonable number of frames:

```python
from kostreet_ai.street_audit.planner import build_audit_scan_plan

frames = build_audit_scan_plan(
    waypoints=[(42.6596, 21.1545), (42.6617, 21.1578), (42.6640, 21.1611)],
    step_meters=30,
    headings=[0, 60, 120, 180, 240, 300],
    pitches=[-10, 0],
)
print(f"Total frames: {len(frames)}")
# Expected: between 120 and 200
```

### Step 3 — Haversine accuracy check

```python
from kostreet_ai.street_audit.planner import haversine_meters

d = haversine_meters(42.6629, 21.1655, 42.6638, 21.1655)
assert 95 < d < 105, f"Expected ~100m, got {d}"
print(f"Haversine test: {d:.1f}m — OK")
```

---

## Files Changed Summary

| File | Action |
|---|---|
| `street_audit/planner.py` | Create |

No existing files are modified.

---

## Gate to Pass Before Phase 4

1. `pytest tests/test_street_audit_planner.py -v` → PASSED
2. Demo route produces between 120 and 200 total frames
3. Haversine of ~100m segment returns a value between 95 and 105 meters
