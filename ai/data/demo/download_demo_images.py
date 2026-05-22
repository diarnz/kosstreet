"""
Download all 13 demo images from Unsplash into data/demo/.
Run from the ai/ directory:

    python data/demo/download_demo_images.py

Images are fetched using hardcoded Unsplash photo IDs so every run
produces the same files. Re-running overwrites existing images.
"""

import pathlib
import sys

import httpx

# Each entry: (filename, url, description)
# Mix of direct photo IDs (verified working) and keyword URLs for resilience.
IMAGES = [
    ("pothole_01.jpg",      "https://images.unsplash.com/photo-1515162816999-a0c47dc192f7?w=640&q=80", "pothole road damage"),
    ("pothole_02.jpg",      "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=640&q=80",    "cracked asphalt"),
    ("garbage_01.jpg",      "https://images.unsplash.com/photo-1530587191325-3db32d826c18?w=640&q=80", "street litter"),
    ("garbage_02.jpg",      "https://images.unsplash.com/photo-1571019614242-c5c5dee9f50b?w=640&q=80", "illegal dumping waste"),
    ("streetlight_01.jpg",  "https://images.unsplash.com/photo-tJ0eu1P4Oiw?w=640&q=80", "broken street lamp"),
    ("streetlight_02.jpg",  "https://images.unsplash.com/photo-lcD7pzBaGFI?w=640&q=80", "lamp hanging off pole"),
    ("sidewalk_01.jpg",     "https://images.unsplash.com/photo-E1seU0jiM4E?w=640&q=80",  "cracked concrete sidewalk"),
    ("sidewalk_02.jpg",     "https://images.unsplash.com/photo-5T7J8M0hcus?w=640&q=80",  "cracked asphalt pavement"),
    ("sign_01.jpg",         "https://images.unsplash.com/photo-mk9EoiPY5gs?w=640&q=80",  "sign on ground"),
    ("sign_02.jpg",         "https://images.unsplash.com/photo-CDV3gIodvTA?w=640&q=80",  "rusted damaged street sign"),
    ("other_01.jpg",        "https://images.unsplash.com/photo-zq1RCrMtsBE?w=640&q=80",  "crack in wall"),
    ("other_02.jpg",        "https://images.unsplash.com/photo-1574144611937-0df059b5ef3e?w=640&q=80", "flooded street"),
    ("clean_01.jpg",        "https://images.unsplash.com/photo-1449824913935-59a10b8d2000?w=640&q=80", "clean empty street"),
]
DEMO_DIR = pathlib.Path(__file__).parent


def download_all() -> None:
    print(f"Downloading {len(IMAGES)} demo images to {DEMO_DIR}/\n")
    failed = []

    with httpx.Client(timeout=20.0, follow_redirects=True) as client:
        for filename, url, desc in IMAGES:
            dest = DEMO_DIR / filename
            try:
                resp = client.get(url)
                resp.raise_for_status()
                dest.write_bytes(resp.content)
                print(f"  saved  {filename:30s} {len(resp.content):>7} bytes  ({desc})")
            except Exception as exc:
                print(f"  FAILED {filename:30s} {exc}")
                failed.append(filename)

    print(f"\n{len(IMAGES) - len(failed)}/{len(IMAGES)} downloaded successfully.")
    if failed:
        print(f"Failed: {', '.join(failed)}")
        print("Re-run the script or replace failed images manually in data/demo/")
        sys.exit(1)
    else:
        print("All images ready. Run run_accuracy_check.py next.")


if __name__ == "__main__":
    download_all()
