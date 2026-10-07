#!/usr/bin/env python3
"""
Comprehensive Export Suite for PLB Story Universe Factory
==========================================================
Exports:
1. Universe JSON (Full universe data, metrics, character pool, relationships, all stories)
2. Story Bible Markdown (Grand formatted Bible with Story DNA, worlds, ranked stories, lineage)
3. Character Bible Markdown (Profiles, physical specs, temperaments, compatibility, story usage)
4. Relationship Graph Markdown (Pairwise dynamics, tension models, comedic triggers)
5. Top Stories CSV (Ranked stories spreadsheet)
6. Full ZIP Bundle (All documents and keyframe images)
"""

import json
import csv
import io
import zipfile
from pathlib import Path
from typing import Dict, Any, List

from story_forge.storage.db import (
    get_session,
    get_all_stories_for_session,
    get_lineage_graph
)
from story_forge.engine.quality_engine import rank_story_universe

def export_universe_json(session_id: str) -> str:
    """Exports entire Story Universe data as structured JSON."""
    session = get_session(session_id)
    if not session:
        raise ValueError(f"Session not found: {session_id}")

    stories = get_all_stories_for_session(session_id)
    lineage_tree = get_lineage_graph(session_id)

    export_payload = {
        "export_engine": "PLB Story Universe Factory V2.0",
        "session_id": session_id,
        "created_at": session.get("created_at"),
        "source_video": {
            "name": session.get("source_video_name"),
            "hash": session.get("source_video_hash"),
            "duration_seconds": session.get("duration_seconds"),
            "file_size_bytes": session.get("file_size_bytes")
        },
        "settings": session.get("settings", {}),
        "universe_metrics": session.get("universe_metrics", {}),
        "story_dna": session.get("story_dna", {}),
        "character_universe": session.get("character_universe", {}),
        "total_stories_count": len(stories),
        "stories": stories,
        "lineage_graph": lineage_tree
    }
    return json.dumps(export_payload, indent=2, ensure_ascii=False)

def export_story_bible_markdown(session_id: str) -> str:
    """Generates an exhaustive, production-grade Story Bible in GitHub-flavored Markdown."""
    session = get_session(session_id)
    if not session:
        raise ValueError(f"Session not found: {session_id}")

    stories = get_all_stories_for_session(session_id)
    dna = session.get("story_dna", {})
    char_univ = session.get("character_universe", {})
    metrics = session.get("universe_metrics", {})

    root_stories = [s for s in stories if s.get("generation", 1) == 1]
    child_stories = [s for s in stories if s.get("generation", 1) > 1]

    lines = [
        "# 🎬 PLB STORY FORGE — COMPLETE STORY BIBLE & MASTER STORY BIBLE (UNIVERSE FACTORY)",
        f"**Source Video**: `{session.get('source_video_name')}`  ",
        f"**Asset Hash**: `{session.get('source_video_hash')}`  ",
        f"**Universe Size**: `{len(stories)} Stories` across `{metrics.get('unique_species_count', 0)} Species`  ",
        f"**Quality Score (Avg)**: `{metrics.get('quality_score_range', {}).get('avg', 85.0)}/100` | **Diversity (Avg)**: `{metrics.get('diversity_score_range', {}).get('avg', 0.85)}`  ",
        f"**Generated**: `{session.get('created_at')}`  ",
        "",
        "---",
        "",
        "## 🧬 I. STORY DNA",
        f"* **Core Premise**: {dna.get('core_premise', 'N/A')}",
        f"* **Central Tension**: {dna.get('central_tension', 'N/A')}",
        f"* **Primary Dynamic**: {dna.get('primary_character_dynamic', 'N/A')}",
        f"* **Comedic / Emotional Engine**: {dna.get('primary_comedic_emotional_engine', 'N/A')}",
        f"* **Observed Setting**: {dna.get('setting_observed', dna.get('setting', 'N/A'))}",
        f"* **Core Action Arc**: {dna.get('core_action', 'N/A')}",
        f"* **Hook (0-3s)**: {dna.get('hook', 'N/A')}",
        f"* **Twist**: {dna.get('twist', 'N/A')}",
        f"* **Payoff**: {dna.get('payoff', 'N/A')}",
        "",
        "---",
        "",
        "## 🐾 II. CHARACTER UNIVERSE SUMMARY",
        f"Total Characters in Universe: `{char_univ.get('total_characters', len(char_univ.get('creative_pool', [])) + len(char_univ.get('canon_characters', [])))}` ",
        "",
        "### Canon Characters (Source Evidence Grounded)",
    ]

    for c in char_univ.get("canon_characters", []):
        lines.append(f"- **{c.get('name')}** ({c.get('species')}, {c.get('breed')}): {c.get('temperament')} • Natural Behavior: {c.get('natural_behavior')}")

    lines.extend([
        "",
        "---",
        "",
        "## 🌳 II. 50 ROOT STORIES (GENERATION 1)",
        f"> The initial root seeds forged from source evidence ({len(root_stories)} Stories).",
        ""
    ])
    for s in root_stories[:50]:
        lines.append(f"### [{s.get('story_id')}] {s.get('title')}")
        lines.append(f"* **Premise**: {s.get('one_line_premise')}")
        lines.append(f"* **Hook**: {s.get('hook')}")
        lines.append(f"* **Twist**: {s.get('twist')}")
        lines.append(f"* **Payoff**: {s.get('payoff')}")
        lines.append("")

    if child_stories:
        lines.extend([
            "---",
            "",
            "## 🌿 III. RECURSIVELY EXPANDED STORIES (GENERATION 2+)",
            f"> Stories expanded from parent nodes ({len(child_stories)} Stories).",
            ""
        ])
        for s in child_stories[:50]:
            lines.append(f"### [{s.get('story_id')}] {s.get('title')} (Parent: {s.get('parent_id')})")
            lines.append(f"* **Premise**: {s.get('one_line_premise')}")
            lines.append(f"* **Hook**: {s.get('hook')}")
            lines.append(f"* **Payoff**: {s.get('payoff')}")
            lines.append("")

    lines.extend([
        "---",
        "",
        "## 🏆 IV. TOP RANKED STORIES (QUALITY & NOVELTY GATE)",
        "> Stories ranked by composite Story Quality Score.",
        ""
    ])

    top_stories = rank_story_universe(stories, top_n=25, sort_by="quality")
    for idx, s in enumerate(top_stories, 1):
        evo = s.get("evolution_metadata", {})
        lines.extend([
            f"### #{idx} [{s.get('story_id')}] {s.get('title')}",
            f"* **World**: `{s.get('world_name', s.get('mode'))}` | **Quality Score**: `{s.get('quality_score', 85.0)}/100` | **Diversity**: `{s.get('diversity_score', 0.85)}`",
            f"* **Parent**: `[{s.get('parent_id')}]` | **Generation**: `{s.get('generation')}`",
            f"* **Premise**: {s.get('one_line_premise')}",
            f"* **Hook**: {s.get('hook')}",
            f"* **Conflict**: {s.get('conflict')}",
            f"* **Twist**: {s.get('twist')}",
            f"* **Payoff**: {s.get('payoff')}",
            f"* **Characters**: {', '.join([c.get('name', '') for c in s.get('characters', [])])}",
            f"* **Relationship**: `{s.get('relationships', {}).get('type', 'COMPANION')}`",
            f"* **New Elements**: `{', '.join(evo.get('new_elements', []))}`",
            ""
        ])

    return "\n".join(lines)

def export_character_bible_markdown(session_id: str) -> str:
    """Exports a comprehensive Character Bible detailing all canon and creative characters."""
    session = get_session(session_id)
    if not session:
        raise ValueError(f"Session not found: {session_id}")

    char_univ = session.get("character_universe", {})
    stories = get_all_stories_for_session(session_id)

    # Count appearances per character
    usage_counts: Dict[str, int] = {}
    for s in stories:
        for c in s.get("characters", []):
            name = c.get("name")
            if name:
                usage_counts[name] = usage_counts.get(name, 0) + 1

    lines = [
        "# 🐾 PLB STORY UNIVERSE — CHARACTER BIBLE",
        f"**Session ID**: `{session_id}`  ",
        f"**Asset**: `{session.get('source_video_name')}`  ",
        f"**Total Characters in Universe**: `{char_univ.get('total_characters', 0)}`  ",
        "",
        "---",
        "",
        "## 👑 CANON CHARACTERS (Direct Forensic Evidence)",
        ""
    ]

    for c in char_univ.get("canon_characters", []):
        lines.extend([
            f"### {c.get('name')} [{c.get('id')}]",
            f"* **Species / Breed**: `{c.get('species')}` • `{c.get('breed')}`",
            f"* **Age & Size**: `{c.get('age_class')}` • `{c.get('size_class')}`",
            f"* **Temperament**: {c.get('temperament')}",
            f"* **Natural Behavior**: {c.get('natural_behavior')}",
            f"* **Movement Style**: {c.get('movement_style')}",
            f"* **Comedy Style**: {c.get('comedy_style')}",
            f"* **Compatible Companions**: `{', '.join(c.get('compatibility', []))}`",
            f"* **Story Appearances in Universe**: `{usage_counts.get(c.get('name'), 0)} Stories`",
            ""
        ])

    lines.extend([
        "---",
        "",
        "## 🎨 CREATIVE CHARACTER POOL",
        "> Controlled domestic animal profiles compatible with the source universe.",
        ""
    ])

    for c in char_univ.get("creative_pool", []):
        lines.extend([
            f"### {c.get('name')} [{c.get('id')}]",
            f"* **Species / Breed**: `{c.get('species')}` • `{c.get('breed')}`",
            f"* **Age & Size**: `{c.get('age_class')}` • `{c.get('size_class')}`",
            f"* **Temperament**: {c.get('temperament')}",
            f"* **Natural Behavior**: {c.get('natural_behavior')}",
            f"* **Movement Style**: {c.get('movement_style')}",
            f"* **Comedy Style**: {c.get('comedy_style')}",
            f"* **Compatible Companions**: `{', '.join(c.get('compatibility', []))}`",
            f"* **Story Appearances in Universe**: `{usage_counts.get(c.get('name'), 0)} Stories`",
            ""
        ])

    return "\n".join(lines)

def export_relationship_graph_markdown(session_id: str) -> str:
    """Exports Relationship Graph documenting dynamics and character pairings."""
    session = get_session(session_id)
    if not session:
        raise ValueError(f"Session not found: {session_id}")

    stories = get_all_stories_for_session(session_id)

    # Aggregate relationship occurrences
    rel_counts: Dict[str, int] = {}
    rel_examples: Dict[str, List[str]] = {}

    for s in stories:
        rel = s.get("relationships", {})
        rtype = rel.get("type", "COMPANION")
        rel_counts[rtype] = rel_counts.get(rtype, 0) + 1
        chars = [c.get("name") for c in s.get("characters", [])]
        pairing = " & ".join(chars)
        if rtype not in rel_examples:
            rel_examples[rtype] = []
        if pairing and pairing not in rel_examples[rtype] and len(rel_examples[rtype]) < 4:
            rel_examples[rtype].append(pairing)

    lines = [
        "# 🤝 PLB STORY UNIVERSE — RELATIONSHIP GRAPH",
        f"**Session ID**: `{session_id}`  ",
        f"**Asset**: `{session.get('source_video_name')}`  ",
        f"**Total Distinct Relationship Dynamics**: `{len(rel_counts)}`  ",
        "",
        "---",
        "",
        "| Relationship Type | Occurrence Count | Example Character Pairings |",
        "| :--- | :--- | :--- |"
    ]

    for rtype, count in sorted(rel_counts.items(), key=lambda x: x[1], reverse=True):
        examples = ", ".join(rel_examples.get(rtype, [])) or "Solo Explorer"
        lines.append(f"| **{rtype.replace('_', ' ').title()}** | `{count}` | {examples} |")

    lines.extend([
        "",
        "---",
        "",
        "### Relationship Dynamics Definitions",
        "- **Friend**: Mutual trust and synchronized reactions.",
        "- **Rival**: Territorial posturing and constant one-upmanship.",
        "- **Sibling**: Playful jealousy and collective mischief.",
        "- **Parent / Cub**: Protective elder guiding a fearless little explorer.",
        "- **Mentor / Student**: Master demonstrating proper form to an eager rookie.",
        "- **Protector**: Sturdy guardian shielding a smaller timid companion.",
        "- **Mismatched Partners**: Distinct species or temperaments paired by circumstance.",
        "- **Unexpected Team**: Former adversaries uniting to defeat a common challenge."
    ])

    return "\n".join(lines)

def export_top_stories_csv(session_id: str) -> str:
    """Exports top ranked stories spreadsheet in standard CSV format."""
    session = get_session(session_id)
    if not session:
        raise ValueError(f"Session not found: {session_id}")

    stories = get_all_stories_for_session(session_id)
    top_stories = rank_story_universe(stories, top_n=100, sort_by="quality")

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "Story ID", "Title", "World", "Quality Score", "Diversity Score",
        "Generation", "Parent ID", "Characters", "Relationship",
        "Setting", "Premise", "Hook", "Twist", "Payoff"
    ])

    for s in top_stories:
        chars_str = ", ".join([c.get("name", "") for c in s.get("characters", [])])
        writer.writerow([
            s.get("story_id"),
            s.get("title"),
            s.get("world_name", s.get("mode")),
            s.get("quality_score"),
            s.get("diversity_score"),
            s.get("generation"),
            s.get("parent_id"),
            chars_str,
            s.get("relationships", {}).get("type", "COMPANION"),
            s.get("setting"),
            s.get("one_line_premise"),
            s.get("hook"),
            s.get("twist"),
            s.get("payoff")
        ])

    return output.getvalue()

def build_full_universe_zip_bundle(session_id: str) -> bytes:
    """Builds complete ZIP bundle containing all Universe documents and keyframes."""
    session = get_session(session_id)
    if not session:
        raise ValueError(f"Session not found: {session_id}")

    json_str = export_universe_json(session_id)
    bible_md = export_story_bible_markdown(session_id)
    char_md = export_character_bible_markdown(session_id)
    rel_md = export_relationship_graph_markdown(session_id)
    top_csv = export_top_stories_csv(session_id)

    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("story_universe.json", json_str.encode("utf-8"))
        z.writestr("story_bible.md", bible_md.encode("utf-8"))
        z.writestr("character_bible.md", char_md.encode("utf-8"))
        z.writestr("relationship_graph.md", rel_md.encode("utf-8"))
        z.writestr("top_stories.csv", top_csv.encode("utf-8"))

        # Cached Keyframe Images
        video_hash = session.get("source_video_hash")
        frames_dir = Path(__file__).resolve().parent.parent / "storage" / "frames" / video_hash
        if frames_dir.exists():
            for f in frames_dir.glob("*.jpg"):
                z.write(f, arcname=f"frames/{f.name}")

    zip_buffer.seek(0)
    return zip_buffer.getvalue()

def export_session_txt(session_id: str) -> str:
    """Exports session summary as formatted plain text."""
    session = get_session(session_id)
    if not session:
        raise ValueError(f"Session not found: {session_id}")
    stories = get_all_stories_for_session(session_id)
    lines = [
        "=" * 70,
        "PLB STORY FORGE — SUMMARY LOG",
        f"Session: {session_id} | Asset: {session.get('source_video_name')}",
        "=" * 70,
        ""
    ]
    for s in stories:
        lines.append(f"[{s.get('story_id')}] {s.get('title')}")
        lines.append(f"Premise: {s.get('one_line_premise')}")
        lines.append(f"Hook: {s.get('hook')}")
        lines.append(f"Conflict: {s.get('conflict')}")
        lines.append(f"Payoff: {s.get('payoff')}")
        lines.append("-" * 40)
    return "\n".join(lines)

# Backward Compatibility Aliases
export_session_json = export_universe_json
export_session_markdown = export_story_bible_markdown
build_session_zip_bundle = build_full_universe_zip_bundle
