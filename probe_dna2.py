import sys
sys.path.insert(0, '/c/Users/Admin/Desktop/google-project')

from pathlib import Path
import tempfile, os
import cv2
import numpy as np

from story_forge.engine.evidence import EvidenceItem, EvidenceLevel, EvidenceType
from story_forge.engine.story_dna import build_story_dna
from story_forge.engine.story_generator import generate_50_root_stories

print("=== TEST: Story DNA Synthesis ===")
mock_evidence = {
    "source_video_name": "Test_Video.mp4",
    "source_video_hash": "a1b2c3d4",
    "visual_profile_name": "chickens_lime",
    "evidence_items": [],
    "domains": {
        "characters": {"fact": "1 white Silkie chicken", "inference": "White Silkie chicken", "count": 1},
        "objects": {"fact": "Fresh green cut lime half", "inference": "Sour citrus fruit"},
        "setting": {"fact": "Wooden outdoor coop railing", "inference": "Backyard farm coop"},
        "visible_actions": {"fact": "Approach -> Peck -> Recoil head shake", "inference": "Sour taste test"},
        "beginning_state": {"fact": "Chicken standing quietly on perch"},
        "middle_events": {"fact": "Beak contact with citrus pulp"},
        "ending_state": {"fact": "Sudden startled head tilt and recoil"},
        "conflict": {"fact": "Pungent acidity of the novel object"},
        "cause_effect": [{"cause": "Beak pecks citrus", "effect": "Sour shock triggers recoil"}],
        "repeating_motifs": ["Rustic wood grain", "Citrus lime green"]
    }
}
dna = build_story_dna(mock_evidence)
print("story_id:", dna["story_id"])
print("confidence:", dna["confidence"], "expected 0.0")
print("cv_limitation_disclosed:", dna["cv_limitation_disclosed"], "expected False")
print("core_premise:", dna.get("core_premise"))
print("central_tension:", dna.get("central_tension"))
print("reusable_story_elements count:", len(dna["reusable_story_elements"]))
print("visual_profile:", dna["visual_profile"])
print("metadata_cue:", dna["metadata_cue"])
print("classification_status:", dna["characters"][0]["classification_status"])
