# Reverse-Engineering Investigation & Evidence-Based SEO Report

**Target Asset**: `C:\Users\Admin\Downloads\test-reel\test-reel.mp4`  
**Accompanying File**: `C:\Users\Admin\Downloads\test-reel\Caption.md`  
**Investigation Date**: October 7, 2026  
**Provider**: REA Framework & Local Forensic Toolchain (FFmpeg 9.0.2, OpenCV 5.0, Python 3.14)

---

## 1. Technical Container & Stream Metadata (Ground Truth)

* **Container Format**: ISO/IEC 14496-12 QuickTime / MP4 (`isom`)
* **File Size**: `112,324,145 bytes` (107.12 MB)
* **Muxer / Tag**: `Lavf58.76.100` (FFmpeg libavformat)
* **Video Stream (Track 1)**:
  * **Codec**: H.264 / AVC (`avc1`)
  * **Profile / Level**: High Profile (`0x64`), Level 3.1
  * **Resolution**: `720 x 1280` pixels (9:16 vertical portrait aspect ratio)
  * **Frame Rate**: `24.000 fps` progressive (`r_frame_rate: 24/1`)
  * **Total Video Frames**: `721` frames
  * **Duration**: `30.041667 s` (Movie duration `30.080 s`)
  * **Video Bitrate**: `29,764 kbps` (~29.76 Mbps)
  * **Pixel Format**: `yuv420p`, progressive
  * **B-Frames**: Present (`has_b_frames: 2`, `ctts` atom verified)
* **Audio Stream (Track 2)**:
  * **Codec**: AAC LC (`mp4a`)
  * **Channels**: 2 (Stereo)
  * **Sample Rate**: 32,000 Hz
  * **Bitrate**: `129.22 kbps`
  * **Duration**: `30.080 s`
  * **Total Audio Packets**: `941` packets
* **Cryptographic Provenance (C2PA Manifest)**:
  * Embedded ISO 19566-5 JUMBF box (`d8fec3d6-1b0e-483c-9297-5828877ec481`, 44,926 bytes)
  * **Generator**: `BytePlus_ModelArk` v1.0.0 / `Dola` v`seedance_v2.5`
  * **Underlying Generative Model**: `dreamina-seedance-2-5` (ByteDance / BytePlus SeaDance 2.5)
  * **IPTC Digital Source Type**: `http://cv.iptc.org/newscodes/digitalsourcetype/trainedAlgorithmicMedia` (Synthetic AI Media)
  * **Signing Authority**: GlobalSign S/MIME CA 2025 (`c2pa-rs` v0.78.4 / 0.78.6)
  * **Creation Timestamp**: `2026-09-30T01:55:55Z`

---

## 2. Visual Narrative & Frame Breakdown

14 representative frames were extracted across the timeline (`scratch/frames/`):

1. **00.00s (Frame 1)**: Opening Hook Setup. A pure white Pekin duck with bright orange bill and a fluffy black puppy with a white chest star stand side-by-side on a lush green lawn directly behind a stationary black pop-up sprinkler head. Both face forward.
2. **01.00s (Frame 25)**: Sudden Action Hook. The sprinkler erupts, firing high-pressure radial water jets directly into the camera lens and showering the duck and puppy.
3. **02.00s (Frame 49)**: Reaction Cut. The duck turns and scurries away across the grass through the perimeter of the spray.
4. **03.00s (Frame 73)**: Pursuit Initiation. The black puppy leaps into an energetic bounding chase directly behind the duck, running through the mist.
5. **04.50s (Frame 109)**: Side-by-side sprint across the field.
6. **06.33s (Frame 153)**: High-mist action shot. The puppy leaps in mid-stride, racing behind the duck as a heavy fan of water blankets the left of the frame.
7. **09.00s (Frame 217)**: Wide spray arch. The sprinkler shoots a tall water fountain into the sky; the animals navigate the surrounding mist.
8. **11.50s (Frame 277)**: Synchronized flight. Duck and puppy run away in tandem through the falling spray.
9. **15.00s (Frame 361)**: Midpoint landscape shot. Shows depth of the backyard with dense background foliage and a small white wooden shed / coop.
10. **18.42s (Frame 443)**: Close-up trot. The duck walks proudly forward, followed closely by the prancing puppy.
11. **21.08s (Frame 507)**: Return to camera. Both animals head back toward the foreground.
12. **23.79s (Frame 572)**: Final water burst. They weave back through the active sprinkler spray.
13. **27.00s (Frame 649)**: The Climax / Stand-Down. The sprinkler shuts down. Both puppy and duck stand side-by-side, thoroughly soaked, staring squarely into the camera.
14. **29.92s (Frame 719)**: The Payoff / Double Shake. Both animals shake off the water with a tiny residual puff of steam/mist from the sprinkler head. The puppy’s curly tail is raised triumphantly.

---

## 3. Audio & Acoustic Analysis

* **Overall Audio Energy**: Overall RMS `-25.06 dBFS`, Peak `-2.03 dBFS`.
* **Acoustic Structure**:
  * **0.0s – 1.0s**: Quiet lawn atmosphere (`-20.7 dBFS`).
  * **1.0s – 2.0s**: Sudden dynamic surge (`-18.6 dBFS`) matching the sprinkler turn-on and pressurized water jet.
  * **2.0s – 26.0s**: Continuous broad-spectrum water rushing, splashing, and environmental sprinkler hiss (dominant energy in 250 Hz – 8 kHz bands).
  * **27.0s**: Sharp drop in energy (`-43.8 dBFS`) corresponding to the sprinkler stopping.
  * **28.0s – 30.0s**: Secondary audio event (`-32.3 dBFS`) matching the fur/feather shaking and water droplets landing.
* **Autocorrelation & Pitch**: Low autocorrelation ($<0.30$) confirms **absence of musical melodies, singing, speech voiceovers, or human dialogue**. The audio track is composed entirely of **environmental Sound Effects (SFX) / water spraying and nature ambiance**.

---

## 4. OCR & Branding Inspection

* **Scanned Areas**: Top banners, bottom lower-thirds, four screen corners, and full central frame across all 14 frames.
* **Result**: **0 text overlays, 0 usernames, 0 logos, 0 burned-in captions, and 0 watermarks**.
* **Status**: Clean raw visual footage.

---

## 5. Evidence Matrix

| Category | Directly Observed Facts (100% Proven) | High-Confidence Inferences | Unknown / Not Determinable |
| :--- | :--- | :--- | :--- |
| **Media Details** | 720x1280 9:16 vertical, 24.0 fps progressive H.264 High@3.1, 30.08s, 29.8 Mbps bitrate, 32kHz stereo AAC. | Optimized for mobile vertical platforms (TikTok, Reels, Shorts). | Exact camera sensor or rendering render farm specifications beyond the reported software stack. |
| **Visuals** | White Pekin duck, black mixed-breed puppy with white chest, black pop-up lawn sprinkler, green yard, background shed. | Animals have a playful, friendly domestic bond (no predatory aggression). | Exact breed mix of the black puppy. |
| **Story Arc** | Sprinkler erupts -> Duck flees -> Puppy chases duck through water spray -> Both return soaked -> Both shake off water. | Narrative designed to generate wholesome humor and high watch completion via the anticipation of the final shake. | Intentional staging vs organic capture (though C2PA proves synthetic algorithmic generation). |
| **Audio** | No speech dialogue, no voiceover, no background music melody; stereo environmental water sound effects. | Sound design was either synthesized or foley-recorded to match the visual water events. | Sound library source of the water audio asset. |
| **Provenance** | C2PA assertion specifies `dreamina-seedance-2-5` via `BytePlus_ModelArk 1.0.0` and `Dola seedance_v2.5` on 2026-09-30T01:55:55Z. | Generated using ByteDance's generative AI video pipeline (SeaDance / Dreamina) and managed through Dola Pro. | The exact natural language text prompt used to generate the video in Dreamina. |
