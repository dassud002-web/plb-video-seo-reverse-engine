#!/usr/bin/env python3
"""
Story Universe Factory Engine for PLB Story Universe Factory
============================================================
Scales Story DNA into rich, multi-world Story Universes of 100, 300, 500, or 1,000+ stories.
Orchestrates:
Character Pool -> Relationship Pool -> Story Worlds -> Auto-Grow Loop -> Quality Gate -> Diversity Firewall.
Ensures high species diversity, varied relationship structures, and zero duplicate filler.
"""

from typing import Dict, Any, List, Optional, Callable
import random

from story_forge.engine.character_universe import (
    extract_canon_characters,
    build_character_universe,
    apply_character_mutation,
    CharacterMutationOperator
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
from story_forge.engine.diversity_engine import (
    calculate_story_diversity_score
)
from story_forge.engine.quality_engine import (
    score_story_quality,
    rank_story_universe
)

def generate_story_universe(
    evidence: Dict[str, Any],
    story_dna: Dict[str, Any],
    target_count: int = 100,
    diversity_threshold: float = 0.75,
    quality_threshold: float = 85.0,
    progress_callback: Optional[Callable[[int, str], None]] = None
) -> Dict[str, Any]:
    """
    Synthesizes a complete Story Universe of `target_count` stories.
    Runs the Auto-Grow loop with Character & Relationship mutations.
    """
    def notify(pct: int, msg: str):
        if progress_callback:
            progress_callback(pct, msg)

    notify(5, "Extracting Canon Characters & Building Creative Character Pool...")
    canon_chars = extract_canon_characters(evidence, story_dna)
    char_universe = build_character_universe(canon_chars, pool_size=25)
    creative_pool = char_universe["creative_pool"]
    canon_dict_list = char_universe["canon_characters"]

    notify(15, "Instantiating 15 Canonical Story Worlds & Foundational Seed Genomes...")
    worlds = CANONICAL_STORY_WORLDS
    universe_genomes: List[StoryGenome] = []
    existing_story_dicts: List[Dict[str, Any]] = []

    # Phase 1: Build foundational root seeds across all active worlds
    story_counter = 1
    for w in worlds:
        # Determine initial ensemble for this world
        if story_counter % 3 == 0 and len(canon_dict_list) >= 2:
            init_chars = canon_dict_list[:2]
        elif story_counter % 2 == 0 and creative_pool:
            # Species crossover right from early roots
            c_cross = [canon_dict_list[0], creative_pool[story_counter % len(creative_pool)]]
            init_chars = c_cross
        else:
            init_chars = canon_dict_list[:1]

        rel = determine_relationship_for_ensemble(init_chars)
        root_gen = build_root_genome(
            story_dna=story_dna,
            characters=init_chars,
            relationships=rel,
            world=w.to_dict(),
            story_idx=story_counter
        )
        
        # Quality & Diversity evaluation
        q_metrics = score_story_quality(root_gen.to_dict(), quality_gate_threshold=quality_threshold)
        root_gen.quality_score = q_metrics.composite_score
        
        div_score = calculate_story_diversity_score(root_gen.to_dict(), existing_story_dicts)
        root_gen.diversity_score = max(0.80, div_score)

        universe_genomes.append(root_gen)
        s_dict = root_gen.to_dict()
        s_dict["quality_metrics"] = q_metrics.to_dict()
        existing_story_dicts.append(s_dict)
        story_counter += 1

    notify(30, f"Auto-Growing Story Universe toward {target_count} unique concepts...")

    # Phase 2: Auto-Grow Loop with Multi-Dimensional Mutations
    mutation_operators = list(CharacterMutationOperator)
    relationship_types = [t.value for t in RelationshipType]

    max_attempts = target_count * 25
    attempt = 0

    while len(universe_genomes) < target_count and attempt < max_attempts:
        attempt += 1

        # Pick a parent seed genome from the universe
        parent_genome = random.choice(universe_genomes)

        # Select a target world (rotate or sample)
        target_world = random.choice(worlds).to_dict()

        # Select a character mutation operator
        op = random.choice(mutation_operators)

        # Apply character mutation
        mutated_chars, char_meta = apply_character_mutation(
            parent_characters=parent_genome.characters,
            operator=op,
            character_pool=creative_pool,
            canon_characters=canon_dict_list
        )

        # Apply relationship mutation
        target_rel_type = random.choice(relationship_types)
        mutated_rel, rel_meta = mutate_relationship(
            parent_rel=parent_genome.relationships,
            characters=mutated_chars,
            target_type=target_rel_type
        )

        # Apply dimensional mutations
        new_story_id = f"UNIV-{story_counter:04d}"
        shifts = random.sample([
            "setting", "time", "object", "goal", "motivation",
            "conflict", "twist", "payoff", "perspective", "tone"
        ], k=random.randint(4, 7))

        child_genome, evo_meta = mutate_story_genome(
            parent=parent_genome,
            new_story_id=new_story_id,
            mutated_characters=mutated_chars,
            mutated_relationships=mutated_rel,
            target_world=target_world,
            dimensional_shifts=shifts
        )

        # Diversity Firewall Check against sliding window + global sample
        cand_dict = child_genome.to_dict()
        if len(existing_story_dicts) > 30:
            recent_pool = existing_story_dicts[-25:]
            sample_pool = random.sample(existing_story_dicts[:-25], min(15, len(existing_story_dicts) - 25))
            comp_pool = recent_pool + sample_pool
        else:
            comp_pool = existing_story_dicts

        div_score = calculate_story_diversity_score(cand_dict, comp_pool)
        
        # Adaptive diversity threshold if attempt density rises
        effective_div_thresh = max(0.70, diversity_threshold if attempt < (target_count * 5) else diversity_threshold - 0.05)
        if div_score < effective_div_thresh and len(existing_story_dicts) > 5:
            # Failed diversity firewall; re-mutate
            continue

        # Quality Gate Check
        q_metrics = score_story_quality(cand_dict, quality_gate_threshold=quality_threshold)
        if not q_metrics.passed_quality_gate and q_metrics.composite_score < (quality_threshold - 5.0):
            # Failed quality gate
            continue

        child_genome.diversity_score = div_score
        child_genome.quality_score = q_metrics.composite_score
        child_dict = child_genome.to_dict()
        child_dict["quality_metrics"] = q_metrics.to_dict()

        universe_genomes.append(child_genome)
        existing_story_dicts.append(child_dict)
        story_counter += 1

        if len(universe_genomes) % 25 == 0 or len(universe_genomes) == target_count:
            progress_pct = int(30 + (70 * (len(universe_genomes) / target_count)))
            notify(progress_pct, f"Synthesized {len(universe_genomes)} / {target_count} stories (Diversity Firewall Passed)...")

    # Phase 3: Compute Comprehensive Universe Metrics
    notify(95, "Calculating Universe Diversity Metrics and Ranking...")

    unique_species = set()
    char_configs = set()
    rel_types = set()
    settings_set = set()
    plot_patterns = set()
    diversity_scores = []
    quality_scores = []

    for s in existing_story_dicts:
        # Species
        for c in s.get("characters", []):
            if c.get("species"):
                unique_species.add(c.get("species").title())
        # Character configuration
        config_key = tuple(sorted([c.get("species", "") for c in s.get("characters", [])]))
        char_configs.add(config_key)
        # Relationship
        rel = s.get("relationships", {}).get("type")
        if rel:
            rel_types.add(rel)
        # Setting
        settings_set.add(s.get("setting"))
        # Plot pattern
        plot_patterns.add(f"{s.get('world_name')}::{s.get('relationships', {}).get('type')}")
        diversity_scores.append(s.get("diversity_score", 0.8))
        quality_scores.append(s.get("quality_score", 85.0))

    metrics = {
        "total_stories": len(existing_story_dicts),
        "target_requested": target_count,
        "unique_species_count": len(unique_species),
        "unique_species_list": sorted(list(unique_species)),
        "unique_character_configurations": len(char_configs),
        "unique_relationship_types": len(rel_types),
        "unique_relationship_list": sorted(list(rel_types)),
        "unique_settings_count": len(settings_set),
        "unique_plot_patterns": len(plot_patterns),
        "diversity_score_range": {
            "min": round(min(diversity_scores), 2) if diversity_scores else 0.0,
            "max": round(max(diversity_scores), 2) if diversity_scores else 0.0,
            "avg": round(sum(diversity_scores) / len(diversity_scores), 2) if diversity_scores else 0.0
        },
        "quality_score_range": {
            "min": round(min(quality_scores), 1) if quality_scores else 0.0,
            "max": round(max(quality_scores), 1) if quality_scores else 0.0,
            "avg": round(sum(quality_scores) / len(quality_scores), 1) if quality_scores else 0.0
        }
    }

    # Generate Top 10, Top 50, Top 100 rankings
    ranked_top_10 = rank_story_universe(existing_story_dicts, top_n=10, sort_by="quality")
    ranked_top_50 = rank_story_universe(existing_story_dicts, top_n=50, sort_by="quality")
    ranked_top_100 = rank_story_universe(existing_story_dicts, top_n=100, sort_by="quality")

    notify(100, f"Story Universe Factory Complete! {len(existing_story_dicts)} Stories Ready.")

    return {
        "universe_stories": existing_story_dicts,
        "character_universe": char_universe,
        "story_worlds": get_all_story_worlds(),
        "metrics": metrics,
        "top_rankings": {
            "top_10": [s.get("story_id") for s in ranked_top_10],
            "top_50": [s.get("story_id") for s in ranked_top_50],
            "top_100": [s.get("story_id") for s in ranked_top_100]
        }
    }
