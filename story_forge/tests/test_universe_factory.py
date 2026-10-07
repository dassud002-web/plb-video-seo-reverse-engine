#!/usr/bin/env python3
"""
Comprehensive Test Suite for PLB Story Universe Factory
========================================================
Verifies:
1. Canon Character extraction & Creative Pool multi-species catalog
2. 15 Character Mutation Operators & 14 Relationship Types
3. 15 Canonical Story Worlds
4. 20-Dimensional Story Genome & structural mutations
5. 9-Dimensional Quality Engine, scoring & ranking
6. Scalable Universe Auto-Grow (100 and 300 stories)
7. Chicken / Lime diversity test (ensures unique species > 5, varied relationships)
8. 9-Part Production Pipeline (Script, Storyboard, AI prompts, SEO)
9. SQLite Persistence of Universe & Production packages
10. Multi-Format Exports (Universe JSON, Story Bible, Character Bible, CSV, ZIP)
11. Flask API Integration with test client
"""

import sys
import os
import json
import uuid
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

from story_forge.engine.character_universe import (
    extract_canon_characters,
    build_character_universe,
    apply_character_mutation,
    CharacterMutationOperator,
    CREATIVE_ANIMAL_TEMPLATES
)
from story_forge.engine.relationship_engine import (
    determine_relationship_for_ensemble,
    mutate_relationship,
    RelationshipType
)
from story_forge.engine.story_worlds import (
    CANONICAL_STORY_WORLDS,
    get_all_story_worlds
)
from story_forge.engine.story_genome import (
    StoryGenome,
    build_root_genome,
    mutate_story_genome
)
from story_forge.engine.quality_engine import (
    score_story_quality,
    rank_story_universe,
    QualityMetrics
)
from story_forge.engine.production_pipeline import (
    produce_story_package
)
from story_forge.engine.universe_engine import (
    generate_story_universe
)
from story_forge.storage.db import (
    init_db,
    save_session,
    save_stories_batch,
    get_session,
    get_story,
    get_all_stories_for_session,
    save_production_package,
    get_production_package
)
from story_forge.exports.exporter import (
    export_universe_json,
    export_story_bible_markdown,
    export_character_bible_markdown,
    export_relationship_graph_markdown,
    export_top_stories_csv,
    build_full_universe_zip_bundle
)
from story_forge.app import app

def run_tests():
    print("=" * 75)
    print("PLB STORY UNIVERSE FACTORY — COMPREHENSIVE TEST SUITE")
    print("=" * 75)

    # -------------------------------------------------------------
    # Test 1: Canon Characters & Creative Pool
    # -------------------------------------------------------------
    print("\n[TEST 1] Canon Character Extraction & Multi-Species Catalog...")
    mock_evidence = {
        "source_video_name": "Chicken Coop Video_TJX_no_watermark.mp4",
        "evidence_items": [
            {
                "category": "FACT",
                "claim": "A brown chicken pecks inquisitively at a halved green lime inside a coop run.",
                "timestamp_range": "00:00 - 00:08",
                "confidence": 0.98
            }
        ]
    }
    mock_story_dna = {
        "core_premise": "A curious chicken discovers a sour lime in the coop.",
        "characters": [
            {"name": "Brown Hen", "observed_fact": "Brown hen inside coop run"}
        ],
        "setting": "Coop Run",
        "central_tension": "Curiosity vs sour taste aversion",
        "hook": "Hen inspects mysterious bright lime",
        "conflict": "Pecking the lime reveals unexpected sourness",
        "twist": "A second peck confirms the shock",
        "payoff": "Comedic feather ruffle and head shake"
    }

    canon_chars = extract_canon_characters(mock_evidence, mock_story_dna)
    assert len(canon_chars) >= 1, "Must extract at least 1 canon character"
    assert canon_chars[0].species.lower() in ("chicken", "hen"), f"Canon species must be chicken/hen, got {canon_chars[0].species}"

    char_univ = build_character_universe(canon_chars, pool_size=25)
    assert len(char_univ["canon_characters"]) >= 1, "Must contain canon characters"
    assert len(char_univ["creative_pool"]) >= 20, "Creative pool must have at least 20 character profiles"

    # Verify multi-species presence in catalog
    catalog_species = {c["species"].lower() for c in char_univ["creative_pool"]}
    print(f"  ✓ Extracted {len(canon_chars)} Canon Characters: {[c.name for c in canon_chars]}")
    print(f"  ✓ Creative Pool contains {len(char_univ['creative_pool'])} characters across {len(catalog_species)} species: {sorted(list(catalog_species))[:8]}...")
    assert len(catalog_species) >= 10, "Creative catalog must span at least 10 domestic animal species"

    # -------------------------------------------------------------
    # Test 2: 15 Character Mutation Operators & 14 Relationship Types
    # -------------------------------------------------------------
    print("\n[TEST 2] Character Mutation Operators & Relationship Engine...")
    operators = list(CharacterMutationOperator)
    assert len(operators) == 15, f"Must have exactly 15 mutation operators, got {len(operators)}"

    # Test SPECIES_CROSSOVER operator
    mutated_crossover, meta_cross = apply_character_mutation(
        parent_characters=[c.to_dict() for c in canon_chars],
        operator=CharacterMutationOperator.SPECIES_CROSSOVER,
        character_pool=char_univ["creative_pool"],
        canon_characters=char_univ["canon_characters"]
    )
    assert len(mutated_crossover) >= 2, "Species crossover must produce at least 2 characters"
    species_pair = [c.get("species") for c in mutated_crossover]
    assert len(set(species_pair)) >= 2, f"Species crossover must involve distinct species, got {species_pair}"
    print(f"  ✓ SPECIES_CROSSOVER successfully paired {species_pair[0]} with {species_pair[1]}")

    # Test Relationship Modeling
    rel = determine_relationship_for_ensemble(mutated_crossover)
    assert "type" in rel and "tension_level" in rel, "Relationship must define type and tension_level"
    
    # Test Relationship Mutation
    mut_rel, rel_meta = mutate_relationship(rel, mutated_crossover, target_type=RelationshipType.MISCHIEF_PARTNERS.value)
    assert mut_rel["type"] == RelationshipType.MISCHIEF_PARTNERS.value, "Relationship type mutation failed"
    print(f"  ✓ Relationship mutated to {mut_rel['type']} (Tension: {mut_rel['tension_level']})")

    # -------------------------------------------------------------
    # Test 3: 15 Canonical Story Worlds
    # -------------------------------------------------------------
    print("\n[TEST 3] 15 Canonical Story Worlds...")
    worlds = CANONICAL_STORY_WORLDS
    assert len(worlds) == 15, f"Must have exactly 15 canonical story worlds, got {len(worlds)}"
    world_names = [w.name for w in worlds]
    print(f"  ✓ 15 Story Worlds verified: {world_names[:6]}... and 9 more.")

    # -------------------------------------------------------------
    # Test 4: 20-Dimensional Story Genome & Structural Shifts
    # -------------------------------------------------------------
    print("\n[TEST 4] 20-Dimensional Story Genome & Structural Evolution...")
    root_genome = build_root_genome(
        story_dna=mock_story_dna,
        characters=mutated_crossover,
        relationships=mut_rel,
        world=worlds[0].to_dict(),
        story_idx=1
    )
    assert root_genome.story_id == "UNIV-0001"
    assert len(root_genome.characters) >= 2
    assert root_genome.world_name == worlds[0].name

    child_genome, evo_meta = mutate_story_genome(
        parent=root_genome,
        new_story_id="UNIV-0002",
        mutated_characters=mutated_crossover,
        mutated_relationships=mut_rel,
        target_world=worlds[1].to_dict(),
        dimensional_shifts=["setting", "goal", "twist"]
    )
    assert child_genome.story_id == "UNIV-0002"
    assert child_genome.parent_id == "UNIV-0001"
    assert evo_meta["novelty_score"] >= 0.70
    print(f"  ✓ Genome mutated with Novelty Score: {evo_meta['novelty_score']} | Shifts: {evo_meta['dimensional_shifts']}")

    # -------------------------------------------------------------
    # Test 5: 9-Dimensional Quality Engine & Ranking
    # -------------------------------------------------------------
    print("\n[TEST 5] 9-Dimensional Quality Engine & Gate Scoring...")
    q_metrics = score_story_quality(child_genome.to_dict(), quality_gate_threshold=85.0)
    assert isinstance(q_metrics, QualityMetrics)
    assert 70.0 <= q_metrics.composite_score <= 100.0, f"Quality score out of range: {q_metrics.composite_score}"
    assert "novelty" in q_metrics.to_dict()["breakdown"]
    assert "short_form_potential" in q_metrics.to_dict()["breakdown"]
    assert "animal_appeal" in q_metrics.to_dict()["breakdown"]
    print(f"  ✓ Quality Composite Score: {q_metrics.composite_score:.1f} (Animal Appeal: {q_metrics.animal_appeal}, Hook Potency: {q_metrics.hook_potency})")

    # -------------------------------------------------------------
    # Test 6: Universe Auto-Grow (100 Stories) + Chicken/Lime Diversity
    # -------------------------------------------------------------
    print("\n[TEST 6] Auto-Grow Story Universe (100 Stories) & Diversity Firewall...")
    progress_log = []
    def on_progress(pct, msg):
        progress_log.append((pct, msg))

    univ_100 = generate_story_universe(
        evidence=mock_evidence,
        story_dna=mock_story_dna,
        target_count=100,
        diversity_threshold=0.75,
        quality_threshold=85.0,
        progress_callback=on_progress
    )

    stories_100 = univ_100["universe_stories"]
    metrics_100 = univ_100["metrics"]

    assert len(stories_100) == 100, f"Target count 100 requested, got {len(stories_100)}"
    assert metrics_100["unique_species_count"] >= 5, f"CRITICAL: Single chicken video must generate > 5 distinct species in universe, got {metrics_100['unique_species_count']} ({metrics_100['unique_species_list']})"
    assert metrics_100["unique_relationship_types"] >= 6, f"Must have >= 6 relationship types, got {metrics_100['unique_relationship_types']}"
    assert metrics_100["quality_score_range"]["avg"] >= 85.0, f"Avg quality score must be >= 85.0, got {metrics_100['quality_score_range']['avg']}"
    assert metrics_100["diversity_score_range"]["avg"] >= 0.75, f"Avg diversity score must be >= 0.75, got {metrics_100['diversity_score_range']['avg']}"

    print(f"  ✓ 100 Stories Generated Successfully!")
    print(f"  ✓ Species Diversity: {metrics_100['unique_species_count']} unique species: {metrics_100['unique_species_list']}")
    print(f"  ✓ Relationship Variety: {metrics_100['unique_relationship_types']} relationship types: {metrics_100['unique_relationship_list']}")
    print(f"  ✓ Avg Quality Score: {metrics_100['quality_score_range']['avg']} | Avg Diversity: {metrics_100['diversity_score_range']['avg']}")

    # -------------------------------------------------------------
    # Test 7: Universe Scaling (300 Stories)
    # -------------------------------------------------------------
    print("\n[TEST 7] Scaling to 300 Stories Universe...")
    univ_300 = generate_story_universe(
        evidence=mock_evidence,
        story_dna=mock_story_dna,
        target_count=300,
        diversity_threshold=0.75,
        quality_threshold=85.0
    )
    stories_300 = univ_300["universe_stories"]
    metrics_300 = univ_300["metrics"]
    assert len(stories_300) == 300, f"Target count 300 requested, got {len(stories_300)}"
    assert metrics_300["unique_species_count"] >= 8, f"In 300 stories, unique species must be >= 8, got {metrics_300['unique_species_count']}"
    print(f"  ✓ 300 Stories Scaled Successfully! Unique species: {metrics_300['unique_species_count']}, Plot patterns: {metrics_300['unique_plot_patterns']}")

    # -------------------------------------------------------------
    # Test 8: 9-Part Production Pipeline Studio
    # -------------------------------------------------------------
    print("\n[TEST 8] 9-Part Production Pipeline Synthesis...")
    selected_story = stories_100[0]
    prod_package = produce_story_package(selected_story, mock_story_dna)

    assert "production_script_15s" in prod_package
    assert len(prod_package["production_script_15s"]["beats"]) == 4, "Script must have 4 distinct beats"
    assert "storyboard_6_shots" in prod_package
    assert len(prod_package["storyboard_6_shots"]) == 6, "Storyboard must have exactly 6 shots"
    assert "hero_frame" in prod_package
    assert "continuity_lock" in prod_package
    assert "seedance_prompt" in prod_package and len(prod_package["seedance_prompt"]) > 50
    assert "veo_prompt" in prod_package and len(prod_package["veo_prompt"]) > 50
    assert "audio_plan" in prod_package
    assert "platform_captions" in prod_package
    assert "tiktok" in prod_package["platform_captions"]
    assert "seo_pack" in prod_package
    assert len(prod_package["seo_pack"]["hashtags"]) >= 5

    print(f"  ✓ 15-Second Script: {len(prod_package['production_script_15s']['beats'])} beats with Foley & timestamps")
    print(f"  ✓ 6-Shot Storyboard: {len(prod_package['storyboard_6_shots'])} shots")
    print(f"  ✓ Seedance Prompt: {prod_package['seedance_prompt'][:60]}...")
    print(f"  ✓ Google Veo Prompt: {prod_package['veo_prompt'][:60]}...")
    print(f"  ✓ SEO Pack: Topic: '{prod_package['seo_pack']['primary_topic']}' | Primary Keyword: '{prod_package['seo_pack']['primary_keyword']}'")

    # -------------------------------------------------------------
    # Test 9: SQLite Database Persistence
    # -------------------------------------------------------------
    print("\n[TEST 9] Database Persistence of Sessions, Universe & Packages...")
    init_db()
    test_session_id = f"test_{uuid.uuid4().hex[:6]}"
    save_session(
        session_id=test_session_id,
        meta=mock_evidence,
        story_dna=mock_story_dna,
        settings={"target_count": 100},
        character_universe=univ_100["character_universe"],
        universe_metrics=univ_100["metrics"]
    )
    save_stories_batch(test_session_id, stories_100)
    save_production_package(test_session_id, selected_story["story_id"], prod_package)

    retrieved_session = get_session(test_session_id)
    assert retrieved_session is not None, "Failed to retrieve session"
    assert retrieved_session["universe_metrics"]["unique_species_count"] >= 5
    assert len(retrieved_session["character_universe"]["creative_pool"]) >= 20

    retrieved_stories = get_all_stories_for_session(test_session_id)
    assert len(retrieved_stories) == 100, f"Expected 100 persisted stories, got {len(retrieved_stories)}"

    retrieved_pkg = get_production_package(test_session_id, selected_story["story_id"])
    assert retrieved_pkg is not None, "Failed to retrieve production package"
    assert retrieved_pkg["seedance_prompt"] == prod_package["seedance_prompt"]
    print(f"  ✓ Session, 100 Stories & Production Package persisted & retrieved successfully.")

    # -------------------------------------------------------------
    # Test 10: Multi-Format Exports
    # -------------------------------------------------------------
    print("\n[TEST 10] Multi-Format Exports Suite...")
    json_export = export_universe_json(test_session_id)
    assert len(json_export) > 1000
    parsed_json = json.loads(json_export)
    assert parsed_json["total_stories_count"] == 100

    bible_md = export_story_bible_markdown(test_session_id)
    assert "MASTER STORY BIBLE" in bible_md
    assert "TOP RANKED STORIES" in bible_md

    char_bible_md = export_character_bible_markdown(test_session_id)
    assert "CHARACTER BIBLE" in char_bible_md
    assert "CANON CHARACTERS" in char_bible_md

    rel_graph_md = export_relationship_graph_markdown(test_session_id)
    assert "RELATIONSHIP GRAPH" in rel_graph_md

    top_csv = export_top_stories_csv(test_session_id)
    assert "Story ID,Title,World,Quality Score" in top_csv

    zip_bundle = build_full_universe_zip_bundle(test_session_id)
    assert len(zip_bundle) > 2000, f"ZIP bundle size too small: {len(zip_bundle)}"
    print(f"  ✓ Verified Universe JSON ({len(json_export)} bytes)")
    print(f"  ✓ Verified Grand Story Bible MD ({len(bible_md)} bytes)")
    print(f"  ✓ Verified Character Bible MD ({len(char_bible_md)} bytes)")
    print(f"  ✓ Verified Relationship Graph MD ({len(rel_graph_md)} bytes)")
    print(f"  ✓ Verified Top Stories CSV ({len(top_csv)} bytes)")
    print(f"  ✓ Verified Full ZIP Bundle ({len(zip_bundle)} bytes)")

    # -------------------------------------------------------------
    # Test 11: Flask Test Client API Endpoints
    # -------------------------------------------------------------
    print("\n[TEST 11] Flask Application API Endpoints...")
    client = app.test_client()

    # GET /api/universe/<session_id>
    res_univ = client.get(f"/api/universe/{test_session_id}")
    assert res_univ.status_code == 200
    data_univ = res_univ.get_json()
    assert data_univ["total_stories"] == 100
    assert len(data_univ["top_rankings"]["top_10"]) == 10

    # GET /api/ranking/<session_id>?top_n=10&sort_by=quality
    res_rank = client.get(f"/api/ranking/{test_session_id}?top_n=10&sort_by=quality")
    assert res_rank.status_code == 200
    data_rank = res_rank.get_json()
    assert len(data_rank["stories"]) == 10
    assert data_rank["stories"][0]["quality_score"] >= data_rank["stories"][-1]["quality_score"]

    # GET /api/production/<session_id>/<story_id>
    res_prod = client.get(f"/api/production/{test_session_id}/{selected_story['story_id']}")
    assert res_prod.status_code == 200
    data_prod = res_prod.get_json()
    assert "production_script_15s" in data_prod["package"]

    # GET /api/export/story_bible/<session_id>
    res_exp = client.get(f"/api/export/story_bible/{test_session_id}")
    assert res_exp.status_code == 200
    assert b"MASTER STORY BIBLE" in res_exp.data

    print(f"  ✓ /api/universe/{test_session_id} -> 200 OK")
    print(f"  ✓ /api/ranking/{test_session_id}?top_n=10 -> 200 OK (Ranked order verified)")
    print(f"  ✓ /api/production/{test_session_id}/{selected_story['story_id']} -> 200 OK")
    print(f"  ✓ /api/export/story_bible/{test_session_id} -> 200 OK")

    print("\n" + "=" * 75)
    print("ALL 11 TEST MODULES PASSED SUCCESSFULLY! 🌟")
    print("=" * 75)

if __name__ == "__main__":
    run_tests()
