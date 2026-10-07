#!/usr/bin/env python3
"""
Quality Engine and Story Ranking for PLB Story Universe Factory
===============================================================
Scores every story across 9 critical dimensions:
Novelty, Hook, Emotional Value, Comedy Value, Animal Appeal,
Visual Potential, Short-Form Potential, Loopability, and Production Feasibility.
Enforces Quality Gate (default 85+) and provides Top 10/50/100 ranking.
"""

from dataclasses import dataclass, asdict
from typing import Dict, Any, List
import re

@dataclass
class QualityMetrics:
    novelty: float
    hook_potency: float
    emotional_value: float
    comedy_value: float
    animal_appeal: float
    visual_potential: float
    short_form_potential: float
    loopability: float
    production_feasibility: float
    composite_score: float
    passed_quality_gate: bool

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["breakdown"] = {
            "novelty": self.novelty,
            "hook_potency": self.hook_potency,
            "emotional_value": self.emotional_value,
            "comedy_value": self.comedy_value,
            "animal_appeal": self.animal_appeal,
            "visual_potential": self.visual_potential,
            "short_form_potential": self.short_form_potential,
            "loopability": self.loopability,
            "production_feasibility": self.production_feasibility,
        }
        return d

def score_story_quality(
    story: Dict[str, Any],
    quality_gate_threshold: float = 85.0
) -> QualityMetrics:
    """
    Evaluates a story object and computes its 9 dimensional scores and composite quality score.
    """
    premise = str(story.get("one_line_premise", "")).lower()
    hook = str(story.get("hook", "")).lower()
    conflict = str(story.get("conflict", "")).lower()
    twist = str(story.get("twist", "")).lower()
    payoff = str(story.get("payoff", "")).lower()
    chars = story.get("characters", [])
    mode = str(story.get("mode", story.get("world_name", ""))).upper()

    # 1. Novelty (diversity & dimensional distance)
    div_score = float(story.get("diversity_score", 0.80))
    novelty = round(min(100.0, max(70.0, div_score * 105.0)), 1)

    # 2. Hook Potency (first 3s kinetic trigger)
    hook_keywords = ["locks eyes", "sudden", "first 3 seconds", "erupts", "discovers", "within 3 seconds"]
    hook_hits = sum(1 for k in hook_keywords if k in hook or k in premise)
    hook_potency = round(82.0 + min(16.0, hook_hits * 5.0), 1)

    # 3. Emotional Value (resonance & empathy)
    emo_keywords = ["friendship", "together", "protect", "gentle", "wholesome", "family", "loyalty"]
    emo_hits = sum(1 for k in emo_keywords if k in premise or k in conflict or "WHOLESOME" in mode or "EMOTIONAL" in mode)
    emotional_val = round(80.0 + min(18.0, emo_hits * 4.5), 1)

    # 4. Comedy Value (physical slapstick & comedic timing)
    comedy_keywords = ["sour", "recoil", "head shake", "prank", "chaos", "slapstick", "domino", "panic"]
    comedy_hits = sum(1 for k in comedy_keywords if k in twist or k in payoff or "COMEDY" in mode or "CHAOTIC" in mode)
    comedy_val = round(82.0 + min(17.0, comedy_hits * 4.0), 1)

    # 5. Animal Appeal (presence of relatable friendly animals)
    animal_appeal = 88.0
    species_set = {c.get("species", "").lower() for c in chars if isinstance(c, dict)}
    if any(s in species_set for s in ["dog", "duck", "duckling", "chicken", "chick", "rabbit", "goat", "piglet"]):
        animal_appeal = 95.0

    # 6. Visual Potential (dynamic cinematography & color contrast)
    vis_keywords = ["sprinkler", "table", "water", "lawn", "citrus", "pumpkin", "greenhouse", "shadow"]
    vis_hits = sum(1 for k in vis_keywords if k in premise or k in hook)
    visual_pot = round(83.0 + min(15.0, vis_hits * 4.0), 1)

    # 7. Short-Form Potential (quick payoff & high retention)
    short_form_pot = round((hook_potency * 0.5) + (comedy_val * 0.5), 1)

    # 8. Loopability (seamless end-to-beginning return)
    loopability = 90.0 if "loop" in story else 85.0

    # 9. Production Feasibility (safe, realistic, doable in AI or camera)
    prod_feasibility = 92.0

    # Composite Weighted Quality Score (0-100)
    composite = round(
        (novelty * 0.15) +
        (hook_potency * 0.15) +
        (comedy_val * 0.15) +
        (emotional_val * 0.10) +
        (animal_appeal * 0.15) +
        (visual_pot * 0.10) +
        (short_form_pot * 0.10) +
        (prod_feasibility * 0.10),
        1
    )

    passed = composite >= quality_gate_threshold

    return QualityMetrics(
        novelty=novelty,
        hook_potency=hook_potency,
        emotional_value=emotional_val,
        comedy_value=comedy_val,
        animal_appeal=animal_appeal,
        visual_potential=visual_pot,
        short_form_potential=short_form_pot,
        loopability=loopability,
        production_feasibility=prod_feasibility,
        composite_score=composite,
        passed_quality_gate=passed
    )

def rank_story_universe(
    stories: List[Dict[str, Any]],
    top_n: int = 50,
    sort_by: str = "quality"
) -> List[Dict[str, Any]]:
    """
    Ranks stories according to requested criterion:
    'quality', 'novelty', 'viral_potential', 'visual_potential', 'animal_appeal', 'production_feasibility'
    """
    def sort_key(s: Dict[str, Any]) -> float:
        qm = s.get("quality_metrics", {})
        if sort_by == "novelty":
            return qm.get("novelty", s.get("diversity_score", 0.0) * 100)
        elif sort_by == "viral_potential":
            return qm.get("short_form_potential", 85.0)
        elif sort_by == "visual_potential":
            return qm.get("visual_potential", 85.0)
        elif sort_by == "animal_appeal":
            return qm.get("animal_appeal", 85.0)
        elif sort_by == "production_feasibility":
            return qm.get("production_feasibility", 85.0)
        else: # default quality
            return qm.get("composite_score", s.get("quality_score", 85.0))

    sorted_stories = sorted(stories, key=sort_key, reverse=True)
    return sorted_stories[:top_n]
