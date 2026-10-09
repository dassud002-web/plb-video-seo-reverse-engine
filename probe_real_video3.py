"""Real-video acceptance test: trace the full pipeline from video to grounded Story DNA."""
import sys
sys.path.insert(0, '/c/Users/Admin/Desktop/google-project')

import cv2
import numpy as np
from pathlib import Path

from story_forge.engine.video_story_extractor import extract_video_story_evidence
from story_forge.engine.story_dna import build_story_dna
from story_forge.engine.character_universe import extract_canon_characters
from story_forge.engine.prompt_compiler import compile_prompt_package

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

        canon = extract_canon_characters(ev, dna)
        print(f"[canon] count: {len(canon)}")
        for c in canon:
            print(f"[canon] {c.name} | species={c.species} | is_canon={c.is_canon}")

        # Prompt compilation verification
        hero = {"composition": "test", "lighting": "golden", "color_palette_lock": ["green"], "camera_lens": "50mm"}
        cont = {"character_morphology_rules": [" Preserve"], "environment_rules": [" Keep"], "immutable_traits": [" Object scale"]}
        pkg = compile_prompt_package(story=dna, story_dna=dna, hero_frame=hero, continuity_lock=cont)
        sd = pkg.get('seedance_25_prompt', '')
        print(f"[prompt] seedance_25 present: {bool(sd)}  chars={len(sd)}")
        print(f"[prompt] models keys: {list(pkg.get('models', {}).keys())}")
        return ev, dna, canon, pkg
    except Exception as e:
        print(f"[ERROR] {type(e).__name__}: {e}")
        import traceback; traceback.print_exc()
        return None, None, None, None

# 1. Dola chickens video (expected: Chicken / Hen)
dola = UPLOADS / "d70c5a_dola_20261007060757_video.mp4"
if dola.exists():
    report(dola, "Dola Chickens")
else:
    print("Dola video does not exist")

# 2. Ref video (cockatoo) in input/
ref = INPUT / "ref-video.mp4"
if ref.exists():
    report(ref, "Ref Video (Cockatoo)")
else:
    print("Ref video does not exist")

# 3. Winter Colobok (cat in snow)
cats = list(INPUT.glob("*Winter*"))
if cats:
    report(cats[0], "Winter Colobok (Cat)")
else:
    print("No Winter Colobok in input")
