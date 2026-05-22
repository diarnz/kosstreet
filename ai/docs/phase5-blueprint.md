# Phase 5 Blueprint: Demo Data Setup & Accuracy Validation

## Goal

Populate `ai/data/demo/` with real, legally usable images that cover all 6 issue
categories. Validate that the classifier scores at least 75% accuracy against them.
Create `fixtures.json` that both the accuracy script and the backend seed script use.

After this phase:
- 13 demo images exist on disk (2 per category + 1 negative sample)
- `fixtures.json` maps each image to its expected category and Prishtina coordinates
- The accuracy script confirms Gemma 4 classifies at least 10 of 12 civic images correctly
- Any prompt adjustments needed to reach 75% are identified and applied
- The backend team can use `fixtures.json` to seed the demo database

---

## Current Project State

```
ai/data/demo/     ← empty, needs all images
ai/data/demo/     ← no fixtures.json yet

ai/src/kostreet_ai/
├── inference/classifier.py    ← get_classifier() ready
└── preprocessing/image.py     ← encode_image_to_base64() ready
```

---

## Image Requirements

### Source rules (from AI_BLUEPRINT.md)
- Citizen-uploaded or team-captured images: use freely
- Google Street View imagery: do NOT store, do NOT use for model testing
- Public domain / open-license imagery: allowed for demo and validation

### Source to use: Unsplash (free, no attribution required for demos)
Unsplash provides royalty-free images via direct URL with `?w=640&q=80` parameters.
We download and store them — they are not Google Street View, so storage is permitted.

---

## Images to Download: 13 Total

| Filename | Category | Expected result | Unsplash search hint |
|---|---|---|---|
| `pothole_01.jpg` | pothole | is_civic_issue=true | pothole road damage |
| `pothole_02.jpg` | pothole | is_civic_issue=true | cracked asphalt road |
| `garbage_01.jpg` | garbage | is_civic_issue=true | street litter garbage |
| `garbage_02.jpg` | garbage | is_civic_issue=true | illegal dumping waste |
| `streetlight_01.jpg` | broken_streetlight | is_civic_issue=true | broken street lamp |
| `streetlight_02.jpg` | broken_streetlight | is_civic_issue=true | damaged light pole |
| `sidewalk_01.jpg` | blocked_sidewalk | is_civic_issue=true | cracked sidewalk pavement |
| `sidewalk_02.jpg` | blocked_sidewalk | is_civic_issue=true | broken pavement walkway |
| `sign_01.jpg` | damaged_sign | is_civic_issue=true | bent road sign |
| `sign_02.jpg` | damaged_sign | is_civic_issue=true | damaged street sign |
| `other_01.jpg` | other | is_civic_issue=true | graffiti wall urban |
| `other_02.jpg` | other | is_civic_issue=true | flooded street urban |
| `clean_01.jpg` | other | is_civic_issue=false | clean empty street |

**Total: 12 civic issue images + 1 negative sample**

### How images are downloaded
A Python download script uses `httpx` to fetch each image from Unsplash by
searching for a direct photo URL. During implementation, specific Unsplash photo
IDs will be used for reproducibility (same image every run).

---

## File to Create: `data/demo/fixtures.json`

This JSON file is the single source of truth for demo data.
Used by:
- The accuracy validation script in this phase
- The backend seed script (`scripts/seed_demo_data.py`)
- The demo runner in Phase 8

```json
[
  {
    "filename": "pothole_01.jpg",
    "expected_category": "pothole",
    "expected_civic": true,
    "latitude": 42.6596,
    "longitude": 21.1545,
    "label": "Pothole on Bill Clinton Boulevard",
    "department": "Roads / Public Works"
  },
  {
    "filename": "pothole_02.jpg",
    "expected_category": "pothole",
    "expected_civic": true,
    "latitude": 42.6601,
    "longitude": 21.1552,
    "label": "Road surface damage near Zahir Pajaziti Square",
    "department": "Roads / Public Works"
  },
  {
    "filename": "garbage_01.jpg",
    "expected_category": "garbage",
    "expected_civic": true,
    "latitude": 42.6617,
    "longitude": 21.1578,
    "label": "Scattered waste on Rexhep Luci Street",
    "department": "Sanitation"
  },
  {
    "filename": "garbage_02.jpg",
    "expected_category": "garbage",
    "expected_civic": true,
    "latitude": 42.6622,
    "longitude": 21.1585,
    "label": "Illegal dumping near residential area",
    "department": "Sanitation"
  },
  {
    "filename": "streetlight_01.jpg",
    "expected_category": "broken_streetlight",
    "expected_civic": true,
    "latitude": 42.6629,
    "longitude": 21.1600,
    "label": "Damaged lamp post on Nene Tereza Boulevard",
    "department": "Electrical / Infrastructure"
  },
  {
    "filename": "streetlight_02.jpg",
    "expected_category": "broken_streetlight",
    "expected_civic": true,
    "latitude": 42.6634,
    "longitude": 21.1610,
    "label": "Missing streetlight fixture near city park",
    "department": "Electrical / Infrastructure"
  },
  {
    "filename": "sidewalk_01.jpg",
    "expected_category": "blocked_sidewalk",
    "expected_civic": true,
    "latitude": 42.6640,
    "longitude": 21.1618,
    "label": "Cracked sidewalk on Garibaldi Street",
    "department": "Urban Maintenance"
  },
  {
    "filename": "sidewalk_02.jpg",
    "expected_category": "blocked_sidewalk",
    "expected_civic": true,
    "latitude": 42.6644,
    "longitude": 21.1625,
    "label": "Blocked pedestrian path near school",
    "department": "Urban Maintenance"
  },
  {
    "filename": "sign_01.jpg",
    "expected_category": "damaged_sign",
    "expected_civic": true,
    "latitude": 42.6650,
    "longitude": 21.1635,
    "label": "Bent road sign at intersection",
    "department": "Public Works"
  },
  {
    "filename": "sign_02.jpg",
    "expected_category": "damaged_sign",
    "expected_civic": true,
    "latitude": 42.6655,
    "longitude": 21.1640,
    "label": "Graffitied and damaged street sign",
    "department": "Public Works"
  },
  {
    "filename": "other_01.jpg",
    "expected_category": "other",
    "expected_civic": true,
    "latitude": 42.6660,
    "longitude": 21.1650,
    "label": "Graffiti on municipal wall",
    "department": "General"
  },
  {
    "filename": "other_02.jpg",
    "expected_category": "other",
    "expected_civic": true,
    "latitude": 42.6665,
    "longitude": 21.1660,
    "label": "Flooded street section",
    "department": "General"
  },
  {
    "filename": "clean_01.jpg",
    "expected_category": "other",
    "expected_civic": false,
    "latitude": 42.6670,
    "longitude": 21.1670,
    "label": "Clean street - negative sample",
    "department": null
  }
]
```

---

## Script to Create: `data/demo/download_demo_images.py`

A standalone Python script (not part of the package) that fetches all images
from Unsplash using hardcoded photo IDs for reproducibility and saves them to
`data/demo/`. Running this script again will overwrite with the same images.

The script:
1. Defines a list of `(filename, unsplash_photo_id)` pairs
2. For each pair, fetches `https://images.unsplash.com/photo-{id}?w=640&q=80`
3. Saves the bytes to `data/demo/{filename}`
4. Prints `saved: {filename} ({size} bytes)` for each
5. Prints a final count and any failures

---

## Script to Create: `data/demo/run_accuracy_check.py`

A standalone validation script that runs the full classifier against every
fixture image and prints a results table. Not part of the package — runs manually.

Output format:
```
filename           expected          actual            conf   match
pothole_01.jpg     pothole           pothole           0.91   OK
pothole_02.jpg     pothole           pothole           0.84   OK
garbage_01.jpg     garbage           garbage           0.76   OK
...
clean_01.jpg       other (no civic)  other             0.00   OK

Results: 12/13 correct (92.3%)
Gate: PASSED (threshold 75%)
```

Logic:
- For civic images: correct if `result.category == expected_category`
- For the negative sample: correct if `result.is_civic_issue == False`
- Print each row as it completes (no buffering) so progress is visible
- Final summary: `N/13 correct (X.X%) — Gate: PASSED/FAILED`

---

## Prompt Calibration (if accuracy < 75%)

If the accuracy script shows failures, apply these targeted fixes to
`inference/classifier.py` system prompt before re-running:

| Failure pattern | Fix to apply |
|---|---|
| Pothole called `other` | Add "pavement depression, asphalt fracture" to pothole definition |
| Garbage called `blocked_sidewalk` | Add "waste material on any surface" to garbage definition |
| Damaged sign called `other` | Add "any signage that is visually altered or displaced" to damaged_sign |
| Streetlight called `other` | Add "any lamp structure that appears non-functional or physically damaged" |
| Low confidence across all | Add "When uncertain, lean toward detecting the issue. Municipal workers verify." |

Only apply the specific fix for the observed failure — do not rewrite the whole prompt.

---

## Data Flow After Phase 5

```
data/demo/pothole_01.jpg  ──┐
data/demo/garbage_01.jpg  ──┤
...                         ├──► run_accuracy_check.py
data/demo/clean_01.jpg    ──┘         │
                                      ▼
                              13 ClassificationResults
                                      │
                                      ▼
                              accuracy >= 75%? → Gate PASSED
                              accuracy <  75%? → prompt calibration → re-run

data/demo/fixtures.json  ──► backend seed script (scripts/seed_demo_data.py)
                         ──► Phase 8 demo runner
```

---

## Files Changed Summary

| File | Action |
|---|---|
| `data/demo/*.jpg` (13 files) | Download via script |
| `data/demo/fixtures.json` | Create |
| `data/demo/download_demo_images.py` | Create (standalone script) |
| `data/demo/run_accuracy_check.py` | Create (standalone script) |

No source package files are modified.

---

## Gate to Pass Before Phase 6

1. All 13 images exist in `data/demo/`
2. `fixtures.json` is valid JSON with 13 entries
3. `run_accuracy_check.py` prints `Gate: PASSED` (>= 10/13 correct)
4. If any prompt calibration was needed, it is documented as a comment
   in `inference/classifier.py` above the adjusted line
