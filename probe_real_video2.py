import sys
sys.path.insert(0, '/c/Users/Admin/Desktop/google-project')

import cv2
import numpy as np
from pathlib import Path

from story_forge.engine.video_story_extractor import extract_video_story_evidence
from story_forge.engine.story_dna import build_story_dna
from story_forge.engine.character_universe import extract_canon_characters

INPUT = Path('/c/Users/Admin/Desktop/google-project/input')
UPLOADS = Path('/c/Users/Admin/Desktop/google-project/temp_uploads')

def report(video_path, label):
    print(f"\n{'='*60}")
    print(f"VIDEO: {label}  ({video_path.name})")
    print('='*60)
    try:
        # Verify it's a valid video first
        cap = cv2.VideoCapture(str(video_path))
        ok = cap.isOpened()
        n = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) if ok else 0
        w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)) if ok else 0
        h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)) if ok else 0
        fps = cap.get(cv2.CAP_PROP_FPS) if ok else 0
        cap.release()
        print(f"[metadata] valid={ok} frames={n} {w}x{h} fps={fps}")

        ev = extract_video_story_evidence(video_path)
        print(f"[evidence] visual_profile: {ev['visual_profile_name']}")
        print(f"[evidence] source_video_hash: {ev['source_video_hash'][:8]}")
        print(f"[evidence] characters.inference: {ev['domains']['characters']['inference'][:90]}")
        print(f"[evidence] setting.inference: {ev['domains']['setting']['inference'][:90]}")

        dna = build_story_dna(ev)
        print(f"[dna] confidence: {dna['confidence']} (0.0=unverified, not 1.0)")
        print(f"[dna] cv_limitation_disclosed: {dna['cv_limitation_disclosed']}")
        print(f"[dna] characters[0].name: {dna['characters'][0]['name']}")
        print(f"[dna] characters[0].species: {dna['characters'][0]['species']}")
        print(f"[dna] characters[0].level: {dna['characters'][0]['level']}")
        print(f"[dna] classification_status: {dna['characters'][0]['classification_status'][:80]}")
        print(f"[dna] core_premise: {dna['core_premise'][:110]}")
        print(f"[dna] central_tension: {dna['central_tension'][:110]}")
        print(f"[dna] setting: {dna['setting'][:90]}")
        print(f"[dna] objects[0].name: {dna['objects'][0]['name']}")
        print(f"[dna] evidence_refs count: {len(dna['evidence_refs'])}")
        print(f"[dna] visual_profile: {dna['visual_profile']}")
        return ev, dna
    except Exception as e:
        print(f"[ERROR] {type(e).__name__}: {e}")
        import traceback; traceback.print_exc()
        return None, None

# 1. Ref video in input (cockatoo), real 2.65MB
ref = INPUT / "ref-video.mp4"
if ref.exists():
    report(ref, "Ref Video (Cockatoo)")
else:
    print("Ref video NOT found")

# 2. Winter Colobok in input (cat)
cats = list(INPUT.glob("*Winter*"))
if cats:
    report(cats[0], "Winter Colobok (Cat)")
else:
    print("No Winter Colobok in input")

# 3. Real chicken sample videos in temp_uploads named *_colobok* - find the longest
samples = sorted(UPLOADS.glob("*.mp4"))
print(f"\n--- temp_uploads: {len(samples)} videos ---")
best = None
for s in samples:
    cap = cv2.VideoCapture(str(s))
    n = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) if cap.isOpened() else 0
    cap.release()
    if n > (best[1] if best else 0):
        best = (s, n)
print(f"Largest sample: {best[0].name} ({best[1]} frames)" if best else "none")
if best:
    s, _ = best
    cap = cv2.VideoCapture(str(s))
    n = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) if cap.isOpened() else 0
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)) if cap.isOpened() else 0
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)) if cap.isOpened() else 0
    fps = cap.get(cv2.CAP_PROP_FPS) if cap.isOpened() else 0
    cap.release()
    print(f"[metadata] {s.name}: valid={cap.isOpened()} frames={n} {w}x{h} fps={fps}")
    report(s, "Largest temp_upload sample")
