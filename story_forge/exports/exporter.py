#!/usr/bin/env python3
"""
Multi-Format Export Engine for PLB Story Forge
==============================================
Exports Story DNA, root stories, recursive generations, and evolution graphs
in JSON, Markdown (Story Bible), TXT, and complete ZIP packages.
"""

import json
import zipfile
import io
from pathlib import Path
from typing import Dict, Any, List

from story_forge.storage.db import (
    get_session,
    get_all_stories_for_session,
    get_lineage_graph
)

def export_session_json(session_id: str) -> str:
    """Exports entire session data, Story DNA, stories, and lineage tree as structured JSON."""
    session = get_session(session_id)
    if not session:
        raise ValueError(f"Session not found: {session_id}")

    stories = get_all_stories_for_session(session_id)
    lineage_tree = get_lineage_graph(session_id)

    export_payload = {
        "export_engine": "PLB Story Forge V1.0",
        "session_id": session_id,
        "created_at": session.get("created_at"),
        "source_video": {
            "name": session.get("source_video_name"),
            "hash": session.get("source_video_hash"),
            "duration_seconds": session.get("duration_seconds"),
            "file_size_bytes": session.get("file_size_bytes")
        },
        "settings": session.get("settings", {}),
        "story_dna": session.get("story_dna", {}),
        "total_stories_count": len(stories),
        "stories": stories,
        "lineage_graph": lineage_tree
    }
    return json.dumps(export_payload, indent=2, ensure_ascii=False)

def export_session_markdown(session_id: str) -> str:
    """Generates an exhaustive, production-grade Story Bible in GitHub-flavored Markdown."""
    session = get_session(session_id)
    if not session:
        raise ValueError(f"Session not found: {session_id}")

    stories = get_all_stories_for_session(session_id)
    dna = session.get("story_dna", {})

    lines = [
        "# 🎬 PLB STORY FORGE — COMPLETE STORY BIBLE",
        f"**Source Asset**: `{session.get('source_video_name')}`  ",
        f"**Asset Hash**: `{session.get('source_video_hash')}`  ",
        f"**Duration**: `{session.get('duration_seconds')}s`  ",
        f"**Created At**: `{session.get('created_at')}`  ",
        f"**Total Generated Concepts**: `{len(stories)}`  ",
        "",
        "---",
        "",
        "## 🧬 I. STORY DNA",
        f"* **Core Premise**: {dna.get('core_premise', 'N/A')}",
        f"* **Central Tension**: {dna.get('central_tension', 'N/A')}",
        f"* **Character Dynamic**: {dna.get('primary_character_dynamic', 'N/A')}",
        f"* **Comedic / Emotional Engine**: {dna.get('primary_comedic_emotional_engine', 'N/A')}",
        f"* **Observed Setting**: {dna.get('setting_observed', dna.get('setting', 'N/A'))}",
        f"* **Core Action Arc**: {dna.get('core_action', 'N/A')}",
        f"* **Hook (0-3s)**: {dna.get('hook', 'N/A')}",
        f"* **Primary Conflict**: {dna.get('conflict', 'N/A')}",
        f"* **Twist**: {dna.get('twist', 'N/A')}",
        f"* **Payoff**: {dna.get('payoff', 'N/A')}",
        "",
        "### Reusable Story Elements",
    ]

    for elem in dna.get("reusable_story_elements", []):
        lines.append(f"- **{elem.get('element')}** ({elem.get('reusability')} Reusability): {elem.get('source')}")

    lines.extend([
        "",
        "---",
        "",
        "## 🌳 II. 50 ROOT STORIES (GENERATION 1)",
        "> Each root story is derived from Story DNA and varies character, goal, conflict, tone, and stakes.",
        ""
    ])

    gen1_stories = [s for s in stories if s.get("generation") == 1]
    for s in gen1_stories:
        lines.extend([
            f"### [{s.get('story_id')}] {s.get('title')}",
            f"* **Mode**: `{s.get('mode')}` | **Diversity Score**: `{s.get('diversity_score')}`",
            f"* **Premise**: {s.get('one_line_premise')}",
            f"* **Hook**: {s.get('hook')}",
            f"* **Goal**: {s.get('goal')}",
            f"* **Conflict**: {s.get('conflict')}",
            f"* **Escalation**: {s.get('escalation')}",
            f"* **Twist**: {s.get('twist')}",
            f"* **Payoff**: {s.get('payoff')}",
            f"* **Emotional Arc**: {s.get('emotional_arc')}",
            f"* **Evidence References**: `{', '.join(s.get('evidence_refs', []))}`",
            ""
        ])

    # Recursive Children (Gen 2+)
    expanded_stories = [s for s in stories if s.get("generation", 1) > 1]
    if expanded_stories:
        lines.extend([
            "---",
            "",
            "## 🌿 III. RECURSIVELY EXPANDED STORIES (GENERATION 2+)",
            "> Child stories branched from selected parent nodes, inheriting core DNA while evolving along dimensional vectors.",
            ""
        ])
        for s in expanded_stories:
            evo = s.get("evolution_metadata", {})
            lines.extend([
                f"### [{s.get('story_id')}] {s.get('title')}",
                f"* **Parent**: `[{s.get('parent_id')}]` | **Generation**: `{s.get('generation')}` | **Novelty Score**: `{evo.get('novelty_score', 'N/A')}`",
                f"* **Changed Dimensions**: `{', '.join(evo.get('changed_dimensions', []))}`",
                f"* **Premise**: {s.get('one_line_premise')}",
                f"* **Conflict**: {s.get('conflict')}",
                f"* **Twist**: {s.get('twist')}",
                f"* **Payoff**: {s.get('payoff')}",
                f"* **New Elements**: {', '.join(evo.get('new_elements', []))}",
                f"* **Inherited Elements**: {', '.join(evo.get('inherited_elements', []))}",
                ""
            ])

    return "\n".join(lines)

def export_session_txt(session_id: str) -> str:
    """Produces clean plain-text log of all generated story concepts."""
    session = get_session(session_id)
    if not session:
        raise ValueError(f"Session not found: {session_id}")

    stories = get_all_stories_for_session(session_id)
    lines = [
        f"PLB STORY FORGE — SUMMARY LOG",
        f"Video: {session.get('source_video_name')} ({session.get('source_video_hash')})",
        f"Generated: {session.get('created_at')}",
        f"Total Stories: {len(stories)}",
        "=" * 70,
        ""
    ]

    for s in stories:
        lines.append(f"[{s.get('story_id')}] (Gen {s.get('generation')}) {s.get('title')}")
        lines.append(f"Mode: {s.get('mode')} | Diversity: {s.get('diversity_score')}")
        lines.append(f"Premise: {s.get('one_line_premise')}")
        lines.append(f"Hook: {s.get('hook')}")
        lines.append(f"Conflict: {s.get('conflict')}")
        lines.append(f"Payoff: {s.get('payoff')}")
        lines.append("-" * 50)

    return "\n".join(lines)

def build_session_zip_bundle(session_id: str) -> bytes:
    """Builds a complete in-memory ZIP package containing JSON, MD, TXT, and keyframes."""
    session = get_session(session_id)
    if not session:
        raise ValueError(f"Session not found: {session_id}")

    json_str = export_session_json(session_id)
    md_str = export_session_markdown(session_id)
    txt_str = export_session_txt(session_id)

    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("story_bible.md", md_str.encode("utf-8"))
        z.writestr("story_data.json", json_str.encode("utf-8"))
        z.writestr("story_summary.txt", txt_str.encode("utf-8"))

        # Include timeline keyframes if cached on disk
        video_hash = session.get("source_video_hash")
        frames_dir = Path(__file__).resolve().parent.parent / "storage" / "frames" / video_hash
        if frames_dir.exists():
            for f in frames_dir.glob("*.jpg"):
                z.write(f, arcname=f"frames/{f.name}")

    zip_buffer.seek(0)
    return zip_buffer.getvalue()
