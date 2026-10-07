# PLB Video SEO Reverse Engineering Engine

[![Video SEO Reverse Engineering](https://github.com/dassud002-web/plb-video-seo-reverse-engine/actions/workflows/video-seo.yml/badge.svg)](https://github.com/dassud002-web/plb-video-seo-reverse-engine/actions/workflows/video-seo.yml)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FFmpeg](https://img.shields.io/badge/FFmpeg-Enabled-green.svg)](https://ffmpeg.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> **Repository**: [https://github.com/dassud002-web/plb-video-seo-reverse-engine](https://github.com/dassud002-web/plb-video-seo-reverse-engine)

A forensic, non-destructive reverse-engineering toolchain and workflow designed to extract, analyze, and optimize metadata from short-form and long-form video files (TikTok, Instagram Reels, YouTube Shorts, Facebook Reels).

---

## Key Principles & Forensic Standards

1. **Non-Destructive Execution**: The engine operates purely in read-only mode against source video assets and sidecar documents. It never alters, overwrites, or deletes original media.
2. **Strict Metadata Provenance**: Verified original source metadata (from `Caption.md`, manifests, TXT, JSON, or container tags) is strictly separated from reconstructed/algorithm-optimized SEO.
3. **No Hallucinations**: When an original metadata field is absent in source files, it is explicitly stamped as `[NOT PRESENT IN SOURCE]`.
4. **C2PA Cryptographic Provenance**: Automatically detects ISO 19566-5 JUMBF boxes and Content Credentials (C2PA) manifests to identify generative AI foundation models (e.g. ByteDance/BytePlus SeaDance 2.5), digital source types, and signing authorities.
5. **Acoustic Waveform Analysis**: Decodes audio into uncompressed PCM to perform RMS energy profiling, peak detection, sub-band FFT spectral decomposition, and normalized autocorrelation for pitch/melody detection (distinguishing speech, music, and environmental sound effects).
6. **Timeline Frame Extraction**: Captures 12–14 critical editorial keyframes covering the 0–3s hook window, action progression, landscape depth, and payoff ending.
7. **Burned-In OCR & Watermark Scanning**: Analyzes top/bottom letterboxes, lower-thirds, and borders to verify unbranded raw footage vs. platform watermarks.

---

## Directory Structure

```
plb-video-seo-reverse-engine/
├── .github/
│   └── workflows/
│       └── video-seo.yml             # Automated CI & Workflow Dispatch runner
├── scripts/
│   └── video_seo_reverse_engineer.py # Reusable core reverse-engineering engine
├── requirements.txt                  # Python runtime dependencies
├── README.md                         # Documentation and usage guide
└── VIDEO-SEO-REVERSE-ENGINEERING-REPORT.md # Generated audit report sample
```

---

## Installation & Prerequisites

### 1. System Requirements
* **Python 3.10+**
* **FFmpeg & FFprobe** (must be on system `PATH`):
  * **macOS**: `brew install ffmpeg`
  * **Ubuntu/Debian**: `sudo apt-get install -y ffmpeg`
  * **Windows**: `choco install ffmpeg` or `winget install Gyan.FFmpeg`

### 2. Install Python Dependencies
```bash
pip install -r requirements.txt
```

---

## Usage

### Run Locally on Any Video Asset

To analyze any local video and its accompanying sidecars:

```bash
python scripts/video_seo_reverse_engineer.py \
  --video "/path/to/your/video.mp4" \
  --output "VIDEO-SEO-REVERSE-ENGINEERING-REPORT.md"
```

#### Optional CLI Arguments:
* `--video`: *(Required)* Path to the local video file.
* `--output`: *(Optional)* Path to output markdown report (default: `VIDEO-SEO-REVERSE-ENGINEERING-REPORT.md`).
* `--frames-dir`: *(Optional)* Custom directory to save extracted timeline JPEG frames.

---

## GitHub Actions Automated CI Runner

The repository includes `.github/workflows/video-seo.yml`, which runs automatically on push/PR and supports manual trigger (`workflow_dispatch`):

1. Go to the **Actions** tab on GitHub.
2. Select **Video SEO Reverse Engineering**.
3. Click **Run workflow**.
4. *(Optional)* Provide a `video_path` inside the repo or a direct `video_url` download link.
5. Upon completion, download the audit report artifact `video-seo-reverse-engineering-report` containing the generated `VIDEO-SEO-REVERSE-ENGINEERING-REPORT.md`.

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
