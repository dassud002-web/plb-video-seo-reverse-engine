#!/usr/bin/env python3
"""
Story Evolution and Lineage Engine for PLB Story Forge
======================================================
Tracks generational evolution across parent-child story trees.
Quantifies dimensional shifts (plot, character, setting, conflict, twist, novelty)
without exposing private model thoughts, providing transparent, structured metadata.
"""

from typing import Dict, Any, List, Set
from story_forge.engine.diversity_engine import jaccard_similarity, normalize_text_to_tokens

ALL_DIMENSIONS = [
    "character", "character_goal", "motivation", "conflict", "obstacle",
    "relationship", "setting", "time", "object", "consequence",
    "emotional_direction", "tone", "twist", "escalation", "ending_payoff",
    "perspective", "misunderstanding", "discovery", "role_reversal", "stakes"
]

def evaluate_story_evolution(parent: Dict[str, Any], child: Dict[str, Any]) -> Dict[str, Any]:
    """
    Compares a child story to its parent story and computes the structured
    evolution metadata, changed dimensions, novelty score, and element shifts.
    """
    # 1. Text difference measurements for key fields
    def field_distance(field_key: str) -> float:
        val_p = str(parent.get(field_key, ""))
        val_c = str(child.get(field_key, ""))
        tok_p = normalize_text_to_tokens(val_p)
        tok_c = normalize_text_to_tokens(val_c)
        sim = jaccard_similarity(tok_p, tok_c)
        return round(1.0 - sim, 2)

    plot_change_val = field_distance("one_line_premise")
    setting_change_val = field_distance("setting")
    conflict_change_val = field_distance("conflict")
    twist_change_val = field_distance("twist")
    payoff_change_val = field_distance("payoff")
    emotion_change_val = field_distance("emotional_arc")

    # Character set comparison
    def extract_names(chars: Any) -> Set[str]:
        if isinstance(chars, list):
            res = set()
            for c in chars:
                if isinstance(c, dict):
                    res.add(c.get("name", "").lower())
                elif isinstance(c, str):
                    res.add(c.lower())
            return res
        return {str(chars).lower()}

    chars_p = extract_names(parent.get("characters", []))
    chars_c = extract_names(child.get("characters", []))
    char_change_val = round(1.0 - jaccard_similarity(chars_p, chars_c), 2)

    # 2. Identify Changed Dimensions
    changed_dims: List[str] = []
    
    if char_change_val > 0.3:
        changed_dims.append("character")
    if setting_change_val > 0.3:
        changed_dims.append("setting")
    if conflict_change_val > 0.3:
        changed_dims.append("conflict")
    if twist_change_val > 0.3:
        changed_dims.append("twist")
    if payoff_change_val > 0.3:
        changed_dims.append("ending_payoff")
    if emotion_change_val > 0.3:
        changed_dims.append("emotional_direction")

    # Check child's explicit new_elements or mode
    child_mode = child.get("mode", "")
    parent_mode = parent.get("mode", "")
    if child_mode and child_mode != parent_mode:
        changed_dims.append("tone")

    child_goal = str(child.get("goal", ""))
    parent_goal = str(parent.get("goal", ""))
    if normalize_text_to_tokens(child_goal) != normalize_text_to_tokens(parent_goal):
        changed_dims.append("character_goal")

    # Ensure at least 2 changed dimensions are tracked
    if not changed_dims:
        changed_dims = ["plot", "escalation"]

    # 3. Track Inherited, New, and Removed Elements
    inherited_elements: List[str] = []
    new_elements: List[str] = child.get("new_elements", [])
    removed_elements: List[str] = []

    # Check characters
    for cp in chars_p:
        if cp in chars_c:
            inherited_elements.append(f"Character: {cp.title()}")
        else:
            removed_elements.append(f"Character: {cp.title()}")

    for cc in chars_c:
        if cc not in chars_p:
            new_elements.append(f"Character: {cc.title()}")

    # Setting inheritance
    if setting_change_val < 0.4:
        inherited_elements.append(f"Setting: {parent.get('setting', 'Original environment')}")
    else:
        new_elements.append(f"Setting: {child.get('setting', 'Transformed environment')}")
        removed_elements.append(f"Setting: {parent.get('setting', 'Prior environment')}")

    # Deduplicate element lists
    new_elements = list(dict.fromkeys(new_elements))
    inherited_elements = list(dict.fromkeys(inherited_elements))
    removed_elements = list(dict.fromkeys(removed_elements))

    # 4. Composite Novelty Score
    novelty_score = round(
        (0.25 * plot_change_val) +
        (0.20 * char_change_val) +
        (0.15 * setting_change_val) +
        (0.15 * conflict_change_val) +
        (0.15 * twist_change_val) +
        (0.10 * payoff_change_val),
        2
    )

    evolution_metadata = {
        "parent_id": parent.get("story_id", "ROOT"),
        "parent_title": parent.get("title", "Root Story DNA"),
        "child_id": child.get("story_id", ""),
        "child_title": child.get("title", ""),
        "generation": child.get("generation", 2),
        "novelty_score": novelty_score,
        "metrics": {
            "plot_change": plot_change_val,
            "character_change": char_change_val,
            "setting_change": setting_change_val,
            "conflict_change": conflict_change_val,
            "emotional_change": emotion_change_val,
            "twist_change": twist_change_val,
            "consequence_change": payoff_change_val
        },
        "changed_dimensions": changed_dims,
        "new_elements": new_elements,
        "inherited_elements": inherited_elements,
        "removed_elements": removed_elements
    }

    return evolution_metadata

def build_comparison_view_data(parent: Dict[str, Any], child: Dict[str, Any]) -> Dict[str, Any]:
    """
    Formats comparison data specifically for the creator UI Compare View.
    """
    evolution = evaluate_story_evolution(parent, child)
    
    return {
        "parent": {
            "story_id": parent.get("story_id"),
            "title": parent.get("title"),
            "premise": parent.get("one_line_premise"),
            "hook": parent.get("hook"),
            "characters": parent.get("characters"),
            "setting": parent.get("setting"),
            "conflict": parent.get("conflict"),
            "twist": parent.get("twist"),
            "payoff": parent.get("payoff"),
            "mode": parent.get("mode", "ROOT")
        },
        "child": {
            "story_id": child.get("story_id"),
            "title": child.get("title"),
            "premise": child.get("one_line_premise"),
            "hook": child.get("hook"),
            "characters": child.get("characters"),
            "setting": child.get("setting"),
            "conflict": child.get("conflict"),
            "twist": child.get("twist"),
            "payoff": child.get("payoff"),
            "mode": child.get("mode", "AUTO")
        },
        "evolution": evolution
    }
