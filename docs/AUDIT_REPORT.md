# PLB Studio — Codebase Audit Report

**Project:** google-project (`C:\Users\Admin\Desktop\google-project`)  
**Date:** October 9, 2026  
**Engineer:** PLB Studio Principal Engineer & Autonomous Repair Agent  
**Scope:** Full codebase, engines, Flask routes, frontend JS, storage, packaging, tests.

---

## 1. Project Root & Entry Points

```
google-project/
├── app.py               (marathon launcher, port 5050)
├── run_app.py
├── desktop_app.py
├── build_exe.bat
├── START-PLB-STUDIO.bat
├── run_app.bat
├── plb_studio.spec      (PyInstaller spec)
├── requirements.txt
├── README.md
├── story_forge/
│   ├── app.py           (Flask, 62K chars)
│   ├── static/
│   │   └── js/app.js    (102K chars, endpoint catalog generated)
│   ├── templates/       (HTML/CSS frontend)
│   ├── storage/
│   │   └── db.py        (SQLite: sessions, stories, universe, exports)
│   ├── engine/
│   │   ├── video_story_extractor.py
│   │   ├── vision_pipeline.py
│   │   ├── story_dna.py
│   │   ├── quality_engine.py
│   │   ├── story_generator.py
│   │   ├── production_pipeline.py
│   │   ├── prompt_compiler.py
│   │   ├── evidence.py
│   │   ├── story_genome.py
│   │   ├── character_universe.py
│   │   ├── character_universe.py
│   │   ├── universe_engine.py
│   │   ├── expansion_engine.py
│   │   ├── relationship_engine.py
│   │   ├── lineage_engine.py
│   │   ├── diversity_engine.py
│   │   ├── story_worlds.py
│   │   └── providers/
│   │       └── local.py
│   └── tests/
│       ├── test_vision_understanding.py
│       ├── test_bug002_video_identity.py
│       ├── test_story_forge.py
│       ├── test_creator_features.py
│       └── test_upload_pipeline.py
├── scripts/
│   └── video_seo_reverse_engineer.py   (SEO reverse-engineering, 104K chars)
├── input/               (user videos: ref-video.mp4, Winter colobok forest)
└── temp_uploads/        (runtime upload dir, 588 mp4)
```

**Entry points:** `app.py` (marathon), `run_app.py`, `desktop_app.py`, `START-PLB-STUDIO.bat`, `build_exe.bat`, `plb_studio.spec`.

**Detection notes:**
- `story_forge/app.py` resolves base dir differently when frozen (PyInstaller) vs source.
- `video_seo_reverse_engineer.py` was initially looked up under `story_forge/engine/scripts/` and was **not** found; the real path is `/c/Users/Admin/Desktop/google-project/scripts/video_seo_reverse_engineer.py`. The Flask `scan` route imports it dynamically (`from scripts.video_seo_reverse_engineer import extract_technical_metadata`) and both Python paths import it locally, so this is consistent — the audit path lookup was simply wrong.

---

## 2. Core Workflow Trace

```
VIDEO INPUT
  -> video_story_extractor.py (metadata + frame extraction)
  -> vision_pipeline.py (object/animal classification, motion, temporal analysis)
  -> evidence.py (EvidenceItem construction + provenance)
  -> story_dna.py (Story DNA construction: grounding, confidence, CV disclosure)
  -> character_universe.py / universe_engine.py (identity management)
  -> story_generator.py (generate_50_root_stories, diversity firewall)
  -> quality_engine.py (loopability, quality scoring)
  -> prompt_compiler.py (story -> Seedance/Veo prompts)
  -> production_pipeline.py (produce_story_package, validate)
  -> storage/db.py (SQLite persistence)
  -> exports (JSON, MD, TXT, ZIP)
  -> Flask API (/api/upload, /scan, /analyze, /status, /produce, /export)
```

---

## 3. Defects Found & Repaired

| # | File | Defect | Fix |
|---|---|---|---|
| P1 | `story_dna.py` | Hardcoded `confidence = 1.0`; unverified char turned into "Verified Benchmark/Sidecar Profile" with `cv_limitation_disclosed = False` | Grounded confidence 0.0/100.0; CV disclosure disclosed only when vision is unverified |
| P1 | `quality_engine.py` | Loopability = 90.0 merely because dict contained a `"loop"` key | Loopability requires actual `"loop"` keyword in the `loop` field |
| P1 | `local.py` | Diversity score forced up to threshold; fallback templates padded to 50 | Return only stories that genuinely pass the gate; no fabricated padding |
| P2 | `story_generator.py` | 50 IDs, no real diversity filtering, duplicate creation | Honest diversity firewall; distinct IDs; partial results on failure |
| P3 | `tests/test_story_forge.py` | Asserted buggy `confidence == 1.0` + 50-fallback layout | Assert grounded behavior and partial partial-results |
| P3 | `tests/test_upload_pipeline.py` | Asserted 50 stories produced | Assert honest partial results (`>=40`) |

---

## 4. Duplicate / Stale / Broken Things Verified

- **No duplicate module implementations** of the same operation were found (engines are cleanly separated).
- **No circular dependencies** detected among the engine modules.
- **No hardcoded secrets/tokens/passwords/credentials** found in source or config.
- **API routes consistent:** all `/api/*` endpoints in `app.js` have Flask counterparts.
- **`plb_studio.spec`** and `build_exe.bat` target PyInstaller; resource paths resolve for the frozen app.

---

## 5. Platform / Windows Notes

- `app.js` uses relative paths / service workers appropriately; no Windows-specific path bugs found in JS.
- Backend returns `path` as a normalized forward-slash string (no `WindowsPath` in JSON).
- Launch scripts (`START-PLB-STUDIO.bat`, `run_app.bat`) use Python/PyInstaller.

---

## 6. Documentation & Report Files Created

| File | Purpose |
|---|---|
| `docs/AUDIT_REPORT.md` | This document |
| `docs/REPAIR_REPORT.md` | Full repair & recovery report |
| `docs/TEST_REPORT.md` | Test results + real-video acceptance + packaging verification |

---

## 7. Git

- Recovery checkpoint: `3f944c1`
- Latest commit: `c002ca6` (guardian auto-snapshot)
- Working tree clean except 6 repaired files + untracked probe scripts.

---

## 8. Unverified Items (marked for accurate reporting)

| Item | Status |
|---|---|
| Standalone EXE end-to-end run in an isolated Windows process | **UNVERIFIED** (build + resource verification only) |
| Online vision model availability (cv2 dnn5 graph-engine error) | Unavailable in this env; offline path operational |
| GUI click-through by a human operator | Probe-verified HTTP contract; no manual GUI session run |

Per acceptance criteria, **no item is marked PASSED that could not be verified** — the EXE and GUI criteria are UNVERIFIED where a real run did not occur.
