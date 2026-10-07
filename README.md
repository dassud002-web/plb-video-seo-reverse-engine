# PLB Video SEO Reverse Engineering Engine (V2)

[![Video SEO Reverse Engineering](https://github.com/dassud002-web/plb-video-seo-reverse-engine/actions/workflows/video-seo.yml/badge.svg)](https://github.com/dassud002-web/plb-video-seo-reverse-engine/actions/workflows/video-seo.yml)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FFmpeg](https://img.shields.io/badge/FFmpeg-Enabled-green.svg)](https://ffmpeg.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> **Repository**: [https://github.com/dassud002-web/plb-video-seo-reverse-engine](https://github.com/dassud002-web/plb-video-seo-reverse-engine)

A forensic, non-destructive reverse-engineering toolchain and automated GitHub Actions workflow designed to extract, analyze, and optimize metadata from short-form and long-form video files (TikTok, Instagram Reels, YouTube Shorts, Facebook Reels).

---

## V2 End-to-End Workflow

**`LOCAL VIDEO → GIT PUSH → GITHUB ACTIONS → SEO REPORT ARTIFACT`**

### LOCAL:

1. **Copy video to**:
   ```
   input/target.mp4
   ```

2. **Run**:
   ```bash
   git add input/target.mp4
   git commit -m "feat: analyze new video"
   git push
   ```

3. **GitHub Actions automatically analyzes the video**.

4. **Download the generated**:
   ```
   VIDEO-SEO-REVERSE-ENGINEERING-REPORT.md
   ```

*(You can also place optional sidecar files like `input/Caption.md`, `input/notes.txt`, or `input/metadata.json` in the `input/` directory to have their original metadata automatically integrated).*

---

## Key Principles & Forensic Standards

1. **Non-Destructive Execution**: The engine operates purely in read-only mode against source video assets and sidecar documents. It never alters, overwrites, or deletes original media.
2. **Strict Metadata Provenance**: Verified original source metadata (from `Caption.md`, manifests, TXT, JSON, or container tags) is strictly separated from reconstructed/algorithm-optimized SEO.
3. **No Hallucinations**: When an original metadata field is absent in source files, it is explicitly stamped as `[NOT PRESENT IN SOURCE]`.
4. **C2PA Cryptographic Provenance**: Automatically detects ISO 19566-5 JUMBF boxes and Content Credentials (C2PA) manifests to identify generative AI foundation models (e.g. ByteDance/BytePlus SeaDance 2.5), digital source types, and signing authorities.
5. **Acoustic Waveform Analysis**: Decodes audio into uncompressed PCM to perform RMS energy profiling, peak detection, sub-band FFT spectral decomposition, and normalized autocorrelation for pitch/melody detection (distinguishing speech, music, and environmental sound effects).
6. **Timeline Frame Extraction**: Captures critical editorial keyframes covering the 0–3s hook window, action progression, landscape depth, and payoff ending.
7. **Burned-In OCR & Watermark Scanning**: Analyzes top/bottom letterboxes, lower-thirds, and borders to verify unbranded raw footage vs. platform watermarks.

---

## Directory Structure

```
plb-video-seo-reverse-engine/
├── .github/
│   └── workflows/
│       └── video-seo.yml             # Automated CI runner for input/target.mp4
├── input/
│   └── .gitkeep                      # Target directory for input/target.mp4
├── scripts/
│   └── video_seo_reverse_engineer.py # Reusable core reverse-engineering engine
├── requirements.txt                  # Python runtime dependencies
├── README.md                         # Documentation and usage guide
└── VIDEO-SEO-REVERSE-ENGINEERING-REPORT.md # Generated audit report sample
```

---

## Local CLI Usage

You can also run the engine directly on any local video asset outside of Git:

```bash
python scripts/video_seo_reverse_engineer.py \
  --video "input/target.mp4" \
  --output "VIDEO-SEO-REVERSE-ENGINEERING-REPORT.md"
```

### CLI Arguments:
* `--video`: *(Required)* Path to the local video file.
* `--output`: *(Optional)* Path to output markdown report (default: `VIDEO-SEO-REVERSE-ENGINEERING-REPORT.md`).
* `--frames-dir`: *(Optional)* Custom directory to save extracted timeline JPEG frames.

---

## Output Report Structure

Each generated `VIDEO-SEO-REVERSE-ENGINEERING-REPORT.md` includes:
1. **Target Identification & Discovered Sidecars** (Captions, prompts, manifests).
2. **Original Metadata vs. Reconstructed SEO** (Clean demarcation with `[NOT PRESENT IN SOURCE]` for unrecorded items).
3. **C2PA Cryptographic Provenance** (AI foundation model, generator platform, timestamp).
4. **Deep Technical Specifications** (Resolution, bitrate, FPS, B-frames, sample rate).
5. **Narrative & Acoustic Breakdown** (0–3s hook dynamics, acoustic classification).
6. **Multi-Platform SEO Packages**:
   * Primary Topic, Primary Keyword, Secondary Keywords, Long-Tail Queries.
   * 10 High-Ranking Titles + 3 High-Retention Algorithmic Titles.
   * Tailored Copy Packages: TikTok, Instagram Reels, Facebook Reels, YouTube Shorts.
   * 5 Thumbnail / Cover Concepts & 5 Alternative Hooks.
7. **Master Evidence Table** (Facts, Inferences, Confidence, and Unknowns).

---

## License

MIT License. Free for open-source and commercial reverse-engineering workflows.
