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
    char_fact = domains.get("characters", {}).get("fact", "Dynamic foreground focal subject tracked across timeline milestone frames")
    char_infer = domains.get("characters", {}).get("inference", "Observed Protagonist")
    char_count = domains.get("characters", {}).get("count", 1)

    c_name = char_infer.split(" / ")[0] if " / " in char_infer else char_infer
    if c_name.lower().startswith("benchmark profile: "):
        c_name = c_name[19:].strip()
    elif c_name.lower().startswith("identified as "):
        c_name = c_name[14:].strip()

    is_generic = (profile == "generic" or "unclassified" in char_infer.lower() or "foreground focal subject" in char_infer.lower())
    
    from scripts.video_seo_reverse_engineer import sanitize_filename_tokens
    clean_vid = sanitize_filename_tokens(video_name)
    metadata_cue = clean_vid.title() if clean_vid and clean_vid.lower() not in ["video", "vid", "clip", "ref", "test", "target"] else ""

    vision_ev = evidence.get("vision_evidence")
    has_verified_vision = bool(vision_ev and vision_ev.get("consensus_entity", {}).get("is_verified"))
    c_species = "Unclassified Subject"

    if has_verified_vision:
        cent = vision_ev["consensus_entity"]
        c_name = cent.get("display") or cent.get("label", "Observed Subject")
        c_species = cent.get("species", "Unclassified Subject")
        classification_status = f"Local Vision Inference ({cent.get('confidence_tier', 'MODERATE')} Confidence: {cent.get('confidence_pct', 0.0)}%)"
        cv_limitation_disclosed = False
    elif is_generic or not c_name or c_name.lower() in ["protagonist", "entity", "subject", "lead subject", "foreground focal subject"]:
        c_name = "Observed Protagonist"
        c_species = "Unclassified Subject"
        classification_status = "Visual Detection (Local Offline CV - Entity Unverified)"
        cv_limitation_disclosed = True
    else:
        classification_status = "Verified Benchmark / Sidecar Profile"
        cv_limitation_disclosed = False

    characters = [
        {
            "name": c_name,
            "species": c_species,
            "role": "Protagonist",
            "observed_fact": char_fact,
            "count": char_count,
            "level": EvidenceLevel.SOURCE_EVIDENCE.value,
            "classification_status": classification_status,
            "metadata_cue": metadata_cue
        }
    ]

    setting_fact = domains.get("setting", {}).get("fact", "Real-world environment")
    setting_infer = domains.get("setting", {}).get("inference", "Natural setting")

    objects_fact = domains.get("objects", {}).get("fact", "Foreground interaction element and surface contact zone")
    objects_infer = domains.get("objects", {}).get("inference", "Foreground Interactive Object")
    o_name = objects_infer.split(" / ")[0] if " / " in objects_infer else objects_infer
    if o_name.lower().startswith("benchmark profile: "):
        o_name = o_name[19:].strip()
    elif o_name.lower().startswith("identified as "):
        o_name = o_name[14:].strip()
    if is_generic or not o_name or any(f in o_name.lower() for f in ["target object", "focal element", "core visual narrative focal elements", "unclassified", "interactive element"]):
        o_name = "Foreground Interactive Object"

    objects = [
        {
            "name": o_name,
            "observed_fact": objects_fact,
            "level": EvidenceLevel.SOURCE_EVIDENCE.value,
            "classification_status": "Visual Detection (Local Offline CV - Object Taxonomy Unclassified)" if is_generic else "Verified Benchmark / Sidecar Object"
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
    clean_setting = setting_fact.replace("Observed: ", "").split(" (")[0]
    if has_verified_vision:
        core_premise = f"In {clean_setting}, the {c_name} investigates {objects[0]['name']}, displaying authentic natural behavior and kinetic reactions."
        central_tension = f"{c_name} vs. environmental stimuli and {objects[0]['name']} in {setting_infer}."
        primary_character_dynamic = "Unfiltered natural movement and environmental interaction"
        primary_comedic_emotional_engine = "Expectation of quiet scene animated by sudden candid animal movement and curiosity"
    elif is_generic:
        core_premise = f"In {clean_setting}, the {characters[0]['name'].lower()} navigates an authentic visual progression, escalating in kinetic intensity at mid-timeline (35%-65%) before reaching sequence stabilization."
        central_tension = f"{characters[0]['name']} vs. kinetic motion dynamics and environmental stimuli in {setting_infer}."
        primary_character_dynamic = "Unfiltered natural movement and environmental interaction"
        primary_comedic_emotional_engine = "Authentic timeline progression from initial framing to peak kinetic change and loop resolution"
    else:
        core_premise = f"An eager {characters[0]['name']} encounters {objects[0]['name']} in {setting_infer}, triggering an unexpected sequence of reactions."
        central_tension = f"{characters[0]['name']} vs. the sensory or physical challenge of {objects[0]['name']}."
        primary_character_dynamic = "Unfiltered curiosity meeting unfamiliar stimulus"
        primary_comedic_emotional_engine = "Expectation of a simple event inverted by a rapid, candid physical reaction"
    
    reusable_story_elements = [
        {"element": c_name if has_verified_vision else "Observed Protagonist", "source": char_fact, "reusability": "High"},
        {"element": "Interactive Focus", "source": objects_fact, "reusability": "High"},
        {"element": "Unfiltered Kinetic Reaction", "source": ending_fact, "reusability": "Very High"},
        {"element": "Atmospheric Setting", "source": setting_fact, "reusability": "Medium"}
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
        "classification_status": classification_status,
        "cv_limitation_disclosed": cv_limitation_disclosed,
        "metadata_cue": metadata_cue,
        "vision_evidence": vision_ev,
        "directly_observed_facts": vision_ev.get("layers", {}).get("directly_observed_facts", []) if vision_ev else [],
        "model_inferences": vision_ev.get("layers", {}).get("model_inferences", []) if vision_ev else [],
        "uncertain_information": vision_ev.get("layers", {}).get("uncertain_information", []) if vision_ev else [],
        # Derived Fields:
        "core_premise": core_premise,
        "central_tension": central_tension,
        "primary_character_dynamic": primary_character_dynamic,
        "primary_comedic_emotional_engine": primary_comedic_emotional_engine,
        "reusable_story_elements": reusable_story_elements,
        "visual_profile": profile
    }

    return story_dna
