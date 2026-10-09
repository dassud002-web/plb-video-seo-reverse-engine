#!/usr/bin/env python3
import sys
from pathlib import Path
import json

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from story_forge.engine.vision_pipeline import extract_multi_timestamp_evidence

videos = [
    ("Video 1 (Winter Colobok)", list(Path("input").glob("*Winter*"))[0]),
    ("Video 2 (Dola Chickens)", Path("temp_uploads/d70c5a_dola_20261007060757_video.mp4")),
    ("Video 3 (Cockatoo Ref)", Path("input/ref-video.mp4"))
]

for label, v in videos:
    print("=" * 70)
    print(f"TESTING: {label} ({v.stem[:30]})")
    ev = extract_multi_timestamp_evidence(v, num_samples=5)
    print(f"Setting: {ev['setting_environment']['description']}")
    print(f"Consensus Entity: {json.dumps(ev['consensus_entity'], indent=2)}")
    print("Direct Facts:")
    for f in ev['layers']['directly_observed_facts']:
        print(f"  - {f}")
    print("Model Inferences:")
    for m in ev['layers']['model_inferences']:
        print(f"  - {m}")
    print("Metadata Hints:")
    for h in ev['layers']['metadata_hints']:
        print(f"  - {h}")
    print("Uncertainties:")
    for u in ev['layers']['uncertain_information']:
        print(f"  - {u}")
    print(f"Runtime Info: {ev['model_runtime']}")
