# ⚡ PLB STORY FORGE — VIDEO → 50 STORY → RECURSIVE STORY ENGINE

A production-grade, local-first narrative engineering tool that analyzes any video asset, extracts deep grounded narrative evidence, synthesizes structured **Story DNA**, generates **exactly 50 distinct root stories**, and enables **recursive 50-child branching** with full generational lineage tracking.

---

## 🌟 Core Capabilities

1. **Forensic Video Narrative Extraction (18 Domains)**:
   - Characters, animals, people, objects, setting, location type, visible actions, interactions, beginning state, middle events, ending state, cause → effect, conflict, emotional signals, surprise/payoff, repeating motifs, visual details, audio signals, OCR text.
   - Strict separation of `SOURCE_EVIDENCE`, `INFERENCE`, and `CREATIVE_EXPANSION`.
2. **Recombinant Story DNA**:
   - Synthesizes core premise, central tension, primary character dynamic, comedic/emotional engine, and reusable story elements grounded in timestamped keyframes.
3. **50 Distinct Root Stories (Generation 1)**:
   - Generates exactly 50 varied narrative concepts across 20 evolutionary dimensions (character, goal, motivation, conflict, obstacle, setting, tone, twist, stakes, etc.).
   - Guaranteed `parent_id = 'ROOT'` and `generation = 1`.
4. **Recursive Expansion (EXPAND ×50)**:
   - Branch any story into 50 child stories (`ROOT` → `STORY-01` → `STORY-01-01` → `STORY-01-01-01`).
   - Generation incrementing (`generation = parent.generation + 1`).
   - Lineage preservation with changed dimensions, new elements, and novelty scores.
5. **Deterministic Diversity Engine**:
   - Multi-field text & structural similarity checks (token sets, n-gram Jaccard, field comparisons).
   - Enforces diversity threshold $\ge 0.70$ (configurable in UI).
6. **Transparent Story Evolution Graph**:
   - Side-by-side parent vs child comparison showing inherited, changed, new, and removed elements.
   - No private model chain-of-thought exposed.
7. **Local-First Provider Architecture**:
   - 100% offline rule-based deterministic matrix generator with optional external LLM API fallback.
8. **Multi-Format Export & Local Persistence**:
   - SQLite local storage for sessions, stories, and lineage trees.
   - 1-click downloads for JSON, Markdown Story Bible, TXT summaries, and complete ZIP packages.

---

## 🚀 Quick Start & How to Run

### 1. Launch via Python
```powershell
python story_forge/run_app.py
```

### 2. Launch via Batch File (Windows)
Double-click `story_forge\run_app.bat` or run:
```cmd
.\story_forge\run_app.bat
```

### 3. Open in Browser
Visit:
```
http://127.0.0.1:5050
```
*(Runs independently on port 5050 alongside the Video SEO Reverse Engine on port 5000).*

---

## 🧪 Running the Test Suites

### Unit & Integration Tests:
```powershell
python story_forge/tests/test_story_forge.py
```

### 5-Video End-to-End Test Suite:
```powershell
python story_forge/tests/test_e2e_video.py
```

---

## 📁 Directory Structure

```
story_forge/
├── app.py                     # Flask web server & REST API
├── run_app.py                 # CLI launcher script
├── run_app.bat                # Windows batch launcher
├── requirements.txt           # Dependency specifications
├── README.md                  # Complete documentation
├── engine/
│   ├── evidence.py            # Evidence tagging & classification
│   ├── video_story_extractor.py # Forensic 18-domain extractor
│   ├── story_dna.py           # Story DNA builder
│   ├── diversity_engine.py    # Anti-duplication similarity engine
│   ├── lineage_engine.py      # Evolutionary comparison & novelty scoring
│   ├── story_generator.py     # 50 root stories orchestrator
│   ├── expansion_engine.py    # Recursive 50-child branching engine
│   └── providers/
│       ├── base.py            # Base provider interface
│       ├── local.py           # Local deterministic narrative engine
│       └── configurable.py    # Optional external LLM provider
├── storage/
│   ├── db.py                  # SQLite persistence layer
│   ├── story_forge.db         # Persistent SQLite database
│   └── frames/                # Cached keyframe thumbnails
├── exports/
│   └── exporter.py            # JSON, Markdown, TXT, and ZIP exporter
├── templates/
│   └── index.html             # 7-tab creator UI
├── static/
│   ├── css/
│   │   └── styles.css         # Dark-themed responsive stylesheet
│   └── js/
│       └── app.js             # Interactive client-side application
└── tests/
    ├── test_story_forge.py    # Unit & integration test suite
    ├── test_e2e_video.py      # Real video 5-target E2E test suite
    └── generic_unseen.mp4     # Generated test asset
```
