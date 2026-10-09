import sys
sys.path.insert(0, "/c/Users/Admin/Desktop/google-project")

from story_forge.engine.story_dna import build_story_dna
from story_forge.engine.evidence import EvidenceItem, EvidenceLevel, EvidenceType

ev = {
    "source_video_name": "test.mp4",
    "source_video_hash": "abc",
    "visual_profile_name": "generic",
    "domains": {
        "characters": {"fact": "Observed: Hen tracked across 5 timeline milestones (MODERATE Confidence: 85.0%)", "inference": "Hen (Chicken)", "count": 1},
        "setting": {"fact": "Observed: Rustic wooden garden patio (100% Fact)", "inference": "Backyard domestic poultry coop", "confidence": "100% (Fact)"},
        "objects": {"fact": "Observed: Fresh cut lime half on coop ledge", "inference": "Benchmark Profile: Fresh sour green lime half", "confidence": "100% (Fact)"},
        "visible_actions": {"fact": "Perch approach -> Curious inspection -> Direct beak peck", "inference": "Peck into citrus pulp", "confidence": "100% (Fact)"},
        "conflict": {"fact": "Curiosity vs bitter citrus flavor", "inference": "Flavor shock", "confidence": "100% (Fact)"},
        "cause_effect": [{"cause": "Peck", "effect": "Sour recoil"}],
        "evidence_items": [{"evidence_id": "EV-01", "claim": "Hen pecks lime"}],
    },
    "vision_evidence": {
        "consensus_entity": {"display": "Hen", "species": "Chicken", "confidence_tier": "MODERATE", "confidence_pct": 85.0, "is_verified": True},
        "layers": {"directly_observed_facts": ["Container: 1280x720 resolution, 24.0 fps, 12.00s duration"],
                   "model_inferences": ["Vision Model: MobileNetV2-ONNX"],
                   "metadata_hints": [],
                   "uncertain_information": []}
    }
}
dna = build_story_dna(ev)
print("T1 confidence:", dna["confidence"], "(expected 1.0 hardcoded)")
print("T1 cv_limitation_disclosed:", dna["cv_limitation_disclosed"])
print("T1 character name:", dna["characters"][0]["name"], "species:", dna["characters"][0]["species"])
print("T1 level:", dna["characters"][0]["level"])

from story_forge.engine.providers.local import LocalStoryProvider
from story_forge.engine.story_generator import generate_50_root_stories
stories = generate_50_root_stories({}, mode="AUTO", threshold=0.70)
low = [s for s in stories if s["diversity_score"] < 0.70]
print("T2 stories with diversity_score < 0.70:", len(low), "(should be 0 - forced by max())")

from story_forge.engine.quality_engine import score_story_quality
s1 = {"story_id": "STORY-01", "title": "Test", "one_line_premise": "A curious pet explores a bubble machine", "hook": "lock eyes", "conflict": "peck", "twist": "sour", "payoff": "head shake", "characters": [], "mode": "FUNNY"}
qm = score_story_quality(s1)
print("T3 loopability:", qm.loopability, "(90.0 because 'loop' in story dict - fabrication)")

from story_forge.engine.prompt_compiler import compile_prompt_package
pkg = compile_prompt_package(story=s1, story_dna={})
print("T4 seedance_25_prompt present:", bool(pkg.get("seedance_25_prompt")), "models keys:", list(pkg.get("models", {}).keys()))
print("T4 models keys len:", len(pkg.get("models", {})))
