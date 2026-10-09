#!/usr/bin/env python3
"""
Story DNA Construction Engine for PLB Story Forge
==================================================
Transforms raw video forensic evidence into a structured, recombinant Story DNA object.
"""

from typing import Dict, Any, List
from pathlib import Path
from story_forge.engine.evidence import EvidenceLevel

def build_story_dna(evidence: Dict[str, Any]) -> Dict[str, Any]:
    """
    Constructs the canonical Story DNA object from extracted video evidence.
    """
    domains = evidence.get("domains", {})
    video_name = evidence.get("source_video_name", "Unknown Video")
    video_hash = evidence.get("source_video_hash", "00000000")
    profile = evidence.get("visual_profile_name", "generic")

    # Extract character items
    char_fact = domains.get("characters", {}).get("fact", "Foreground subject")
    char_infer = domains.get("characters", {}).get("inference", "Protagonist")
    char_count = domains.get("characters", {}).get("count", 1)

    c_name = char_infer.split(" / ")[0] if " / " in char_infer else char_infer
    if c_name.lower().startswith("identified as "):
        c_name = c_name[14:].strip()
    if not c_name or c_name.lower() in ["protagonist", "entity", "subject", "lead subject"]:
        from scripts.video_seo_reverse_engineer import sanitize_filename_tokens
        clean_vid = sanitize_filename_tokens(video_name)
        if clean_vid and clean_vid.lower() not in ["video", "vid", "clip", "ref", "test", "target"]:
            c_name = clean_vid.title()
        else:
            c_name = "Lead Protagonist"

    characters = [
        {
            "name": c_name,
            "role": "Protagonist",
            "observed_fact": char_fact,
            "count": char_count,
            "level": EvidenceLevel.SOURCE_EVIDENCE.value
        }
    ]

    setting_fact = domains.get("setting", {}).get("fact", "Real-world environment")
    setting_infer = domains.get("setting", {}).get("inference", "Natural setting")

    objects_fact = domains.get("objects", {}).get("fact", "Focal element")
    objects_infer = domains.get("objects", {}).get("inference", "Target object")
    o_name = objects_infer.split(" / ")[0] if " / " in objects_infer else objects_infer
    if o_name.lower().startswith("identified as "):
        o_name = o_name[14:].strip()
    if not o_name or o_name.lower() in ["target object", "focal element", "core visual narrative focal elements"]:
        o_name = f"Focal Element in {setting_infer}"

    objects = [
        {
            "name": o_name,
            "observed_fact": objects_fact,
            "level": EvidenceLevel.SOURCE_EVIDENCE.value
        }
    ]

    actions_fact = domains.get("visible_actions", {}).get("fact", "Dynamic motion progression")
    beginning_fact = domains.get("beginning_state", {}).get("fact", "Scene begins")
    middle_fact = domains.get("middle_events", {}).get("fact", "Peak transition")
    ending_fact = domains.get("ending_state", {}).get("fact", "Scene resolves")

    # Core Action & Goal
    core_action = actions_fact
    goal = f"Investigate, reach, or interact with {objects[0]['name']}"
    conflict = domains.get("conflict", {}).get("fact", "Kinetic obstacle or resistance during interaction")
    
    cause_effect = [
        f"{ce.get('cause')} → {ce.get('effect')}"
        for ce in domains.get("cause_effect", [])
    ]

    emotional_arc = [
        {"stage": "Opening Hook (5%)", "emotion": "Curiosity & Anticipation", "fact": beginning_fact},
        {"stage": "Middle Escalation (50%)", "emotion": "Surprise & Tension", "fact": middle_fact},
        {"stage": "Payoff Resolution (95%)", "emotion": "Comedic Relief / Satisfaction", "fact": ending_fact}
    ]

    hook = f"Within the first 3 seconds, {beginning_fact}"
    escalation = [
        f"Initial approach: {beginning_fact}",
        f"Kinetic acceleration / contact: {middle_fact}",
        f"Final reaction / recoil: {ending_fact}"
    ]
    twist = f"Unexpected physical or behavioral reaction at peak transition ({middle_fact})"
    payoff = f"Final comedic, triumphant, or loop-ready ending state ({ending_fact})"

    visual_motifs = domains.get("repeating_motifs", [])
    evidence_refs = [
        item.get("evidence_id") for item in evidence.get("evidence_items", [])[:10]
    ]

    # Derived High-Level Story Elements
    core_premise = f"An eager {characters[0]['name']} encounters {objects[0]['name']} in {setting_infer}, triggering an unexpected sequence of reactions."
    central_tension = f"{characters[0]['name']} vs. the sensory or physical challenge of {objects[0]['name']}."
    primary_character_dynamic = "Unfiltered curiosity meeting unfamiliar stimulus"
    primary_comedic_emotional_engine = "Expectation of a simple event inverted by a rapid, candid physical reaction"
    
    reusable_story_elements = [
        {"element": "Innocent Protagonist", "source": char_infer, "reusability": "High"},
        {"element": "Mystery Object", "source": objects_infer, "reusability": "High"},
        {"element": "Unfiltered Reaction", "source": ending_fact, "reusability": "Very High"},
        {"element": "Dynamic Setting", "source": setting_infer, "reusability": "Medium"}
    ]

    story_dna = {
        "story_id": "ROOT",
        "source_video": video_name,
        "source_video_hash": video_hash,
        "characters": characters,
        "setting": setting_infer,
        "setting_observed": setting_fact,
        "objects": objects,
        "core_action": core_action,
        "goal": goal,
        "conflict": conflict,
        "cause_effect": cause_effect,
        "emotional_arc": emotional_arc,
        "hook": hook,
        "escalation": escalation,
        "twist": twist,
        "payoff": payoff,
        "visual_motifs": visual_motifs,
        "evidence_refs": evidence_refs,
        "confidence": 1.0,
        # Derived Fields:
        "core_premise": core_premise,
        "central_tension": central_tension,
        "primary_character_dynamic": primary_character_dynamic,
        "primary_comedic_emotional_engine": primary_comedic_emotional_engine,
        "reusable_story_elements": reusable_story_elements,
        "visual_profile": profile
    }

    return story_dna
