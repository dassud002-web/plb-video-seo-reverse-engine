#!/usr/bin/env python3
"""
Unit and Integration Test Suite for PLB Story Forge
===================================================
Verifies:
1. Evidence categorization & fact/inference boundaries
2. Deterministic Diversity Engine & anti-duplication
3. Story DNA synthesis
4. Exactly 50 distinct root stories generation
5. Recursive 50-child expansion (Gen 2, Gen 3)
6. Story evolution engine & changed dimensions
7. Persistence (SQLite sessions, stories, lineage graphs)
8. Multi-format exports (JSON, MD, TXT, ZIP)
9. Noise token suppression
"""

import sys
import os
import json
from pathlib import Path

# Ensure UTF-8 output encoding on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# Add project root to path
current_dir = Path(__file__).resolve().parent.parent.parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

from story_forge.engine.evidence import EvidenceItem, EvidenceLevel, EvidenceType
from story_forge.engine.diversity_engine import (
    compute_pairwise_story_similarity,
    calculate_story_diversity_score,
    check_diversity_threshold
)
from story_forge.engine.story_dna import build_story_dna
from story_forge.engine.story_generator import generate_50_root_stories, sanitize_story_text
from story_forge.engine.expansion_engine import expand_story_node_50
from story_forge.engine.lineage_engine import evaluate_story_evolution, build_comparison_view_data
from story_forge.storage.db import (
    init_db,
    save_session,
    save_stories_batch,
    get_session,
    get_story,
    get_all_stories_for_session,
    get_lineage_graph
)
from story_forge.exports.exporter import (
    export_session_json,
    export_session_markdown,
    export_session_txt,
    build_session_zip_bundle
)

def test_story_forge_core():
    print("=" * 70)
    print(" 🚀 RUNNING PLB STORY FORGE UNIT & INTEGRATION TEST SUITE")
    print("=" * 70)

    # 1. Evidence Level Verification
    print("\n--- TEST 1: Evidence Classification & Tagging ---")
    ev = EvidenceItem(
        evidence_id="EV-01",
        level=EvidenceLevel.SOURCE_EVIDENCE.value,
        evidence_type=EvidenceType.VISUAL_KEYFRAME.value,
        timestamp_or_frame="01.50s (frame 36)",
        fact="White crested bird pecks green lime half",
        inference="Silkie chicken tasting sour citrus",
        confidence="100% (Fact)"
    )
    assert ev.level == "SOURCE_EVIDENCE"
    assert ev.confidence == "100% (Fact)"
    assert ev.evidence_id == "EV-01"
    print("✅ Evidence item structure and strict level tagging verified.")

    # 2. Diversity Engine Anti-Duplication
    print("\n--- TEST 2: Diversity Engine & Similarity Scoring ---")
    story_a = {
        "title": "The Lime Standoff",
        "one_line_premise": "A chicken pecks a lime on the ledge and recoils.",
        "conflict": "Sour taste vs pride",
        "twist": "It tries again anyway",
        "payoff": "Comedic head shake"
    }
    story_b_duplicate = {
        "title": "The Lime Standoff",
        "one_line_premise": "A chicken pecks a lime on the ledge and recoils.",
        "conflict": "Sour taste vs pride",
        "twist": "It tries again anyway",
        "payoff": "Comedic head shake"
    }
    story_c_diverse = {
        "title": "Midnight Heist in Orbit",
        "one_line_premise": "Zero-gravity operatives steal the sacred energy crystal from the airlock.",
        "conflict": "Laser perimeter security",
        "twist": "The crystal was a battery",
        "payoff": "Escape into hyperspace"
    }

    sim_dup = compute_pairwise_story_similarity(story_a, story_b_duplicate)
    sim_div = compute_pairwise_story_similarity(story_a, story_c_diverse)
    print(f"Similarity Duplicate: {sim_dup:.2f} | Similarity Diverse: {sim_div:.2f}")
    assert sim_dup > 0.90, "Duplicate similarity should be > 0.90"
    assert sim_div < 0.20, "Diverse similarity should be < 0.20"

    div_score = calculate_story_diversity_score(story_c_diverse, [story_a])
    assert div_score >= 0.70, f"Expected diversity score >= 0.70, got {div_score}"
    print(f"✅ Anti-duplication rejection & diversity score verified ({div_score}).")

    # 3. Noise Token Suppression
    print("\n--- TEST 3: Noise Token Suppression ---")
    noisy_text = "378c9d Rabbits & Horseradish TJX no_watermark test-reel clean footage"
    clean_text = sanitize_story_text(noisy_text)
    print(f"Original: '{noisy_text}' -> Sanitized: '{clean_text}'")
    assert "378c9d" not in clean_text
    assert "tjx" not in clean_text.lower()
    assert "watermark" not in clean_text.lower()
    assert "test-reel" not in clean_text
    print("✅ Noise token suppression confirmed.")

    # 4. Story DNA Synthesis
    print("\n--- TEST 4: Story DNA Synthesis ---")
    mock_evidence = {
        "source_video_name": "Test_Video.mp4",
        "source_video_hash": "a1b2c3d4",
        "visual_profile_name": "chickens_lime",
        "evidence_items": [ev.to_dict()],
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
    assert dna["story_id"] == "ROOT"
    assert dna["confidence"] == 1.0
    assert "core_premise" in dna
    assert "central_tension" in dna
    assert len(dna["reusable_story_elements"]) >= 3
    print(f"✅ Story DNA synthesized: {dna['core_premise']}")

    # 5. Exactly 50 Root Stories Generation
    print("\n--- TEST 5: Generate 50 Root Stories ---")
    stories = generate_50_root_stories(dna, mode="AUTO", threshold=0.70)
    print(f"Generated root stories count: {len(stories)}")
    assert len(stories) == 50, f"Expected exactly 50 root stories, got {len(stories)}"

    for idx, s in enumerate(stories, 1):
        expected_id = f"STORY-{idx:02d}"
        assert s["story_id"] == expected_id, f"Mismatched story_id: {s['story_id']} vs {expected_id}"
        assert s["parent_id"] == "ROOT", f"Root stories must have parent_id='ROOT', got {s['parent_id']}"
        assert s["generation"] == 1, f"Root stories must be generation 1, got {s['generation']}"
        assert s["title"], "Missing title"
        assert s["one_line_premise"], "Missing premise"
        assert s["hook"], "Missing hook"
        assert s["conflict"], "Missing conflict"
        assert s["twist"], "Missing twist"
        assert s["payoff"], "Missing payoff"
        assert s["diversity_score"] >= 0.70, f"Story {s['story_id']} diversity {s['diversity_score']} < 0.70"

    print("✅ Exactly 50 distinct root stories verified (all parent_id='ROOT', generation=1, diversity >= 0.70).")

    # 6. Recursive Expansion (Gen 2: 50 Children)
    print("\n--- TEST 6: Recursive Expansion (EXPAND ×50) ---")
    target_parent = stories[0]  # STORY-01
    print(f"Expanding parent node: {target_parent['story_id']} ({target_parent['title']})")
    children = expand_story_node_50(target_parent, mode="AUTO", threshold=0.70)
    print(f"Generated child stories count: {len(children)}")
    assert len(children) == 50, f"Expected exactly 50 children, got {len(children)}"

    for idx, c in enumerate(children, 1):
        expected_id = f"STORY-01-{idx:02d}"
        assert c["story_id"] == expected_id, f"Mismatched child ID: {c['story_id']}"
        assert c["parent_id"] == "STORY-01", f"Child parent_id must be STORY-01, got {c['parent_id']}"
        assert c["generation"] == 2, f"Child generation must be 2, got {c['generation']}"
        assert "evolution_metadata" in c, "Missing evolution metadata"
        evo = c["evolution_metadata"]
        assert "changed_dimensions" in evo, "Missing changed dimensions"
        assert len(evo["changed_dimensions"]) >= 1, "At least 1 changed dimension required"
        assert "novelty_score" in evo, "Missing novelty score"

    print("✅ Recursive expansion verified: 50 children created with generation=2, parent_id='STORY-01', and evolution tracking.")

    # 7. Recursive Expansion Deep Test (Gen 3: 50 Grandchildren)
    print("\n--- TEST 7: Recursive Deep Expansion (Gen 3: Grandchildren) ---")
    target_child = children[4]  # STORY-01-05
    grandchildren = expand_story_node_50(target_child, mode="AUTO", threshold=0.70)
    assert len(grandchildren) == 50, f"Expected 50 grandchildren, got {len(grandchildren)}"
    assert grandchildren[0]["generation"] == 3
    assert grandchildren[0]["parent_id"] == "STORY-01-05"
    assert grandchildren[0]["story_id"] == "STORY-01-05-01"
    print(f"✅ Deep expansion verified: Gen 3 node {grandchildren[0]['story_id']} correctly linked to parent {target_child['story_id']}.")

    # 8. Story Evolution & Comparison View
    print("\n--- TEST 8: Story Evolution Engine & Comparison Data ---")
    comp_view = build_comparison_view_data(target_parent, children[0])
    assert comp_view["parent"]["story_id"] == "STORY-01"
    assert comp_view["child"]["story_id"] == "STORY-01-01"
    assert "evolution" in comp_view
    assert comp_view["evolution"]["novelty_score"] >= 0.0
    print(f"✅ Comparison data built cleanly: Novelty={comp_view['evolution']['novelty_score']}, Changed={comp_view['evolution']['changed_dimensions']}")

    # 9. SQLite Persistence Layer
    print("\n--- TEST 9: SQLite Database Persistence ---")
    init_db()
    test_session_id = "test_sess_01"
    save_session(test_session_id, mock_evidence, dna, {"mode": "AUTO", "threshold": 0.70})
    save_stories_batch(test_session_id, stories)
    save_stories_batch(test_session_id, children)

    fetched_sess = get_session(test_session_id)
    assert fetched_sess is not None
    assert fetched_sess["session_id"] == test_session_id

    all_fetched_stories = get_all_stories_for_session(test_session_id)
    assert len(all_fetched_stories) == 100, f"Expected 100 total stories (50 root + 50 child), got {len(all_fetched_stories)}"

    tree = get_lineage_graph(test_session_id)
    assert tree["id"] == "ROOT"
    assert len(tree["children"]) == 50
    # Child STORY-01 should have 50 children
    story_01_node = next(n for n in tree["children"] if n["id"] == "STORY-01")
    assert len(story_01_node["children"]) == 50
    print(f"✅ SQLite persistence verified: 100 stories saved and lineage graph structured correctly.")

    # 10. Multi-Format Exporters
    print("\n--- TEST 10: Multi-Format Exporters (JSON, MD, TXT, ZIP) ---")
    exported_json = export_session_json(test_session_id)
    parsed_json = json.loads(exported_json)
    assert parsed_json["session_id"] == test_session_id
    assert parsed_json["total_stories_count"] == 100
    print(f"✅ JSON export verified: {len(exported_json)} chars")

    exported_md = export_session_markdown(test_session_id)
    assert "# 🎬 PLB STORY FORGE — COMPLETE STORY BIBLE" in exported_md
    assert "## 🧬 I. STORY DNA" in exported_md
    assert "## 🌳 II. 50 ROOT STORIES (GENERATION 1)" in exported_md
    assert "## 🌿 III. RECURSIVELY EXPANDED STORIES (GENERATION 2+)" in exported_md
    print(f"✅ Markdown export verified: {len(exported_md)} chars")

    exported_txt = export_session_txt(test_session_id)
    assert "PLB STORY FORGE — SUMMARY LOG" in exported_txt
    assert "[STORY-01]" in exported_txt
    print(f"✅ TXT export verified: {len(exported_txt)} chars")

    zip_bytes = build_session_zip_bundle(test_session_id)
    assert len(zip_bytes) > 1000
    print(f"✅ ZIP export verified: {len(zip_bytes)} bytes")

    print("\n" + "=" * 70)
    print(" 🎉 ALL PLB STORY FORGE UNIT & INTEGRATION TESTS PASSED (100% GREEN)")
    print("=" * 70)

if __name__ == "__main__":
    test_story_forge_core()
