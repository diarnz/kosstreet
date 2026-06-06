# AI Classification Accuracy Improvement Blueprint

> **Status:** Phase 10 complete — Phase 11 deferred; live Street View eval added  
> **Scope:** `ai/` directory only  
> **Constraint:** Do not start Phase N+1 until Phase N checklist is signed off

---

## 1. Goal

Improve civic-issue classification accuracy for categories that underperform in real use — especially **garbage**, **blocked_sidewalk**, **damaged_sign**, and **other** — while **keeping pothole accuracy** at its current strong level.

### Success criteria

| # | Criterion | Target |
|---|-----------|--------|
| 1 | Per-category accuracy on eval set | ≥ 85% for garbage, blocked_sidewalk, damaged_sign, other |
| 2 | Pothole accuracy | ≥ 90% (no regression) |
| 3 | Civic detection rate (issues found vs missed) | ≥ 90% on eval set |
| 4 | False positives on clean streets | ≤ 10% |
| 5 | Street View–style images (distant, compressed) | garbage recall ≥ 75% |
| 6 | All existing `pytest` tests still pass | 100% green |

### Non-goals (this blueprint)

- Changing backend, frontend, or API contracts outside `ai/`
- Pixel-perfect bounding boxes (that is a separate overlay/detection track)
- Replacing OpenRouter with a self-hosted LLM in production (optional path only)
- Bulk-downloading or storing Google Street View imagery (TOS violation)

---

## 2. Current state (baseline)

### Architecture today

```
Image bytes
  → preprocessing/image.py (resize to 1024px, JPEG encode)
  → inference/classifier.py (single Gemma 4 call via OpenRouter)
  → JSON parse + severity floor post-processing
  → ClassificationResult
```

There is **no local model training** in the live pipeline. Accuracy depends almost entirely on:

1. The system prompt in `inference/classifier.py`
2. Image quality and framing
3. The vision model (`google/gemma-4-26b-a4b-it`)

Optional deps (`torch`, `ultralytics`) exist in `pyproject.toml` but are **not wired** into production inference.

### Baseline accuracy run (2026-06-06)

Command: `python data/demo/run_accuracy_check.py`  
Model: `google/gemma-4-26b-a4b-it`  
Dataset: 13 stock Unsplash images in `data/demo/`

| Category | Correct | Total | Rate | Notes |
|----------|---------|-------|------|-------|
| pothole | 2 | 2 | **100%** | Strong — do not regress |
| garbage | 2 | 2 | **100%** | Good on close-up stock photos |
| broken_streetlight | 2 | 2 | **100%** | Good on stock photos |
| blocked_sidewalk | 1 | 2 | **50%** | `sidewalk_01` → predicted `pothole` |
| damaged_sign | 1 | 2 | **50%** | `sign_02` → predicted `broken_streetlight` |
| other | 1 | 2 | **50%** | `other_02` (flooded street) → `is_civic_issue=false` |
| clean (negative) | 1 | 1 | **100%** | Correctly rejected |

**Aggregate:** civic detection 92.3%, category match 83.3%.

### Why potholes work but other categories struggle

| Factor | Potholes | Garbage / other |
|--------|----------|-----------------|
| Visual salience | Dark holes, high contrast on asphalt | Small litter, distant bins, blends with background |
| Training bias | Common in vision LLM pretraining | Often confused with `blocked_sidewalk` or `other` |
| Street View distance | Still visible as road texture change | Bags/bottles often sub-pixel at 30m scan distance |
| Category overlap | Sometimes cracks on sidewalks → `pothole` | Signs vs poles, waste on sidewalk vs blocked path |

**Key insight:** Stock demo images are close-up and clean. Real Kosovo Street View frames are the harder case. The blueprint must optimize for **distant, compressed, oblique street-level photos**, not just the current 13 demo fixtures.

---

## 3. Root causes to fix

### 3.1 Prompt ambiguity

The current prompt lists categories but does not teach **disambiguation**:

- `pothole` vs `blocked_sidewalk` when cracks appear on a walking surface
- `damaged_sign` vs `broken_streetlight` when vertical infrastructure is damaged
- `garbage` vs `blocked_sidewalk` when waste sits on a sidewalk
- `other` vs `is_civic_issue=false` for flooding, graffiti, drainage issues

### 3.2 Single-pass classification

One generic user message (`"Analyze this street-level photograph…"`) forces the model to classify and detect in one shot. Weak categories benefit from a **focused second pass** only when the first pass is uncertain.

### 3.3 Eval set is too small and too easy

- 13 images, 1–2 per category
- All stock photos; none from Prishtina streets
- No dedicated **hard negatives** (shadows, wet pavement, construction that looks like damage)
- No **Street View simulation** set (lower resolution, wider FOV)

### 3.4 No per-category metrics or confusion tracking

`run_accuracy_check.py` prints a table but does not produce a confusion matrix, per-category recall, or a regression gate per category.

### 3.5 Confidence is uncalibrated

The model returns `confidence=1.0` on many stock images but `0.0` on edge cases (`other_02`). There is no category-specific threshold tuning.

---

## 4. Proposed approach (four phases)

We improve accuracy in layers: fast prompt wins first, then eval rigor, then optional local detection, then Kosovo-specific data.

```
Phase 9  Prompt & disambiguation     ← 1–2 days, no GPU, highest ROI
Phase 10 Eval harness & dataset      ← 1–2 days, enables measurement
Phase 11 Hybrid detector (optional) ← 2–4 days, needs GPU for training
Phase 12 Kosovo field dataset       ← ongoing, team photos
```

---

## Phase 9: Prompt Engineering & Category Disambiguation

**Goal:** Lift weak categories without changing API shape or adding GPU deps.

### 9.1 Split system prompt into modules

Refactor `inference/classifier.py` prompt into composable sections:

```
prompts/
  base.py           # role, JSON schema, severity guide
  disambiguation.py # decision tree rules
  street_view.py    # distance/compression hints (for audit frames)
```

`classifier.py` assembles the final prompt from these modules. Pothole definitions stay **unchanged** to avoid regression.

### 9.2 Add explicit disambiguation rules (new prompt section)

Example rules to embed:

| If you see… | Choose… | Not… | Because… |
|-------------|---------|------|----------|
| Waste, bags, bottles, bins on any surface | `garbage` | `blocked_sidewalk` | Sanitation issue, not path obstruction |
| Crack/hole **in the road lane** | `pothole` | `blocked_sidewalk` | Road surface damage |
| Crack/obstacle **on sidewalk/pedestrian path only** | `blocked_sidewalk` | `pothole` | Walking infrastructure |
| Bent/fallen **sign board** | `damaged_sign` | `broken_streetlight` | Signage, not lighting |
| Damaged **lamp/pole/light fixture** | `broken_streetlight` | `damaged_sign` | Electrical infrastructure |
| Flooding, graffiti, drainage, vandalism | `other` | `is_civic_issue=false` | Still a civic issue |
| Clean street, no actionable issue | `other` + `is_civic_issue=false` | any issue category | Negative sample |

### 9.3 Category-specific detection bias (prompt only)

Add a short **"look harder for"** block for weak categories:

- **garbage:** single plastic bottles, cigarette packs, scattered papers, overflowing green bins, construction debris piles, tire dumps
- **other:** standing water on road, wall graffiti, broken curb without pothole, exposed cables, fallen tree branches
- **damaged_sign:** rust, missing face, bent post, graffiti on sign face (not the pole light)

**Do not** add similar bias language for potholes — they already work.

### 9.4 Two-pass "uncertainty resolver" (new, internal only)

When first-pass result meets **any** of:

- `confidence < 0.70`
- predicted category in `(_WEAK_CATEGORIES)` and `confidence < 0.85`
- predicted `pothole` but description mentions sidewalk/waste/sign

…run a **second focused prompt**:

```
"You previously classified this image as {category} with confidence {conf}.
Re-examine ONLY whether it should instead be one of: {alternatives}.
Respond with the same JSON schema."
```

`_WEAK_CATEGORIES = {garbage, blocked_sidewalk, damaged_sign, other}`

This adds one extra API call only on uncertain frames (~15–25% of Street View frames estimated), keeping cost manageable.

**API contract unchanged** — still returns one `ClassificationResult`.

### 9.5 Audit vs citizen context flag

Add optional `context: "street_audit" | "citizen_upload"` to internal classify path (not necessarily a public API change — can be set by `audit.py` vs `classify.py`).

When `street_audit`:

- Append `street_view.py` hints: *"Camera may be 10–30m from objects; small litter counts; lean toward reporting garbage if any waste is visible."*

When `citizen_upload`:

- Append: *"Photo is likely close-up; citizen is pointing at the issue."*

### 9.6 Confidence floor adjustments (post-processing)

Extend post-processing in `classifier.py`:

| Category | Min confidence to accept as civic issue | Notes |
|----------|------------------------------------------|-------|
| pothole | 0.55 (unchanged) | Already strong |
| garbage | 0.50 | Lower bar — easy to miss at distance |
| blocked_sidewalk | 0.55 | |
| damaged_sign | 0.55 | |
| broken_streetlight | 0.55 | |
| other | 0.45 | Catch-all; prefer recall |

Configurable via `KOSTREET_AI_CATEGORY_THRESHOLDS` JSON in `.env` (optional).

### Phase 9 files to touch

| File | Change |
|------|--------|
| `src/kostreet_ai/inference/classifier.py` | Modular prompts, two-pass logic, context flag |
| `src/kostreet_ai/inference/prompts/` | **New** — prompt modules |
| `src/kostreet_ai/api/v1/audit.py` | Pass `context="street_audit"` to classifier |
| `src/kostreet_ai/config.py` | Optional per-category thresholds |
| `tests/test_classifier.py` | Tests for two-pass, disambiguation, context |

### Phase 9 verification gate

```bash
cd ai
pytest tests/ -v
python data/demo/run_accuracy_check.py
# Target after Phase 9:
#   category match >= 11/12 on demo fixtures (fix sidewalk_01, sign_02, other_02)
#   pothole still 2/2
```

---

## Phase 10: Evaluation Harness & Expanded Dataset

**Goal:** Measure per-category accuracy and prevent regressions before every prompt change.

### 10.1 New eval layout

```
ai/data/eval/
  manifest.json          # all eval images + labels
  images/
    garbage/             # 10+ images
    pothole/             # 5+ (regression guard)
    blocked_sidewalk/
    damaged_sign/
    broken_streetlight/
    other/
    clean/               # hard negatives
  street_view_sim/       # downscaled / cropped wide-FOV variants
```

### 10.2 `manifest.json` schema

```json
{
  "filename": "eval/images/garbage/g01_distant_bin.jpg",
  "expected_category": "garbage",
  "expected_civic": true,
  "difficulty": "hard",
  "source": "team_capture | stock | synthetic_downscale",
  "notes": "Overflowing bin, 20m distance, Bill Clinton Blvd"
}
```

### 10.3 New script: `data/eval/run_eval.py`

Outputs:

- Per-category precision / recall / F1
- Confusion matrix (text + `eval_report.json`)
- Regression diff vs last run (`eval_baseline.json`)
- **Per-category gates** — fail CI if any category drops below threshold

### 10.4 Upgrade `run_accuracy_check.py`

- Delegate to shared metrics from `evaluation/metrics.py`
- Keep backward compatibility for demo fixtures
- Add `--category garbage` filter for quick iteration

### 10.5 Synthetic Street View simulation

Pure-Pillow pipeline in `preprocessing/street_view_sim.py`:

- Downscale to 640px width
- JPEG recompress at quality 60
- Optional mild blur

Apply to a subset of eval images to approximate Street View without storing Google imagery.

### Phase 10 verification gate

```bash
python data/eval/run_eval.py --report
# garbage recall >= 0.80 on eval set (stock + sim)
# pothole recall >= 0.90
# clean false-positive rate <= 0.10
```

---

## Phase 11: Hybrid Local Detector (Optional, GPU)

**Goal:** Add a **specialist garbage/waste detector** that boosts recall on small/distant litter, while keeping Gemma for category + severity + description.

> **Recommendation:** Only pursue Phase 11 if Phase 9–10 do not hit garbage recall ≥ 75% on `street_view_sim/` images.

### 11.1 Architecture

```
Image
  ├─→ YOLOv8-nano (local, fine-tuned) ─→ garbage candidates + bounding boxes
  └─→ Gemma 4 (OpenRouter) ─────────────→ category, severity, description

Merge logic (inference/hybrid.py):
  - If YOLO fires "garbage" with conf >= 0.4 AND Gemma says not civic or category != garbage
    → override category to garbage, bump confidence
  - If Gemma says garbage AND YOLO agrees → boost confidence (+0.15 cap 1.0)
  - Pothole path unchanged — YOLO not trained for potholes initially
```

### 11.2 Training data sources (legal)

| Source | Use |
|--------|-----|
| TACO dataset | Litter bounding boxes (academic, open) |
| Team-captured Kosovo photos | Fine-tune augmentations |
| `ai/data/raw/` | Your labeled images |

**Not** Street View downloads.

### 11.3 New files

```
ai/
  src/kostreet_ai/training/
    __init__.py
    export_yolo_dataset.py    # manifest → YOLO format
    train_garbage_detector.py # ultralytics CLI wrapper
  models/
    garbage_yolov8n.pt        # gitignored, shipped separately
  src/kostreet_ai/inference/
    hybrid.py                 # merge YOLO + Gemma
    yolo_detector.py          # lazy-load local model
```

### 11.4 Dependency gate

```bash
pip install -e ".[models]"
# Only required for training and hybrid inference
# Production can stay OpenRouter-only via KOSTREET_AI_HYBRID_ENABLED=false
```

### 11.5 Config

```
KOSTREET_AI_HYBRID_ENABLED=false
KOSTREET_AI_YOLO_MODEL_PATH=models/garbage_yolov8n.pt
KOSTREET_AI_YOLO_GARBAGE_THRESHOLD=0.40
```

### Phase 11 verification gate

```bash
python data/eval/run_eval.py --subset street_view_sim --category garbage
# garbage recall >= 0.75 with hybrid enabled
# pothole recall unchanged vs Phase 10 baseline
```

---

## Phase 12: Kosovo Field Dataset (Ongoing)

**Goal:** Close the gap between stock photos and real municipal imagery.

### Minimum collection targets

| Category | Team photos | Priority |
|----------|-------------|----------|
| garbage | 15 | **P0** — bags, bins, scattered litter, dumping |
| other | 10 | **P0** — flooding, graffiti, broken curb |
| blocked_sidewalk | 8 | P1 |
| damaged_sign | 8 | P1 |
| pothole | 5 | P2 — regression guard only |
| clean | 10 | P1 — hard negatives |

### Capture guidelines (1-page sheet in `data/eval/CAPTURE_GUIDE.md`)

- Stand where a Street View car would stand; shoot at eye level
- Include **distance variants**: 5m, 15m, 30m from the issue
- One issue per photo when possible
- GPS tag optional; filename encodes location

### Integration

New photos land in `data/eval/images/` → row added to `manifest.json` → `run_eval.py` picks them up automatically.

---

## 5. Category-by-category improvement plan

| Category | Current issue | Phase 9 action | Phase 10+ action |
|----------|---------------|----------------|------------------|
| **pothole** | Strong | **No prompt changes**; regression tests only | Keep 5+ eval images |
| **garbage** | Misses distant litter in SV | SV context prompt, lower threshold, "look harder" | YOLO hybrid, 15+ field photos |
| **blocked_sidewalk** | Confused with pothole | Disambiguation: sidewalk vs road surface | Eval images with cracks on paths only |
| **damaged_sign** | Confused with streetlight | Disambiguation: sign face vs lamp | Sign-specific eval set |
| **broken_streetlight** | OK on stock | Minor disambiguation only | Maintain |
| **other** | Missed civic issues (flooding) | Explicit "flooding/graffiti = other + civic" | Field photos for edge cases |
| **clean** | OK | Stricter "no issue" guidance | Hard negative eval images |

---

## 6. Risk matrix

| Risk | Impact | Mitigation |
|------|--------|------------|
| Pothole regression after prompt edits | High | Pothole-specific regression tests; no pothole prompt changes |
| Two-pass doubles API cost on uncertain frames | Medium | Only trigger on low confidence / weak categories |
| YOLO adds deploy complexity | Medium | Off by default; optional `[models]` extra |
| OpenRouter rate limits during eval | Low | Cache eval results; batch runs offline |
| Garbage false positives (shadows, leaves) | Medium | Require YOLO + Gemma agreement for boost; citizen review anyway |

---

## 7. Implementation order (recommended)

```
Week 1
  ✓ Phase 9.1–9.3  Prompt modules + disambiguation
  ✓ Phase 9.4      Two-pass resolver
  ✓ Phase 9.5–9.6  Context flag + thresholds
  ✓ Re-run demo accuracy check

Week 1–2
  ✓ Phase 10.1–10.3  Eval dataset + run_eval.py
  ✓ Phase 10.5       Street View simulation
  ✓ Phase 12         Start collecting Kosovo garbage/other photos

Week 2+ (only if needed)
  ○ Phase 11         YOLO garbage detector
```

---

## 8. Phase gate summary

| Phase | Deliverable | Gate |
|-------|-------------|------|
| 9 | Prompt v2 + two-pass classifier | Demo: ≥ 11/12 category match; pothole 2/2; `pytest` green |
| 10 | Eval harness + 50+ labeled images | garbage recall ≥ 80%; pothole ≥ 90% |
| 11 | Hybrid YOLO (optional) | garbage SV-sim recall ≥ 75% |
| 12 | Kosovo field dataset | 15+ garbage photos in eval manifest |

---

## 9. What I need from you before coding

Please confirm:

1. **Start with Phase 9 only?** (prompt + two-pass — fastest, no GPU)  
   Or also Phase 10 eval harness in the same pass?

2. **Two-pass OK for cost?** (~1 extra API call on uncertain frames)

3. **Phase 11 YOLO** — defer unless Phase 9–10 insufficient?

4. **Can you provide 5–10 real Prishtina garbage photos** for eval? (phone photos are fine)

Reply **"go"** (and any choices above) when ready for implementation.

---

## 10. Quick reference — files that exist today

| Path | Role |
|------|------|
| `src/kostreet_ai/inference/classifier.py` | Main prompt + inference |
| `data/demo/fixtures.json` | 13 demo labels |
| `data/demo/run_accuracy_check.py` | Current accuracy script |
| `evaluation/metrics.py` | Stub — will expand in Phase 10 |
| `inference/engine.py` | Unused VisionModel protocol — not in live path |
| `pyproject.toml` `[models]` | torch/ultralytics optional group |
