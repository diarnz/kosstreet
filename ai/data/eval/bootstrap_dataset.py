"""
Populate ai/data/eval/ from demo fixtures and generate Street View simulations.

Run from the ai/ directory:

    python data/eval/bootstrap_dataset.py

Requires demo images in data/demo/ (run data/demo/download_demo_images.py first).
"""

from __future__ import annotations

import json
import pathlib
import shutil
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "src"))

from kostreet_ai.preprocessing.street_view_sim import simulate_street_view_frame

EVAL_DIR = pathlib.Path(__file__).parent
DEMO_DIR = EVAL_DIR.parent / "demo"
FIXTURES_FILE = DEMO_DIR / "fixtures.json"
MANIFEST_FILE = EVAL_DIR / "manifest.json"

SIM_SOURCE_CATEGORIES = {
    "garbage",
    "pothole",
    "blocked_sidewalk",
    "damaged_sign",
    "broken_streetlight",
    "other",
    "clean",
}


def _category_folder(expected_category: str, expected_civic: bool) -> str:
    if not expected_civic:
        return "clean"
    return expected_category


def bootstrap() -> None:
    fixtures = json.loads(FIXTURES_FILE.read_text(encoding="utf-8"))
    manifest: list[dict] = []
    missing: list[str] = []

    for fixture in fixtures:
        filename = fixture["filename"]
        source_path = DEMO_DIR / filename
        if not source_path.exists():
            missing.append(filename)
            continue

        folder = _category_folder(fixture["expected_category"], fixture["expected_civic"])
        dest_dir = EVAL_DIR / "images" / folder
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest_path = dest_dir / filename
        shutil.copy2(source_path, dest_path)

        sample_id = pathlib.Path(filename).stem
        rel_path = f"images/{folder}/{filename}"
        manifest.append(
            {
                "id": sample_id,
                "filename": rel_path,
                "expected_category": fixture["expected_category"],
                "expected_civic": fixture["expected_civic"],
                "difficulty": "easy",
                "source": "stock",
                "notes": fixture.get("label", ""),
            }
        )

        if folder not in SIM_SOURCE_CATEGORIES:
            continue

        sim_dir = EVAL_DIR / "street_view_sim" / folder
        sim_dir.mkdir(parents=True, exist_ok=True)
        sim_name = f"{sample_id}_sim.jpg"
        sim_path = sim_dir / sim_name
        sim_bytes = simulate_street_view_frame(source_path.read_bytes())
        sim_path.write_bytes(sim_bytes)

        manifest.append(
            {
                "id": f"{sample_id}_sim",
                "filename": f"street_view_sim/{folder}/{sim_name}",
                "expected_category": fixture["expected_category"],
                "expected_civic": fixture["expected_civic"],
                "difficulty": "hard",
                "source": "synthetic_downscale",
                "source_image": rel_path,
                "notes": f"Street View simulation of {filename}",
            }
        )

    MANIFEST_FILE.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print(f"Wrote {len(manifest)} manifest entries to {MANIFEST_FILE}")
    print(f"Original images: {sum(1 for m in manifest if m['source'] == 'stock')}")
    print(f"Simulated frames: {sum(1 for m in manifest if m['source'] == 'synthetic_downscale')}")

    if missing:
        print(f"\nMissing demo images ({len(missing)}): {', '.join(missing)}")
        print("Run: python data/demo/download_demo_images.py")
        sys.exit(1)


if __name__ == "__main__":
    bootstrap()
