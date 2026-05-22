"""
Demo rehearsal script — simulates every API call the backend makes during the pitch.
Run with the AI service already running on port 8001.

    python data/demo/run_demo_rehearsal.py

Prints PASS / FAIL for each check, then exits 0 (all passed) or 1 (any failed).
"""

import base64
import json
import pathlib
import sys
import time

import httpx

AI_BASE = "http://localhost:8001"
DEMO_DIR = pathlib.Path(__file__).parent

PASS = "[PASS]"
FAIL = "[FAIL]"


def _ok(label: str, latency: float) -> None:
    print(f"  {PASS}  {label:<45} {latency*1000:.0f} ms")


def _fail(label: str, reason: str) -> None:
    print(f"  {FAIL}  {label:<45} {reason}")


def run_checks() -> int:
    failures = 0

    print()
    print("KoStreet AI - Demo Rehearsal")
    print("=" * 55)

    with httpx.Client(timeout=40.0) as client:

        # ── CHECK 1: Health ──────────────────────────────────────
        label = "GET /health"
        try:
            t0 = time.perf_counter()
            r = client.get(f"{AI_BASE}/health")
            elapsed = time.perf_counter() - t0
            data = r.json()
            assert r.status_code == 200
            assert data.get("status") == "ok"
            _ok(label, elapsed)
        except Exception as exc:
            _fail(label, str(exc))
            failures += 1

        # ── CHECK 2: OpenAPI docs ─────────────────────────────────
        label = "GET /docs (OpenAPI)"
        try:
            t0 = time.perf_counter()
            r = client.get(f"{AI_BASE}/docs")
            elapsed = time.perf_counter() - t0
            assert r.status_code == 200
            _ok(label, elapsed)
        except Exception as exc:
            _fail(label, str(exc))
            failures += 1

        # ── CHECK 3: Classify — pothole image ─────────────────────
        label = "POST /api/v1/classify (pothole)"
        pothole_path = DEMO_DIR / "pothole_01.jpg"
        if not pothole_path.exists():
            _fail(label, "pothole_01.jpg not found")
            failures += 1
        else:
            try:
                b64 = base64.b64encode(pothole_path.read_bytes()).decode()
                payload = {"image_base64": b64, "latitude": 42.6596, "longitude": 21.1545}
                t0 = time.perf_counter()
                r = client.post(f"{AI_BASE}/api/v1/classify", json=payload)
                elapsed = time.perf_counter() - t0
                data = r.json()
                assert r.status_code == 200, f"status={r.status_code}"
                assert data.get("is_civic_issue") is True, "not a civic issue"
                assert data.get("confidence", 0) >= 0.55, f"confidence={data.get('confidence')}"
                _ok(label, elapsed)
            except Exception as exc:
                _fail(label, str(exc))
                failures += 1

        # ── CHECK 4: Classify upload — multipart ──────────────────
        label = "POST /api/v1/classify/upload (multipart)"
        garbage_path = DEMO_DIR / "garbage_01.jpg"
        if not garbage_path.exists():
            _fail(label, "garbage_01.jpg not found")
            failures += 1
        else:
            try:
                t0 = time.perf_counter()
                with garbage_path.open("rb") as f:
                    r = client.post(
                        f"{AI_BASE}/api/v1/classify/upload",
                        files={"image": ("garbage_01.jpg", f, "image/jpeg")},
                    )
                elapsed = time.perf_counter() - t0
                data = r.json()
                assert r.status_code == 200, f"status={r.status_code}"
                assert data.get("is_civic_issue") is True, "not a civic issue"
                _ok(label, elapsed)
            except Exception as exc:
                _fail(label, str(exc))
                failures += 1

        # ── CHECK 5: Audit plan ───────────────────────────────────
        label = "POST /api/v1/audit/plan"
        try:
            payload = {
                "waypoints": [
                    {"lat": 42.6596, "lng": 21.1545},
                    {"lat": 42.6617, "lng": 21.1578},
                ],
                "step_meters": 50,
                "headings": [0, 90, 180, 270],
                "pitches": [0],
            }
            t0 = time.perf_counter()
            r = client.post(f"{AI_BASE}/api/v1/audit/plan", json=payload)
            elapsed = time.perf_counter() - t0
            data = r.json()
            assert r.status_code == 200, f"status={r.status_code}"
            assert len(data.get("scan_points", [])) > 0, "no scan_points"
            _ok(label, elapsed)
        except Exception as exc:
            _fail(label, str(exc))
            failures += 1

        # ── CHECK 6: Audit results JSON (pre-computed) ────────────
        label = "audit_results.json (pre-computed file)"
        results_path = DEMO_DIR / "audit_results.json"
        try:
            assert results_path.exists(), "file missing — run precompute_audit.py"
            data = json.loads(results_path.read_text(encoding="utf-8"))
            detections = data.get("detections", [])
            assert len(detections) >= 3, f"only {len(detections)} detections"
            t0 = 0.0
            elapsed = 0.0
            _ok(label, elapsed)
        except Exception as exc:
            _fail(label, str(exc))
            failures += 1

    print()
    print("=" * 55)
    total = 6
    passed = total - failures
    print(f"Result: {passed}/{total} checks passed")
    if failures == 0:
        print("All checks PASSED. AI layer is demo-ready!")
    else:
        print(f"{failures} check(s) FAILED. Fix them before the pitch.")
    print()
    return failures


if __name__ == "__main__":
    sys.exit(run_checks())
