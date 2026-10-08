#!/usr/bin/env python3
"""
Production Pipeline for PLB Story Universe Factory
===================================================
Converts any selected story into a 9-part production package:
1. 15-second Script (Action, dialogue, Foley timestamps)
2. 6-Shot Storyboard (Hook, Setup, Escalation, Twist, Payoff, Loop)
3. Hero Frame Specification
4. Continuity Lock (Character morphology & environment rules)
5. Seedance Prompt (Dreamina / Seedance prompt optimization)
6. Veo Prompt (Google Veo text-to-video prompt optimization)
7. Audio Plan (Foley, SFX, tempo, mood)
8. Platform Captions (TikTok, IG Reels, Shorts, FB Reels)
9. SEO Pack (Primary keyword, long-tail queries, hashtags, pinned comment)
"""

from dataclasses import dataclass, asdict
from typing import Dict, Any, List

def produce_story_package(story: Dict[str, Any], story_dna: Dict[str, Any]) -> Dict[str, Any]:
    """
    Synthesizes a production package from a single Story Genome.
    """
    story_id = story.get("story_id", "STORY-01")
    title = story.get("title", "Story Concept")
    premise = story.get("one_line_premise", "")
    hook = story.get("hook", "")
    conflict = story.get("conflict", "")
    twist = story.get("twist", "")
    payoff = story.get("payoff", "")
    chars = story.get("characters", [{"name": "Protagonist", "species": "Animal"}])
    setting = story.get("setting", "Garden Run")
    objects = story.get("objects", [{"name": "Mystery Object"}])
    obj_name = objects[0].get("name", "Mystery Object")

    char_names = [c.get("name", "Animal") for c in chars]
    primary_char = char_names[0]
    secondary_char = char_names[1] if len(char_names) > 1 else ""

    # 1. 15-Second Script
    script_15s = {
        "duration_seconds": 15,
        "beats": [
            {
                "timestamp": "00:00 - 00:03",
                "beat_name": "The Visual Hook",
                "action": f"Extreme close-up on {primary_char} locking eyes with {obj_name} in {setting}. First 3 seconds kinetic tension established.",
                "foley": "Subtle ambient breeze, soft paw/feet pitter-patter, dramatic comedic clock tick.",
                "audio_cue": "Music drops to a sudden inquisitive beat."
            },
            {
                "timestamp": "00:03 - 00:07",
                "beat_name": "The Cautious Approach",
                "action": f"{primary_char} inches forward with twitching whiskers/feathers. {f'{secondary_char} watches skeptically from the background.' if secondary_char else 'Camera pans with the stealth approach.'}",
                "foley": "Rhythmic stealth footsteps, curious inquisitive snort/chirp.",
                "audio_cue": "Pizzicato strings building playful suspense."
            },
            {
                "timestamp": "00:07 - 00:11",
                "beat_name": "The Climax / Decisive Contact",
                "action": f"Decisive contact! {primary_char} pecks or bites into {obj_name}. Immediate visual realization registers.",
                "foley": "Distinct crisp crunch/squish sound effect followed by cartoon whoosh.",
                "audio_cue": "Record scratch or sudden bass drop."
            },
            {
                "timestamp": "00:11 - 00:15",
                "beat_name": "The Comedic Payoff & Loop Point",
                "action": f"{payoff}. {primary_char} delivers unforgettable direct-to-camera face, resetting into opening posture.",
                "foley": "Frantic rapid shake sound effect, relieved gentle chirp/whimper.",
                "audio_cue": "Comedic musical sting resolving seamlessly into the opening bar."
            }
        ]
    }

    # 2. 6-Shot Storyboard
    storyboard_6shot = [
        {
            "shot_number": 1,
            "beat": "Hook (0-3s)",
            "framing": "Extreme Close-Up (ECU)",
            "camera_movement": "Rapid push-in on subject's eyes",
            "description": f"{primary_char} stares intently with heightened curiosity.",
            "visual_anchor": f"Reflection of {obj_name} in the pupil."
        },
        {
            "shot_number": 2,
            "beat": "Setup (3-5s)",
            "framing": "Medium Wide Shot (MWS)",
            "camera_movement": "Low-angle static ground tracking",
            "description": f"Establishes {setting}. Spatial relationship between {primary_char} and {obj_name} is crystal clear.",
            "visual_anchor": "Crisp depth of field with blurred backdrop."
        },
        {
            "shot_number": 3,
            "beat": "Escalation (5-8s)",
            "framing": "Profile Two-Shot (if duo) or Dutch Angle Tracking",
            "camera_movement": "Slow creeping creep-in",
            "description": f"{conflict}. Extreme hesitation before the final lunge.",
            "visual_anchor": "Tense paw/foot poised mid-air."
        },
        {
            "shot_number": 4,
            "beat": "Twist / Contact (8-11s)",
            "framing": "Over-the-Shoulder Tight (OTS)",
            "camera_movement": "Instant micro-whip pan to point of impact",
            "description": f"Contact occurs: {twist}.",
            "visual_anchor": "Droplets of water/juice scattering in slow motion."
        },
        {
            "shot_number": 5,
            "beat": "Payoff (11-14s)",
            "framing": "Direct Frontal Close-Up",
            "camera_movement": "Static locked tripod frame",
            "description": f"{payoff}.",
            "visual_anchor": "Wide-eyed candid facial reaction staring directly into camera."
        },
        {
            "shot_number": 6,
            "beat": "Loop Transition (14-15s)",
            "framing": "Medium Return Shot",
            "camera_movement": "Gentle zoom out",
            "description": "Subject shakes off the shock, circles around, and faces the object again.",
            "visual_anchor": "Matches Shot 1 opening posture for seamless video replay."
        }
    ]

    # 3. Hero Frame Specification
    genome = story.get("genome") or {}

    comp_val = (
        story.get("composition")
        or genome.get("composition")
        or f"Rule-of-thirds low angle: {primary_char} on left third, {obj_name} on right third."
    )
    lighting_val = (
        story.get("lighting")
        or genome.get("lighting")
        or "Golden natural sunlight rim-lighting with soft warm fill."
    )
    palette_raw = (
        story.get("color_palette")
        or story.get("palette")
        or genome.get("palette")
        or ["Lush Natural Green", "Warm Terracotta/Wood Tan", "High-Luminance White", "Crisp Accent Hue"]
    )
    if isinstance(palette_raw, list):
        palette_list = palette_raw
        palette_str = ", ".join(palette_raw)
    else:
        palette_str = str(palette_raw)
        palette_list = [p.strip() for p in palette_str.split(",") if p.strip()]

    lens_val = (
        story.get("camera_lens")
        or story.get("lens")
        or genome.get("camera_lens")
        or "f/2.8 shallow depth with creamy background bokeh (50mm prime)"
    )

    hero_frame = {
        "composition": comp_val or "Not specified",
        "lighting": lighting_val or "Not specified",
        "focal_lighting": lighting_val or "Not specified",
        "color_palette": palette_str or "Not specified",
        "color_palette_lock": palette_list if palette_list else ["Not specified"],
        "camera_lens": lens_val or "Not specified",
        "depth_of_field": lens_val or "Not specified",
        "focal_expression": f"Wide-eyed astonishment and comically frozen posture."
    }

    # 4. Continuity Lock
    morph_rules = [
        f"Preserve consistent fur/feather coat texture for {primary_char}.",
        "Zero artificial anatomical distortion; realistic organic proportions.",
        "Maintain ear and tail posture rules throughout all frames."
    ]
    env_rules = [
        f"Strict adherence to {setting} architecture.",
        "Consistent sun position casting shadows to the camera left.",
        "Weather conditions remain stable across all sequential shots."
    ]
    traits_list = [
        f"Object scale: {obj_name} proportional to {primary_char}",
        "Zero anatomical distortion",
        "Physical gravity & momentum invariants"
    ]
    invariants = [
        f"Object scale: {obj_name} must remain physically proportional to {primary_char}.",
        "Physical contact physics: obey real-world gravity and momentum."
    ]

    continuity_lock = {
        "character_morphology": " ".join(morph_rules),
        "character_morphology_rules": morph_rules,
        "environment_lock": " ".join(env_rules),
        "environment_rules": env_rules,
        "immutable_traits": traits_list,
        "interaction_invariants": invariants
    }

    # 5. Seedance Prompt (Dreamina / Seedance 2.5 optimized)
    seedance_prompt = (
        f"Cinematic photorealistic 8k video, {setting}, high-speed camera capture. "
        f"A gorgeous {primary_char} curiously approaches a {obj_name}. "
        f"Golden hour lighting, detailed fur and feather textures, dynamic physical comedy, "
        f"{twist}, finishing with an adorable comedic head shake looking directly into the camera lens. "
        f"Masterpiece, natural movements, 24fps, hyper-detailed, award-winning cinematography."
    )

    # 6. Google Veo Prompt (Google Veo 2 optimized)
    veo_prompt = (
        f"A cinematic 15-second tracking shot at ground level in {setting}. "
        f"{primary_char} cautiously approaches {obj_name}. "
        f"Direct sunlight creates rim lighting along the edges. "
        f"The subject takes a cautious investigative bite, followed by a startled, comedic recoil "
        f"and double-shake of head and fur. Photorealistic nature documentary style, sharp focus, f/2.8, slow-motion splash."
    )

    # 7. Audio Plan
    audio_plan = {
        "tempo_bpm": "118 BPM (Playful, bouncy swing rhythm)",
        "instrumentation": "Pizzicato strings, acoustic bass, comedic bassoon, bright xylophone accents",
        "foley_cues": [
            "00:02 - Soft grass rustle / wood rail tap",
            "00:08 - Wet squish or sharp crunchy bite sound effect",
            "00:11 - Cartoon slip whistle or rapid flutter vibration",
            "00:14 - Satisfying deep sigh / contented purr"
        ],
        "voiceover_pantomime": "Pantomime physical comedy: zero distracting speech, universal visual humor."
    }

    # 8. Platform Captions
    species_tag = chars[0].get("species", "animals").lower()
    platform_captions = {
        "tiktok": (
            f"POV: your {species_tag} discovers a {obj_name.lower()} for the very first time 😂 "
            f"Wait for the face at the end 💀 #animals #{species_tag} #funnyanimals #pets #fyp #viral #animalsoftiktok"
        ),
        "instagram_reels": (
            f"He was NOT expecting that! 😂 {primary_char} vs {obj_name}.\n\n"
            f"Drop a 🍋 if you've ever made this exact face!\n\n"
            f"#{species_tag} #petreels #funnyanimals #cuteanimals #explorepage #farmlife #reelsinstagram"
        ),
        "youtube_shorts": (
            f"{primary_char} vs {obj_name}! Hilarious confused reaction 😂 #shorts\n\n"
            f"Subscribe for more wholesome daily animal adventures!\n\n"
            f"#shorts #{species_tag} #funny #viral"
        ),
        "facebook_reels": (
            f"Our little {primary_char} thought they found the ultimate treat! "
            f"Watch what happens when they take that first curious taste 😂 Have your pets ever done this? 👇"
        )
    }

    # 9. SEO Pack
    seo_pack = {
        "primary_topic": f"{primary_char} vs {obj_name} / Funny Animal Reaction",
        "primary_keyword": f"{primary_char.lower()} reacts to {obj_name.lower()}",
        "secondary_keywords": [
            f"funny {species_tag} reaction",
            f"{primary_char.lower()} taste test",
            f"cute {species_tag} funny face",
            f"viral animal reaction 2026",
            f"wholesome {species_tag} comedy"
        ],
        "video_tags": [f"funny {species_tag}", "animals", "pets", "taste test", "reaction", "viral shorts"],
        "hashtags": [f"#{species_tag}", "#animals", "#pets", "#funnyanimals", "#cuteanimals", "#viralshorts"],
        "pinned_comment": f"The face right at the end took me out completely 😂 What should we let {primary_char} try next?"
    }

    return {
        "story_id": story_id,
        "title": title,
        "script_15s": script_15s,
        "production_script_15s": script_15s,
        "storyboard_6shot": storyboard_6shot,
        "storyboard_6_shots": storyboard_6shot,
        "hero_frame": hero_frame,
        "continuity_lock": continuity_lock,
        "seedance_prompt": seedance_prompt,
        "veo_prompt": veo_prompt,
        "audio_plan": audio_plan,
        "platform_captions": platform_captions,
        "seo_pack": seo_pack
    }


def validate_production_package(pkg: Dict[str, Any]) -> List[str]:
    """Validates that a production package has all critical fields populated without blanks."""
    warnings = []
    hero = pkg.get("hero_frame") or {}
    for f in ["composition", "lighting", "color_palette", "camera_lens"]:
        val = hero.get(f)
        if not val or not str(val).strip() or str(val).strip() == "Not specified":
            warnings.append(f"Hero Frame field '{f}' is empty or not specified")

    cont = pkg.get("continuity_lock") or {}
    for f in ["character_morphology", "environment_lock", "immutable_traits"]:
        val = cont.get(f)
        if not val or (isinstance(val, str) and not val.strip()) or val == "Not specified" or (isinstance(val, list) and not val):
            warnings.append(f"Continuity field '{f}' is empty or not specified")

    if not pkg.get("seedance_prompt") or not str(pkg.get("seedance_prompt")).strip():
        warnings.append("Seedance prompt is missing")
    if not pkg.get("veo_prompt") or not str(pkg.get("veo_prompt")).strip():
        warnings.append("Google Veo prompt is missing")

    return warnings
