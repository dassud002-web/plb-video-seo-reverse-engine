import sys
sys.path.insert(0, '/c/Users/Admin/Desktop/google-project')
from story_forge.engine.providers.local import LocalStoryProvider
from story_forge.engine.story_generator import generate_50_root_stories
from story_forge.engine.story_dna import build_story_dna
from story_forge.engine.evidence import EvidenceItem, EvidenceLevel, EvidenceType

ev = {
    "source_video_name": "Test_Video.mp4", "source_video_hash": "a1b2c3d4",
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
dna = build_story_dna(ev)
provider = LocalStoryProvider()
raw = provider.generate_stories(story_dna=dna, count=50, mode="AUTO", threshold=0.70)
scores = sorted([(s['story_id'], round(s['diversity_score'],2)) for s in raw], key=lambda x: x[1])
print("total raw:", len(raw))
below = [s for s in raw if s['diversity_score'] < 0.70]
print("below 0.70:", [(s['story_id'], round(s['diversity_score'],2)) for s in below])
print("min:", min(s['diversity_score'] for s in raw), "max:", max(s['diversity_score'] for s in raw))
print("avg:", round(sum(s['diversity_score'] for s in raw)/len(raw), 3))
# check duplicates of titles
titles = [s['title'] for s in raw]
print("unique titles:", len(set(titles)))
print("all >=0.70:", all(s['diversity_score']>=0.70 for s in raw))
