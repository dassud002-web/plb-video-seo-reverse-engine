#!/usr/bin/env python3
"""
Recursive Story Expansion Engine for PLB Story Forge
=====================================================
Recursively expands any parent story node into exactly 50 child stories.
Tracks generational incrementing (generation = parent.generation + 1),
evolution metadata, changed dimensions, and anti-duplication diversity.
"""

from typing import Dict, Any, List, Optional
from story_forge.engine.providers.local import LocalStoryProvider
from story_forge.engine.providers.base import BaseStoryProvider
from story_forge.engine.story_generator import sanitize_story_text
from story_forge.engine.lineage_engine import evaluate_story_evolution

def expand_story_node_50(
    parent_story: Dict[str, Any],
    mode: str = "AUTO",
    threshold: float = 0.70,
    provider: Optional[BaseStoryProvider] = None
) -> List[Dict[str, Any]]:
    """
    Expands a single parent story into exactly 50 children.
    Each child is named f"{parent_id}-{idx:02d}", with generation = parent_gen + 1.
    """
    if provider is None:
        provider = LocalStoryProvider()

    parent_id = parent_story.get("story_id", "STORY-01")
    parent_gen = parent_story.get("generation", 1)
    child_gen = parent_gen + 1

    raw_children = provider.expand_story(
        parent_story=parent_story,
        count=50,
        mode=mode,
        threshold=threshold
    )

    final_children: List[Dict[str, Any]] = []
    for idx, child in enumerate(raw_children[:50], 1):
        c = dict(child)
        c["story_id"] = f"{parent_id}-{idx:02d}"
        c["parent_id"] = parent_id
        c["generation"] = child_gen
        c["title"] = sanitize_story_text(c.get("title", f"Expansion {idx:02d}"))
        c["one_line_premise"] = sanitize_story_text(c.get("one_line_premise", ""))
        c["hook"] = sanitize_story_text(c.get("hook", ""))
        c["conflict"] = sanitize_story_text(c.get("conflict", ""))
        c["twist"] = sanitize_story_text(c.get("twist", ""))
        c["payoff"] = sanitize_story_text(c.get("payoff", ""))
        c["derived_from"] = parent_id

        # Calculate / refresh evolution metadata
        c["evolution_metadata"] = evaluate_story_evolution(parent_story, c)
        if "diversity_score" not in c:
            c["diversity_score"] = threshold

        final_children.append(c)

    return final_children
